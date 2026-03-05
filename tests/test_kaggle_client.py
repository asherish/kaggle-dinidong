from types import SimpleNamespace
from unittest.mock import MagicMock

from src.config import FilterConfig
from src.kaggle_client import _parse_reward, apply_filters, fetch_competitions


def _make_competition(ref="test-comp", title="Test", category="Featured",
                      reward="$10,000", tags=None, deadline=None):
    """Create a mock competition object."""
    if tags is None:
        tags = []
    return SimpleNamespace(
        ref=ref,
        title=title,
        category=category,
        reward=reward,
        tags=tags,
        deadline=deadline,
        url=f"https://www.kaggle.com/competitions/{ref}",
    )


class TestParseReward:
    def test_dollar_amount(self):
        assert _parse_reward("$50,000") == 50000.0

    def test_large_dollar_amount(self):
        assert _parse_reward("$1,000,000") == 1000000.0

    def test_knowledge(self):
        assert _parse_reward("Knowledge") == 0.0

    def test_swag(self):
        assert _parse_reward("Swag") == 0.0

    def test_kudos(self):
        assert _parse_reward("Kudos") == 0.0

    def test_empty_string(self):
        assert _parse_reward("") == 0.0

    def test_zero(self):
        assert _parse_reward("$0") == 0.0


class TestApplyFilters:
    def test_category_filter(self):
        comps = [
            _make_competition(ref="a", category="Featured"),
            _make_competition(ref="b", category="Research"),
            _make_competition(ref="c", category="Playground"),
        ]
        filters = FilterConfig(categories=["featured", "research"])
        result = apply_filters(comps, filters)
        assert [c.ref for c in result] == ["a", "b"]

    def test_category_filter_empty_allows_all(self):
        comps = [
            _make_competition(ref="a", category="Featured"),
            _make_competition(ref="b", category="Research"),
        ]
        filters = FilterConfig(categories=[])
        result = apply_filters(comps, filters)
        assert len(result) == 2

    def test_tag_inclusion_filter(self):
        comps = [
            _make_competition(ref="a", tags=["tabular", "time-series"]),
            _make_competition(ref="b", tags=["nlp"]),
            _make_competition(ref="c", tags=["tabular"]),
        ]
        filters = FilterConfig(tags=["tabular"])
        result = apply_filters(comps, filters)
        assert [c.ref for c in result] == ["a", "c"]

    def test_tag_inclusion_empty_allows_all(self):
        comps = [
            _make_competition(ref="a", tags=["tabular"]),
            _make_competition(ref="b", tags=["nlp"]),
        ]
        filters = FilterConfig(tags=[])
        result = apply_filters(comps, filters)
        assert len(result) == 2

    def test_tag_exclusion_filter(self):
        comps = [
            _make_competition(ref="a", tags=["tabular"]),
            _make_competition(ref="b", tags=["getting started"]),
            _make_competition(ref="c", tags=["nlp", "tabular"]),
        ]
        filters = FilterConfig(exclude_tags=["getting started"])
        result = apply_filters(comps, filters)
        assert [c.ref for c in result] == ["a", "c"]

    def test_min_reward_filter(self):
        comps = [
            _make_competition(ref="a", reward="$50,000"),
            _make_competition(ref="b", reward="Knowledge"),
            _make_competition(ref="c", reward="$10,000"),
        ]
        filters = FilterConfig(min_reward=10000)
        result = apply_filters(comps, filters)
        assert [c.ref for c in result] == ["a", "c"]

    def test_min_reward_none_allows_all(self):
        comps = [
            _make_competition(ref="a", reward="Knowledge"),
            _make_competition(ref="b", reward="$1,000"),
        ]
        filters = FilterConfig(min_reward=None)
        result = apply_filters(comps, filters)
        assert len(result) == 2

    def test_combined_filters(self):
        comps = [
            _make_competition(ref="a", category="Featured", tags=["tabular"], reward="$50,000"),
            _make_competition(ref="b", category="Featured", tags=["nlp"], reward="$10,000"),
            _make_competition(ref="c", category="Playground", tags=["tabular"], reward="$5,000"),
            _make_competition(ref="d", category="Featured", tags=["tabular", "getting started"], reward="$20,000"),
        ]
        filters = FilterConfig(
            categories=["featured"],
            tags=["tabular"],
            exclude_tags=["getting started"],
            min_reward=10000,
        )
        result = apply_filters(comps, filters)
        assert [c.ref for c in result] == ["a"]


class TestFetchCompetitions:
    def test_fetches_multiple_pages(self):
        api = MagicMock()
        api.competitions_list.side_effect = [
            [_make_competition(ref="a")],
            [_make_competition(ref="b")],
            [_make_competition(ref="c")],
        ]
        result = fetch_competitions(api, pages=3)
        assert len(result) == 3
        assert api.competitions_list.call_count == 3
        api.competitions_list.assert_any_call(page=1)
        api.competitions_list.assert_any_call(page=2)
        api.competitions_list.assert_any_call(page=3)
