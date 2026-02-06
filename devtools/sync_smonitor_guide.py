#!/usr/bin/env python
"""Sync the canonical SMONITOR_GUIDE.md to sibling repos.

Usage:
  python devtools/sync_smonitor_guide.py
  python devtools/sync_smonitor_guide.py --root /home/diego/repos@uibcdf
"""

from __future__ import annotations

import argparse
from pathlib import Path

REPO_NAMES = [
    "molsysmt",
    "molsysviewer",
    "pyunitwizard",
    "argdigest",
    "depdigest",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync SMONITOR_GUIDE.md to sibling repos")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Root directory that contains smonitor and sibling repos",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing files")
    args = parser.parse_args()

    root = args.root.resolve()
    source = root / "smonitor" / "standards" / "SMONITOR_GUIDE.md"
    if not source.exists():
        raise SystemExit(f"Source guide not found: {source}")

    payload = source.read_text(encoding="utf-8")

    for name in REPO_NAMES:
        target = root / name / "SMONITOR_GUIDE.md"
        if args.dry_run:
            print(f"[dry-run] {source} -> {target}")
            continue
        target.write_text(payload, encoding="utf-8")
        print(f"Synced {target}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
