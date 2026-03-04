from pathlib import Path

from smonitor.config.discovery import discover_config


def test_discover_config_from_parent(tmp_path: Path):
    root = tmp_path / 'proj'
    child = root / 'pkg' / 'sub'
    child.mkdir(parents=True)
    (root / '_smonitor.py').write_text('SMONITOR = {}\n')
    cfg = discover_config(child)
    assert cfg is not None
    assert 'SMONITOR' in cfg

    none_cfg = discover_config(tmp_path / 'other')
    assert none_cfg is None


def test_load_config_returns_none_when_spec_has_no_loader(monkeypatch, tmp_path: Path):
    from smonitor.config import discovery as mod

    cfg_file = tmp_path / "_smonitor.py"
    cfg_file.write_text("SMONITOR = {}\n")

    class _Spec:
        loader = None

    monkeypatch.setattr(mod.importlib.util, "spec_from_file_location", lambda *a, **k: _Spec())
    assert mod.load_config_from_path(cfg_file) is None
