"""No module under `integrations/` may reach through the package for a late-defined name.

uibcdf/smonitor#3. `smonitor/__init__.py` imports `integrations` before it defines
`configure`, `emit` and `resolve`. A module that binds the package with `import smonitor`
and later evaluates `smonitor.configure(...)` therefore depends on the package body having
progressed past that definition -- which is true single-threaded, and false as soon as a
second thread enters through a different top-level package with its own import lock. The
observed failure was `AttributeError: partially initialized module 'smonitor' has no
attribute 'configure'`.

The fix is to import the name inside the function: that goes through the import machinery,
which waits on a module still initializing elsewhere, where an attribute read does not.
Measured on the cross-package reproduction: attribute access 14/15 failures, deferred
import 0/15.

This checks the invariant rather than the race. A race test for this window could not be
made to reproduce standalone -- the reproduction needs two real downstream packages, which
this repository cannot depend on -- and a green test that never opens the window would
certify the defect instead of catching it.
"""

from __future__ import annotations

import ast
import pathlib

import pytest


ROOT = pathlib.Path(__file__).resolve().parents[1] / "smonitor"
INIT = ROOT / "__init__.py"
INTEGRATIONS = ROOT / "integrations"


def _names_defined_after_integrations_import() -> set[str]:
    """Top-level names bound *after* `from . import integrations` runs."""
    tree = ast.parse(INIT.read_text(encoding="utf-8"))

    import_line = None
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.level == 1:
            if any(alias.name == "integrations" for alias in node.names):
                import_line = node.lineno
                break
    assert import_line is not None, "smonitor/__init__.py no longer imports integrations"

    late: set[str] = set()
    for node in tree.body:
        if node.lineno <= import_line:
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            late.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    late.add(target.id)
    return late


def _reachthroughs(path: pathlib.Path, late: set[str]) -> list[tuple[int, str]]:
    """`smonitor.<name>` attribute reads, for names the package defines late."""
    found = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "smonitor"
            and node.attr in late
        ):
            found.append((node.lineno, node.attr))
    return found


def test_the_late_definitions_are_still_late():
    """Guards the guard: if nothing is defined late, every case below is vacuous."""
    late = _names_defined_after_integrations_import()
    assert "configure" in late, (
        "`configure` is no longer defined after the integrations import. If it moved to a "
        "leaf module the hazard is gone and this file can go; if it merely moved earlier, "
        "the hazard remains for whatever is still below that line."
    )


@pytest.mark.parametrize(
    "path",
    sorted(INTEGRATIONS.glob("*.py")),
    ids=lambda p: p.name,
)
def test_no_module_reaches_through_the_package(path):
    late = _names_defined_after_integrations_import()
    offenders = _reachthroughs(path, late)
    assert not offenders, "\n".join(
        f"{path.name}:{line} reads `smonitor.{attr}` off the package object. "
        f"`{attr}` is defined after `from . import integrations`, so a thread that arrives "
        f"while the package body is still running sees it missing. "
        f"Use `from smonitor import {attr}` inside the function instead."
        for line, attr in offenders
    )
