from smonitor.validation import validate_event


def test_validate_event_missing_fields():
    errors = validate_event({"level": "INFO"})
    assert any("timestamp" in e for e in errors)
    assert any("message" in e for e in errors)


def test_validate_event_invalid_level():
    errors = validate_event({"timestamp": "t", "level": "NOPE", "message": "m"})
    assert any("Invalid level" in e for e in errors)
