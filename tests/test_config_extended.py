from smonitor.config import (
    build_effective_config,
    extract_codes,
    extract_signals,
    validate_codes_signals,
    validate_config,
)


def test_build_effective_config_without_project_config():
    out = build_effective_config(None, {"profile": "dev", "level": "INFO"})
    assert out["profile"] == "dev"
    assert out["level"] == "INFO"


def test_extract_codes_and_signals_without_project_config():
    assert extract_codes(None) == {}
    assert extract_signals(None) == {}


def test_validate_config_rejects_wrong_top_level_types():
    errors = validate_config(
        {
            "SMONITOR": "bad",
            "PROFILES": "bad",
            "ROUTES": "bad",
            "FILTERS": "bad",
            "CODES": "bad",
            "SIGNALS": "bad",
        }
    )
    assert "SMONITOR must be a dict" in errors
    assert "PROFILES must be a dict" in errors
    assert "ROUTES must be a list" in errors
    assert "FILTERS must be a list" in errors
    assert "CODES must be a dict" in errors
    assert "SIGNALS must be a dict" in errors


def test_validate_config_detects_handlers_type_and_profile_type():
    errors = validate_config(
        {
            "SMONITOR": {"handlers": "not-list"},
            "PROFILES": {"qa": "not-dict"},
        }
    )
    assert any("SMONITOR.handlers must be a list" in e for e in errors)
    assert any("PROFILE qa must be a dict" in e for e in errors)


def test_validate_codes_signals_type_and_entry_errors():
    errors = validate_codes_signals(
        codes={
            1: "bad",
            "C1": {"title": 1, "user_message": 123},
        },
        signals={
            1: "bad",
            "sig": {"warnings": "bad", "errors": [1]},
        },
    )
    assert any("CODES key must be a string" in e for e in errors)
    assert any("CODES[C1].title must be a string" in e for e in errors)
    assert any("CODES[C1].user_message must be a string" in e for e in errors)
    assert any("SIGNALS key must be a string" in e for e in errors)
    assert any("SIGNALS[sig].warnings must be a list of strings" in e for e in errors)
    assert any("SIGNALS[sig].errors must be a list of strings" in e for e in errors)


def test_validate_codes_signals_non_dict_inputs():
    errors = validate_codes_signals(codes="bad", signals="bad")
    assert "CODES must be a dict" in errors
    assert "SIGNALS must be a dict" in errors
