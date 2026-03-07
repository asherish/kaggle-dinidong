import json
import urllib.request

# Slack Block Kit allows max 50 blocks per message.
# header(1) + (divider+section)(2) × N, so N<=24 keeps it under 50.
_CHUNK_SIZE = 24


def build_slack_blocks(competitions: list[dict]) -> list[dict]:
    """Build Slack Block Kit blocks for competition notifications."""
    blocks: list[dict] = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "New Kaggle Competitions"},
        }
    ]
    for comp in competitions:
        blocks.append({"type": "divider"})
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*<{comp['url']}|{comp['title']}>*\n"
                        f"Category: {comp['category']} | "
                        f"Reward: {comp['reward']} | "
                        f"Deadline: {comp['deadline']}"
                    ),
                },
            }
        )
    return blocks


def send_slack(competitions: list[dict], webhook_url: str) -> None:
    """Send competition notifications to Slack via Incoming Webhook."""
    for i in range(0, len(competitions), _CHUNK_SIZE):
        chunk = competitions[i : i + _CHUNK_SIZE]
        payload = json.dumps({"blocks": build_slack_blocks(chunk)}).encode()
        req = urllib.request.Request(
            webhook_url, data=payload, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30):
            pass
