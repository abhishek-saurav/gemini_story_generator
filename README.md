# ✦ Luminara — AI Story Engine

> Transform images into living, multi-chapter narratives — streamed live, narrated aloud, in your language.

Built with **Google Gemini** · **Streamlit** · **Yellow/Black Glassmorphism UI**

---

## Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Real-Time Streaming** | Story text appears word-by-word as the AI writes. First token visible in under 1 second. |
| 2 | **Story History & Versioning** | Every story auto-saved locally. Browse, restore, or delete past stories from the sidebar. Version numbers track re-generations of the same images. |
| 3 | **Multi-Chapter Continuation** | Add unlimited chapters after Chapter 1, each with a genre twist (e.g. Comedy → Thriller → Sci-Fi). |
| 4 | **Download (.txt)** | Export the full multi-chapter story as a formatted plain-text file with metadata header. |
| 5 | **Multi-Language** | Generate stories and narration in **English**, **Hindi**, or **Bhojpuri**. |

---

## Tech Stack

- **AI Model** — Google Gemini 2.5 Flash Lite (multimodal, streaming)
- **Frontend** — Streamlit with custom Yellow/Black Glassmorphism CSS
- **TTS** — Google Text-to-Speech via gTTS (`en` / `hi`)
- **Image Processing** — Pillow (PIL)
- **Persistence** — Local JSON file (`.story_history.json`)
- **Config** — python-dotenv

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd gemini_story_generator
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your API key

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_gemini_api_key_here
```

Get your key at [Google AI Studio](https://aistudio.google.com).

### 4. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Usage

### Generating a Story

1. **Upload images** (1–10) using the sidebar uploader — PNG, JPEG, JPG, WEBP
2. **Choose a genre**: Comedy, Thriller, Fairy Tale, Sci-Fi, Mystery, Adventure, or Morale
3. **Choose a language**: English, Hindi, or Bhojpuri
4. Click **✦ Generate Story** — watch it write itself live

### Continuing the Story

After Chapter 1 is generated, the **Continue the Story** panel appears below:

1. Select a **Twist Genre** for the next chapter
2. Click **✦ Add Chapter N**
3. The new chapter streams live, connecting seamlessly to the previous chapters
4. Repeat for as many chapters as you like

### Downloading

Click **⬇ Download Story (.txt)** at any point. The file includes all chapters with a formatted header showing generation date, language, genre chain, and image filenames.

### Narration

Audio narration is generated automatically after each story or continuation. The narration covers the **full story** (all chapters combined). For Bhojpuri, a Hindi TTS voice is used (closest available).

### History

The **Story History** panel in the sidebar shows your last 10 stories. Click **Restore** to reload any past story into the main view. Restored stories can be continued with new chapters.

---

## Supported Languages

| Language | Story Generation | Narration | Script |
|----------|-----------------|-----------|--------|
| English | ✅ | ✅ | Latin |
| Hindi | ✅ | ✅ | Devanagari |
| Bhojpuri | ✅ | ✅ (Hindi voice) | Devanagari |

---

## Project Structure

```
gemini_story_generator/
├── app.py                  # Main Streamlit app (UI + orchestration)
├── story_generator.py      # Gemini API, prompts, TTS, language configs
├── story_history.py        # JSON-backed story persistence module
├── requirements.txt        # Python dependencies
├── .env                    # API key (not committed)
├── .gitignore
├── README.md
├── CHANGELOG.txt           # Complete developer audit trail
└── PROJECT_DETAILS.txt     # Full technical documentation
```

---

## Story Genres

| Genre | Description |
|-------|-------------|
| 😂 Comedy | Absurd escalations, witty dialogue, punchlines |
| 🔪 Thriller | Tension, ticking clock, unseen threat, twist ending |
| 🧚 Fairy Tale | Magical beings, enchanted objects, moral lesson |
| 🚀 Sci-Fi | Plausible future science, technological dilemma |
| 🔍 Mystery | Red herrings, clues across images, satisfying reveal |
| ⚔️ Adventure | Bold protagonist, escalating obstacles, triumph |
| 💛 Morale | Profound life lesson woven through characters' choices |

---

## Requirements

```
streamlit
python-dotenv
google-genai
google-generativeai
Pillow
gTTS
```

---

## Notes

- **Internet required** for Gemini API (story generation) and gTTS (narration).
- **Story history** is stored in `.story_history.json` locally — not committed to git.
- **Bhojpuri narration** uses the Hindi TTS voice (gTTS has no native Bhojpuri code).
- **Streamlit ≥ 1.30.0** required for stable `st.empty()` in-place streaming updates.

---

*Made with Gemini AI · Luminara Story Engine*
