"""
story_generator.py
Core AI engine for the Luminara Story Generator.

Features:
  - Streaming story generation (Gemini token-by-token stream API)
  - Story continuation with genre-twist streaming
  - Multi-language support: English, Hindi, Bhojpuri
  - Style-specific enriched prompt engineering
  - Language-aware TTS narration
  - Image hashing for versioning
"""

import os
import hashlib
from io import BytesIO
from typing import Generator, Optional

from google import genai
from gtts import gTTS
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

# NOTE: Do NOT cache the key at module level.
# Reading it fresh inside _get_client() ensures Streamlit Cloud secrets
# (injected into os.environ by app.py at startup) are always picked up,
# even if the module was imported before the secrets were available.
MODEL_NAME = "gemini-2.5-flash-lite"

# ─── LANGUAGE CONFIGURATION ───────────────────────────────────────────────────
# Maps UI language name → TTS language code + prompt instruction for Gemini.
# Bhojpuri uses Hindi TTS (closest available in gTTS); Gemini generates
# authentic Bhojpuri prose.

LANGUAGE_CONFIGS = {
    "English": {
        "tts_code": "en",
        "prompt_directive": "Write the entire story in clear, vivid, modern English.",
        "tts_note": None,
    },
    "Hindi": {
        "tts_code": "hi",
        "prompt_directive": (
            "पूरी कहानी हिंदी में लिखें। सरल, आधुनिक और प्रवाहमयी हिंदी का प्रयोग करें। "
            "देवनागरी लिपि में लिखें।"
        ),
        "tts_note": None,
    },
    "Bhojpuri": {
        "tts_code": "hi",   # gTTS has no Bhojpuri code; Hindi voice is closest
        "prompt_directive": (
            "पूरी कहानी भोजपुरी भाषा में लिखें। असली भोजपुरी शब्दों, मुहावरों और "
            "बोलचाल का प्रयोग करें। देवनागरी लिपि में लिखें।"
        ),
        "tts_note": "Bhojpuri narration uses Hindi voice (closest available in TTS).",
    },
}

# ─── STYLE-SPECIFIC PROMPT DIRECTIVES ─────────────────────────────────────────

_STYLE_DIRECTIVES = {
    "Comedy": (
        "Make it laugh-out-loud funny. Use comedic timing, absurd escalations, "
        "witty dialogue, and unexpected punchlines. Each image should introduce a "
        "new layer of chaos or irony that builds to a hilarious conclusion."
    ),
    "Thriller": (
        "Build dread from the first sentence. Use short, punchy sentences at peak "
        "tension. Introduce an unseen threat, a ticking clock, and a twist the reader "
        "never sees coming. Leave them breathless."
    ),
    "Fairy Tale": (
        "Open with 'Once upon a time' energy. Include magical beings, enchanted objects, "
        "a clear moral lesson, and a triumphant resolution. Use lyrical, warm language "
        "that appeals to imagination."
    ),
    "Sci-Fi": (
        "Ground the story in plausible future science — AI, space travel, genetic "
        "engineering, or quantum phenomena. Introduce a technological dilemma and explore "
        "its human consequences. Think Arthur C. Clarke meets Ursula Le Guin."
    ),
    "Mystery": (
        "Open with an unexplained anomaly. Plant exactly three red herrings. Build "
        "clues across each image-scene. The final image must contain the key that "
        "unlocks the mystery. Resolution should feel both surprising and inevitable."
    ),
    "Adventure": (
        "Launch immediately into action. Feature a protagonist with a clear goal, "
        "escalating obstacles tied to each image, a moment of near-failure, and a "
        "triumphant resolution earned through courage and ingenuity."
    ),
    "Morale": (
        "Weave a profound life lesson through the narrative without being preachy. "
        "Show, don't tell. The moral should emerge organically from the characters' "
        "choices and consequences across each image-scene."
    ),
}


# ─── PROMPT BUILDERS ──────────────────────────────────────────────────────────

