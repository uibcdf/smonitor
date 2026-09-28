---
summary: PR CI can be bypassed and skipped direct pushes are unchecked
issue: uibcdf/smonitor#33
status: partial
opened: 2026-09-28
closed:
severity: high
verification: inspected
area: [ci, governance]
guard: tests/test_ci_backlog.py
normative:
blocked_by: []
supersedes: []
---

# PR CI can be bypassed and skipped direct pushes are unchecked

**Reported:** 2026-09-28 during the phased MolSysSuite Python CI review.

## What

At `fc042c4`, the primary `CI.yaml` PR test ignored documentation paths and
allowed `[skip ci]` in PR titles or `skip-ci` in branch names to skip its test
job. The repository's `main` branch had neither classic protection nor
effective rules. Direct push skip markers had no daily full-suite recovery.
The [weekly twelve-cell matrix](https://github.com/uibcdf/smonitor/actions/runs/36457179148)
passed at that commit; this is a route and enforcement gap, not a failing test
suite. The [routine CI run](https://github.com/uibcdf/smonitor/actions/runs/36310563701)
and [QA run](https://github.com/uibcdf/smonitor/actions/runs/36310563693)
also passed at the same commit.

## How

Run the complete Linux 3.13 PR route without workflow path or title/branch
skip conditions. Require its stable test check along with the QA and collective
integration checks on PRs, while administrators retain direct pushes. Preserve
the existing weekly and manual full matrix. Add a conditional daily full matrix
in America/Mexico_City that detects skipped commits since the last executed,
green Linux matrix. If run history or API evidence is unavailable, run it.
The probe input checks the backlog without dispatching test jobs.

## Why

SMonitor is shared infrastructure. A green weekly matrix does not guard a PR
whose required tests never ran, and consecutive skipped pushes can leave a
regression untested. The conditional daily route protects integrity without
requiring a full matrix after each direct commit, per `uibcdf/molsyssuite#39`.

## What was refuted

Treating the configured weekly schedule as a substitute for branch protection
was rejected: it ran and passed, but it does not stop an untested PR. Requiring
the twelve-cell matrix for every direct push was rejected because the accepted
suite policy permits maintainers to iterate more quickly.

## Resolution

Commits `4b3f8c3` and `709ecfd` implement the workflow and detector. The first
hosted QA run failed during collection because the new test imported `devtools`
through a path unavailable to the `pytest` executable; `709ecfd` loads the
script by file path. At that exact commit, [CI](https://github.com/uibcdf/smonitor/actions/runs/36483279101),
[QA and collective E2E](https://github.com/uibcdf/smonitor/actions/runs/36483279046),
and [MolSysSuite policy](https://github.com/uibcdf/smonitor/actions/runs/36483280197)
passed. The [probe-only dispatch](https://github.com/uibcdf/smonitor/actions/runs/36483329864)
recognized executed weekly matrix `36457179148` at `fc042c4` as the watermark,
found zero later skipped commits, and omitted the full matrix.

The `main` branch now requires strict checks `Test on ubuntu-latest, Python
3.13`, `qa` and `collective-e2e`. Administrators are exempt from this PR gate;
the only current collaborators with push permission are `dprada` and `LMMV`,
both administrators. The direct push of `69bb1a3` with `[skip ci]` exercised
that bypass. A second [probe-only dispatch](https://github.com/uibcdf/smonitor/actions/runs/36484514827)
found exactly that skipped commit after the `fc042c4` full-matrix watermark
and reported that full recovery is due. The probe omitted all matrix jobs by
design. Hosted PR and first nightly execution have not yet been observed.
Keep the issue open until those outcomes and the platform-claim review are
recorded.
