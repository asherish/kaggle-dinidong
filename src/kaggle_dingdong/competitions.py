from kaggle.api.kaggle_api_extended import KaggleApi


def fetch_competitions(max_pages: int = 3) -> list[dict]:
    """Fetch competitions from the Kaggle API."""
    api = KaggleApi()
    api.authenticate()

    competitions = []
    for page in range(1, max_pages + 1):
        page_comps = api.competitions_list(page=page)
        if not page_comps:
            break
        for c in page_comps:
            competitions.append({
                "title": c.title,
                "url": f"https://www.kaggle.com/competitions/{c.ref}",
                "category": c.category,
                "reward": c.reward,
                "deadline": str(c.deadline),
                "tags": [t.name for t in (c.tags or [])],
            })
    return competitions


def filter_competitions(
    comps: list[dict], filters: dict, sent_titles: set[str]
) -> list[dict]:
    """Filter competitions by category, allowed tags, and sent history."""
    categories = set(filters.get("category", []))
    allowed_tags = {t.lower() for t in filters.get("tags", [])}

    result = []
    for comp in comps:
        if comp["title"] in sent_titles:
            continue
        if categories and comp["category"] not in categories:
            continue
        if allowed_tags:
            comp_tags = {t.lower() for t in comp.get("tags", [])}
            if not allowed_tags & comp_tags:
                continue
        result.append(comp)
    return result
