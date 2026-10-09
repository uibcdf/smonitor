"""The owner invokes shared contracts without weakening its publication gates."""

from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "smonitor_dependency_preflight", ROOT / "devtools/check_distribution_inputs.py"
)
preflight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preflight)


def test_inventory_classifies_required_and_optional_scope():
    data = tomllib.loads((ROOT / "devtools/dependency_routes.toml").read_text())
    assert data["schema"] == "molsyssuite.dependency-routes@2"
    assert data["shared_tool"]["commit"] == "6d6172d6cd00c5ac2d4ebadb71df554ec5b7fa26"
    assert len(data["recipes"]) == 1
    assert len(data["environments"]) == 5
    assert len(data["workflows"]) == 9
    assert data["source_routes"] == []
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    assert project["dependencies"] == []
    assert "pytest-receptor>=1.2,<2" in project["optional-dependencies"]["pytest"]
    assert data["recipes"][0]["resource_inventory"] == "devtools/conda-build/resources.toml"


def test_provider_identity_and_modified_tools_are_refused(tmp_path):
    tool = tmp_path / "devtools/scripts/dependency_routes.py"
    tool.parent.mkdir(parents=True)
    tool.write_text("# tool fixture\n")
    for arguments in (
        ["init", "-q"],
        ["add", "devtools"],
        [
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
    ):
        subprocess.run(["git", *arguments], cwd=tmp_path, check=True, capture_output=True)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tmp_path, text=True).strip()
    assert preflight.checked_tool(tmp_path, commit) == tool
    with pytest.raises(ValueError, match="expected"):
        preflight.checked_tool(tmp_path, "0" * 40)
    tool.write_text("# changed provider\n")
    with pytest.raises(ValueError, match="modified"):
        preflight.checked_tool(tmp_path, commit)


def test_native_candidate_profile_requires_all_workflows_and_jobs():
    plan = tomllib.loads((ROOT / "devtools/conda-build/release_plan.toml").read_text())
    preflight.required_jobs(plan)
    assert sum(len(jobs) for jobs in plan["gate_jobs"].values()) == 13
    for change in ("missing", "empty"):
        bad = dict(plan)
        bad["gate_jobs"] = dict(plan["gate_jobs"])
        workflow = plan["required_workflows"][0]
        if change == "missing":
            del bad["gate_jobs"][workflow]
        else:
            bad["gate_jobs"][workflow] = {}
        with pytest.raises(ValueError, match="executed"):
            preflight.required_jobs(bad)


def test_source_workflows_execute_default_qualification_before_tests_or_builds():
    before = {
        "CI.yaml": "- name: Run tests",
        "CI_full_matrix.yaml": "- name: Run tests",
        "qa_ci.yaml": "- name: Run tests (default profile)",
        "docs_ci.yaml": "- name: Build docs",
        "sphinx_docs_to_gh_pages.yaml": "- name: Build docs",
    }
    for filename, marker in before.items():
        text = (ROOT / ".github/workflows" / filename).read_text()
        assert text.index("- name: Check distribution inputs") < text.index(marker)
        assert "--declared-only" not in text
        assert "6d6172d6cd00c5ac2d4ebadb71df554ec5b7fa26" in text
    for filename in ("docs_ci.yaml", "sphinx_docs_to_gh_pages.yaml"):
        text = (ROOT / ".github/workflows" / filename).read_text()
        assert "channel_priority: strict" in text
        assert "- defaults" not in text


def test_candidate_qualification_precedes_all_publication_actions():
    text = (ROOT / ".github/workflows/build_and_upload_conda_packages.yaml").read_text()
    check = text.index("- name: Check candidate distribution inputs and executed source gates")
    assert check < text.index("- name: Build, test, and upload the staging candidate")
    assert check < text.index("- name: Build, test, and upload the unstaged release")
    assert "--candidate-sha" in text
    assert "distribution-candidate-" in text


