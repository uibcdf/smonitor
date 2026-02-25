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
