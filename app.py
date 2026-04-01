"""
app.py
Luminara — AI Story Engine  v2.2
Yellow/Black Glassmorphism UI with:
  - Real-time streaming story generation          [Feature 1]
  - Story versioning & history                   [Feature 2]
  - Multi-chapter continuation with twist genre  [Feature 3]
  - Download full story as .txt                  [Feature 4]
  - Multi-language: English / Hindi / Bhojpuri   [Feature 5]
"""

import html
from datetime import datetime

import streamlit as st
from PIL import Image

from story_generator import (
    generate_story_streaming,
    generate_continuation_streaming,
    summarize_story,
    narrate_story,
    get_tts_note,
    LANGUAGE_CONFIGS,
)
from story_history import (
    save_story,
    get_all_stories,
    delete_story,
    clear_all_history,
    get_stats,
)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Luminara · AI Story Engine",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM — Yellow/Black Glassmorphism (Apple Liquid Glass)
# ═══════════════════════════════════════════════════════════════════════════════

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,700;1,500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.stApp {
    background:
        radial-gradient(ellipse 80% 60% at 10% 40%, rgba(255,215,0,0.04) 0%, transparent 70%),
        radial-gradient(ellipse 60% 50% at 90% 10%, rgba(255,215,0,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 50% 70% at 50% 90%, rgba(255,180,0,0.03) 0%, transparent 70%),
        linear-gradient(160deg, #080808 0%, #0e0e0e 40%, #080808 100%);
    font-family: 'Inter', sans-serif;
    color: #efefef;
    min-height: 100vh;
}

#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }

[data-testid="stSidebar"] {
    background: rgba(6,6,6,0.85) !important;
    backdrop-filter: blur(40px) saturate(1.2) !important;
    -webkit-backdrop-filter: blur(40px) saturate(1.2) !important;
    border-right: 1px solid rgba(255,215,0,0.12) !important;
    box-shadow: 4px 0 40px rgba(0,0,0,0.6) !important;
}
[data-testid="stSidebar"] > div:first-child { background: transparent !important; }

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1100px !important;
}

/* ── GLASS CARD ── */
.glass-card {
    background: rgba(255,255,255,0.025);
    backdrop-filter: blur(24px) saturate(1.4);
    -webkit-backdrop-filter: blur(24px) saturate(1.4);
    border: 1px solid rgba(255,215,0,0.13);
    border-radius: 20px;
    padding: 28px 32px;
    margin: 14px 0;
    box-shadow: 0 8px 40px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,215,0,0.09);
    transition: border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}
.glass-card:hover {
    border-color: rgba(255,215,0,0.25);
    box-shadow: 0 12px 50px rgba(255,215,0,0.06), 0 8px 40px rgba(0,0,0,0.45);
    transform: translateY(-1px);
}

/* ── HERO ── */
.hero-wrap { text-align: center; padding: 36px 20px 28px; }
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.4rem, 5vw, 3.8rem);
    font-weight: 700;
    background: linear-gradient(135deg, #FFD700 0%, #FFF4B0 45%, #FFC200 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1.5px;
    line-height: 1.05;
}
.hero-subtitle {
    margin-top: 10px;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 3.5px;
    text-transform: uppercase;
    color: rgba(255,215,0,0.45);
}
.hero-divider {
    width: 60px; height: 2px;
    background: linear-gradient(90deg, transparent, #FFD700, transparent);
    margin: 18px auto 0;
    border-radius: 1px;
}

/* ── SECTION LABEL ── */
.section-label {
    font-size: 0.65rem; font-weight: 600;
    letter-spacing: 2.5px; text-transform: uppercase;
    color: rgba(255,215,0,0.55);
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 10px;
}
.section-label::after {
    content: ''; flex: 1; height: 1px;
    background: rgba(255,215,0,0.12);
}

/* ── GOLD DIVIDER ── */
.gold-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(255,215,0,0.3) 50%, transparent 100%);
    margin: 22px 0; border: none;
}

/* ── CHAPTER HEADER ── */
.chapter-header {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 0 6px;
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: 2px; text-transform: uppercase;
    color: rgba(255,215,0,0.6);
    border-bottom: 1px solid rgba(255,215,0,0.12);
    margin-bottom: 16px; margin-top: 28px;
}
.chapter-header:first-child { margin-top: 0; }

/* ── STORY DISPLAY ── */
.story-display {
    background: rgba(255,215,0,0.018);
    border: 1px solid rgba(255,215,0,0.10);
    border-radius: 16px;
    padding: 36px 40px;
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.07rem; font-weight: 400;
    line-height: 1.9;
    color: #ddd8cc;
    position: relative; overflow: hidden;
}
.story-display::before {
    content: '\\201C';
    position: absolute; top: -30px; left: 24px;
    font-size: 9rem; color: rgba(255,215,0,0.04);
    font-family: 'Playfair Display', serif;
    line-height: 1; pointer-events: none; user-select: none;
}
.story-display p { margin-bottom: 1.2em; }
.story-display p:last-child { margin-bottom: 0; }

