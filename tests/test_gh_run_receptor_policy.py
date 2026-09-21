from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / ".github" / "gh-run-receptor.yaml"


def test_noarch_conda_publication_declares_its_package_kind():
    """Interpret one noarch build without inventing a native platform matrix."""
    config = CONFIG_PATH.read_text(encoding="utf-8")
    workflow = "path: .github/workflows/build_and_upload_conda_packages.yaml"
    rule = config.split(workflow, maxsplit=1)[1].split("  - match:", maxsplit=1)[0]

    assert "profile: conda" in rule
    assert "package_kind: noarch" in rule
    assert "expected_platforms" not in rule


def test_exact_file_promotion_does_not_claim_a_package_build():
    """Report the promotion run without inventing producer build evidence."""
    config = CONFIG_PATH.read_text(encoding="utf-8")
    workflow = "path: .github/workflows/promote_conda_package.yaml"
    rule = config.split(workflow, maxsplit=1)[1].split("  - match:", maxsplit=1)[0]

    assert "profile: generic" in rule
    assert "package_kind" not in rule
