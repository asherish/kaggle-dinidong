from kaggle_dingdong.email_sender import build_html_body

SAMPLE_COMPS = [
    {
        "title": "Test Competition",
        "url": "https://www.kaggle.com/competitions/test",
        "category": "Featured",
        "reward": "$10,000",
        "deadline": "2026-12-31",
    },
]


def test_build_html_body_returns_html():
    html = build_html_body(SAMPLE_COMPS)
    assert "<html>" in html
    assert "</html>" in html


def test_build_html_body_contains_link():
    html = build_html_body(SAMPLE_COMPS)
    assert 'href="https://www.kaggle.com/competitions/test"' in html
    assert "Test Competition" in html


def test_build_html_body_contains_details():
    html = build_html_body(SAMPLE_COMPS)
    assert "Featured" in html
    assert "$10,000" in html
    assert "2026-12-31" in html


def test_build_html_body_multiple_comps():
    comps = SAMPLE_COMPS + [
        {
            "title": "Another Comp",
            "url": "https://www.kaggle.com/competitions/another",
            "category": "Research",
            "reward": "Swag",
            "deadline": "2026-06-15",
        },
    ]
    html = build_html_body(comps)
    assert "Test Competition" in html
    assert "Another Comp" in html
