import json
import subprocess
import sys
from pathlib import Path


def test_cli_check_event(tmp_path: Path):
    cfg = tmp_path / "_smonitor.py"
    cfg.write_text("SMONITOR = {}\n")
    event = json.dumps({"level": "WARNING", "message": "x"})
    cmd = [
        sys.executable,
        "-m",
        "smonitor.cli",
        "--check",
        "--config-path",
        str(tmp_path),
        "--check-event",
        event,
    ]
    out = subprocess.run(cmd, capture_output=True, text=True)
    assert out.returncode == 0
    assert "OK" in out.stdout


def test_cli_export_bundle(tmp_path: Path):
    cfg = tmp_path / "_smonitor.py"
    cfg.write_text("SMONITOR = {}\n")
    out_path = tmp_path / "bundle.json"
    cmd = [
        sys.executable,
        "-m",
        "smonitor.cli",
        "export",
        "--config-path",
        str(tmp_path),
        "--out",
        str(out_path),
        "--no-events",
        "--force",
    ]
    out = subprocess.run(cmd, capture_output=True, text=True)
    assert out.returncode == 0
    assert out_path.exists()
