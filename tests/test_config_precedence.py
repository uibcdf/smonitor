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
