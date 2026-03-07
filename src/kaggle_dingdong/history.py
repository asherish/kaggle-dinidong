import json
from pathlib import Path


def load_history(path: Path) -> tuple[list[str], set[str]]:
    """Load sent competition titles from a JSON file.

    Returns a tuple of (ordered list, set for fast lookup).
    """
    if not path.exists():
        return [], set()
    with path.open() as f:
        titles = json.load(f)
    return titles, set(titles)


def save_history(
    existing: list[str], new_titles: list[str], path: Path, limit: int = 200
) -> None:
    """Append new titles and trim to the most recent `limit` entries."""
    combined = existing + new_titles
    trimmed = combined[-limit:]
    with path.open("w") as f:
        json.dump(trimmed, f, ensure_ascii=False, indent=2)
