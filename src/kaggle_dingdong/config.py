import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def load_config(config_path: str | None = None) -> dict:
    """Load configuration from a JSON file."""
    if config_path is None:
        config_path = os.environ.get("CONFIG_PATH", str(PROJECT_ROOT / "config.json"))
    path = Path(config_path)
    with path.open() as f:
        return json.load(f)


def get_smtp_config() -> dict | None:
    """Read SMTP settings from environment variables. Returns None if not configured."""
    try:
        recipients = os.environ.get("EMAIL", "")
        return {
            "server": os.environ["SMTP_SERVER"],
            "port": int(os.environ.get("SMTP_PORT", "587")),
            "user": os.environ["SMTP_USER"],
            "password": os.environ["SMTP_PASSWORD"],
            "recipients": [r.strip() for r in recipients.split(",") if r.strip()],
        }
    except KeyError:
        return None


def get_slack_config() -> str | None:
    """Return Slack Incoming Webhook URL if configured."""
    return os.environ.get("SLACK_WEBHOOK_URL") or None


def get_discord_config() -> str | None:
    """Return Discord Webhook URL if configured."""
    return os.environ.get("DISCORD_WEBHOOK_URL") or None
