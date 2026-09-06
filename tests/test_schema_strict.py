import smonitor


def test_strict_schema_raises():
    manager = smonitor.configure(
        profile="dev",
        strict_schema=True,
        strict_signals=False,
        level="DEBUG",
    )
    assert manager.config.profile == "dev"
    try:
        smonitor.emit("NOPE", "", source="x", category=None, code=None)
    except ValueError as exc:
        assert "Missing required field" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_strict_schema_accepts_a_critical_event():
    # The manager scores CRITICAL above ERROR and routes it, so `strict_schema`
    # rejecting it made the highest severity the one severity a dev/qa session
    # could not emit.
    smonitor.configure(
        profile="dev",
        strict_schema=True,
        strict_signals=False,
        level="DEBUG",
        handlers=[],
    )
    event = smonitor.emit("CRITICAL", "boom", source="x", code="X-C001")
    assert event["level"] == "CRITICAL"
    assert "schema_warning" not in event["extra"]