def create_advanced_prompt(style: str, language: str = "English") -> str:
    """
    Construct a style-specific, language-aware system prompt for first-chapter
    story generation from images.
    """
    directive = _STYLE_DIRECTIVES.get(
        style,
        "Write a compelling and engaging story that captivates the reader."
    )
    lang = LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS["English"])
    lang_directive = lang["prompt_directive"]

    return f"""You are a master storyteller — precise, evocative, and deeply skilled \
in the {style} genre.

═══ YOUR MISSION ═══
Create a single, seamless {style} story that weaves ALL provided images into one \
cohesive narrative. Each image represents a distinct scene or story beat.

═══ CRAFT REQUIREMENTS ═══
Genre Direction : {directive}
Structure       : Strong hook → Rising action → Climax → Satisfying resolution
Perspective     : Third-person with close emotional interiority
Length          : 350–500 words — immersive but tightly edited
Imagery         : Each uploaded image must correspond to a specific story moment

═══ LANGUAGE ═══
{lang_directive}

═══ STRICT RULES ═══
• Begin the story immediately — no meta-commentary, no "Here is your story"
• Do NOT reference "the images" or "the pictures" in the story text
• Every scene transition must feel natural and motivated
• The final sentence must deliver emotional or narrative closure

Begin now."""


def summarize_story(story_text: str, language: str = "English") -> str:
    """
    Generate a structured narrative snapshot of the story so far.

    This is used as handoff context before generating a continuation chapter.
    A structured summary gives the model clear knowledge of characters, setting,
    and the exact moment the story ended — preventing it from treating the
    continuation as a fresh start.

    Returns the summary string, or a fallback excerpt on failure.
    """
    client = _get_client()
    lang = LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS["English"])
    lang_directive = lang["prompt_directive"]

    prompt = f"""You are a story analyst. Read the following story carefully.

STORY:
{story_text}

Create a precise narrative snapshot using this exact structure:

CHARACTERS: Name every character, their defining personality trait, and their \
emotional state at the story's end.
SETTING: The specific location(s) and time context established in the story.
KEY EVENTS: The 3–5 most plot-critical things that happened, in chronological order.
ENDING MOMENT: The EXACT final scene, action, or line of dialogue the story \
ends on. Be specific — this is the precise point the next chapter must continue from.
OPEN THREADS: Unresolved tensions, mysteries, or questions the story leaves hanging.

Language for the snapshot: {lang_directive}

Keep each section to 1–3 sentences. Be factual and specific — this snapshot \
will be used to write the next chapter."""

    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=[prompt])
        return response.text or ""
    except Exception as exc:
        print(f"[summarize_story] Failed, using excerpt fallback: {exc}")
        # Fallback: return the last 400 words as rough context
        words = story_text.split()
        return " ".join(words[-400:]) if len(words) > 400 else story_text


def create_continuation_prompt(
    summary: str,
    last_excerpt: str,
    twist_style: str,
    chapter_num: int,
    language: str = "English",
) -> str:
    """
    Build the continuation prompt using a structured story summary + last excerpt.

    Two-layer context strategy:
      summary      — structured snapshot (characters, setting, plot state, ending moment)
                     gives the model deep narrative understanding
      last_excerpt — verbatim last ~250 words of the previous chapter
                     anchors the model's tone, voice, and exact continuation point
    """
    directive = _STYLE_DIRECTIVES.get(
        twist_style,
        "Make the next chapter engaging and surprising."
    )
    lang = LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS["English"])
    lang_directive = lang["prompt_directive"]

    return f"""You are a master serialised storyteller writing Chapter {chapter_num}.

═══ STORY SNAPSHOT (what has happened so far) ═══
{summary}

═══ FINAL LINES OF CHAPTER {chapter_num - 1} (continue from exactly here) ═══
{last_excerpt}

═══ YOUR TASK ═══
Write Chapter {chapter_num} as a SEAMLESS continuation.
• Your first sentence must follow DIRECTLY from the final line above — same \
scene, same characters, same emotional register
• Do NOT recap, summarise, or reference previous chapters
• The reader should not feel any gap between the last line above and your first word

═══ GENRE TWIST ═══
Introduce a {twist_style} energy into this chapter:
{directive}

Blend the twist naturally — it must grow from the existing characters and \
situation, not replace them. The world and people stay the same; the genre \
energy shifts.

═══ LANGUAGE ═══
{lang_directive}

═══ CHAPTER REQUIREMENTS ═══
• No chapter heading, no "Previously…", no preamble — start writing immediately
• 300–450 words
• End on a hook or cliffhanger that makes Chapter {chapter_num + 1} feel inevitable
• Every sentence advances the story

Begin:"""


