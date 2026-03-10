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
            "retry_attempt": 2,
            "retry_max": 5,
            "retry_exhausted": False,
            "retry_delay_s": 1.5,
            "failure_class": "network",
            "last_failure_reason": "timeout",
            "cause_exception_type": "TimeoutError",
            "cause_code": "NET-TIMEOUT",
            "causal_chain": [{"code": "NET-TIMEOUT"}],
        },
    }
    handler.handle(event, profile="agent")
    import json
    payload = json.loads(path.read_text(encoding="utf-8").strip())
    normalized = payload["normalized"]
    assert normalized["source"] == "pkg.mod"
    assert normalized["code"] == "W1"
    assert normalized["tags"] == ["api"]
    assert normalized["fingerprint"] == payload["fingerprint"]
    assert normalized["caller"] == "pkg.mod.fn"
    assert normalized["resource"] == "181l"
    assert normalized["provider"] == "RCSB"
    assert normalized["operation"] == "download"
    assert normalized["retry_attempt"] == 2
    assert normalized["retry_max"] == 5
    assert normalized["retry_exhausted"] is False
    assert normalized["retry_delay_s"] == 1.5
    assert normalized["failure_class"] == "network"
    assert normalized["last_failure_reason"] == "timeout"
    assert normalized["cause_exception_type"] == "TimeoutError"
    assert normalized["cause_code"] == "NET-TIMEOUT"
    assert normalized["causal_chain"] == [{"code": "NET-TIMEOUT"}]
