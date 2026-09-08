---
summary: Use the release profile for the composite Conda publication workflow
issue: uibcdf/smonitor#10
status: resolved
opened: 2026-09-08
closed: 2026-09-08
severity: low
verification: reproduced
area: [tooling, release]
guard: tests/test_gh_run_receptor_policy.py
normative:
blocked_by: []
supersedes: []
---

# The Conda profile cannot see platforms built inside the publishing action

**Reported:** 2026-09-08 during SMonitor's first controlled GH Run Receptor
dogfooding inspection.

## What

SMonitor configured its release-triggered Conda workflow as a native `conda` profile with
four expected platforms. The workflow exposes three GitHub jobs keyed by Python version;
each job delegates all four platforms to
`uibcdf/action-build-and-upload-conda-packages@v2.0.1`. No platform-named job or GitHub
artifact is available to the receptor.

Using gh-run-receptor development commit `921f434` reproduced this result:

```text
./gh-run-receptor --repo uibcdf/smonitor --receptor llm \
  inspect 34278594890 --capture metadata
FAIL conclusion=success status=completed | ... | profile=conda
conda platforms: successful=0 failed=0 missing=4 artifacts=0 observed=0
missing expected: linux-64, osx-64, osx-arm64, win-64
```

## How

The Conda profile maps native platforms from GitHub job and artifact names. SMonitor's
platform dimension exists only inside the composite publishing action, so the four
configured expectations cannot be satisfied from the receptor's GitHub evidence bundle.
The provider-side capability gap is tracked in `uibcdf/gh-run-receptor#35`.

## Why

GitHub run `34278594890` completed successfully at tag `0.14.0`; all three Python jobs
succeeded. The public Anaconda API independently listed 12 distributions on label `main`,
covering Python 3.11--3.13 on `linux-64`, `osx-64`, `osx-arm64`, and `win-64`. The prior
rule therefore produced a derived failure for a successful publication and was unsuitable
as the preferred first inspection path.

## What was refuted

- The workflow did not fail: native GitHub evidence reports `completed`/`success` and
  three successful jobs.
- Publication was not inferred from the green workflow: Anaconda was queried separately
  and returned all 12 expected distributions.
- Removing only `expected_platforms` was rejected because a Conda report with zero
  observed platforms would hide the evidence mismatch.
- Action inputs were not interpreted as outputs; requesting a platform does not prove
  its package was uploaded.

## Resolution

The repository rule now selects the `release` profile. It preserves the release event,
tag, SHA, and package-step outcomes while explicitly reporting `registry=not_observed` and
`archive=not_observed`. Anaconda verification remains an independent release gate.

Inspection with the explicit release profile reported `PASS`, the exact source SHA, three
package phases, no GitHub artifacts, and no inferred registry result. The regression guard
prevents the action-internal platform matrix from being configured again as GitHub-visible
`expected_platforms`.
