import smonitor


def test_strict_schema_raises():
    manager = smonitor.configure(profile="dev", strict_schema=True)
    assert manager.config.profile == "dev"
    try:
        smonitor.emit("NOPE", "", source="x", category=None, code=None)
    except ValueError as exc:
        assert "Missing required field" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
