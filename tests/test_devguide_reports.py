"""Every devguide report carries valid front matter, and the indexes are current.

`devguide/reporting_protocol.md` is normative and adopts the MolSysSuite
reporting vocabulary unchanged, which is what makes `uibcdf/<repo>#<number>` a
reliable reference in every direction. A vocabulary only means the same thing
everywhere if something checks it, and prose does not.

MolSysMT runs these checks from a script in its release gate. Our gate is
`pytest`, so they live here and run on every pull request with no extra wiring.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DEVGUIDE = ROOT / "devguide"
QUEUES = ("pending_bugs", "pending_proposals", "archive")

OPEN_SET = {"open", "active", "blocked", "partial"}
CLOSED_SET = {"resolved", "withdrawn", "superseded"}
STATUSES = OPEN_SET | CLOSED_SET
VERIFICATIONS = {"reproduced", "measured", "inspected", "upstream", "asserted"}
SEVERITIES = {"critical", "high", "medium", "low"}

REQUIRED = ("summary", "issue", "status", "opened", "verification", "area")
#: `uibcdf/<repo>#<n>`, and the upstream forms a blocker may legitimately take.
ISSUE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#\d+$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def read_front_matter(path: Path) -> dict[str, str] | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    _, _, rest = text.partition("---\n")
    block, sep, _ = rest.partition("\n---\n")
    if not sep:
        return None
    fields: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def reports() -> list[Path]:
    found: list[Path] = []
    for queue in QUEUES:
        directory = DEVGUIDE / queue
        if directory.is_dir():
            found += [p for p in sorted(directory.glob("*.md")) if p.name != "README.md"]
    return found


def as_list(value: str) -> list[str]:
    inner = value.strip().removeprefix("[").removesuffix("]").strip()
    return [item.strip() for item in inner.split(",") if item.strip()] if inner else []


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


@pytest.mark.parametrize("path", reports(), ids=rel)
def test_report_front_matter_is_valid(path: Path) -> None:
    fields = read_front_matter(path)
    assert fields is not None, f"{rel(path)} has no parseable front matter"

    missing = [key for key in REQUIRED if not fields.get(key)]
    assert not missing, f"{rel(path)} is missing: {', '.join(missing)}"

    assert ISSUE.match(fields["issue"]), f"{rel(path)} has a malformed issue: {fields['issue']!r}"
    assert fields["status"] in STATUSES, f"{rel(path)} has status {fields['status']!r}"
    assert fields["verification"] in VERIFICATIONS, f"{rel(path)} verification is unknown"
    assert DATE.match(fields["opened"]), f"{rel(path)} opened is not an ISO date"

    # `closed` is set exactly when the status has left the open set.
    closed, status = fields.get("closed", ""), fields["status"]
    if status in CLOSED_SET:
        assert DATE.match(closed), f"{rel(path)} is {status} and needs a `closed` date"
    else:
        assert not closed, f"{rel(path)} is {status} and must not carry `closed`"

    if path.parent.name == "pending_bugs" or (
        path.parent.name == "archive" and fields.get("severity")
    ):
        assert fields.get("severity") in SEVERITIES, f"{rel(path)} needs a valid severity"

    for key in ("blocked_by", "supersedes"):
        for reference in as_list(fields.get(key, "")):
            assert ISSUE.match(reference), f"{rel(path)} has a malformed {key}: {reference!r}"


@pytest.mark.parametrize("path", reports(), ids=rel)
def test_a_named_guard_or_normative_document_exists(path: Path) -> None:
    """A path that has gone stale is wrong in any status, not only in `resolved`.

    The protocol requires the check on resolved entries. Applying it to every
    entry that names one costs nothing and catches the case the narrower version
    missed: an open entry pointing at a guard that was renamed or removed.
    """
    fields = read_front_matter(path) or {}
    for key in ("guard", "normative"):
        target = fields.get(key, "")
        if target:
            assert (ROOT / target).exists(), f"{rel(path)} names a missing {key}: {target}"


@pytest.mark.parametrize("path", reports(), ids=rel)
def test_a_resolved_report_names_a_guard_or_a_normative_document(path: Path) -> None:
    """Resolved means something fails if it comes back, or a rule was written down."""
    fields = read_front_matter(path) or {}
    if fields.get("status") != "resolved":
        pytest.skip("not resolved")
    assert fields.get("guard") or fields.get("normative"), (
        f"{rel(path)} is resolved and names neither guard nor normative"
    )


@pytest.mark.parametrize("path", reports(), ids=rel)
def test_a_closed_report_lives_in_the_archive(path: Path) -> None:
    fields = read_front_matter(path) or {}
    status = fields.get("status", "")
    if status in CLOSED_SET:
        assert path.parent.name == "archive", f"{rel(path)} is {status} and belongs in archive/"
    else:
        assert path.parent.name != "archive", f"{rel(path)} is {status} and is not closed"


def test_the_generated_indexes_are_current() -> None:
    """`devtools/devguide_index.py --check` renders each queue and compares."""
    import importlib.util
    import io
    from contextlib import redirect_stdout

    spec = importlib.util.spec_from_file_location(
        "devguide_index", ROOT / "devtools" / "devguide_index.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        stale = [q for q in module.QUEUES if not module.apply(DEVGUIDE / q, check=True)]
    assert not stale, (
        "run `python devtools/devguide_index.py`: " + buffer.getvalue().strip()
    )
