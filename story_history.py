"""
story_history.py
Feature 2: Story Versioning & Persistent History Engine

Architecture:
  Stories are serialized to a local JSON file (.story_history.json) after each
  generation. Each entry carries a unique ID, timestamp, style, word count,
  image fingerprint, and a version counter that increments when the same set of
  images and style produces a new generation. The module exposes a clean API
  used by app.py to save, retrieve, filter, and delete story entries.

  Session state integration: app.py uses st.session_state to cache the history
  list in memory, avoiding redundant file reads within a single user session.
  The file acts as durable persistent storage across sessions/restarts.

Value:
  - Users never lose a generated story — every output is automatically archived
  - Version numbers let users compare different AI responses to the same prompt
  - Aggregate stats (total stories, favorite genre, average word count) give
    insight into usage patterns
  - One-click restore: any past story can be loaded back into the main view
    and its audio re-generated without re-calling the AI model
"""

import json
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from io import BytesIO

from PIL import Image

# ─── CONFIG ───────────────────────────────────────────────────────────────────

HISTORY_FILE = ".story_history.json"
MAX_HISTORY_ENTRIES = 100  # Hard cap to prevent unbounded file growth


# ─── INTERNAL I/O ─────────────────────────────────────────────────────────────

def _load_history() -> List[Dict]:
    """Read and parse the history JSON file. Returns [] on any failure."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError, ValueError):
        return []


def _save_history(history: List[Dict]) -> None:
    """Persist history to disk, trimming to MAX_HISTORY_ENTRIES oldest-first."""
    if len(history) > MAX_HISTORY_ENTRIES:
        history = history[-MAX_HISTORY_ENTRIES:]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as fh:
            json.dump(history, fh, indent=2, ensure_ascii=False)
    except IOError as exc:
        print(f"[story_history] Failed to write history: {exc}")


# ─── IMAGE FINGERPRINTING ─────────────────────────────────────────────────────

def _fingerprint_images(images: list) -> str:
    """
    Produce a deterministic fingerprint from a list of PIL Images.
    The fingerprint is the MD5 hash of each image concatenated — same images
    in the same order always yield the same string.
    """
    parts = []
    for img in images:
        if isinstance(img, Image.Image):
            buf = BytesIO()
            img.save(buf, format="PNG")
            parts.append(hashlib.md5(buf.getvalue()).hexdigest()[:10])
    return "_".join(parts) if parts else "unknown"


# ─── PUBLIC API ───────────────────────────────────────────────────────────────

def save_story(
    story_text: str,
    style: str,
    images: list,
    image_names: List[str],
    language: str = "English",
    chapters: Optional[List[str]] = None,
    chapter_genres: Optional[List[str]] = None,
) -> str:
    """
    Persist a story (single chapter or multi-chapter) to the history store.

    Version logic: if the same image fingerprint + style combination has been
    generated before, the new entry gets version = previous_max + 1.
    First-time combinations start at version 1.

    Args:
        story_text:     Full combined story text (all chapters joined).
        style:          Initial story genre (Chapter 1 genre).
        images:         PIL Image list (used for fingerprinting).
        image_names:    Filenames of uploaded images.
        language:       Language used for generation.
        chapters:       List of individual chapter texts (optional).
        chapter_genres: Genre per chapter (optional).

    Returns:
        str: The unique entry ID.
    """
    history = _load_history()
    now = datetime.now()

    entry_id = f"{now.strftime('%Y%m%d_%H%M%S')}_{style[:3].upper()}"
    fingerprint = _fingerprint_images(images)

    # Determine version number for this image+style combination
    version = 1
    for entry in history:
        if (
            entry.get("fingerprint") == fingerprint
            and entry.get("style") == style
        ):
            existing_version = entry.get("version", 1)
            if existing_version >= version:
                version = existing_version + 1

    # Default chapters/genres to single-chapter if not provided
    stored_chapters = chapters if chapters else [story_text]
    stored_genres = chapter_genres if chapter_genres else [style]

    entry = {
        "id": entry_id,
        "timestamp_iso": now.isoformat(),
        "timestamp_display": now.strftime("%b %d, %Y · %H:%M"),
        "style": style,
        "language": language,
        "story": story_text,
        "chapters": stored_chapters,
        "chapter_genres": stored_genres,
        "chapter_count": len(stored_chapters),
        "word_count": len(story_text.split()),
        "char_count": len(story_text),
        "image_count": len(images),
        "image_names": image_names,
        "fingerprint": fingerprint,
        "version": version,
    }

    history.append(entry)
    _save_history(history)
    return entry_id


def get_all_stories(limit: int = 20) -> List[Dict]:
    """
    Return up to `limit` stories, newest first.
    """
    history = _load_history()
    return list(reversed(history))[:limit]


def get_story_by_id(entry_id: str) -> Optional[Dict]:
    """Return a single story dict by its ID, or None if not found."""
    for entry in _load_history():
        if entry.get("id") == entry_id:
            return entry
    return None


def get_versions_for_fingerprint(fingerprint: str, style: str) -> List[Dict]:
    """
    Return all stored versions of a specific image+style combination,
    ordered by version number ascending.
    """
    results = [
        e for e in _load_history()
        if e.get("fingerprint") == fingerprint and e.get("style") == style
    ]
    return sorted(results, key=lambda e: e.get("version", 1))


def delete_story(entry_id: str) -> bool:
    """
    Remove a story from history by ID.
    Returns True if the entry was found and deleted, False otherwise.
    """
    history = _load_history()
    new_history = [e for e in history if e.get("id") != entry_id]
    if len(new_history) == len(history):
        return False
    _save_history(new_history)
    return True


def clear_all_history() -> int:
    """
    Delete all history entries.
    Returns the number of entries that were cleared.
    """
    count = len(_load_history())
    _save_history([])
    return count


def get_stats() -> Dict:
    """
    Compute aggregate statistics across all stored stories.

    Returns a dict with:
        total          (int)  : total stories generated
        styles         (dict) : {style_name: count} mapping
        avg_words      (int)  : mean word count
        most_used_style(str)  : style with highest count, or None
        total_words    (int)  : cumulative word count across all stories
    """
    history = _load_history()
    if not history:
        return {
            "total": 0,
            "styles": {},
            "avg_words": 0,
            "most_used_style": None,
            "total_words": 0,
        }

    styles: Dict[str, int] = {}
    total_words = 0

    for entry in history:
        style = entry.get("style", "Unknown")
        styles[style] = styles.get(style, 0) + 1
        total_words += entry.get("word_count", 0)

    return {
        "total": len(history),
        "styles": styles,
        "avg_words": total_words // len(history),
        "most_used_style": max(styles, key=lambda s: styles[s]) if styles else None,
        "total_words": total_words,
    }
