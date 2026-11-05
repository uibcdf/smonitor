"""Distribution checks reject missing SPDX metadata and altered notice bytes."""

import importlib.util
import zipfile
from pathlib import Path

import pytest


def test_wheel_license_guard_checks_metadata_and_exact_notice(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "license_guard", Path(__file__).resolve().parents[1] / "devtools/check_license_artifacts.py"
    )
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    wheel = tmp_path / "smonitor.whl"
    notice = b"MIT original copyright\n"
    for expression, payload, error in (
        ("License: MIT", notice, "declare"),
        ("License-Expression: MIT", b"changed notice", "differs"),
        ("License-Expression: MIT", notice, None),
    ):
        with zipfile.ZipFile(wheel, "w") as archive:
            archive.writestr(
                "smonitor.dist-info/METADATA", expression + "\nLicense-File: LICENSE\n"
            )
            archive.writestr("smonitor.dist-info/licenses/LICENSE", payload)
        if error:
            with pytest.raises(ValueError, match=error):
                guard.check_wheel(wheel, notice)
        else:
            guard.check_wheel(wheel, notice)
