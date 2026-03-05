import logging
import re

from src.config import FilterConfig

logger = logging.getLogger(__name__)


def get_api():
    """Create and authenticate a KaggleApi instance."""
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()
        return api
    except Exception as e:
        raise RuntimeError(
            f"Kaggle API authentication failed: {e}. "
            "Ensure ~/.kaggle/kaggle.json exists with correct permissions (chmod 600), "
            "or set KAGGLE_USERNAME and KAGGLE_KEY environment variables."
        ) from e


def fetch_competitions(api, pages: int = 3) -> list:
    """Fetch competitions from multiple pages of the Kaggle API."""
    all_competitions = []
    for page in range(1, pages + 1):
        try:
            comps = api.competitions_list(page=page)
            all_competitions.extend(comps)
            logger.debug("Fetched page %d: %d competitions", page, len(comps))
        except Exception as e:
            logger.error("Failed to fetch page %d: %s", page, e)
            raise
    return all_competitions


def _parse_reward(reward_str: str) -> float:
    """Parse a reward string into a numeric value.

    Examples:
        "$50,000" -> 50000.0
        "$1,000,000" -> 1000000.0
        "Knowledge" -> 0.0
        "Swag" -> 0.0
    """
    if not reward_str:
        return 0.0
    numbers = re.findall(r"[\d,]+", str(reward_str))
    if numbers:
        try:
            return float(numbers[0].replace(",", ""))
        except ValueError:
            return 0.0
    return 0.0


def _get_tag_names(competition) -> list[str]:
    """Extract tag names from a competition's tags attribute."""
    tags = getattr(competition, "tags", []) or []
    return [str(t).lower() for t in tags]


def apply_filters(competitions: list, filters: FilterConfig) -> list:
    """Apply filter conditions to a list of competitions."""
    result = competitions

    # Category filter
    if filters.categories:
        result = [
            c for c in result
            if str(getattr(c, "category", "")).lower() in filters.categories
        ]
        logger.debug("After category filter: %d competitions", len(result))

    # Tag inclusion filter
    if filters.tags:
        result = [
            c for c in result
            if any(tag in filters.tags for tag in _get_tag_names(c))
        ]
        logger.debug("After tag inclusion filter: %d competitions", len(result))

    # Tag exclusion filter
    if filters.exclude_tags:
        result = [
            c for c in result
            if not any(tag in filters.exclude_tags for tag in _get_tag_names(c))
        ]
        logger.debug("After tag exclusion filter: %d competitions", len(result))

    # Minimum reward filter
    if filters.min_reward is not None:
        result = [
            c for c in result
            if _parse_reward(str(getattr(c, "reward", ""))) >= filters.min_reward
        ]
        logger.debug("After min reward filter: %d competitions", len(result))

    return result
