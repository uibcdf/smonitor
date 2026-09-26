import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "devtools" / "conda-build" / "meta.yaml"
WORKFLOW = ROOT / ".github" / "workflows" / "build_and_upload_conda_packages.yaml"
PROMOTION_WORKFLOW = ROOT / ".github" / "workflows" / "promote_conda_package.yaml"


def test_recipe_declares_one_supported_noarch_python_artifact():
    recipe = RECIPE.read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert "noarch: python" in recipe
    assert "entry_points:\n    - smonitor = smonitor.cli:main" in recipe
    assert 'smonitor = "smonitor.cli:main"' in pyproject
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
    assert "--receptor=ci" in matrix


def test_manual_candidates_are_exact_and_staging_only():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "candidate_sha:" in workflow
    assert "ref: ${{ inputs.candidate_sha || github.event.release.tag_name }}" in workflow
    assert 'test "$(git rev-parse HEAD)" = "$CANDIDATE_SHA"' in workflow
    assert "Build, test, and upload the staging candidate" in workflow
    assert "label: staging" in workflow
    assert "id: conda_staging\n        if: github.event_name == 'workflow_dispatch'" in workflow
    assert "--route staged" in workflow
    assert '[[ "$BUILD_NUMBER" =~ ^[0-9]+$ ]]' in workflow


def test_stable_releases_have_a_guarded_direct_route():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "types: ['released']" in workflow
    assert "prereleased" not in workflow
    assert "Build, test, and upload the unstaged release" in workflow
    assert "label: main" in workflow
    assert (
        "id: conda_release\n        if: github.event_name == 'release' "
        "&& steps.release_plan.outputs.route == 'direct'"
    ) in workflow
    assert "--route direct" in workflow
    assert workflow.index("--route direct") < workflow.index("label: main")
    assert "smonitor-conda-${{ inputs.version || github.event.release.tag_name }}" in workflow


def test_staged_release_is_validated_without_entering_the_direct_build():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "release_route: ${{ steps.release_plan.outputs.route }}" in workflow
    assert 'plan-route --version "$RELEASE_VERSION"' in workflow
    assert (
        "id: route_staged\n        if: github.event_name == 'workflow_dispatch' "
        "|| steps.release_plan.outputs.route == 'staged'"
    ) in workflow
    assert (
        "id: route_direct\n        if: github.event_name == 'release' "
        "&& steps.release_plan.outputs.route == 'direct'"
    ) in workflow
    assert (
        "if: github.event_name == 'workflow_dispatch' || "
        "needs.conda_deployment_with_new_tag.outputs.release_route == 'direct'"
    ) in workflow


def test_noarch_workflow_retains_producer_evidence():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "matrix:" not in workflow
    assert "@v2.1.0" in workflow
    assert "--python" not in workflow
    assert "platform_linux-64: false" in workflow
    assert "platform_win-64: false" in workflow
    assert "always() && steps.conda_staging.outputs.evidence_path != ''" in workflow
    assert "always() && steps.conda_release.outputs.evidence_path != ''" in workflow
    assert '--built-paths "$BUILT_PATHS"' in workflow
    assert "smonitor-conda-route-${{ github.run_id }}-${{ github.run_attempt }}" in workflow


def test_uploaded_package_command_is_checked_on_windows():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "windows_installed_package_smoke:" in workflow
    assert "needs: conda_deployment_with_new_tag" in workflow
    assert "runs-on: windows-latest" in workflow
    assert (
        "smonitor=${{ inputs.version || github.event.release.tag_name }}=py_${{ inputs.build_number || 0 }}"
        in workflow
    )
    assert "shutil.which('smonitor')" in workflow
    assert "smonitor --help" in workflow


def test_promotion_workflow_checks_exact_release_and_file_identity():
    workflow = PROMOTION_WORKFLOW.read_text(encoding="utf-8")

    assert 'test "$GITHUB_REF" = refs/heads/main' in workflow
    assert 'test "$(git rev-parse HEAD)" = "$CANDIDATE_SHA"' in workflow
    assert 'test "$(git rev-list -n 1 "$RELEASE_VERSION")" = "$CANDIDATE_SHA"' in workflow
    assert "releases/tags/$RELEASE_VERSION" in workflow
    assert (
        "uibcdf/smonitor/$RELEASE_VERSION/noarch/smonitor-$RELEASE_VERSION-py_$BUILD_NUMBER.tar.bz2"
        in workflow
    )
    assert "action-build-and-upload-conda-packages/promote@v2.2.2" in workflow
    assert "--route staged" in workflow
    assert "expected-sha256: ${{ inputs.sha256 }}" in workflow
    assert "from-label: staging" in workflow
    assert "to-label: main" in workflow
    assert 'record.get("sha256") == expected' in workflow
    assert 'record["channel"] != "https://conda.anaconda.org/uibcdf/noarch"' in workflow
    assert "ANACONDA_UIBCDF_TOKEN" in workflow
