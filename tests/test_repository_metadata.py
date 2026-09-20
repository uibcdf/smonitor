from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readme_does_not_cite_the_molsysmt_zenodo_archive():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "zenodo.org/badge/137937243" not in readme
    assert "zenodo.org/badge/latestdoi/137937243" not in readme
