import logging
import sys

from src.config import build_config
from src.discord_notifier import build_embed, send_notifications
from src.history import load_history, save_history
from src.kaggle_client import apply_filters, fetch_competitions, get_api

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    # 1. Load configuration
    config = build_config()

    # 2. Fetch competitions from Kaggle API
    api = get_api()
    all_comps = fetch_competitions(api, pages=config.kaggle_pages)
    logger.info("Fetched %d competitions.", len(all_comps))

    # 3. Apply filters
    filtered = apply_filters(all_comps, config.filters)
    logger.info("After filtering: %d competitions.", len(filtered))

    # 4. Deduplicate against history
    history = load_history()
    new_comps = [c for c in filtered if c.ref not in history]
    logger.info("New competitions: %d.", len(new_comps))

    if not new_comps:
        logger.info("No new competitions to notify about.")
        return 0

    # 5. Build embeds and send notifications
    embeds = [build_embed(c) for c in new_comps]
    send_notifications(
        embeds,
        webhook_url=config.discord_webhook_url,
        mention_role_id=config.discord_mention_role_id,
    )
    logger.info("Sent %d notification(s).", len(new_comps))

    # 6. Update history (only after successful notification)
    new_slugs = history | {c.ref for c in new_comps}
    save_history(new_slugs)
    logger.info("History updated (%d total slugs).", len(new_slugs))

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error("Fatal error: %s", e)
        sys.exit(1)
