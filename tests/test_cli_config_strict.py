import subprocess
import sys
from pathlib import Path


def test_cli_validate_config_strict(tmp_path: Path):
    cfg = tmp_path / "_smonitor.py"
    cfg.write_text("FOO = 1\n")
    cmd = [
        sys.executable,
        "-m",
        "smonitor.cli",
        "--validate-config",
        "--config-path",
        str(tmp_path),
    ]
    out = subprocess.run(cmd, capture_output=True, text=True)
    assert out.returncode == 2
    assert "Invalid _smonitor.py" in out.stdout
