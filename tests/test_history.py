import json

from src.history import load_history, save_history


def test_load_history_missing_file(tmp_path):
    path = str(tmp_path / "nonexistent.json")
    result = load_history(path)
    assert result == set()


def test_load_history_valid_file(tmp_path):
    path = tmp_path / "history.json"
    path.write_text(json.dumps({
        "sent_slugs": ["titanic", "house-prices"],
        "last_updated": "2026-01-01T00:00:00Z",
    }))
    result = load_history(str(path))
    assert result == {"titanic", "house-prices"}


def test_load_history_invalid_json(tmp_path):
    path = tmp_path / "history.json"
    path.write_text("not json")
    result = load_history(str(path))
    assert result == set()


def test_save_history(tmp_path):
    path = str(tmp_path / "history.json")
    slugs = {"titanic", "house-prices", "digit-recognizer"}
    save_history(slugs, path)

    with open(path) as f:
        data = json.load(f)

    assert data["sent_slugs"] == ["digit-recognizer", "house-prices", "titanic"]
    assert "last_updated" in data


def test_save_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "history.json")
    original = {"comp-a", "comp-b", "comp-c"}
    save_history(original, path)
    loaded = load_history(path)
    assert loaded == original


def test_deduplication_via_set():
    history = {"titanic", "house-prices"}
    all_slugs = ["titanic", "new-comp", "house-prices", "another-new"]
    new_slugs = [s for s in all_slugs if s not in history]
    assert set(new_slugs) == {"new-comp", "another-new"}
