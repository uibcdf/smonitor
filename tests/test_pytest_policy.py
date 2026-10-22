"""Strict QA reads canonical evidence without changing the pytest run."""

from __future__ import annotations

import json
import sys

import pytest

from smonitor.cli import main
from smonitor.pytest_policy import (
    evaluate_pytest_artifact,
    load_baseline,
    load_provider_codes,
    write_baseline,
)

pytest_plugins = ["pytester"]


def test_policy_uses_identity_set_and_reports_catalog_and_forbidden_rules(
    pytester, monkeypatch, capsys
):
    pytest.importorskip("pytest_receptor")
    pytester.makepyfile(
        test_diagnostics="""
        import smonitor

        def test_first():
            smonitor.configure(level='DEBUG', handlers=[])
            for _ in range(3):
                smonitor.emit('WARNING', 'example', code='EXAMPLE-WARN-001', source='example.test')

        def test_second():
            smonitor.emit('ERROR', 'example', code='EXAMPLE-ERROR-001', source='example.test')
        """
    )
    result = pytester.runpytest("--receptor=llm", "--receptor-events=events.jsonl")
    assert result.ret == pytest.ExitCode.OK
    artifact = pytester.path / "events.jsonl"

    observed = evaluate_pytest_artifact(artifact)
    assert observed["ok"] is True
    assert observed["pytest_outcome"] == "PASS"
    assert observed["diagnostic_records"] == 4
    assert len(observed["identities"]) == 2
    assert {item["code"] for item in observed["identities"]} == {
        "EXAMPLE-WARN-001",
        "EXAMPLE-ERROR-001",
    }

    baseline_path = pytester.path / "baseline.json"
    identities = [
        tuple(item[key] for key in ("code", "source", "fingerprint"))
        for item in observed["identities"]
    ]
    write_baseline(baseline_path, identities)
    assert load_baseline(baseline_path) == set(identities)
    assert evaluate_pytest_artifact(artifact, baseline=load_baseline(baseline_path))["ok"] is True

    policy = evaluate_pytest_artifact(
        artifact,
        known_codes={"EXAMPLE-WARN-001"},
        forbidden_codes={"EXAMPLE-WARN-001"},
        baseline={identities[0]},
    )
    assert policy["ok"] is False
    assert {entry["rule"] for entry in policy["violations"]} == {
        "code_not_in_catalog",
        "forbidden_code",
        "new_diagnostic_identity",
    }
    assert len(policy["violations"]) == 3
    assert policy["disappeared_identities"] == []

    partial = pytester.path / "partial.jsonl"
    partial.write_bytes(b"\n".join(artifact.read_bytes().splitlines()[:-1]) + b"\n")
    incomplete = evaluate_pytest_artifact(partial)
    assert incomplete["ok"] is False
    assert "artifact_incomplete" in {entry["rule"] for entry in incomplete["violations"]}

    pytester.makepyfile(test_empty="def test_ok(): assert True")
    empty_run = pytester.runpytest(
        "test_empty.py", "--receptor=llm", "--receptor-events=empty.jsonl"
    )
    assert empty_run.ret == pytest.ExitCode.OK
    empty = evaluate_pytest_artifact(pytester.path / "empty.jsonl", require_diagnostics=True)
    assert empty["ok"] is False
    assert empty["violations"] == [{"rule": "diagnostics_missing"}]
    empty_baseline = pytester.path / "empty-baseline.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "smonitor",
            "pytest-baseline",
            str(pytester.path / "empty.jsonl"),
            "--out",
            str(empty_baseline),
        ],
    )
    assert main() == 1
    assert not empty_baseline.exists()
    assert "empty_baseline_requires_opt_in" in capsys.readouterr().out

    pytester.makepyfile(test_failure="def test_fails(): assert False")
    failed_run = pytester.runpytest(
        "test_failure.py", "--receptor=llm", "--receptor-events=failed.jsonl"
    )
    assert failed_run.ret == pytest.ExitCode.TESTS_FAILED
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "smonitor",
            "pytest-baseline",
            str(pytester.path / "failed.jsonl"),
            "--out",
            str(empty_baseline),
        ],
    )
    assert main() == 1
    assert not empty_baseline.exists()
    assert "pytest_run_not_passed" in capsys.readouterr().out


def test_provider_catalog_validation_is_explicit_and_does_not_register(pytester):
    root = pytester.path / "provider"
    root.mkdir()
    (root / "_smonitor.py").write_text(
        "CODES = {'EXAMPLE-WARN-001': {'message': 'Example {reason}'}}\n",
        encoding="utf-8",
    )
    codes, problems = load_provider_codes([root])
    assert codes == {"EXAMPLE-WARN-001"}
    assert problems == []

    (root / "_smonitor.py").write_text(
        "CODES = {'EXAMPLE-WARN-001': {'title': 'Missing template'}}\n",
        encoding="utf-8",
    )
    codes, problems = load_provider_codes([root])
    assert codes == set()
    assert [problem["rule"] for problem in problems] == ["provider_catalog_invalid"]

    (root / "_smonitor.py").write_text("raise RuntimeError('private detail')\n", encoding="utf-8")
    codes, problems = load_provider_codes([root])
    assert codes == set()
    assert problems == [
        {
            "rule": "provider_config_error",
            "provider": str(root),
            "exception_type": "RuntimeError",
        }
    ]


def test_baseline_rejects_duplicate_and_malformed_identities(tmp_path):
    baseline = tmp_path / "baseline.json"
    identity = {"code": "EXAMPLE-WARN-001", "source": "example.test", "fingerprint": "a" * 16}
    baseline.write_text(
        json.dumps({"schema": "smonitor.pytest-baseline@1", "identities": [identity, identity]}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="identity"):
        load_baseline(baseline)
    with pytest.raises(FileExistsError):
        write_baseline(baseline, [])
