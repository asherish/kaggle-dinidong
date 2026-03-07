import json

from kaggle_dingdong.history import load_history, save_history


def test_load_history_missing_file(tmp_path):
    path = tmp_path / "missing.json"
    titles_list, titles_set = load_history(path)
    assert titles_list == []
    assert titles_set == set()


def test_load_history_existing_file(tmp_path):
    path = tmp_path / "history.json"
    path.write_text(json.dumps(["A", "B", "C"]))
    titles_list, titles_set = load_history(path)
    assert titles_list == ["A", "B", "C"]
    assert titles_set == {"A", "B", "C"}


def test_save_history_basic(tmp_path):
    path = tmp_path / "history.json"
    save_history(["A", "B"], ["C"], path, limit=200)
    data = json.loads(path.read_text())
    assert data == ["A", "B", "C"]


def test_save_history_trims_to_limit(tmp_path):
    path = tmp_path / "history.json"
    existing = [f"comp_{i}" for i in range(198)]
    new = ["new_1", "new_2", "new_3"]
    save_history(existing, new, path, limit=200)
    data = json.loads(path.read_text())
    assert len(data) == 200
    # The oldest entry should have been dropped
    assert data[0] == "comp_1"
    assert data[-1] == "new_3"
