#!/usr/bin/env python
"""Sync the canonical SMONITOR_GUIDE.md to sibling repos.

Usage:
  python devtools/sync_smonitor_guide.py
  python devtools/sync_smonitor_guide.py --root /home/diego/repos@uibcdf

Authoring note for the guide itself: Ruff formats fenced Python blocks inside
Markdown, and a vendored copy is checked against the *host* repository's Ruff
configuration, not this one. Keep every snippet line short enough that no width
wraps it -- under 88 columns -- and the file then formats identically at 88, 100
and 120, which is every line-length in use across the suite. That is a
mitigation, not a fix: `topomt` sets `quote-style = "single"`, which no way of
writing the document can satisfy alongside the other nine. Tracked in
uibcdf/molsyssuite#12.
"""

from __future__ import annotations

import argparse
from pathlib import Path

#: Repositories seeded explicitly. A new adopter is listed here to receive its
#: first copy; after that it is found on disk and stays in sync whether or not
#: this list remembers it.
REPO_NAMES = [
    "molsysmt",
    "molsysviewer",
    "pyunitwizard",
    "argdigest",
    "depdigest",
    "topomt",
    "pharmacophoremt",
    "elastnetmt",
    "lindelint",
]


def discover_targets(root: Path) -> list[Path]:
    """Every sibling that should receive the guide, listed or not.

    A hand-maintained list is a second place the truth lives, and it drifts. On
    2026-09-06 this one named five repositories while nine carried the guide;
    the four it had forgotten were six months stale, still following the
    pre-`0.13.0` text, and one of them had written a catalog class in the shape
    section 3.3.1 exists to forbid.

    So the list seeds, and the filesystem decides: a repository already carrying
    `SMONITOR_GUIDE.md` is a consumer by demonstration, and receives updates
    even if nobody remembered to add it here.
    """

    targets = {
        path.parent
        for path in sorted(root.glob("*/SMONITOR_GUIDE.md"))
        if path.parent.name != "smonitor"
    }
    for name in REPO_NAMES:
        candidate = root / name
        if candidate.is_dir():
            targets.add(candidate)
        else:
            print(f"[skip] not checked out: {candidate}")
    return sorted(targets)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync SMONITOR_GUIDE.md to sibling repos")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Root directory that contains smonitor and sibling repos",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without writing files",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    source = root / "smonitor" / "standards" / "SMONITOR_GUIDE.md"
    if not source.exists():
        raise SystemExit(f"Source guide not found: {source}")

    payload = source.read_text(encoding="utf-8")
    listed = set(REPO_NAMES)

    for repo in discover_targets(root):
        target = repo / "SMONITOR_GUIDE.md"
        note = "" if repo.name in listed else "  (found on disk, not in REPO_NAMES)"
        if args.dry_run:
            print(f"[dry-run] {source} -> {target}{note}")
            continue
        target.write_text(payload, encoding="utf-8")
        print(f"Synced {target}{note}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
