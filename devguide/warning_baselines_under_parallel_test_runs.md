# Warning baselines under parallel test runs

A constraint on any QA policy built on warning counts, measured rather than
assumed. It applies to `Project A — Pytest/CI Diagnostic Integration` in
[implementation_plan.md](implementation_plan.md) and to the baseline sections of
[pending_proposals/pytest_diagnostics_bridge_and_molsyssuite_policy.md](pending_proposals/pytest_diagnostics_bridge_and_molsyssuite_policy.md),
both of which plan to compare warning sets between runs.

## The constraint

**Under pytest-xdist's default distribution, the number of warnings a suite
reports is not reproducible between runs of unchanged code.** Neither is the set
of tests reported as having emitted them.

Measured on MolSysMT, `tests/form/mdtraj_Topology/`, counting one third-party
warning per test through a `pytest_warning_recorded` hook, 2026-08-16:

| configuration | runs | occurrences | reproducible |
|---|---:|---|---|
| serial | 3 | 2, 2, 2 | yes |
| `-n 12 --dist loadfile` | 3 | 4, 4, 4 | yes |
| `-n 12` (default `--dist load`) | 4 | 30, 32, 34, 40 | **no** |
| `-n 12 -W always` | 3 | 32, 34, 40 | **no** |

Across MolSysMT's full suite the aggregate moved between 129 and 130 over six
runs, and the seven tests credited with the warning were not the same seven each
time — four repeated, three changed.

## Why, and why the obvious fix is not one

The warning comes from reading a file that the library caches per process. The
first test in a worker to need it pays the read and warns; every later test in
that worker hits the cache silently. So the count tracks *how many workers
touched the path*, and which tests pay depends on how `--dist load` hands work
out, which depends on timing.

`-W always` does not help, which is worth stating because it is the first thing
one reaches for. The deduplication is not in Python's `__warningregistry__` —
pytest already resets warning filters per test — it is in the library's cache.
Raising the filter changes nothing because nothing was being filtered.

`--dist loadfile` does help: every test in a file goes to the same worker, so the
caches warm identically every run. Its count differs from the serial count, and
does not need to match — a baseline has to be stable, not minimal.

## What this means for the pytest bridge

A gate phrased as *"no newly introduced warning fingerprint"* or *"warning count
must not increase"* is only meaningful under a deterministic distribution. Under
the default one it will fail intermittently on unchanged code, and — worse for
trust in the gate — it will sometimes pass a run that should have failed.

Three ways out, and the choice belongs to whoever designs the policy:

1. **Require a deterministic distribution for the gate.** `--dist loadfile`, or
   serial for the baseline job. Cheapest, and it keeps counts usable.
2. **Baseline on identity, not on counts.** A set of `(code, source,
   fingerprint)` is far more stable than a tally, because it does not depend on
   how many processes warmed a cache. This fits SMonitor's own model better:
   fingerprints already exist for exactly this kind of comparison.
3. **Compare only diagnostics SMonitor emitted**, ignoring third-party warnings
   entirely. The variance measured here comes from a third-party warning behind
   a library cache; a policy scoped to catalog-backed events would not see it.

Option 2 is the one that survives contact with other suites, since it does not
require every consumer to configure their runner a particular way. It is
recorded here as a finding, not as a decision.

## Reproducing

```bash
# in a repository with a per-process cache on a warned path
pytest -n 12 -q <subset>                    # varies
pytest -n 12 --dist loadfile -q <subset>    # stable
pytest -q <subset>                          # stable
```

Attribution needs a plugin exposing
`pytest_warning_recorded(warning_message, when, nodeid, location)` that appends
`nodeid` and the message. Under xdist the hook fires on the workers, so the file
must be opened per write with `O_APPEND`.

Recorded in MolSysMT as
[`devguide/parallel_test_warning_counts.md`](https://github.com/uibcdf/molsysmt/blob/main/devguide/parallel_test_warning_counts.md),
where the cache lives.
