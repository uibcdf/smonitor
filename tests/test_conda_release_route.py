from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
from urllib.error import HTTPError

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "devtools" / "conda-build" / "release_route.py"
SPEC = importlib.util.spec_from_file_location("smonitor_release_route", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
route = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(route)
SHA = "7daac74c6641e6003df8bbcc6cca91709ec891b9"


def _plan(*, chosen_route: str = "direct") -> dict:
    return {
        "version": "0.17.0",
        "route": chosen_route,
        "reason": "No pre-public installed artifact or coupled consumer gate is required.",
        "decision_by": "release maintainer",
        "required_workflows": [route.FULL_MATRIX],
    }


def test_committed_plan_rejects_unset_fields_and_missing_matrix(tmp_path):
    plan = tmp_path / "release_plan.toml"
    plan.write_text(
        'version = "0.17.0"\nroute = "direct"\nreason = "routine"\n'
        'decision_by = "maintainer"\nrequired_workflows = []\n',
        encoding="utf-8",
    )
    with pytest.raises(route.ReleaseRouteError, match="full-matrix"):
        route.read_plan(plan)
    plan.write_text(
        'version = ""\nroute = "direct"\nreason = "routine"\n'
        'decision_by = "maintainer"\nrequired_workflows = [".github/workflows/CI_full_matrix.yaml"]\n',
        encoding="utf-8",
    )
    with pytest.raises(route.ReleaseRouteError, match="canonical"):
        route.read_plan(plan)


def test_release_event_selects_only_the_matching_committed_route(monkeypatch):
    monkeypatch.setattr(route, "read_plan", lambda: _plan(chosen_route="staged"))
    assert route.committed_plan_for("0.17.0")["route"] == "staged"
    with pytest.raises(route.ReleaseRouteError, match="does not match"):
        route.committed_plan_for("0.17.1")
    with pytest.raises(route.ReleaseRouteError, match="canonical"):
        route.committed_plan_for("v0.17.0")

    monkeypatch.setattr(route, "read_plan", lambda: _plan(chosen_route="direct"))
    assert route.committed_plan_for("0.17.0")["route"] == "direct"


@pytest.mark.parametrize("wrong_field", ["head_sha", "path", "conclusion", "status"])
def test_required_ci_must_have_exact_identity_and_success(monkeypatch, wrong_field):
    run = {
        "id": 123,
        "head_sha": SHA,
        "path": route.FULL_MATRIX,
        "status": "completed",
        "conclusion": "success",
    }
    wrong_values = {
        "head_sha": "0" * 40,
        "path": ".github/workflows/docs_ci.yaml",
        "conclusion": "failure",
        "status": "in_progress",
    }
    run[wrong_field] = wrong_values[wrong_field]
    monkeypatch.setattr(route, "_read_json", lambda *args, **kwargs: {"workflow_runs": [run]})
    with pytest.raises(route.ReleaseRouteError, match="no successful exact-commit run"):
        route.verified_workflow_runs("uibcdf/smonitor", SHA, [route.FULL_MATRIX], "token")


def test_required_ci_accepts_only_exact_successful_run(monkeypatch):
    run = {
        "id": 123,
        "head_sha": SHA,
        "path": route.FULL_MATRIX,
        "status": "completed",
        "conclusion": "success",
    }

    def fake_read(url, *, token=None):
        assert "head_sha=" + SHA in url
        assert token == "token"
        return {"workflow_runs": [run]}

    monkeypatch.setattr(route, "_read_json", fake_read)
    assert route.verified_workflow_runs("uibcdf/smonitor", SHA, [route.FULL_MATRIX], "token") == [
        {"workflow": route.FULL_MATRIX, "run_id": 123}
    ]


def test_direct_preflight_accepts_only_explicit_404(monkeypatch):
    def absent(url, *, token=None):
        raise HTTPError(url, 404, "not found", {}, None)

    monkeypatch.setattr(route, "_read_json", absent)
    assert route.assert_version_unoccupied("0.17.0")["state"] == "absent"


@pytest.mark.parametrize("distributions", [[{"basename": "noarch/smonitor-py_0"}], []])
def test_direct_preflight_rejects_any_existing_version(monkeypatch, distributions):
    monkeypatch.setattr(
        route, "_read_json", lambda *args, **kwargs: {"distributions": distributions}
    )
    with pytest.raises(route.ReleaseRouteError, match="direct upload is forbidden"):
        route.assert_version_unoccupied("0.17.0")


def test_direct_preflight_rejects_registry_error(monkeypatch):
    def unavailable(url, *, token=None):
        raise HTTPError(url, 503, "unavailable", {}, None)

    monkeypatch.setattr(route, "_read_json", unavailable)
    with pytest.raises(route.ReleaseRouteError, match="HTTP 503"):
        route.assert_version_unoccupied("0.17.0")


def test_staged_plan_cannot_enter_the_direct_release_route(monkeypatch, tmp_path):
    monkeypatch.setattr(route, "read_plan", lambda: _plan(chosen_route="staged"))

    def should_not_run(*args, **kwargs):
        raise AssertionError("no gate or registry request is allowed after a route mismatch")

    monkeypatch.setattr(route, "verified_workflow_runs", should_not_run)
    monkeypatch.setattr(route, "assert_version_unoccupied", should_not_run)
    with pytest.raises(route.ReleaseRouteError, match="does not match"):
        route.check_route(
            version="0.17.0",
            route="direct",
            sha=SHA,
            repository="uibcdf/smonitor",
            receipt=tmp_path / "receipt.json",
        )


def test_direct_route_retains_decision_gate_and_preflight(monkeypatch, tmp_path):
    monkeypatch.setattr(route, "read_plan", _plan)
    monkeypatch.setattr(
        route,
        "verified_workflow_runs",
        lambda *args: [{"workflow": route.FULL_MATRIX, "run_id": 123}],
    )
    monkeypatch.setattr(route, "assert_version_unoccupied", lambda version: {"state": "absent"})
    monkeypatch.setenv("GH_TOKEN", "token")
    receipt = tmp_path / "receipt.json"
    evidence = route.check_route(
        version="0.17.0",
        route="direct",
        sha=SHA,
        repository="uibcdf/smonitor",
        receipt=receipt,
    )
    assert evidence["candidate_sha"] == SHA
    assert evidence["gates"][0]["run_id"] == 123
    assert evidence["preflight"]["state"] == "absent"
    assert json.loads(receipt.read_text()) == evidence


def test_public_poststate_matches_the_exact_built_file(monkeypatch, tmp_path):
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps({"version": "0.17.0", "route": "direct"}), encoding="utf-8")
    package = tmp_path / "smonitor-0.17.0-py_0.tar.bz2"
    package.write_bytes(b"noarch candidate")
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    record = {
        "sha256": digest,
        "channel": route.PUBLIC_CHANNEL,
        "fn": package.name,
        "noarch": "python",
        "url": route.PUBLIC_CHANNEL + "/" + package.name,
    }
    monkeypatch.setattr(
        route.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps({"smonitor": [record]}), stderr=""
        ),
    )
    evidence = route.verify_public(
        version="0.17.0", built_paths=str(package), receipt=receipt, attempts=1
    )
    assert evidence["public"]["sha256"] == digest
    assert json.loads(receipt.read_text())["public"]["channel"] == route.PUBLIC_CHANNEL


def test_windows_built_paths_preserve_backslashes_and_quoted_spaces():
    package = r"C:\Users\runneradmin\work\smonitor-0.17.0-py_0.tar.bz2"
    spaced = r"C:\Users\runneradmin\build output\smonitor-0.17.0-py_0.tar.bz2"

    assert route._split_built_paths(package, windows=True) == [package]
    assert route._split_built_paths(f'"{spaced}"', windows=True) == [spaced]


def test_public_poststate_rejects_checksum_mismatch(monkeypatch, tmp_path):
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps({"version": "0.17.0", "route": "direct"}), encoding="utf-8")
    package = tmp_path / "smonitor-0.17.0-py_0.tar.bz2"
    package.write_bytes(b"local candidate")
    record = {
        "sha256": "0" * 64,
        "channel": route.PUBLIC_CHANNEL,
        "fn": package.name,
        "noarch": "python",
    }
    monkeypatch.setattr(
        route.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps({"smonitor": [record]}), stderr=""
        ),
    )
    with pytest.raises(route.ReleaseRouteError, match="does not match"):
        route.verify_public(version="0.17.0", built_paths=str(package), receipt=receipt, attempts=1)
