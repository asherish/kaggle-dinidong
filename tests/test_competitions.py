from kaggle_dingdong.competitions import filter_competitions

SAMPLE_COMPS = [
    {"title": "Comp A", "category": "Featured", "tags": ["tabular"], "url": "", "reward": "$10k", "deadline": "2026-12-31"},
    {"title": "Comp B", "category": "Research", "tags": ["nlp"], "url": "", "reward": "$5k", "deadline": "2026-11-30"},
    {"title": "Comp C", "category": "Playground", "tags": ["tabular"], "url": "", "reward": "Swag", "deadline": "2026-10-15"},
]


def test_filter_by_category():
    filters = {"category": ["Featured"]}
    result = filter_competitions(SAMPLE_COMPS, filters, set())
    assert len(result) == 1
    assert result[0]["title"] == "Comp A"


def test_filter_by_tags():
    filters = {"category": [], "tags": ["tabular"]}
    result = filter_competitions(SAMPLE_COMPS, filters, set())
    assert len(result) == 2
    assert all("tabular" in [t.lower() for t in c["tags"]] for c in result)


def test_filter_by_tags_multiple():
    filters = {"category": [], "tags": ["tabular", "nlp"]}
    result = filter_competitions(SAMPLE_COMPS, filters, set())
    assert len(result) == 3


def test_filter_by_tags_empty_allows_all():
    filters = {"category": [], "tags": []}
    result = filter_competitions(SAMPLE_COMPS, filters, set())
    assert len(result) == 3


def test_filter_skips_sent():
    filters = {"category": ["Featured", "Research"]}
    sent = {"Comp A"}
    result = filter_competitions(SAMPLE_COMPS, filters, sent)
    assert len(result) == 1
    assert result[0]["title"] == "Comp B"


def test_filter_empty_input():
    result = filter_competitions([], {}, set())
    assert result == []


def test_filter_no_filters():
    result = filter_competitions(SAMPLE_COMPS, {}, set())
    assert len(result) == 3
