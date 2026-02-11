from pathlib import Path

import smonitor
from smonitor.core.manager import get_manager


def test_config_precedence_runtime_over_env_and_file(tmp_path: Path, monkeypatch):
    cfg_file = tmp_path / "_smonitor.py"
    cfg_file.write_text("SMONITOR = {\"level\": \"WARNING\"}\n")
    monkeypatch.setenv("SMONITOR_LEVEL", "ERROR")
    smonitor.configure(config_path=tmp_path, level="INFO")
    manager = get_manager()
    assert manager.config.level == "INFO"


def test_config_precedence_env_over_file(tmp_path: Path, monkeypatch):
    cfg_file = tmp_path / "_smonitor.py"
    cfg_file.write_text("SMONITOR = {\"level\": \"WARNING\"}\n")
    monkeypatch.setenv("SMONITOR_LEVEL", "ERROR")
    smonitor.configure(config_path=tmp_path)
    manager = get_manager()
    assert manager.config.level == "ERROR"


def test_config_preserves_codes_when_new_config_has_none(tmp_path: Path):
    cfg_a = tmp_path / "a"
    cfg_b = tmp_path / "b"
    cfg_a.mkdir()
    cfg_b.mkdir()

    (cfg_a / "_smonitor.py").write_text(
        "CODES = {'X001': {'title': 'Test', 'user_message': 'A message'}}\n"
    )
    (cfg_b / "_smonitor.py").write_text(
        "SMONITOR = {'level': 'WARNING'}\n"
    )

    smonitor.configure(config_path=cfg_a)
    manager = get_manager()
    assert "X001" in manager.get_codes()

    smonitor.configure(config_path=cfg_b)
    manager = get_manager()
    assert "X001" in manager.get_codes()
