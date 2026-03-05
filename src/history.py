import json
import logging
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

HISTORY_FILE = "sent_competitions.json"


def load_history(path: str = HISTORY_FILE) -> set[str]:
    """Load the set of already-notified competition slugs.

    Returns an empty set if the file does not exist or is invalid.
    """
    history_path = Path(path)
    if not history_path.exists():
        logger.info("No history file found at %s, starting fresh.", path)
        return set()

    try:
        with open(history_path) as f:
            data = json.load(f)
        slugs = set(data.get("sent_slugs", []))
        logger.info("Loaded %d slugs from history.", len(slugs))
        return slugs
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning("Failed to parse history file %s: %s. Starting fresh.", path, e)
        return set()


def save_history(slugs: set[str], path: str = HISTORY_FILE) -> None:
    """Save the set of notified competition slugs atomically."""
    data = {
        "sent_slugs": sorted(slugs),
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }

    dir_name = os.path.dirname(os.path.abspath(path))
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        os.replace(tmp_path, path)
        logger.info("Saved %d slugs to history.", len(slugs))
    except Exception:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
