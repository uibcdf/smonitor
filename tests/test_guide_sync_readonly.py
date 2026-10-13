"""The legacy guide helper must preserve sibling checkout files (#47)."""

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "devtools" / "sync_smonitor_guide.py"


@pytest.mark.parametrize("options", [[], ["--dry-run"]])
def test_guide_audit_reports_drift_without_writing(tmp_path, options):
    canonical = tmp_path / "smonitor" / "standards" / "SMONITOR_GUIDE.md"
    canonical.parent.mkdir(parents=True)
    canonical.write_text("canonical\n")
    sibling = tmp_path / "molsysmt" / "SMONITOR_GUIDE.md"
    sibling.parent.mkdir()
    sibling.write_text("human work\n")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path), *options],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert f"[drift] {sibling}" in result.stdout
    assert sibling.read_text() == "human work\n"


def test_guide_audit_accepts_identical_copy(tmp_path):
    canonical = tmp_path / "smonitor" / "standards" / "SMONITOR_GUIDE.md"
    canonical.parent.mkdir(parents=True)
    canonical.write_text("canonical\n")
    sibling = tmp_path / "molsysmt" / "SMONITOR_GUIDE.md"
    sibling.parent.mkdir()
    sibling.write_text("canonical\n")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert f"[in-sync] {sibling}" in result.stdout
