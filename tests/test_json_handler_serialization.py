from smonitor.handlers.json import JsonHandler


def test_json_handler_non_serializable_extra(tmp_path):
    path = tmp_path / "out.jsonl"
    handler = JsonHandler(str(path), mode="w")
    event = {"level": "INFO", "message": "m", "extra": {"x": set([1, 2])}}
    handler.handle(event)
    text = path.read_text(encoding="utf-8")
    assert "{1, 2}" in text


def test_json_handler_includes_normalized_machine_payload(tmp_path):
    path = tmp_path / "out.jsonl"
    handler = JsonHandler(str(path), mode="w")
    event = {
        "level": "WARNING",
        "message": "m",
        "source": "pkg.mod",
        "code": "W1",
        "category": "diagnostics",
        "tags": ["api"],
        "extra": {
            "caller": "pkg.mod.fn",
            "resource": "181l",
            "provider": "RCSB",
            "operation": "download",
        },
    }
    handler.handle(event, profile="agent")
    import json
    payload = json.loads(path.read_text(encoding="utf-8").strip())
    normalized = payload["normalized"]
    assert normalized["source"] == "pkg.mod"
    assert normalized["code"] == "W1"
    assert normalized["tags"] == ["api"]
    assert normalized["caller"] == "pkg.mod.fn"
    assert normalized["resource"] == "181l"
    assert normalized["provider"] == "RCSB"
    assert normalized["operation"] == "download"
