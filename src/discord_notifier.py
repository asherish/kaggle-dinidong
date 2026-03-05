import logging
import time
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)

CATEGORY_COLORS = {
    "featured": 0xFFD700,       # Gold
    "research": 0x1E90FF,       # Blue
    "getting started": 0x808080, # Gray
    "playground": 0x808080,      # Gray
    "community": 0x808080,       # Gray
}
DEFAULT_COLOR = 0x808080  # Gray

MAX_EMBEDS_PER_MESSAGE = 10
MAX_RETRIES = 3
INITIAL_BACKOFF = 1.0


def build_embed(competition) -> dict:
    """Build a Discord embed dict from a competition object."""
    ref = getattr(competition, "ref", "")
    title = str(getattr(competition, "title", "Unknown"))[:256]
    url = f"https://www.kaggle.com/competitions/{ref}"
    category = str(getattr(competition, "category", "Other"))
    reward = str(getattr(competition, "reward", "N/A"))
    tags_raw = getattr(competition, "tags", []) or []
    tag_names = ", ".join(str(t) for t in tags_raw) if tags_raw else "None"

    deadline = getattr(competition, "deadline", None)
    if isinstance(deadline, datetime):
        deadline_str = deadline.strftime("%Y-%m-%d")
        timestamp = deadline.isoformat()
    elif deadline:
        deadline_str = str(deadline)
        timestamp = str(deadline)
    else:
        deadline_str = "N/A"
        timestamp = None

    color = CATEGORY_COLORS.get(category.lower(), DEFAULT_COLOR)

    embed = {
        "title": title,
        "url": url,
        "color": color,
        "fields": [
            {"name": "Category", "value": category, "inline": True},
            {"name": "Reward", "value": reward, "inline": True},
            {"name": "Deadline", "value": deadline_str, "inline": True},
            {"name": "Tags", "value": tag_names, "inline": False},
        ],
        "footer": {"text": "Kaggle Competition Notifier"},
    }

    if timestamp:
        embed["timestamp"] = timestamp

    return embed


def batch_embeds(embeds: list[dict]) -> list[list[dict]]:
    """Split embeds into batches of MAX_EMBEDS_PER_MESSAGE."""
    return [
        embeds[i:i + MAX_EMBEDS_PER_MESSAGE]
        for i in range(0, len(embeds), MAX_EMBEDS_PER_MESSAGE)
    ]


def _post_with_retry(client: httpx.Client, url: str, payload: dict) -> None:
    """POST a payload to the webhook URL with retry and exponential backoff."""
    backoff = INITIAL_BACKOFF
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.post(url, json=payload)

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = float(response.headers.get("Retry-After", backoff))
                logger.warning(
                    "Rate limited, retrying after %.1f seconds.", retry_after
                )
                time.sleep(retry_after)
                continue

            response.raise_for_status()
            return
        except (httpx.HTTPStatusError, httpx.TransportError) as e:
            if attempt == MAX_RETRIES:
                raise RuntimeError(
                    f"Discord webhook failed after {MAX_RETRIES} attempts: {e}. "
                    "Check that DISCORD_WEBHOOK_URL is correct and the webhook is active."
                ) from e
            logger.warning(
                "Webhook request failed (attempt %d/%d): %s. Retrying in %.1fs...",
                attempt, MAX_RETRIES, e, backoff,
            )
            time.sleep(backoff)
            backoff *= 2


def send_notifications(
    embeds: list[dict],
    webhook_url: str,
    mention_role_id: str | None = None,
) -> None:
    """Send embed notifications to Discord via webhook."""
    if not embeds:
        return

    batches = batch_embeds(embeds)
    logger.info("Sending %d embeds in %d batch(es).", len(embeds), len(batches))

    with httpx.Client(timeout=30) as client:
        for i, batch in enumerate(batches):
            payload: dict = {"embeds": batch}

            # Add role mention to the first batch only
            if i == 0 and mention_role_id:
                payload["content"] = f"<@&{mention_role_id}>"

            _post_with_retry(client, webhook_url, payload)
            logger.info("Batch %d/%d sent successfully.", i + 1, len(batches))
