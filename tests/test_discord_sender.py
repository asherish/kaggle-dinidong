from kaggle_dingdong.discord_sender import build_discord_embeds

SAMPLE = [
    {
        "title": "Titanic",
        "url": "https://www.kaggle.com/c/titanic",
        "category": "Getting Started",
        "reward": "Knowledge",
        "deadline": "2030-01-01",
    },
]


def test_build_discord_embeds_single():
    embeds = build_discord_embeds(SAMPLE)
    assert len(embeds) == 1
    embed = embeds[0]
    assert embed["title"] == "Titanic"
    assert embed["url"] == "https://www.kaggle.com/c/titanic"
    assert "Getting Started" in embed["description"]
    assert "Knowledge" in embed["description"]
    assert embed["footer"]["text"] == "Deadline: 2030-01-01"
    assert embed["color"] == 0x1A73E8


def test_build_discord_embeds_multiple():
    comps = SAMPLE + [
        {
            "title": "Digit Recognizer",
            "url": "https://www.kaggle.com/c/digit-recognizer",
            "category": "Getting Started",
            "reward": "Knowledge",
            "deadline": "2030-06-01",
        },
    ]
    embeds = build_discord_embeds(comps)
    assert len(embeds) == 2
    assert embeds[1]["title"] == "Digit Recognizer"
