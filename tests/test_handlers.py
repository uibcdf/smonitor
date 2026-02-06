import json
from pathlib import Path

from smonitor.handlers.file import FileHandler
from smonitor.handlers.json import JsonHandler
from smonitor.handlers.memory import MemoryHandler


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


def test_handlers_create_parent_dir(tmp_path: Path):
    file_path = tmp_path / "logs" / "out.log"
    json_path = tmp_path / "logs" / "out.jsonl"
    FileHandler(str(file_path), mode="w").handle({"timestamp": "t", "level": "INFO", "message": "m"})
    JsonHandler(str(json_path), mode="w").handle({"level": "INFO", "message": "m"})
    assert file_path.exists()


def test_memory_handler_buffers():
    handler = MemoryHandler(max_events=2)
    handler.handle({"message": "a"}, profile="user")
    handler.handle({"message": "b"}, profile="user")
    handler.handle({"message": "c"}, profile="user")
    assert len(handler.events) == 2
    assert handler.events[0]["message"] == "b"
