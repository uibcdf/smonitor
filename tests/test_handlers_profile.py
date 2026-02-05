from smonitor.handlers.file import FileHandler
from smonitor.handlers.json import JsonHandler


def test_file_handler_dev_hint(tmp_path):
    path = tmp_path / "out.log"
    handler = FileHandler(str(path), mode="w")
    handler.handle({"timestamp": "t", "level": "INFO", "source": "s", "message": "m", "extra": {"hint": "h"}}, profile="dev")
    text = path.read_text(encoding="utf-8")
    assert "Hint: h" in text


def test_json_handler_profile_field(tmp_path):
    path = tmp_path / "out.jsonl"
    handler = JsonHandler(str(path), mode="w")
    handler.handle({"level": "INFO", "message": "m"}, profile="qa")
    text = path.read_text(encoding="utf-8")
    assert "\"profile\": \"qa\"" in text
