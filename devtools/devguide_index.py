#!/usr/bin/env python
"""Render the generated block in each devguide queue's README.

The head of a queue's README is judgement and is written by hand. The block
below it is data, rendered from the front matter of the documents in the
directory: maintaining a second, hand-written list of documents that already
describe themselves is two authoritative lists, and this repository has spent
enough time removing those.

Usage:
  python devtools/devguide_index.py            # write
  python devtools/devguide_index.py --check    # exit 1 if any block is stale
"""

from __future__ import annotations

import argparse
from pathlib import Path

DEVGUIDE = Path(__file__).resolve().parents[1] / "devguide"
QUEUES = ("pending_bugs", "pending_proposals", "archive")
BEGIN = "<!-- generated: devguide_index -->"
END = "<!-- /generated -->"

#: Ordered so the reader meets what is being worked on before what is waiting.
STATUS_ORDER = ["active", "partial", "blocked", "open", "resolved", "withdrawn", "superseded"]


def read_front_matter(path: Path) -> dict[str, str] | None:
    """Parse the leading YAML block, without a YAML dependency.

    The fields are flat scalars and flat lists by construction -- the protocol
    defines them that way -- so a real parser would buy nothing and would put a
    dependency in front of a documentation check.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    _, _, rest = text.partition("---\n")
    block, sep, _ = rest.partition("\n---\n")
    if not sep:
        return None
    fields: dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def documents(queue: Path) -> list[tuple[Path, dict[str, str]]]:
    found = []
    for path in sorted(queue.glob("*.md")):
        if path.name == "README.md":
            continue
        fields = read_front_matter(path)
        if fields:
            found.append((path, fields))
    return found


def render(queue: Path) -> str:
    entries = documents(queue)
    if not entries:
        return f"{BEGIN}\n\n_No entries._\n\n{END}"
    rows = ["| entry | status | issue | summary |", "| --- | --- | --- | --- |"]

    def sort_key(item: tuple[Path, dict[str, str]]) -> tuple[int, str]:
        status = item[1].get("status", "")
        rank = STATUS_ORDER.index(status) if status in STATUS_ORDER else len(STATUS_ORDER)
        return rank, item[0].name

    for path, fields in sorted(entries, key=sort_key):
        issue = fields.get("issue", "")
        number = issue.rpartition("#")[2]
        link = f"[{issue}](https://github.com/{issue.replace('#', '/issues/')})" if number else ""
        rows.append(
            f"| [`{path.name}`]({path.name}) | `{fields.get('status', '')}` | {link} "
            f"| {fields.get('summary', '')} |"
        )
    return f"{BEGIN}\n\n" + "\n".join(rows) + f"\n\n{END}"


def apply(queue: Path, *, check: bool) -> bool:
    readme = queue / "README.md"
    if not readme.is_file():
        print(f"missing: {readme}")
        return False
    text = readme.read_text(encoding="utf-8")
    if BEGIN not in text or END not in text:
        print(f"no generated block in {readme}")
        return False
    head, _, rest = text.partition(BEGIN)
    _, _, tail = rest.partition(END)
    updated = head + render(queue) + tail
    if updated == text:
        return True
    if check:
        print(f"stale: {readme.relative_to(DEVGUIDE.parent)}")
        return False
    readme.write_text(updated, encoding="utf-8")
    print(f"wrote: {readme.relative_to(DEVGUIDE.parent)}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if any block is stale")
    args = parser.parse_args()
    ok = all(apply(DEVGUIDE / q, check=args.check) for q in QUEUES)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
