#!/usr/bin/env python
"""Run a component's suite under SMonitor, export a bundle, and read its triage.

This is the workflow behind `devguide/operability_evidence_2026-09-08.md`, kept
runnable so the evidence for exit criterion 5 can be reproduced rather than
believed.

Nothing is added to the component. The event buffer and the level arrive through
the environment, which the component's own `ensure_configured()` reads on import
-- a support workflow rarely gets to edit the library it is diagnosing.

    python devtools/operability_evidence.py ../argdigest --out /tmp/run.json
    python devtools/operability_evidence.py ../argdigest --out /tmp/a.json \
        --compare-with /tmp/b.json
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: Run in a child process: the component configures SMonitor on import, and a
#: suite that has already imported it cannot be re-instrumented from here.
CHILD = '''
import json, os, sys
sys.path.insert(0, {smonitor!r})
sys.path.insert(0, {repo!r})
os.chdir({repo!r})
import smonitor, pytest
code = pytest.main(["-q", "--no-header", "-p", "no:cacheprovider", "tests"])
events = smonitor.get_manager().recent_events()
smonitor.export_bundle({out!r}, max_events=100000, force=True)
print(json.dumps({{"exit": int(code), "events": len(events)}}))
'''


def run(repo: Path, out: Path, smonitor_path: Path) -> dict:
    out.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.setdefault("SMONITOR_EVENT_BUFFER", "100000")
    env.setdefault("SMONITOR_LEVEL", "DEBUG")
    source = CHILD.format(smonitor=str(smonitor_path), repo=str(repo), out=str(out))
    result = subprocess.run(
        [sys.executable, "-c", source], env=env, capture_output=True, text=True
    )
    tail = [line for line in result.stdout.splitlines() if line.startswith("{")]
    if not tail:
        print(result.stdout[-2000:], file=sys.stderr)
        print(result.stderr[-2000:], file=sys.stderr)
        raise SystemExit(f"the suite in {repo} produced no summary")
    return json.loads(tail[-1])


def summarise(bundle_path: Path) -> None:
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    triage, events = bundle["triage"], bundle["events"]
    coded = [e for e in events if e.get("code")]
    print(f"\n  events {len(events)}   coded {len(coded)}   "
          f"fingerprints {len(triage['events_by_fingerprint'])}")
    print(f"  run_id {bundle['runtime']['run_id'][:8]}…  "
          f"session_id {bundle['runtime']['session_id'][:8]}…")
    for name in ("top_codes", "top_sources", "top_fingerprints"):
        rows = triage.get(name) or []
        if rows:
            joined = ", ".join(f"{r['key']}×{r['count']}" for r in rows[:4])
            print(f"  {name:<18} {joined}")

    # The check that produced finding A: a fingerprint groups by code, source and
    # exception type, so uncoded events from one source collapse regardless of
    # what they say. Reporting the spread makes that visible instead of implied.
    by_fp = collections.defaultdict(set)
    for event in events:
        by_fp[event.get("fingerprint")].add((event.get("message") or "")[:80])
    worst = max(by_fp.items(), key=lambda item: len(item[1]), default=(None, set()))
    if worst[0] and len(worst[1]) > 1:
        count = triage["events_by_fingerprint"].get(worst[0], 0)
        print(f"  widest fingerprint  {worst[0]}: {count} events, "
              f"{len(worst[1])} distinct messages")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repo", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--compare-with", type=Path, default=None)
    parser.add_argument("--smonitor", type=Path, default=ROOT)
    args = parser.parse_args()

    summary = run(args.repo.resolve(), args.out.resolve(), args.smonitor.resolve())
    print(f"  {args.repo}: pytest exit={summary['exit']}, {summary['events']} events buffered")
    summarise(args.out.resolve())

    if args.compare_with:
        print()
        subprocess.run(
            [sys.executable, "-m", "smonitor.cli", "compare",
             str(args.out.resolve()), str(args.compare_with.resolve()),
             "--format", "markdown"],
            cwd=ROOT, check=False,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
