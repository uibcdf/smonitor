---
summary: Review inherited Python ecosystem policies for SMonitor.
issue: uibcdf/smonitor#24
status: active
opened: 2026-09-24
closed:
verification: inspected
area: [governance, ci, ecosystem]
guard:
normative: MOLSYSSUITE_GUIDE.md
blocked_by: []
supersedes: []
---

# Review inherited Python ecosystem policies for SMonitor

**Reported:** 2026-09-24, while rolling out the effective pair
MOLI@`888902eb2ccc482c62c6f75da9d8f0bf9bb56442` and MolSysSuite
`policy-v1.4.10` under `uibcdf/molsyssuite#6`.

## What

SMonitor needs an explicit member review of the inherited Python support-library
and developer-tool policies. Before this review, its primary hosted CI invoked
native pytest, its full matrix used the local-agent `--receptor=llm` profile in
ephemeral hosted logs, and the test Conda environment specified an open-ended
`pytest-receptor >=1.1.0` dependency. The QA jobs also invoked pytest without
the receptor. These observations are from `origin/main` at `e59e714`.

## How

Pin published pytest-receptor `1.1.0` in the development, test and QA
environments and the independently installed collective E2E job. Use
`--receptor=ci` in every hosted pytest invocation while retaining test
selection, xdist, coverage and JUnit arguments. The GH Run Receptor profile
maps the primary, full-matrix and QA workflows to `ci`; a real inspection of
the pre-change QA run `35989575739` with `gh run-receptor inspect` returned a
two-job success. Review each support-library boundary
against the pinned MOLI applicability rules; record applicable uses or
non-applicability with member evidence before changing the suite inventory.

## Why

MOLI's published policy requires an exact reviewed receptor release for CI and
the `ci` profile for hosted logs. The suite's `pending` inventory deliberately
does not infer adoption from the mere presence of a dependency or a guide.
This member issue keeps implementation evidence and unresolved applicability
decisions linked to the central rollout.

## What was refuted

An installed `pytest-receptor` package alone does not change pytest output;
the hosted command must select its profile. The full matrix's `llm` profile is
intended for an agent with access to the checkout and can point to a local
overflow file that a hosted reader cannot recover. The two QA jobs use a
separate Conda environment, and the collective E2E job installs dependencies
directly, so changing only the primary test environment would miss them.

## Remaining review

- The local changed checkout passed `pytest --receptor=llm -q` with 506 passed
  and four skipped, `ruff check .`, `ruff format --check .`, the developer-guide
  index check, and MolSysSuite's offline component checker.
- Verify the exact Conda `1.1.0` release resolves on all claimed Python minors
  in the hosted full matrix and that the independently installed E2E job runs.
- Record ArgDigest, DepDigest, SMonitor and PyUnitWizard applicability at the
  public boundaries, with tests or a reason for non-applicability.
- Record GH Run Receptor active-use evidence and then update the suite's two
  review states separately. Keep `pending` until each review is complete.

## Support-library applicability checkpoint

The package's published metadata declares no runtime dependency; `rich` is
an optional presentation extra. `smonitor.configure()` and
`smonitor.validation.validate_event()` perform nontrivial configuration and
event validation, so the ArgDigest boundary requires a decision. The rich
handler imports its backend lazily and explains its absence, so the DepDigest
boundary also requires a decision. Both proposed libraries already depend on
SMonitor (`argdigest` directly and through `depdigest`; `depdigest` directly),
which would create a runtime dependency cycle if SMonitor added them. This is
not evidence that the boundaries do not exist; a bounded architecture exception
or a contract change is needed before calling support-library adoption done.

SMonitor is itself the diagnostic provider. Its profiling values are numeric
elapsed times with explicit fixed millisecond keys and thresholds; no public
unit parsing, conversion or dimensional validation was found in this review.
PyUnitWizard is therefore provisionally non-applicable. This remains an
inspected conclusion until the member review is closed.

## Acceptance criteria

- All hosted pytest calls use `--receptor=ci` with an exact published version.
- The existing tests, coverage, xdist and JUnit gates remain intact and hosted
  CI confirms the commands work.
- The support-library applicability review and developer-tool evidence are
  recorded here and in `uibcdf/smonitor#24`; the suite inventory cites them.