/* ── CONTINUATION PANEL ── */
.continuation-panel {
    background: rgba(255,215,0,0.03);
    border: 1px solid rgba(255,215,0,0.12);
    border-radius: 16px;
    padding: 22px 28px;
    margin: 20px 0;
}
.continuation-title {
    font-size: 0.68rem; font-weight: 600;
    letter-spacing: 2px; text-transform: uppercase;
    color: rgba(255,215,0,0.55);
    margin-bottom: 14px;
    display: flex; align-items: center; gap: 8px;
}

/* ── DOWNLOAD STRIP ── */
.download-strip {
    display: flex; align-items: center; gap: 12px;
    padding: 14px 20px;
    background: rgba(255,215,0,0.04);
    border: 1px solid rgba(255,215,0,0.12);
    border-radius: 12px;
    margin: 10px 0;
}

/* ── STREAMING CURSOR ── */
.stream-cursor {
    display: inline-block; width: 2px; height: 1.1em;
    background: #FFD700; margin-left: 2px;
    vertical-align: text-bottom; border-radius: 1px;
    animation: cursor-blink 0.85s ease-in-out infinite;
}
@keyframes cursor-blink {
    0%, 100% { opacity: 1; } 50% { opacity: 0; }
}

/* ── STYLE BADGE ── */
.style-badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 14px;
    background: rgba(255,215,0,0.08);
    border: 1px solid rgba(255,215,0,0.25);
    border-radius: 30px;
    font-size: 0.72rem; font-weight: 600; color: #FFD700;
    letter-spacing: 0.5px; text-transform: uppercase;
}
.lang-badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 14px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 30px;
    font-size: 0.72rem; font-weight: 500; color: rgba(255,255,255,0.5);
}

/* ── METRIC CARDS ── */
.metric-row { display: flex; gap: 10px; margin: 10px 0; }
.metric-card {
    flex: 1; background: rgba(255,215,0,0.04);
    border: 1px solid rgba(255,215,0,0.10);
    border-radius: 14px; padding: 14px 10px; text-align: center;
}
.metric-value { font-size: 1.6rem; font-weight: 700; color: #FFD700; line-height: 1; }
.metric-label {
    font-size: 0.6rem; color: rgba(255,255,255,0.35);
    text-transform: uppercase; letter-spacing: 1.5px; margin-top: 5px;
}

/* ── HISTORY ITEMS ── */
.history-item {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,215,0,0.08);
    border-radius: 12px; padding: 13px 16px; margin: 7px 0;
    transition: all 0.2s ease;
}
.history-item:hover { background: rgba(255,215,0,0.04); border-color: rgba(255,215,0,0.2); }
.history-meta { font-size: 0.68rem; color: rgba(255,255,255,0.35); margin-top: 4px; }
.history-preview {
    font-size: 0.78rem; color: rgba(255,255,255,0.55); margin-top: 6px;
    display: -webkit-box; -webkit-line-clamp: 2;
    -webkit-box-orient: vertical; overflow: hidden;
}
.version-pill {
    display: inline-block; padding: 1px 8px;
    background: rgba(255,215,0,0.1); border-radius: 10px;
    font-size: 0.62rem; color: rgba(255,215,0,0.7); font-weight: 600; margin-left: 6px;
}
.chapter-pill {
    display: inline-block; padding: 1px 8px;
    background: rgba(255,255,255,0.06); border-radius: 10px;
    font-size: 0.62rem; color: rgba(255,255,255,0.4); font-weight: 500; margin-left: 4px;
}

/* ── WELCOME STATE ── */
.welcome-state { text-align: center; padding: 60px 20px; }
.welcome-icon { font-size: 3.5rem; margin-bottom: 16px; opacity: 0.4; }
.welcome-text { font-size: 0.9rem; color: rgba(255,255,255,0.35); line-height: 1.7; max-width: 380px; margin: 0 auto; }
.welcome-steps { display: flex; justify-content: center; gap: 28px; margin-top: 28px; flex-wrap: wrap; }
.welcome-step { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.step-num {
    width: 32px; height: 32px; border-radius: 50%;
    background: rgba(255,215,0,0.1); border: 1px solid rgba(255,215,0,0.2);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 600; color: #FFD700;
}
.step-text { font-size: 0.68rem; color: rgba(255,255,255,0.3); text-align: center; }

/* ── SIDEBAR BRAND ── */
.sidebar-brand { padding: 28px 24px 20px; border-bottom: 1px solid rgba(255,215,0,0.08); margin-bottom: 4px; }
.brand-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.55rem; font-weight: 700;
    background: linear-gradient(135deg, #FFD700 0%, #FFF0A0 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    letter-spacing: -0.5px;
}
.brand-tagline { font-size: 0.62rem; color: rgba(255,215,0,0.35); text-transform: uppercase; letter-spacing: 2px; margin-top: 3px; }

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #FFD700 0%, #FFC000 100%) !important;
    color: #000000 !important; border: none !important; border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
    font-size: 0.88rem !important; letter-spacing: 0.3px !important;
    padding: 11px 20px !important; width: 100% !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 20px rgba(255,215,0,0.22), 0 1px 0 rgba(255,255,255,0.15) inset !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #FFE04D 0%, #FFD700 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(255,215,0,0.35) !important;
}
.stButton > button:active { transform: translateY(0) !important; }
.stButton > button[kind="secondary"] {
    background: rgba(255,215,0,0.06) !important;
    color: rgba(255,215,0,0.8) !important;
    border: 1px solid rgba(255,215,0,0.2) !important;
    box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(255,215,0,0.1) !important;
    border-color: rgba(255,215,0,0.35) !important;
}

