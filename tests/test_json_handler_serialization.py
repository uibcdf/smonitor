from smonitor.handlers.json import JsonHandler


def test_json_handler_non_serializable_extra(tmp_path):
    path = tmp_path / "out.jsonl"
    handler = JsonHandler(str(path), mode="w")
    event = {"level": "INFO", "message": "m", "extra": {"x": set([1, 2])}}
    handler.handle(event)
    text = path.read_text(encoding="utf-8")
    assert "{1, 2}" in text
