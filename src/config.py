import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

CONFIG_FILE = "config.json"
CONFIG_EXAMPLE = "config.json.example"


@dataclass
class FilterConfig:
    tags: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    exclude_tags: list[str] = field(default_factory=list)
    min_reward: float | None = None


@dataclass
class AppConfig:
    filters: FilterConfig
    kaggle_pages: int
    discord_webhook_url: str
    discord_mention_role_id: str | None


def load_config(path: str = CONFIG_FILE) -> dict:
    """Load configuration from a JSON file, falling back to the example config."""
    config_path = Path(path)
    if not config_path.exists():
        config_path = Path(CONFIG_EXAMPLE)
        if not config_path.exists():
            raise FileNotFoundError(
                f"Neither {CONFIG_FILE} nor {CONFIG_EXAMPLE} found. "
                f"Copy {CONFIG_EXAMPLE} to {CONFIG_FILE} and configure it."
            )
        logger.warning(
            "%s not found, falling back to %s", CONFIG_FILE, CONFIG_EXAMPLE
        )
    with open(config_path) as f:
        return json.load(f)


def build_config(config_path: str = CONFIG_FILE) -> AppConfig:
    """Build the application configuration from config file and environment variables."""
    raw = load_config(config_path)

    discord_webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not discord_webhook_url:
        raise RuntimeError(
            "DISCORD_WEBHOOK_URL environment variable is not set. "
            "Set it in your .env file or as a GitHub Actions secret."
        )

    filters_raw = raw.get("filters", {})
    filters = FilterConfig(
        tags=[t.lower() for t in filters_raw.get("tags", [])],
        categories=[c.lower() for c in filters_raw.get("categories", [])],
        exclude_tags=[t.lower() for t in filters_raw.get("exclude_tags", [])],
        min_reward=filters_raw.get("min_reward"),
    )

    kaggle_pages = raw.get("kaggle", {}).get("pages", 3)

    mention_role_id = raw.get("discord", {}).get("mention_role_id")

    return AppConfig(
        filters=filters,
        kaggle_pages=kaggle_pages,
        discord_webhook_url=discord_webhook_url,
        discord_mention_role_id=mention_role_id,
    )
