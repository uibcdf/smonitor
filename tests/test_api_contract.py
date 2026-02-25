import smonitor


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
