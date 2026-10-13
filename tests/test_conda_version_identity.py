"""Guard exact SMonitor version identity in the Conda artifact."""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FREEZER = ROOT / "devtools" / "conda-build" / "freeze_project_version.py"


def _freezer_module():
    spec = importlib.util.spec_from_file_location("freeze_project_version", FREEZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_freezer_writes_one_exact_version_source(tmp_path):
    shutil.copy2(ROOT / "pyproject.toml", tmp_path / "pyproject.toml")
    package = tmp_path / "smonitor"
    package.mkdir()

    _freezer_module().freeze_project_version(tmp_path, "0.15.1")

    pyproject = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "0.15.1"' in pyproject
    assert 'dynamic = ["version"]' not in pyproject
    assert "[tool.versioningit" not in pyproject
    assert (package / "_version.py").read_text(encoding="utf-8") == ('__version__ = "0.15.1"\n')


def test_freezer_rejects_an_untrusted_version(tmp_path):
    with pytest.raises(ValueError, match="Invalid package version"):
        _freezer_module().freeze_project_version(tmp_path, '0.15.1"; echo unsafe')


def test_conda_build_freezes_and_checks_the_exact_version():
    build_script = (ROOT / "devtools" / "conda-build" / "build.sh").read_text(encoding="utf-8")
    freeze = build_script.index("freeze_project_version.py")
    install = build_script.index("pip install")
    assert freeze < install

    recipe = (ROOT / "devtools" / "conda-build" / "meta.yaml").read_text(encoding="utf-8")
    assert "md.version('smonitor') == expected" in recipe
    assert "smonitor.__version__ == expected" in recipe


def test_failed_version_freeze_stops_build_before_install(tmp_path):
    """A partial ephemeral build source must never reach pip installation (#47)."""
    python = tmp_path / "python"
    marker = tmp_path / "pip-was-invoked"
    python.write_text(
        "#!/bin/sh\n"
        'case "$1" in\n'
        "  *freeze_project_version.py) exit 7 ;;\n"
        '  *) touch "$PIP_MARKER"; exit 0 ;;\n'
        "esac\n"
    )
    python.chmod(0o755)
    env = {
        **os.environ,
        "PYTHON": str(python),
        "PKG_VERSION": "0.21.0",
        "PIP_MARKER": str(marker),
    }

    result = subprocess.run(
        ["bash", str(ROOT / "devtools" / "conda-build" / "build.sh")],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 7
    assert not marker.exists()