/* Download button override */
.stDownloadButton > button {
    background: rgba(255,255,255,0.05) !important;
    color: rgba(255,215,0,0.85) !important;
    border: 1px solid rgba(255,215,0,0.25) !important;
    border-radius: 10px !important;
    font-size: 0.82rem !important; font-weight: 500 !important;
    box-shadow: none !important; width: auto !important;
    padding: 8px 18px !important;
}
.stDownloadButton > button:hover {
    background: rgba(255,215,0,0.08) !important;
    border-color: rgba(255,215,0,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── SELECTS ── */
.stSelectbox label {
    color: rgba(255,215,0,0.6) !important; font-size: 0.65rem !important;
    font-weight: 600 !important; letter-spacing: 2px !important; text-transform: uppercase !important;
}
.stSelectbox > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,215,0,0.18) !important; border-radius: 10px !important; color: #f0f0f0 !important;
}
.stSelectbox > div > div:hover { border-color: rgba(255,215,0,0.35) !important; }

/* ── FILE UPLOADER ── */
.stFileUploader label {
    color: rgba(255,215,0,0.6) !important; font-size: 0.65rem !important;
    font-weight: 600 !important; letter-spacing: 2px !important; text-transform: uppercase !important;
}
[data-testid="stFileUploader"] {
    background: rgba(255,215,0,0.02) !important;
    border: 1px dashed rgba(255,215,0,0.22) !important; border-radius: 12px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(255,215,0,0.4) !important; background: rgba(255,215,0,0.04) !important;
}

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    background: rgba(255,215,0,0.03) !important;
    border: 1px solid rgba(255,215,0,0.10) !important; border-radius: 10px !important;
    color: rgba(255,215,0,0.65) !important; font-size: 0.72rem !important;
    font-weight: 600 !important; letter-spacing: 1.5px !important; text-transform: uppercase !important;
}
.streamlit-expanderContent {
    background: transparent !important;
    border: 1px solid rgba(255,215,0,0.08) !important;
    border-top: none !important; border-radius: 0 0 10px 10px !important;
}

/* ── SPINNER ── */
.stSpinner > div { border-color: rgba(255,215,0,0.8) rgba(255,215,0,0.2) rgba(255,215,0,0.2) !important; }

/* ── ALERTS ── */
.stSuccess { background: rgba(0,210,80,0.05) !important; border: 1px solid rgba(0,210,80,0.2) !important; border-radius: 10px !important; }
.stError   { background: rgba(255,60,60,0.05) !important; border: 1px solid rgba(255,60,60,0.2) !important; border-radius: 10px !important; }
.stWarning { background: rgba(255,215,0,0.04) !important; border: 1px solid rgba(255,215,0,0.2) !important; border-radius: 10px !important; }
.stInfo    { background: rgba(255,215,0,0.04) !important; border: 1px solid rgba(255,215,0,0.18) !important; border-radius: 10px !important; color: rgba(255,215,0,0.8) !important; }

/* ── AUDIO ── */
audio { width: 100% !important; border-radius: 10px !important; margin-top: 4px !important; filter: invert(0.85) hue-rotate(180deg) saturate(0.6) !important; }

