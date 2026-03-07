from kaggle_dingdong.slack_sender import build_slack_blocks

SAMPLE = [
    {
        "title": "Titanic",
        "url": "https://www.kaggle.com/c/titanic",
        "category": "Getting Started",
        "reward": "Knowledge",
        "deadline": "2030-01-01",
    },
]


def test_build_slack_blocks_header():
    blocks = build_slack_blocks(SAMPLE)
    assert blocks[0]["type"] == "header"
    assert blocks[0]["text"]["text"] == "New Kaggle Competitions"


def test_build_slack_blocks_section():
    blocks = build_slack_blocks(SAMPLE)
    assert blocks[1]["type"] == "divider"
    section = blocks[2]
    assert section["type"] == "section"
    assert "Titanic" in section["text"]["text"]
    assert "https://www.kaggle.com/c/titanic" in section["text"]["text"]
    assert "Getting Started" in section["text"]["text"]
    assert "Knowledge" in section["text"]["text"]
    assert "2030-01-01" in section["text"]["text"]


def test_build_slack_blocks_multiple():
    comps = SAMPLE + [
        {
            "title": "Digit Recognizer",
            "url": "https://www.kaggle.com/c/digit-recognizer",
            "category": "Getting Started",
            "reward": "Knowledge",
            "deadline": "2030-06-01",
        },
    ]
    blocks = build_slack_blocks(comps)
    # header + (divider + section) * 2 = 5
    assert len(blocks) == 5
