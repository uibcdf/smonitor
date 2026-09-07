#!/usr/bin/env python
"""Run the canonical guide's section 7 checks against one or more integrations.

Section 7 gives each library a test file to copy. This runs the same checks from
outside, over any number of packages at once, which is what a suite-wide sweep
needs: the copied test tells one library whether it is correct, this tells you
where every library stands.

Checks 1, 2, 3 and 5 are covered. Check 4 -- that catalog classes survive a
rebuild -- is not, because it needs one builder per class in the shape a call
site uses, which only the library can supply. Keep that one in the copied test.

Usage:
  python devtools/verify_integration.py ../molsysmt ../argdigest
  python devtools/verify_integration.py --root .. --all
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import smonitor  # noqa: E402
from smonitor.config import validate_project_config  # noqa: E402
from smonitor.config.discovery import load_config_from_path  # noqa: E402

PROFILES = ("user", "dev", "qa", "agent", "debug")

#: Names `CatalogException` and `CatalogWarning` assign last, from what they were
#: given. A subclass setting one before `super().__init__()` writes into a
#: variable about to be overwritten.
RESERVED = {"code", "message", "raw_message", "extra", "hint"}

#: Groups a catalog may key its entries under. `signals` is deliberately absent:
#: those are contracts, not coded diagnostics.
CATALOG_GROUPS = ("exceptions", "warnings", "info", "errors")


class Result:
    def __init__(self, name: str) -> None:
        self.name = name
        self.rows: list[tuple[str, bool | None, str]] = []

    def add(self, check: str, ok: bool | None, detail: str = "") -> None:
        self.rows.append((check, ok, detail))

    @property
    def failed(self) -> bool:
        return any(ok is False for _, ok, _ in self.rows)


PROBE = "_smonitor_verify_probe"


def load_catalog(package: Path, path: Path) -> tuple[types.ModuleType | None, str]:
    """Import a `_private/smonitor/catalog.py` without importing its library.

    Reading the file with `ast.literal_eval` would work for a catalog written as
    a literal and fail for one that derives `CODES` -- MolSysViewer builds its
    entries from a `MESSAGES` table, and it is a member of the suite. So the file
    is executed, but under a synthetic package chain mirroring its real one:
    `_private` and `smonitor` are registered as modules carrying only a
    `__path__`, their own `__init__.py` never runs, and the library's top-level
    `__init__.py` -- the expensive one, the one that pulls the scientific stack --
    is never reached.

    The chain has to span from the package root, not just the catalog's own
    directory: MolSysViewer's `meta.py` does `from ..webs import ...`, which a
    one-level probe cannot resolve.
    """
    parts = path.parent.relative_to(package).parts
    created = [PROBE]
    root = types.ModuleType(PROBE)
    root.__path__ = [str(package)]  # type: ignore[attr-defined]
    sys.modules[PROBE] = root
    for depth, part in enumerate(parts, start=1):
        name = f"{PROBE}." + ".".join(parts[:depth])
        module = types.ModuleType(name)
        module.__path__ = [str(package.joinpath(*parts[:depth]))]  # type: ignore[attr-defined]
        sys.modules[name] = module
        setattr(sys.modules[name.rsplit(".", 1)[0]], part, module)
        created.append(name)
    try:
        full = f"{PROBE}." + ".".join((*parts, path.stem))
        spec = importlib.util.spec_from_file_location(full, path)
        if spec is None or spec.loader is None:
            return None, "catalog.py could not be loaded"
        module = importlib.util.module_from_spec(spec)
        sys.modules[full] = module
        spec.loader.exec_module(module)
        return module, ""
    except Exception as error:
        return None, f"{type(error).__name__}: {error}"
    finally:
        for key in [k for k in sys.modules if k == PROBE or k.startswith(PROBE + ".")]:
            sys.modules.pop(key, None)


def catalog_codes(catalog: object) -> set[str]:
    found: set[str] = set()
    if not isinstance(catalog, dict):
        return found
    for group in CATALOG_GROUPS:
        entries = catalog.get(group)
        if isinstance(entries, dict):
            for entry in entries.values():
                if isinstance(entry, dict) and isinstance(entry.get("code"), str):
                    found.add(entry["code"])
    return found


def reserved_name_assignments(package: Path, bases: set[str]) -> list[str]:
    trees: dict[Path, ast.Module] = {}
    for path in sorted(package.rglob("*.py")):
        if any(part in {"build", "dist", ".git"} for part in path.parts):
            continue
        try:
            trees[path] = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
    # A subclass may sit several files away from the base it derives from, so the
    # set of catalog classes grows until it stops growing.
    known, catalog_classes, changed = set(bases), set(), True
    while changed:
        changed = False
        for tree in trees.values():
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name not in catalog_classes:
                    names = {getattr(b, "id", getattr(b, "attr", "")) for b in node.bases}
                    if names & known:
                        catalog_classes.add(node.name)
                        known.add(node.name)
                        changed = True
    hits: list[str] = []
    for path, tree in trees.items():
        for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
            if cls.name not in catalog_classes:
                continue
            for node in ast.walk(cls):
                if not isinstance(node, ast.Assign):
                    continue
                for target in node.targets:
                    if (
                        isinstance(target, ast.Attribute)
                        and target.attr in RESERVED
                        and getattr(target.value, "id", "") == "self"
                    ):
                        rel = path.relative_to(package)
                        hits.append(f"{rel}:{node.lineno} {cls.name}.self.{target.attr}")
    return hits


def verify(repo: Path) -> Result:
    package = repo / repo.name
    result = Result(repo.name)
    if not package.is_dir():
        result.add("layout", False, f"no package directory at {package}")
        return result

    # Check 1 -- the configuration is found and understood.
    config = package / "_smonitor.py"
    if not config.is_file():
        result.add("1 config", None, "no _smonitor.py in the package")
    else:
        errors = validate_project_config(load_config_from_path(config))
        result.add("1 config", not errors, "; ".join(errors))

    catalog_path = package / "_private" / "smonitor" / "catalog.py"
    if catalog_path.is_file():
        module, why = load_catalog(package, catalog_path)
    else:
        module, why = None, "no _private/smonitor/catalog.py"
    codes = getattr(module, "CODES", None) if module else None
    catalog = getattr(module, "CATALOG", None) if module else None

    if not isinstance(codes, dict):
        detail = why or "CODES is not a dict"
        result.add("2 templates", None, detail)
        result.add("3 renders", None, detail)
    else:
        # Check 2 -- every code the catalog emits has a template.
        orphans = sorted(catalog_codes(catalog) - set(codes))
        result.add("2 templates", not orphans, ", ".join(orphans))

        # Check 3 -- every code renders in every profile.
        empty: list[str] = []
        for profile in PROFILES:
            smonitor.configure(profile=profile, handlers=[], codes=codes)
            blank = [c for c in codes if not smonitor.resolve(code=c, extra={})[0]]
            if blank:
                empty.append(f"{profile}:{len(blank)}/{len(codes)}")
        result.add("3 renders", not empty, ", ".join(empty))

    # Check 5 -- no class assigns a name the base classes own. Base classes are
    # discovered rather than configured: a library names its own, and they are
    # reached from SMonitor's two through the subclass chain.
    hits = reserved_name_assignments(package, {"CatalogException", "CatalogWarning"})
    result.add("5 reserved", not hits, "; ".join(hits))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repos", nargs="*", type=Path)
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--all", action="store_true", help="every sibling carrying the guide")
    args = parser.parse_args()

    repos = [p.resolve() for p in args.repos]
    if args.all:
        root = (args.root or Path(__file__).resolve().parents[2]).resolve()
        repos += sorted(p.parent for p in root.glob("*/SMONITOR_GUIDE.md"))
    if not repos:
        parser.error("name at least one repository, or pass --all")

    results = [verify(repo) for repo in dict.fromkeys(repos)]
    width = max(len(r.name) for r in results)
    failures = 0
    for result in results:
        for check, ok, detail in result.rows:
            mark = {True: "ok", False: "FAIL", None: "n/a"}[ok]
            line = f"  {result.name:<{width}}  {check:<12} {mark}"
            print(f"{line}  {detail}" if detail else line)
        failures += result.failed
    print(f"\n{len(results)} checked, {failures} with at least one failure")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
