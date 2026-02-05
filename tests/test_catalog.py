from pathlib import Path

from smonitor.catalog import generate_catalog, write_catalog


def test_generate_catalog_empty(tmp_path: Path):
    data = generate_catalog(tmp_path)
    assert "Code |" in data["codes"]


def test_write_catalog(tmp_path: Path):
    write_catalog(tmp_path, tmp_path)
    assert (tmp_path / "_generated_codes.md").exists()
    assert (tmp_path / "_generated_signals.md").exists()
