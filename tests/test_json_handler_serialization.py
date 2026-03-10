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
        "run_id": "run-1",
        "session_id": "session-1",
        "correlation_id": "corr-1",
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
            "incident_kind": "network",
            "severity": "medium",
            "priority": "high",
            "diagnostic_confidence": "high",
            "recommended_action": "retry",
            "next_step": "check-network",
            "retryable": True,
            "support_needed": False,
            "evidence": {
                "expected": "download ok",
                "observed": "timeout",
                "resource": "181l",
            },
        },
    }
    handler.handle(event, profile="agent")
    import json
    payload = json.loads(path.read_text(encoding="utf-8").strip())
    normalized = payload["normalized"]
    assert normalized["source"] == "pkg.mod"
    assert normalized["code"] == "W1"
    assert normalized["tags"] == ["api"]
    assert normalized["run_id"] == "run-1"
    assert normalized["session_id"] == "session-1"
    assert normalized["correlation_id"] == "corr-1"
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
    assert normalized["incident_kind"] == "network"
    assert normalized["severity"] == "medium"
    assert normalized["priority"] == "high"
    assert normalized["diagnostic_confidence"] == "high"
    assert normalized["recommended_action"] == "retry"
    assert normalized["next_step"] == "check-network"
    assert normalized["retryable"] is True
    assert normalized["support_needed"] is False
    assert normalized["evidence"] == {
        "expected": "download ok",
        "observed": "timeout",
        "resource": "181l",
    }
