import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "devtools" / "conda-build" / "meta.yaml"
WORKFLOW = ROOT / ".github" / "workflows" / "build_and_upload_conda_packages.yaml"


def test_recipe_declares_one_supported_noarch_python_artifact():
    recipe = RECIPE.read_text(encoding="utf-8")

    assert "noarch: python" in recipe
    assert recipe.count("python >=3.11,<3.15") == 2
    assert "SMONITOR_CONDA_BUILD_NUMBER" in recipe


def test_python_3_14_candidate_metadata_and_hosted_matrix():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    matrix = (ROOT / ".github" / "workflows" / "CI_full_matrix.yaml").read_text(encoding="utf-8")

    assert 'requires-python = ">=3.11,<3.15"' in pyproject
    assert '"Programming Language :: Python :: 3.14"' in pyproject
    cells = set(
        re.findall(
            r'^\s*-\s*\{\s*os:\s*([\w-]+),\s*python-version:\s*"(\d+\.\d+)"\s*\}\s*$',
            matrix,
            flags=re.MULTILINE,
        )
    )
    assert cells == {
        (operating_system, python_version)
        for operating_system in ("ubuntu-latest", "macos-latest", "windows-latest")
        for python_version in ("3.11", "3.12", "3.13", "3.14")
    }
    assert "--receptor=llm" in matrix


def test_manual_candidates_are_exact_and_staging_only():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "types: ['released']" in workflow
    assert "prereleased" not in workflow
    assert "candidate_sha:" in workflow
    assert "ref: ${{ inputs.candidate_sha || github.event.release.tag_name }}" in workflow
    assert 'test "$(git rev-parse HEAD)" = "$CANDIDATE_SHA"' in workflow
    assert "Build, test, and upload the staging candidate" in workflow
    assert "label: staging" in workflow


def test_noarch_workflow_has_one_job_and_retains_producer_evidence():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "matrix:" not in workflow
    assert "@v2.1.0" in workflow
    assert "--python" not in workflow
    assert "platform_linux-64: false" in workflow
    assert "platform_win-64: false" in workflow
    assert "always() && steps.conda_staging.outputs.evidence_path != ''" in workflow
    assert "always() && steps.conda_release.outputs.evidence_path != ''" in workflow