/* ── IMAGES ── */
[data-testid="stImage"] img {
    border-radius: 10px !important; border: 1px solid rgba(255,215,0,0.12) !important;
    transition: transform 0.3s ease, box-shadow 0.3s ease !important;
}
[data-testid="stImage"] img:hover { transform: scale(1.02) !important; box-shadow: 0 8px 30px rgba(0,0,0,0.5) !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
::-webkit-scrollbar-thumb { background: rgba(255,215,0,0.25); border-radius: 2px; }

/* ── ANIMATIONS ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
.animate-fade-in { animation: fadeInUp 0.5s cubic-bezier(0.25,0.46,0.45,0.94) forwards; }

/* ── GEN STATUS ── */
.gen-status {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 16px;
    background: rgba(255,215,0,0.05); border: 1px solid rgba(255,215,0,0.15);
    border-radius: 10px; font-size: 0.78rem; color: rgba(255,215,0,0.75); margin-bottom: 14px;
}
.gen-dot {
    width: 7px; height: 7px; background: #FFD700; border-radius: 50%; flex-shrink: 0;
    animation: pulse-dot 1.2s ease-in-out infinite;
}
@keyframes pulse-dot { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.4;transform:scale(0.7)} }
</style>
"""

st.markdown(THEME_CSS, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

STYLES = ("Comedy", "Thriller", "Fairy Tale", "Sci-Fi", "Mystery", "Adventure", "Morale")
LANGUAGES = list(LANGUAGE_CONFIGS.keys())   # ["English", "Hindi", "Bhojpuri"]

STYLE_ICONS = {
    "Comedy": "😂", "Thriller": "🔪", "Fairy Tale": "🧚",
    "Sci-Fi": "🚀", "Mystery": "🔍", "Adventure": "⚔️", "Morale": "💛",
}
LANG_FLAGS = {"English": "🇬🇧", "Hindi": "🇮🇳", "Bhojpuri": "🪘"}


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════

def _init_state() -> None:
    defaults = {
        "all_chapters": [],          # List[str] — text of each chapter
        "chapter_genres": [],        # List[str] — genre per chapter
        "current_story": None,       # str — combined text of all chapters
        "current_style": None,       # str — initial (Chapter 1) genre
        "current_language": "English",
        "current_images": None,      # List[PIL.Image]
        "current_image_names": None, # List[str]
        "audio_buffer": None,        # BytesIO — audio for full story
        "last_entry_id": None,
        "restore_story": None,       # dict — loaded from history
        "is_generating": False,
        "is_continuing": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _escape(text: str) -> str:
    return html.escape(text)


def _render_story_html(text: str, streaming: bool = False) -> str:
    """Convert raw story text into styled HTML paragraphs."""
    escaped = _escape(text)
    raw_paras = escaped.replace("\r\n", "\n").split("\n\n")
    paras = []
    for p in raw_paras:
        s = p.strip()
        if s:
            paras.append(f"<p>{s.replace(chr(10), '<br>')}</p>")
    body = "\n".join(paras) if paras else escaped
    cursor = '<span class="stream-cursor"></span>' if streaming else ""
    return f'<div class="story-display animate-fade-in">{body}{cursor}</div>'


def _render_chapters(chapters: list, genres: list) -> None:
    """Render all chapters with chapter headers when there are multiple."""
    if len(chapters) == 1:
        st.markdown(_render_story_html(chapters[0]), unsafe_allow_html=True)
    else:
        for i, (chapter, genre) in enumerate(zip(chapters, genres)):
            icon = STYLE_ICONS.get(genre, "")
            label = "Opening Chapter" if i == 0 else f"Chapter {i + 1} — {icon} {genre} Twist"
            st.markdown(
                f'<div class="chapter-header">{label}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(_render_story_html(chapter), unsafe_allow_html=True)


def _metric_card(value: str, label: str) -> str:
    return (
        f'<div class="metric-card">'
        f'<div class="metric-value">{value}</div>'
        f'<div class="metric-label">{label}</div>'
        f'</div>'
    )


def _format_download_text(
    chapters: list,
    genres: list,
    language: str,
    image_names: list,
) -> str:
    """Format the full multi-chapter story as a clean plain-text download."""
    now = datetime.now().strftime("%B %d, %Y at %H:%M")
    genre_chain = " → ".join(f"{STYLE_ICONS.get(g,'')} {g}" for g in genres)
    header = (
        f"LUMINARA — AI STORY ENGINE\n"
        f"{'═' * 50}\n"
        f"Generated : {now}\n"
        f"Language  : {language}\n"
        f"Genre Path: {genre_chain}\n"
        f"Images    : {', '.join(image_names) if image_names else 'N/A'}\n"
        f"{'═' * 50}\n\n"
    )
    body = ""
    for i, (chapter, genre) in enumerate(zip(chapters, genres)):
        if len(chapters) > 1:
            label = "Chapter 1 — Opening" if i == 0 else f"Chapter {i+1} — {genre} Twist"
            body += f"{'─' * 50}\n{label}\n{'─' * 50}\n\n"
        body += chapter.strip() + "\n\n"
    footer = f"\n{'═' * 50}\n© Luminara AI Story Engine\n"
    return header + body + footer


def _story_meta_bar(chapters: list, genres: list, language: str) -> str:
    """One-line HTML meta badges shown below the story."""
    icon = STYLE_ICONS.get(genres[0], "") if genres else ""
    flag = LANG_FLAGS.get(language, "")
    wc = sum(len(c.split()) for c in chapters)
    ch_label = f"{len(chapters)} chapter{'s' if len(chapters)>1 else ''}"
    return (
        f'<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:10px 0;">'
        f'<span class="style-badge">{icon} {genres[0] if genres else ""}</span>'
        f'<span class="lang-badge">{flag} {language}</span>'
        f'<span style="font-size:0.68rem;color:rgba(255,255,255,0.3);">'
        f'{wc} words · {ch_label}</span>'
        f'</div>'
    )


def _show_narration_section(story_text: str, language: str) -> None:
    """Render the narration section, re-generating audio if needed."""
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Full Narration</div>', unsafe_allow_html=True)

    tts_note = get_tts_note(language)
    if tts_note:
        st.info(f"ℹ️ {tts_note}")

    if st.session_state.audio_buffer is None:
        with st.spinner("Generating audio narration…"):
            st.session_state.audio_buffer = narrate_story(story_text, language)

    if st.session_state.audio_buffer:
        st.audio(st.session_state.audio_buffer, format="audio/mp3")
    else:
        st.warning("Audio narration unavailable. Check your internet connection.")


def _show_continuation_panel(language: str) -> tuple:
    """
    Render the 'Continue Story' panel below the current story.
    Returns the twist style and whether the continue button was clicked.
    Streamlit re-runs handle the actual generation logic in the caller.
    """
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="continuation-title">✦ Continue the Story</div>',
        unsafe_allow_html=True,
    )

    chapter_count = len(st.session_state.all_chapters)
    st.markdown(
        f'<p style="font-size:0.72rem;color:rgba(255,255,255,0.3);margin-bottom:14px;">'
        f'Add Chapter {chapter_count + 1} with a genre twist</p>',
        unsafe_allow_html=True,
    )

    col_sel, col_btn = st.columns([3, 2])
    with col_sel:
        twist = st.selectbox(
            "Twist Genre",
            STYLES,
            key="twist_genre_select",
            label_visibility="collapsed",
        )
        st.markdown(
            f'<p style="font-size:0.68rem;color:rgba(255,255,255,0.3);margin-top:4px;">'
            f'{STYLE_ICONS.get(twist,"")} {twist} twist for Ch. {chapter_count + 1}</p>',
            unsafe_allow_html=True,
        )
    with col_btn:
        continue_clicked = st.button(
            f"✦ Add Chapter {chapter_count + 1}",
            key="continue_btn",
            disabled=st.session_state.is_continuing or st.session_state.is_generating,
        )

    return twist, continue_clicked


def _show_download_button(chapters: list, genres: list, language: str, image_names: list) -> None:
    """Render the download-as-txt button."""
    download_text = _format_download_text(chapters, genres, language, image_names)
    ch_label = f"{len(chapters)}ch" if len(chapters) > 1 else "1ch"
    filename = f"luminara_{genres[0].lower().replace(' ','_')}_{ch_label}.txt"
    st.download_button(
        label="⬇ Download Story (.txt)",
        data=download_text.encode("utf-8"),
        file_name=filename,
        mime="text/plain",
        key="download_btn",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand">'
        '<div class="brand-name">✦ Luminara</div>'
        '<div class="brand-tagline">AI Story Engine</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Image upload ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Images</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Upload Images",
        type=["png", "jpeg", "jpg", "webp"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if uploaded_files:
        count = len(uploaded_files)
        color = "#FFD700" if count <= 10 else "#ff6060"
        st.markdown(
            f'<p style="font-size:0.7rem;color:{color};margin:4px 0 12px;">'
            f'{"✓" if count<=10 else "✗"} {count}/10 image{"s" if count!=1 else ""} selected</p>',
            unsafe_allow_html=True,
        )

    # ── Story style ───────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Story Style</div>', unsafe_allow_html=True)
    story_style = st.selectbox("Story Style", STYLES, label_visibility="collapsed")
    st.markdown(
        f'<p style="font-size:0.72rem;color:rgba(255,255,255,0.3);margin:4px 0 0;">'
        f'{STYLE_ICONS.get(story_style,"")} {story_style} narrative</p>',
        unsafe_allow_html=True,
    )

    # ── Language ──────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Language</div>', unsafe_allow_html=True)
    language = st.selectbox("Language", LANGUAGES, label_visibility="collapsed")
    st.markdown(
        f'<p style="font-size:0.72rem;color:rgba(255,255,255,0.3);margin:4px 0 0;">'
        f'{LANG_FLAGS.get(language,"")} Story and narration in {language}</p>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Generate button ───────────────────────────────────────────────────────
    generate_button = st.button(
        "✦ Generate Story",
        type="primary",
        disabled=st.session_state.is_generating or st.session_state.is_continuing,
    )

    # ── Reset button ──────────────────────────────────────────────────────────
    reset_button = st.button(
        "↺ Reset",
        type="secondary",
        disabled=st.session_state.is_generating or st.session_state.is_continuing,
        help="Clear the current story, images, and audio. History is preserved.",
    )
    if reset_button:
        # Reset list fields to empty lists, booleans to False, everything else to None.
        # Do NOT call st.rerun() here — the button click already schedules a rerun.
        # Calling st.rerun() inside a `with st.sidebar:` block raises RerunException
        # mid-render and leaves the app in a broken state.
        list_keys = {"all_chapters", "chapter_genres"}
        bool_keys = {"is_generating", "is_continuing"}
        for key in [
            "all_chapters", "chapter_genres", "current_story", "current_style",
            "current_images", "current_image_names", "audio_buffer",
            "last_entry_id", "restore_story", "is_generating", "is_continuing",
        ]:
            if key in list_keys:
                st.session_state[key] = []
            elif key in bool_keys:
                st.session_state[key] = False
            else:
                st.session_state[key] = None
        st.session_state.current_language = "English"
        # No st.rerun() — button click handles the rerun automatically

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # ── Stats ─────────────────────────────────────────────────────────────────
    stats = get_stats()
    if stats["total"] > 0:
        st.markdown('<div class="section-label">Your Library</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="metric-row">'
            f'{_metric_card(str(stats["total"]), "Stories")}'
            f'{_metric_card(str(stats["avg_words"]), "Avg Words")}'
            f'</div>',
            unsafe_allow_html=True,
        )
        if stats["most_used_style"]:
            icon = STYLE_ICONS.get(stats["most_used_style"], "")
            st.markdown(
                f'<p style="font-size:0.68rem;color:rgba(255,255,255,0.3);margin:6px 0 0;">'
                f'Favourite: <span style="color:rgba(255,215,0,0.65);">{icon} {stats["most_used_style"]}</span></p>',
                unsafe_allow_html=True,
            )
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # ── History panel ─────────────────────────────────────────────────────────
    history_entries = get_all_stories(limit=10)
    if history_entries:
        with st.expander(f"Story History  ({len(history_entries)})"):
            for entry in history_entries:
                icon = STYLE_ICONS.get(entry["style"], "")
                preview = entry["story"][:90].replace("\n", " ") + "…"
                ver = entry.get("version", 1)
                ch_count = entry.get("chapter_count", 1)
                lang = entry.get("language", "English")
                flag = LANG_FLAGS.get(lang, "")
                ver_pill = f'<span class="version-pill">v{ver}</span>' if ver > 1 else ""
                ch_pill = (
                    f'<span class="chapter-pill">{ch_count} ch</span>'
                    if ch_count > 1 else ""
                )
                st.markdown(
                    f'<div class="history-item">'
                    f'<div style="display:flex;align-items:center;justify-content:space-between;">'
                    f'<span style="font-size:0.75rem;font-weight:600;color:#e8e8e8;">'
                    f'{icon} {entry["style"]}{ver_pill}{ch_pill}</span>'
                    f'<span class="history-meta">{flag} {entry["word_count"]}w</span>'
                    f'</div>'
                    f'<div class="history-meta">{entry["timestamp_display"]}</div>'
                    f'<div class="history-preview">{_escape(preview)}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                col_r, col_d = st.columns([3, 1])
                with col_r:
                    if st.button("Restore", key=f"restore_{entry['id']}"):
                        st.session_state.restore_story = entry
                        st.session_state.all_chapters = entry.get("chapters", [entry["story"]])
                        st.session_state.chapter_genres = entry.get("chapter_genres", [entry["style"]])
                        st.session_state.current_story = entry["story"]
                        st.session_state.current_style = entry["style"]
                        st.session_state.current_language = entry.get("language", "English")
                        st.session_state.current_image_names = entry.get("image_names", [])
                        st.session_state.audio_buffer = None
                        st.rerun()
                with col_d:
                    if st.button("✕", key=f"del_{entry['id']}"):
                        delete_story(entry["id"])
                        if st.session_state.last_entry_id == entry["id"]:
                            st.session_state.current_story = None
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Clear All History", type="secondary"):
                clear_all_history()
                st.session_state.current_story = None
                st.session_state.audio_buffer = None
                st.session_state.all_chapters = []
                st.session_state.chapter_genres = []
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown(
    '<div class="hero-wrap">'
    '<div class="hero-title">AI Story Engine</div>'
    '<div class="hero-subtitle">Transform Images into Living Narratives</div>'
    '<div class="hero-divider"></div>'
    '</div>',
    unsafe_allow_html=True,
)

# ─── PATH 1: NEW GENERATION ───────────────────────────────────────────────────

if generate_button:
    if not uploaded_files:
        st.warning("Upload at least one image to begin.")
    elif len(uploaded_files) > 10:
        st.error("Maximum 10 images allowed. Please remove some and try again.")
    else:
        _trigger_continuation = False  # flag to rerun AFTER finally clears is_generating
        try:
            st.session_state.is_generating = True
            st.session_state.restore_story = None
            st.session_state.audio_buffer = None

            pil_images = [Image.open(f) for f in uploaded_files]
            image_names = [f.name for f in uploaded_files]

            st.session_state.current_images = pil_images
            st.session_state.current_image_names = image_names
            st.session_state.current_style = story_style
            st.session_state.current_language = language

            # Image grid
            st.markdown('<div class="section-label">Visual Inspiration</div>', unsafe_allow_html=True)
            cols = st.columns(min(len(pil_images), 5))
            for i, img in enumerate(pil_images):
                with cols[i % 5]:
                    st.image(img, use_container_width=True)

            st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

            icon = STYLE_ICONS.get(story_style, "")
            flag = LANG_FLAGS.get(language, "")
            st.markdown(
                f'<div class="section-label">Your {icon} {story_style} Story &nbsp;·&nbsp; {flag} {language}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="gen-status"><div class="gen-dot"></div>'
                '<span>Luminara is writing your story in real-time…</span></div>',
                unsafe_allow_html=True,
            )

            story_slot = st.empty()
            full_story = ""
            error_occurred = False

            try:
                for chunk in generate_story_streaming(pil_images, story_style, language):
                    full_story += chunk
                    story_slot.markdown(_render_story_html(full_story, streaming=True), unsafe_allow_html=True)
                story_slot.markdown(_render_story_html(full_story, streaming=False), unsafe_allow_html=True)
            except EnvironmentError as e:
                st.error(f"Configuration error: {e}")
                error_occurred = True
            except Exception as e:
                st.error(f"Generation failed: {e}")
                error_occurred = True

            if not error_occurred and full_story:
                st.session_state.all_chapters = [full_story]
                st.session_state.chapter_genres = [story_style]
                st.session_state.current_story = full_story

                entry_id = save_story(
                    full_story, story_style, pil_images, image_names,
                    language=language,
                    chapters=[full_story],
                    chapter_genres=[story_style],
                )
                st.session_state.last_entry_id = entry_id

                st.markdown(_story_meta_bar([full_story], [story_style], language), unsafe_allow_html=True)
                _show_download_button([full_story], [story_style], language, image_names)
                _show_narration_section(full_story, language)

                twist, continue_clicked = _show_continuation_panel(language)
                if continue_clicked:
                    st.session_state.is_continuing = True
                    _trigger_continuation = True

        finally:
            # Always reset the flag — even if the script was interrupted mid-stream
            st.session_state.is_generating = False

        # st.rerun() is called AFTER finally so is_generating is already False
        if _trigger_continuation:
            st.rerun()

# ─── PATH 2: STORY CONTINUATION ──────────────────────────────────────────────
# Runs when continue button triggers a rerun and all_chapters already exists.

elif (
    st.session_state.is_continuing
    and st.session_state.all_chapters
    and not st.session_state.restore_story
):
    pil_images = st.session_state.current_images or []
    image_names = st.session_state.current_image_names or []
    language = st.session_state.current_language or "English"
    chapters = list(st.session_state.all_chapters)   # local copy
    genres = list(st.session_state.chapter_genres)
    twist_style = st.session_state.get("twist_genre_select", genres[-1])
    chapter_num = len(chapters) + 1

    _trigger_next_continuation = False
    error_occurred = False

    try:
        # Show existing chapters first
        if pil_images:
            st.markdown('<div class="section-label">Visual Inspiration</div>', unsafe_allow_html=True)
            cols = st.columns(min(len(pil_images), 5))
            for i, img in enumerate(pil_images):
                with cols[i % 5]:
                    st.image(img, use_container_width=True)
            st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

        icon_init = STYLE_ICONS.get(genres[0], "")
        flag = LANG_FLAGS.get(language, "")
        st.markdown(
            f'<div class="section-label">Your Story &nbsp;·&nbsp; {icon_init} {genres[0]} &nbsp;·&nbsp; {flag} {language}</div>',
            unsafe_allow_html=True,
        )
        _render_chapters(chapters, genres)

        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        icon_twist = STYLE_ICONS.get(twist_style, "")
        st.markdown(
            f'<div class="section-label">Chapter {chapter_num} — {icon_twist} {twist_style} Twist</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="gen-status"><div class="gen-dot"></div>'
            f'<span>Writing Chapter {chapter_num} with a {twist_style} twist…</span></div>',
            unsafe_allow_html=True,
        )

        prev_text = "\n\n".join(chapters)
        prev_words = prev_text.split()
        last_excerpt = " ".join(prev_words[-250:]) if len(prev_words) > 250 else prev_text

        summary_status = st.empty()
        summary_status.markdown(
            '<div class="gen-status"><div class="gen-dot"></div>'
            '<span>Analysing story context…</span></div>',
            unsafe_allow_html=True,
        )
        story_summary = summarize_story(prev_text, language)
        summary_status.empty()

        cont_slot = st.empty()
        new_chapter = ""

        try:
            for chunk in generate_continuation_streaming(
                story_summary, last_excerpt, twist_style, chapter_num, language
            ):
                new_chapter += chunk
                cont_slot.markdown(_render_story_html(new_chapter, streaming=True), unsafe_allow_html=True)
            cont_slot.markdown(_render_story_html(new_chapter, streaming=False), unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Continuation failed: {e}")
            error_occurred = True

        if not error_occurred and new_chapter:
            chapters.append(new_chapter)
            genres.append(twist_style)
            full_story = "\n\n".join(chapters)

            st.session_state.all_chapters = chapters
            st.session_state.chapter_genres = genres
            st.session_state.current_story = full_story
            st.session_state.audio_buffer = None

            pil_images_for_save = st.session_state.current_images or []
            entry_id = save_story(
                full_story, genres[0], pil_images_for_save, image_names,
                language=language, chapters=chapters, chapter_genres=genres,
            )
            st.session_state.last_entry_id = entry_id

            all_ch = st.session_state.all_chapters
            all_g = st.session_state.chapter_genres
            st.markdown(_story_meta_bar(all_ch, all_g, language), unsafe_allow_html=True)
            _show_download_button(all_ch, all_g, language, image_names)
            _show_narration_section(full_story, language)

            twist2, cont2 = _show_continuation_panel(language)
            if cont2:
                st.session_state.is_continuing = True
                _trigger_next_continuation = True

    finally:
        # Always reset — even if script was interrupted mid-stream
        if not _trigger_next_continuation:
            st.session_state.is_continuing = False

    # st.rerun() called AFTER finally block
    if _trigger_next_continuation:
        st.rerun()

# ─── PATH 3: RESTORED STORY FROM HISTORY ──────────────────────────────────────

elif st.session_state.restore_story is not None:
    entry = st.session_state.restore_story
    chapters = st.session_state.all_chapters
    genres = st.session_state.chapter_genres
    language = st.session_state.current_language
    image_names = st.session_state.current_image_names or entry.get("image_names", [])

    icon = STYLE_ICONS.get(entry["style"], "")
    flag = LANG_FLAGS.get(language, "")

    st.markdown(
        f'<div class="section-label">Restored · {icon} {entry["style"]} · {flag} {language}</div>',
        unsafe_allow_html=True,
    )
    _render_chapters(chapters, genres)
    st.markdown(_story_meta_bar(chapters, genres, language), unsafe_allow_html=True)
    _show_download_button(chapters, genres, language, image_names)
    _show_narration_section(entry["story"], language)

    # Allow continuation from restored story
    if st.session_state.current_images:
        twist, cont = _show_continuation_panel(language)
        if cont:
            st.session_state.restore_story = None
            st.session_state.is_continuing = True
            st.rerun()

# ─── PATH 4: PERSIST CURRENT STORY ───────────────────────────────────────────

elif st.session_state.current_story and st.session_state.all_chapters:
    chapters = st.session_state.all_chapters
    genres = st.session_state.chapter_genres
    language = st.session_state.current_language or "English"
    images = st.session_state.current_images or []
    image_names = st.session_state.current_image_names or []

    if images:
        st.markdown('<div class="section-label">Visual Inspiration</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(images), 5))
        for i, img in enumerate(images):
            with cols[i % 5]:
                st.image(img, use_container_width=True)
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    icon = STYLE_ICONS.get(genres[0] if genres else "", "")
    flag = LANG_FLAGS.get(language, "")
    st.markdown(
        f'<div class="section-label">Your Story &nbsp;·&nbsp; {icon} {genres[0] if genres else ""} &nbsp;·&nbsp; {flag} {language}</div>',
        unsafe_allow_html=True,
    )

    _render_chapters(chapters, genres)
    st.markdown(_story_meta_bar(chapters, genres, language), unsafe_allow_html=True)
    _show_download_button(chapters, genres, language, image_names)
    _show_narration_section(st.session_state.current_story, language)

    twist, cont = _show_continuation_panel(language)
    if cont:
        st.session_state.is_continuing = True
        st.rerun()

# ─── PATH 5: WELCOME / EMPTY STATE ───────────────────────────────────────────

else:
    st.markdown(
        '<div class="welcome-state">'
        '<div class="welcome-icon">✦</div>'
        '<div class="welcome-text">'
        'Upload images, pick a genre and language in the sidebar.<br>'
        'Luminara streams your story live — then continue it chapter by chapter.'
        '</div>'
        '<div class="welcome-steps">'
        '<div class="welcome-step"><div class="step-num">1</div><div class="step-text">Upload<br>1–10 images</div></div>'
        '<div class="welcome-step"><div class="step-num">2</div><div class="step-text">Choose genre<br>+ language</div></div>'
        '<div class="welcome-step"><div class="step-num">3</div><div class="step-text">Watch it<br>write live</div></div>'
        '<div class="welcome-step"><div class="step-num">4</div><div class="step-text">Continue<br>with a twist</div></div>'
        '<div class="welcome-step"><div class="step-num">5</div><div class="step-text">Download<br>+ narrate</div></div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
