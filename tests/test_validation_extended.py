import pytest

from smonitor.validation import enforce_schema, validate_event


def test_validate_event_type_errors():
    errors = validate_event(
        {
            "timestamp": 123,
            "level": "NOPE",
            "message": "x",
            "tags": "bad",
            "extra": "bad",
            "context": "bad",
            "source": 1,
            "code": 2,
            "category": 3,
        }
    )
    assert "timestamp must be a string in ISO format" in errors
    assert "Invalid level: NOPE" in errors
    assert "tags must be a list of strings" in errors
    assert "extra must be a dict" in errors
    assert "context must be a dict" in errors
    assert "source must be a string" in errors
    assert "code must be a string" in errors
    assert "category must be a string" in errors


def test_validate_event_missing_code_and_category():
    errors = validate_event(
        {
            "timestamp": "2026-01-01T00:00:00+00:00",
            "level": "INFO",
            "message": "ok",
            "code": None,
            "category": None,
        }
    )
    assert "Missing code/category" in errors


def test_enforce_schema_strict_raises():
    with pytest.raises(ValueError):
        enforce_schema({"level": "INFO"}, strict=True)


def test_enforce_schema_non_strict_returns_errors():
    errors = enforce_schema({"level": "INFO"}, strict=False)
    assert errors
