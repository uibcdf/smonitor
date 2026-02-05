from pathlib import Path

from smonitor.config import load_project_config, build_effective_config, extract_policy, load_env_config


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
    cfg = load_env_config()
    assert cfg["profile"] == "dev"
    assert cfg["level"] == "INFO"
    assert cfg["trace_depth"] == 5
    assert cfg["capture_warnings"] is True
