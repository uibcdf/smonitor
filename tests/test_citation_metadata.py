from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CITATION = ROOT / "CITATION.cff"


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


def test_citation_version_matches_the_latest_repository_tag() -> None:
    completed = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    if completed.returncode != 0:
        return  # Source archives and shallow CI checkouts may not contain Git tags.

    text = CITATION.read_text(encoding="utf-8")
    assert _scalar(text, "version") == completed.stdout.strip()
