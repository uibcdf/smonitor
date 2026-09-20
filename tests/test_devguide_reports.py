"""Every devguide report carries valid front matter, and the indexes are current.

`devguide/reporting_protocol.md` is normative and adopts the MolSysSuite
reporting vocabulary unchanged, which is what makes `uibcdf/<repo>#<number>` a
reliable reference in every direction. A vocabulary only means the same thing
everywhere if something checks it, and prose does not.

MolSysMT runs these checks from a script in its release gate. Our gate is
`pytest`, so they live here and run on every pull request with no extra wiring.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path, PurePosixPath

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
PYTHON_IDENTIFIER = re.compile(r"^[A-Za-z_]\w*$")
GUARD_POLICY_EFFECTIVE_DATE = "2026-09-20"
PYTEST_ROOTS = (PurePosixPath("tests"), PurePosixPath("devtools/tests"))


def _is_test_class(node: ast.ClassDef) -> bool:
    if node.name.startswith("Test"):
        return True
    return any(
        (isinstance(base, ast.Name) and base.id.endswith("TestCase"))
        or (isinstance(base, ast.Attribute) and base.attr.endswith("TestCase"))
        for base in node.bases
    )


def _test_functions(nodes: list[ast.stmt]) -> dict[str, ast.AST]:
    return {
        node.name: node
        for node in nodes
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    }


def validate_pytest_guard(root: Path, selector: str) -> list[str]:
    """Validate the safe static pytest selector subset used by MolSysSuite."""

    if any(character.isspace() for character in selector) or any(
        token in selector for token in (",", "(", ")", "*", "?")
    ):
        return [f"guard {selector!r} uses unsupported selector syntax"]
    parts = selector.split("::")
    if not 1 <= len(parts) <= 3 or any(not part for part in parts):
        return [f"guard {selector!r} uses unsupported selector syntax"]
    if any("[" in part or "]" in part for part in parts[1:]):
        return [
            (
                f"guard {selector!r}: parameterized selectors are not supported by "
                "the static Python profile; name the unparameterized test or the module"
            )
        ]

    relative = PurePosixPath(parts[0])
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or relative.suffix != ".py"
        or not any(relative.is_relative_to(base) for base in PYTEST_ROOTS)
    ):
        return [f"guard {selector!r} must name a safe Python file under tests/ or devtools/tests/"]
    target = root.joinpath(*relative.parts)
    if not target.is_file():
        return [f"guard {selector!r} names a file that does not exist"]
    try:
        tree = ast.parse(target.read_text(encoding="utf-8"), filename=str(target))
    except (OSError, SyntaxError) as error:
        return [f"guard {selector!r} cannot be statically indexed: {error}"]

    functions = _test_functions(tree.body)
    classes = {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and _is_test_class(node)
    }
    if len(parts) == 1:
        if functions or any(_test_functions(node.body) for node in classes.values()):
            return []
        return [f"guard {selector!r} does not resolve to a collected test"]
    if not all(PYTHON_IDENTIFIER.fullmatch(part) for part in parts[1:]):
        return [f"guard {selector!r} uses unsupported selector syntax"]
    if len(parts) == 2 and parts[1] in functions:
        return []
    if len(parts) == 3:
        class_node = classes.get(parts[1])
        if class_node is not None and parts[2] in _test_functions(class_node.body):
            return []
    return [f"guard {selector!r} does not resolve to a collected test"]


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
    """New guards resolve as pytest selectors; older records keep path checks."""
    fields = read_front_matter(path) or {}
    normative = fields.get("normative", "")
    if normative:
        assert (ROOT / normative).exists(), (
            f"{rel(path)} names a missing normative document: {normative}"
        )

    guard = fields.get("guard", "")
    if not guard:
        return
    if (
        fields.get("status") == "resolved"
        and fields.get("closed", "") >= GUARD_POLICY_EFFECTIVE_DATE
    ):
        assert validate_pytest_guard(ROOT, guard) == []
    else:
        target = guard.split("::", maxsplit=1)[0]
        assert (ROOT / target).exists(), f"{rel(path)} names a missing guard: {guard}"


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
    assert not stale, "run `python devtools/devguide_index.py`: " + buffer.getvalue().strip()


def test_pytest_guard_rejects_a_missing_file(tmp_path: Path) -> None:
    errors = validate_pytest_guard(tmp_path, "tests/test_missing.py")

    assert any("file that does not exist" in error for error in errors)


def test_pytest_guard_rejects_a_missing_node_and_parameter_id(tmp_path: Path) -> None:
    test_file = tmp_path / "tests/test_example.py"
    test_file.parent.mkdir()
    test_file.write_text("def test_present():\n    pass\n", encoding="utf-8")

    missing = validate_pytest_guard(tmp_path, "tests/test_example.py::test_absent")
    parameterized = validate_pytest_guard(tmp_path, "tests/test_example.py::test_present[param]")

    assert any("does not resolve" in error for error in missing)
    assert any("parameterized selectors are not supported" in error for error in parameterized)


def test_pytest_guard_accepts_a_module_function_and_class_method(tmp_path: Path) -> None:
    test_file = tmp_path / "tests/test_example.py"
    test_file.parent.mkdir()
    test_file.write_text(
        "def test_function():\n"
        "    pass\n\n"
        "class TestGroup:\n"
        "    def test_method(self):\n"
        "        pass\n",
        encoding="utf-8",
    )

    for selector in (
        "tests/test_example.py",
        "tests/test_example.py::test_function",
        "tests/test_example.py::TestGroup::test_method",
    ):
        assert validate_pytest_guard(tmp_path, selector) == []
