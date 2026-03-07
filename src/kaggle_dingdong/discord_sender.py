import json
import urllib.request


def build_discord_embeds(competitions: list[dict]) -> list[dict]:
    """Build Discord embed objects for competition notifications."""
    return [
        {
            "title": c["title"],
            "url": c["url"],
            "description": f"Category: {c['category']} | Reward: {c['reward']}",
            "footer": {"text": f"Deadline: {c['deadline']}"},
            "color": 0x1A73E8,
        }
        for c in competitions
    ]


def send_discord(competitions: list[dict], webhook_url: str) -> None:
    """Send competition notifications to Discord via Webhook (max 10 embeds per message)."""
    webhook_url = webhook_url.replace("https://discordapp.com/", "https://discord.com/")
    for i in range(0, len(competitions), 10):
        chunk = competitions[i : i + 10]
        payload = json.dumps(
            {
                "content": "**New Kaggle Competitions**" if i == 0 else None,
                "embeds": build_discord_embeds(chunk),
            }
        ).encode()
        req = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "KaggleDingDong/1.0",
            },
        )
        with urllib.request.urlopen(req, timeout=30):
            pass
