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
design. A [manual full-matrix dispatch](https://github.com/uibcdf/smonitor/actions/runs/36485266297)
then passed all twelve jobs at `534367f`, including the four Linux test steps.
The [post-matrix probe](https://github.com/uibcdf/smonitor/actions/runs/36485441346)
recognized `534367f` as the new executed watermark and found zero pending
skipped commits; its matrix jobs were omitted. Hosted PR and first nightly
execution have not yet been observed.
Keep the issue open until those outcomes and the platform-claim review are
recorded.

**Correction on 2026-09-29:** GitHub's workflow-run API listing with
`branch=main` returned an old run (`31378148035`), omitting the more recent
green matrix `36485266297`; the unfiltered listing included the current runs
with `head_branch=main`. The detector now lists runs without the API branch
filter and checks `head_branch` itself. It still requires an ancestor commit
and four executed green Linux test jobs. The
[corrected probe](https://github.com/uibcdf/smonitor/actions/runs/36539973071)
recognized `534367f` as the executed watermark and reported zero skipped
commits. The [actual daily scheduled run](https://github.com/uibcdf/smonitor/actions/runs/36571010365)
at `2e03716` also executed the detector, found zero debt, and omitted
the matrix jobs. The first real daily trigger is now observed; hosted PR
execution and platform claims still need review. Routine CI, QA and
MolSysSuite policy also passed at `2e03716`.

## Routine policy 1.5.4 adoption — 2026-10-03

The maintainer authorized publication and adoption of policy-v1.5.4 under
uibcdf/molsyssuite#39. The immutable tag points to central e459ea0; the
component now calls that published gate and receives the byte-identical
canonical guide through the suite synchronizer. Routine development uses
Python 3.14. The existing full Python 3.11–3.14 matrices and skipped-commit
recovery semantics are preserved; no public package is published here.
Local conformance and changed-workflow Actionlint checks pass. Hosted
policy and applicable routine checks are dispatched separately from skipped
direct pushes; their exact commits and outcomes remain to be measured.

The single Linux routine package suite moves to Python 3.14; the required
PR check must use its new name while preserving strict checks and administrator
direct-push bypass. The complete weekly matrix still includes every older minor.

## Python 3.14 hosted routine checks — 2026-10-03

The branch protection API reports strict required checks `qa`,
`collective-e2e` and `Test on ubuntu-latest, Python 3.14`. Commit `65f981f`
completed the documentation and publication-tooling transition through the
authorized administrator direct-push route. GitHub reported a bypass of the PR
rule and the three expected pre-push checks. After the push, [CI](https://github.com/uibcdf/smonitor/actions/runs/37154594493),
[QA](https://github.com/uibcdf/smonitor/actions/runs/37154594483),
[Docs CI](https://github.com/uibcdf/smonitor/actions/runs/37154594525) and
[MolSysSuite policy](https://github.com/uibcdf/smonitor/actions/runs/37154594874)
all passed on that exact commit. This verifies the hosted direct-push route at
Python 3.14; the hosted PR route and platform-claim review remain unobserved.
