from __future__ import annotations

import re
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CITATION = ROOT / "CITATION.cff"
RELEASE_PLAN = ROOT / "devtools" / "conda-build" / "release_plan.toml"


def _scalar(text: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*[\"']?([^\n\"']+)[\"']?\s*$", text, re.MULTILINE)
    assert match is not None, f"CITATION.cff has no top-level {key!r} field"
    return match.group(1).strip()


def test_citation_metadata_identifies_smonitor() -> None:
    text = CITATION.read_text(encoding="utf-8")

    assert _scalar(text, "cff-version") == "1.2.0"
    assert _scalar(text, "title") == "SMonitor"
    assert _scalar(text, "type") == "software"
    assert _scalar(text, "url") == "https://github.com/uibcdf/smonitor"
    assert _scalar(text, "repository-code") == "https://github.com/uibcdf/smonitor"
    assert _scalar(text, "license") == "MIT"
    assert not re.search(r"^doi:", text, re.MULTILINE)

    assert "https://orcid.org/0000-0003-3375-870X" in text
    assert "https://orcid.org/0000-0003-2812-1499" in text


def test_citation_version_matches_the_release_tag_or_next_candidate() -> None:
    text = CITATION.read_text(encoding="utf-8")
    version = _scalar(text, "version")
    assert re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", version)

    exact = subprocess.run(
        ["git", "describe", "--tags", "--exact-match", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    if exact.returncode == 0:
        assert version == exact.stdout.strip()
        return

    latest = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    if latest.returncode != 0:
        return  # Source archives and shallow CI checkouts may not contain Git tags.

    assert tuple(map(int, version.split("."))) >= tuple(map(int, latest.stdout.strip().split(".")))


def test_citation_version_matches_committed_release_plan() -> None:
    citation_version = _scalar(CITATION.read_text(encoding="utf-8"), "version")
    plan = tomllib.loads(RELEASE_PLAN.read_text(encoding="utf-8"))
    assert citation_version == plan["version"]