def test_helper_cannot_report_an_offline_review_as_installed_qualification():
    with pytest.raises(ValueError, match="qualification"):
        preflight.require_qualification({"qualification": "declared-only"}, candidate=False)
    preflight.require_qualification({"qualification": "declared-only"}, candidate=True)


def test_native_candidate_source_is_bound_before_any_gate_query(monkeypatch):
    monkeypatch.setattr(preflight, "source_head", lambda root: "1" * 40)
    with pytest.raises(ValueError, match="candidate"):
        preflight.verify_candidate(ROOT, ROOT, "0" * 40, {})


def test_default_invocation_preserves_provider_failure_exit(monkeypatch, capsys):
    monkeypatch.setattr(preflight, "checked_tool", lambda root, commit: Path("tool.py"))
    monkeypatch.setattr(
        preflight.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 7, "bad runtime floor", ""),
    )
    monkeypatch.setattr(preflight.sys, "argv", ["preflight", "--suite-root", "."])
    assert preflight.main() == 7
    assert "bad runtime floor" in capsys.readouterr().err


def test_native_failure_cannot_qualify_a_candidate(monkeypatch):
    monkeypatch.setattr(preflight, "source_head", lambda root: "1" * 40)
    plan = tomllib.loads((ROOT / "devtools/conda-build/release_plan.toml").read_text())

    def run(command, **kwargs):
        if command[0] == "git":
            return subprocess.CompletedProcess(command, 0)
        assert "input" in kwargs
        return subprocess.CompletedProcess(command, 1, "", "no successful executed native jobs")

    monkeypatch.setattr(preflight.subprocess, "run", run)
    with pytest.raises(ValueError, match="executed native jobs"):
        preflight.verify_candidate(ROOT, ROOT, "1" * 40, plan)


def test_recipe_tests_installed_templates_before_upload():
    recipe = (ROOT / "devtools/conda-build/meta.yaml").read_text()
    assert "importlib.resources" in recipe
    assert "_smonitor.py" in recipe
    assert "README.md" in recipe
    assert "md.version('smonitor') == expected" in recipe


def test_recipe_host_respects_the_declared_build_backend_requirements():
    import yaml
    from packaging.requirements import Requirement

    declared = tomllib.loads((ROOT / "pyproject.toml").read_text())["build-system"]["requires"]
    expected = {Requirement(item).name: Requirement(item) for item in declared}
    from jinja2 import Environment

    plan = tomllib.loads((ROOT / "devtools/conda-build/release_plan.toml").read_text())
    rendered = (
        Environment()
        .from_string((ROOT / "devtools/conda-build/meta.yaml").read_text())
        .render(
            environ={
                "GIT_DESCRIBE_TAG": plan["version"],
                "MOLSYSSUITE_CONDA_BUILD_NUMBER": str(plan["build_number"]),
            }
        )
    )
    recipe = yaml.safe_load(rendered)
    actual = {Requirement(item).name: Requirement(item) for item in recipe["requirements"]["host"]}
    assert set(expected) <= set(actual)
    assert actual["setuptools"].specifier == expected["setuptools"].specifier
    assert expected["versioningit"].specifier.contains("3.0")
    assert actual["versioningit"].specifier.contains("3.0")
    assert not actual["versioningit"].specifier.contains("4.0")


def test_reviewed_provider_checkouts_and_workflow_bytes_match_inventory():
    import yaml

    data = tomllib.loads((ROOT / "devtools/dependency_routes.toml").read_text())
    expected = data["shared_tool"]["commit"]
    paired_checkouts = 0
    for record in data["workflows"]:
        path = ROOT / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
        workflow = yaml.safe_load(path.read_text())
        for job in workflow["jobs"].values():
            for step in job.get("steps", []):
                if step.get("name") == "Check out reviewed distribution tools":
                    assert step["with"]["repository"] == "uibcdf/molsyssuite"
                    assert step["with"]["ref"] == expected
                    assert step["with"]["path"] == ".governance-tools"
                    paired_checkouts += 1
    # Source CI/docs, both QA jobs and candidate/promotion preflight must agree.
    assert paired_checkouts == 8