# ─── IMAGE UTILITIES ──────────────────────────────────────────────────────────

def compute_image_hash(image: Image.Image) -> str:
    """8-char MD5 fingerprint for a PIL Image (used by history versioning)."""
    buf = BytesIO()
    image.save(buf, format="PNG")
    return hashlib.md5(buf.getvalue()).hexdigest()[:8]


# ─── CLIENT FACTORY ───────────────────────────────────────────────────────────

def _get_client() -> genai.Client:
    """
    Return an authenticated Gemini client.
    Reads the API key fresh on every call so that keys injected into
    os.environ after module import (e.g. from Streamlit Cloud secrets)
    are always picked up correctly.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GOOGLE_API_KEY is not set. "
            "Add it to your .env file (local) or Streamlit Cloud secrets (deployed)."
        )
    return genai.Client(api_key=api_key)


def _build_contents(images: list, style: str, language: str = "English") -> list:
    """Flat content list: [prompt_string, img1, img2, ...]"""
    return [create_advanced_prompt(style, language)] + images


# ─── STREAMING: FIRST CHAPTER FROM IMAGES ─────────────────────────────────────

def generate_story_streaming(
    images: list,
    style: str,
    language: str = "English",
) -> Generator[str, None, None]:
    """
    Stream the first chapter of a story from uploaded images.

    Yields token chunks as Gemini produces them. Falls back to single-shot
    generation if generate_content_stream is unavailable on the SDK version.
    """
    client = _get_client()
    contents = _build_contents(images, style, language)

    try:
        for chunk in client.models.generate_content_stream(
            model=MODEL_NAME,
            contents=contents,
        ):
            if chunk.text:
                yield chunk.text

    except AttributeError:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
        )
        if response.text:
            yield response.text


# ─── STREAMING: STORY CONTINUATION WITH TWIST ─────────────────────────────────

def generate_continuation_streaming(
    summary: str,
    last_excerpt: str,
    twist_style: str,
    chapter_num: int,
    language: str = "English",
) -> Generator[str, None, None]:
    """
    Stream the next chapter of a story using a two-layer context strategy.

    Args:
        summary:      Structured narrative snapshot (from summarize_story()).
        last_excerpt: Verbatim last ~250 words of the previous chapter.
        twist_style:  Genre to introduce in this chapter (e.g. "Thriller").
        chapter_num:  The chapter number being written (2, 3, 4…).
        language:     Language for output ("English", "Hindi", "Bhojpuri").

    Yields:
        str: Token chunks as the model produces them.
    """
    client = _get_client()
    prompt = create_continuation_prompt(
        summary, last_excerpt, twist_style, chapter_num, language
    )

    try:
        for chunk in client.models.generate_content_stream(
            model=MODEL_NAME,
            contents=[prompt],
        ):
            if chunk.text:
                yield chunk.text

    except AttributeError:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt],
        )
        if response.text:
            yield response.text


# ─── NON-STREAMING FALLBACK ───────────────────────────────────────────────────

def generate_story_from_images(
    images: list,
    style: str,
    language: str = "English",
) -> str:
    """Single-shot (non-streaming) story generation. Returns full text."""
    client = _get_client()
    contents = _build_contents(images, style, language)
    response = client.models.generate_content(model=MODEL_NAME, contents=contents)
    if not response.text:
        raise ValueError("Gemini returned an empty response. Please retry.")
    return response.text


# ─── TTS NARRATION ────────────────────────────────────────────────────────────

def narrate_story(story_text: str, language: str = "English") -> Optional[BytesIO]:
    """
    Convert story text to MP3 audio using language-appropriate TTS voice.

    Returns BytesIO MP3 buffer, or None on failure (non-fatal).
    """
    if not story_text or not story_text.strip():
        return None

    lang_config = LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS["English"])
    tts_code = lang_config["tts_code"]

    try:
        tts = gTTS(text=story_text.strip(), lang=tts_code, slow=False)
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer

    except Exception as exc:
        print(f"[narrate_story] TTS error ({language}/{tts_code}): {exc}")
        return None


def get_tts_note(language: str) -> Optional[str]:
    """Return a user-facing note about TTS limitations for the given language."""
    return LANGUAGE_CONFIGS.get(language, {}).get("tts_note")
