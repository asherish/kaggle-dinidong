from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.discord_notifier import (
    CATEGORY_COLORS,
    DEFAULT_COLOR,
    MAX_EMBEDS_PER_MESSAGE,
    batch_embeds,
    build_embed,
    send_notifications,
)


_UNSET = object()


def _make_competition(ref="test-comp", title="Test Competition",
                      category="Featured", reward="$10,000",
                      tags=None, deadline=_UNSET):
    if tags is None:
        tags = ["tabular", "time-series"]
    if deadline is _UNSET:
        deadline = datetime(2026, 12, 31, tzinfo=timezone.utc)
    return SimpleNamespace(
        ref=ref, title=title, category=category,
        reward=reward, tags=tags, deadline=deadline,
        url=f"https://www.kaggle.com/competitions/{ref}",
    )


class TestBuildEmbed:
    def test_basic_structure(self):
        comp = _make_competition()
        embed = build_embed(comp)
        assert embed["title"] == "Test Competition"
        assert embed["url"] == "https://www.kaggle.com/competitions/test-comp"
        assert embed["color"] == CATEGORY_COLORS["featured"]
        assert len(embed["fields"]) == 4
        assert embed["footer"]["text"] == "Kaggle Competition Notifier"

    def test_fields_content(self):
        comp = _make_competition()
        embed = build_embed(comp)
        fields = {f["name"]: f["value"] for f in embed["fields"]}
        assert fields["Category"] == "Featured"
        assert fields["Reward"] == "$10,000"
        assert fields["Deadline"] == "2026-12-31"
        assert "tabular" in fields["Tags"]

    def test_category_colors(self):
        for cat, expected_color in CATEGORY_COLORS.items():
            comp = _make_competition(category=cat.title())
            embed = build_embed(comp)
            assert embed["color"] == expected_color

    def test_unknown_category_gets_default_color(self):
        comp = _make_competition(category="Unknown")
        embed = build_embed(comp)
        assert embed["color"] == DEFAULT_COLOR

    def test_title_truncation(self):
        long_title = "A" * 300
        comp = _make_competition(title=long_title)
        embed = build_embed(comp)
        assert len(embed["title"]) == 256

    def test_no_deadline(self):
        comp = _make_competition(deadline=None)
        embed = build_embed(comp)
        fields = {f["name"]: f["value"] for f in embed["fields"]}
        assert fields["Deadline"] == "N/A"
        assert "timestamp" not in embed

    def test_no_tags(self):
        comp = _make_competition(tags=[])
        embed = build_embed(comp)
        fields = {f["name"]: f["value"] for f in embed["fields"]}
        assert fields["Tags"] == "None"


class TestBatchEmbeds:
    def test_empty_list(self):
        assert batch_embeds([]) == []

    def test_under_limit(self):
        embeds = [{"title": f"comp-{i}"} for i in range(5)]
        batches = batch_embeds(embeds)
        assert len(batches) == 1
        assert len(batches[0]) == 5

    def test_exact_limit(self):
        embeds = [{"title": f"comp-{i}"} for i in range(MAX_EMBEDS_PER_MESSAGE)]
        batches = batch_embeds(embeds)
        assert len(batches) == 1

    def test_over_limit(self):
        embeds = [{"title": f"comp-{i}"} for i in range(25)]
        batches = batch_embeds(embeds)
        assert len(batches) == 3
        assert len(batches[0]) == 10
        assert len(batches[1]) == 10
        assert len(batches[2]) == 5


class TestSendNotifications:
    @patch("src.discord_notifier.httpx.Client")
    def test_sends_embeds(self, mock_client_cls):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        embeds = [{"title": f"comp-{i}"} for i in range(3)]
        send_notifications(embeds, "https://discord.com/api/webhooks/test/test")

        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert len(call_args.kwargs["json"]["embeds"]) == 3

    @patch("src.discord_notifier.httpx.Client")
    def test_mention_role_in_first_batch(self, mock_client_cls):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        embeds = [{"title": f"comp-{i}"} for i in range(3)]
        send_notifications(
            embeds,
            "https://discord.com/api/webhooks/test/test",
            mention_role_id="123456",
        )

        call_args = mock_client.post.call_args
        assert call_args.kwargs["json"]["content"] == "<@&123456>"

    @patch("src.discord_notifier.httpx.Client")
    def test_empty_embeds_no_request(self, mock_client_cls):
        send_notifications([], "https://discord.com/api/webhooks/test/test")
        mock_client_cls.assert_not_called()

    @patch("src.discord_notifier.httpx.Client")
    def test_multiple_batches(self, mock_client_cls):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        embeds = [{"title": f"comp-{i}"} for i in range(15)]
        send_notifications(embeds, "https://discord.com/api/webhooks/test/test")

        assert mock_client.post.call_count == 2
        # First batch: 10, second batch: 5
        first_call = mock_client.post.call_args_list[0]
        second_call = mock_client.post.call_args_list[1]
        assert len(first_call.kwargs["json"]["embeds"]) == 10
        assert len(second_call.kwargs["json"]["embeds"]) == 5
