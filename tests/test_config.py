from pathlib import Path

from smonitor.config import (
    load_project_config,
    build_effective_config,
    extract_policy,
    load_env_config,
    validate_config,
    validate_project_config,
)


def test_build_effective_config_profile(tmp_path: Path):
    cfg_file = tmp_path / "_smonitor.py"
    cfg_file.write_text(
        "PROFILE = 'dev'\n"
        "SMONITOR = {'level': 'WARNING'}\n"
        "PROFILES = {'dev': {'level': 'INFO', 'profile': 'dev'}}\n"
        "ROUTES = []\n"
    )
    cfg = load_project_config(tmp_path)
    effective = build_effective_config(cfg, {})
    assert effective["level"] == "INFO"
    assert effective["profile"] == "dev"


def test_extract_policy(tmp_path: Path):
    cfg_file = tmp_path / "_smonitor.py"
    cfg_file.write_text("ROUTES = [{'when': {'level': 'WARNING'}, 'send_to': ['console']}]")
    cfg = load_project_config(tmp_path)
    policy = extract_policy(cfg)
    assert policy["routes"]


def test_load_env_config(monkeypatch):
    monkeypatch.setenv("SMONITOR_PROFILE", "dev")
    monkeypatch.setenv("SMONITOR_LEVEL", "INFO")
    monkeypatch.setenv("SMONITOR_TRACE_DEPTH", "5")
    monkeypatch.setenv("SMONITOR_CAPTURE_WARNINGS", "1")
    monkeypatch.setenv("SMONITOR_HANDLER_ERROR_THRESHOLD", "3")
    cfg = load_env_config()
    assert cfg["profile"] == "dev"
    assert cfg["level"] == "INFO"
    assert cfg["trace_depth"] == 5
    assert cfg["capture_warnings"] is True
    assert cfg["handler_error_threshold"] == 3


def test_load_env_config_invalid_profiling_sample(monkeypatch):
    monkeypatch.setenv("SMONITOR_PROFILING_SAMPLE", "not-a-float")
    cfg = load_env_config()
    assert cfg["profiling_sample_rate"] is None


def test_load_env_config_out_of_range_profiling_sample(monkeypatch):
    monkeypatch.setenv("SMONITOR_PROFILING_SAMPLE", "1.5")
    cfg = load_env_config()
    assert cfg["profiling_sample_rate"] is None


def test_validate_config_unknown_key(tmp_path: Path):
    cfg_file = tmp_path / "_smonitor.py"
    cfg_file.write_text("FOO = 1")
    cfg = load_project_config(tmp_path)
    errors = validate_config(cfg)
    assert errors and "Unknown top-level key" in errors[0]


def test_validate_config_unknown_smonitor_key(tmp_path: Path):
    cfg_file = tmp_path / "_smonitor.py"
    cfg_file.write_text("SMONITOR = {'bad': 1}\n")
    cfg = load_project_config(tmp_path)
    errors = validate_config(cfg)
    assert any("Unknown SMONITOR key" in e for e in errors)


def test_validate_config_profile_types(tmp_path: Path):
    cfg_file = tmp_path / "_smonitor.py"
    cfg_file.write_text(
        "SMONITOR = {'trace_depth': 'nope'}\n"
        "PROFILES = {'dev': {'level': 1}}\n"
    )
    cfg = load_project_config(tmp_path)
    errors = validate_config(cfg)
    assert any("SMONITOR.trace_depth must be an int" in e for e in errors)
    assert any("PROFILES.dev.level must be a string" in e for e in errors)


def test_validate_project_config_codes(tmp_path: Path):
    cfg_file = tmp_path / "_smonitor.py"
    cfg_file.write_text(
        "CODES = {\n"
        "  'X001': {'title': 'Test'}\n"
        "}\n"
    )
    cfg = load_project_config(tmp_path)
    errors = validate_project_config(cfg)
    assert any("must define a message field" in e for e in errors)


def test_validate_project_config_signals(tmp_path: Path):
    cfg_file = tmp_path / "_smonitor.py"
    cfg_file.write_text(
        "SIGNALS = {\n"
        "  'mod.fn': {'extra_required': 'nope'}\n"
        "}\n"
    )
    cfg = load_project_config(tmp_path)
    errors = validate_project_config(cfg)
    assert any("extra_required must be a list of strings" in e for e in errors)
