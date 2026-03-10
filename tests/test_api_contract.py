import json

import smonitor
from smonitor.handlers.json import JsonHandler


def test_public_exports_contract():
    expected = {
        "configure",
        "emit",
        "resolve",
        "report",
        "signal",
        "get_manager",
        "export_bundle",
        "collect_bundle",
        "integrations",
    }
    assert expected.issubset(set(smonitor.__all__))


def test_configure_emit_resolve_report_contract():
    manager = smonitor.configure(profile="user", strict_signals=False, handlers=[])
    assert manager is smonitor.get_manager()

    manager.configure(codes={"TST-001": {"user_message": "Field {field} missing"}})
    message, hint = smonitor.resolve(code="TST-001", extra={"field": "x"})
    assert message == "Field x missing"
    assert hint is None

    event = smonitor.emit("WARNING", "", code="TST-001", extra={"field": "x"})
    assert event["message"] == "Field x missing"
    assert event["level"] == "WARNING"

    report = smonitor.report()
    assert "warnings_total" in report
    assert "events_by_code" in report
    assert "events_by_category" in report
    assert "events_by_fingerprint" in report
    assert "slow_signals_recent" in report
    assert "coalesced_warnings" in report
    assert "duplicate_summaries" in report


def test_json_machine_contract_is_documented_via_handler_output(tmp_path):
    path = tmp_path / "event.jsonl"
    JsonHandler(str(path), mode="w").handle({"level": "INFO", "message": "m"}, profile="agent")
    payload = json.loads(path.read_text(encoding="utf-8").strip())
    assert "normalized" in payload
    assert "fingerprint" in payload
    assert payload["normalized"]["fingerprint"] == payload["fingerprint"]
