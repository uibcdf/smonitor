"""Retained support evidence must not mask executed operation failures."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "devtools/operability_evidence.py"


@pytest.mark.parametrize("suite_fails", [False, True])
@pytest.mark.parametrize("bad_comparison", [False, True])
def test_cli_propagates_failure_and_keeps_requested_evidence(tmp_path, suite_fails, bad_comparison):
    repo = tmp_path / "controlled component"
    tests = repo / "tests"
    tests.mkdir(parents=True)
    (tests / "test_controlled.py").write_text(
        "def test_controlled():\n    assert " + str(not suite_fails) + "\n",
        encoding="utf-8",
    )
    sentinel = repo / "caller-owned"
    sentinel.write_text("keep", encoding="utf-8")
    output = tmp_path / "evidence" / "report.json"
    command = [sys.executable, str(SCRIPT), str(repo), "--out", str(output)]
    if bad_comparison:
        invalid = tmp_path / "invalid-baseline.json"
        invalid.write_text("{broken", encoding="utf-8")
        command += ["--compare-with", str(invalid)]
    completed = subprocess.run(command, capture_output=True, text=True, timeout=30)
    assert completed.returncode == (1 if suite_fails or bad_comparison else 0), (
        completed.stdout + completed.stderr
    )
    assert f"pytest exit={int(suite_fails)}" in completed.stdout
    assert isinstance(json.loads(output.read_text(encoding="utf-8"))["triage"], dict)
    assert sentinel.read_text(encoding="utf-8") == "keep"
    # Pytest's cache is explicitly disabled in this evidence tool.
    assert not (repo / ".pytest_cache").exists()
    if bad_comparison:
        assert invalid.read_text(encoding="utf-8") == "{broken"


def test_main_keeps_suite_failure_as_primary_outcome(monkeypatch, tmp_path):
    spec = importlib.util.spec_from_file_location("operability_probe_test", SCRIPT)
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    monkeypatch.setattr(tool, "run", lambda *args: {"exit": 2, "events": 0})
    monkeypatch.setattr(tool, "summarise", lambda *args: None)
    monkeypatch.setattr(
        tool.subprocess, "run", lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 7)
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(SCRIPT),
            str(tmp_path),
            "--out",
            str(tmp_path / "report.json"),
            "--compare-with",
            str(tmp_path / "baseline.json"),
        ],
    )
    assert tool.main() == 2
