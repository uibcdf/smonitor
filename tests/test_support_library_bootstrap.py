"""Guard the diagnostic bootstrap boundary while provider cycles exist."""

from __future__ import annotations

import importlib.metadata
import importlib.util
import itertools
import os
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
from packaging.requirements import Requirement

ROOT = Path(__file__).resolve().parents[1]


def _required_names(distribution: str) -> set[str]:
    requirements = importlib.metadata.requires(distribution) or []
    return {
        parsed.name.lower().replace("_", "-")
        for raw in requirements
        if (parsed := Requirement(raw)).marker is None or parsed.marker.evaluate({"extra": ""})
    }


def test_no_required_dependency_cycle_with_diagnostic_providers():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    smonitor_requires = {
        Requirement(raw).name.lower().replace("_", "-")
        for raw in project["project"]["dependencies"]
    }
    for provider in ("argdigest", "depdigest"):
        try:
            provider_requires = _required_names(provider)
        except importlib.metadata.PackageNotFoundError:
            continue
        if "smonitor" in provider_requires:
            assert provider not in smonitor_requires, (
                f"{provider} requires smonitor; a reverse required edge would form a cycle"
            )


@pytest.mark.skipif(
    any(importlib.util.find_spec(name) is None for name in ("argdigest", "depdigest")),
    reason="both diagnostic providers must be installed for the import-order check",
)
def test_provider_import_orders_preserve_smonitor_validation(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(filter(None, (str(ROOT), env.get("PYTHONPATH", ""))))
    for order in itertools.permutations(("smonitor", "argdigest", "depdigest")):
        code = (
            "import importlib; "
            f"[importlib.import_module(name) for name in {order!r}]; "
            "import smonitor; "
            "from smonitor.validation import validate_event; "
            "smonitor.configure(handlers=[]); "
            "assert validate_event({'level': 'INFO'})"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"{order}: {result.stderr}"
