"""
utils.py — Pure Python helpers for File Explorer.
No Dash dependencies; safe to import anywhere.
"""

import os
import mimetypes


def format_size(size: int) -> str:
    """Convert a byte count to a human-readable string (e.g. 1.2 MB)."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def get_mime_label(path: str) -> str:
    """Return the MIME type string for a file, or 'unknown' if undetectable."""
    mime, _ = mimetypes.guess_type(path)
    return mime or "unknown"


def get_file_icon(path: str, is_dir: bool) -> str:
    """Return an emoji icon that represents the file type or directory."""
    if is_dir:
        return "📁"
    _, ext = os.path.splitext(path)
    icons = {
        ".py": "🐍", ".js": "📜", ".ts": "📜", ".jsx": "⚛️", ".tsx": "⚛️",
        ".html": "🌐", ".css": "🎨", ".json": "🗂️", ".yaml": "🗂️", ".yml": "🗂️",
        ".md": "📝", ".txt": "📄", ".pdf": "📕", ".csv": "📊", ".xlsx": "📊",
        ".png": "🖼️", ".jpg": "🖼️", ".jpeg": "🖼️", ".gif": "🖼️", ".svg": "🖼️",
        ".mp4": "🎬", ".mp3": "🎵", ".wav": "🎵",
        ".zip": "📦", ".tar": "📦", ".gz": "📦", ".sh": "⚙️",
        ".toml": "🗂️", ".ini": "⚙️", ".cfg": "⚙️",
    }
    return icons.get(ext.lower(), "📄")