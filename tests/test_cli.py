import json
import subprocess
import sys
from pathlib import Path


def test_cli_check_event(tmp_path: Path):
    cfg = tmp_path / "_smonitor.py"
    cfg.write_text("SMONITOR = {}\n")
    event = json.dumps({"level": "WARNING", "message": "x"})
    cmd = [sys.executable, "-m", "smonitor.cli", "--check", "--config-path", str(tmp_path), "--check-event", event]
    out = subprocess.run(cmd, capture_output=True, text=True)
    assert out.returncode == 0
    assert "OK" in out.stdout
