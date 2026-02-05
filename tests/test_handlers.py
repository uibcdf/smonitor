import json
from pathlib import Path

from smonitor.handlers.file import FileHandler
from smonitor.handlers.json import JsonHandler


def test_file_handler_writes(tmp_path: Path):
    path = tmp_path / "out.log"
    handler = FileHandler(str(path), mode="w")
    handler.handle({"timestamp": "t", "level": "INFO", "source": "s", "message": "m"})
    assert path.read_text(encoding="utf-8").strip().endswith("INFO | m")


def test_json_handler_writes(tmp_path: Path):
    path = tmp_path / "out.jsonl"
    handler = JsonHandler(str(path), mode="w")
    event = {"level": "INFO", "message": "m"}
    handler.handle(event, profile="dev")
    data = json.loads(path.read_text(encoding="utf-8").strip())
    assert data["message"] == "m"
    assert data["profile"] == "dev"
