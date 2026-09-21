---
summary: Routine GitHub Releases no longer publish Conda packages
issue: uibcdf/smonitor#20
status: active
opened: 2026-09-21
closed:
severity: high
verification: inspected
area: [packaging, release, ci]
guard:
normative:
blocked_by: []
supersedes: []
---

# Routine GitHub Releases no longer publish Conda packages

**Reported:** 2026-09-21 while reviewing the 0.16.0 Conda recovery against the normal
0.17.0 release procedure. Shared policy evaluation belongs to `uibcdf/molsyssuite#27`.

## What

The current `.github/workflows/build_and_upload_conda_packages.yaml` subscribes only to
`workflow_dispatch`. Its staging route uploads only to `uibcdf/label/staging`. The separate
promotion workflow also requires manual dispatch. Therefore tagging and publishing a
routine GitHub Release cannot trigger a Conda upload, even if no pre-public staging gate
is needed. No 0.17.0 tag or Release has been created to test this externally; the trigger
absence is established by source inspection.

## How

The 0.16.0 release workflow had built and uploaded build 0 to `main`, colliding with an
earlier build-0 upload under `staging`. The recovery correctly replaced that second
upload with exact-file promotion, but also removed the release event entirely. That
prevented the collision by requiring staging for every subsequent release, which was
not the intended general release contract.

Restore a guarded direct route for a release that explicitly declares it before tagging,
has passed its exact-commit gates, and has no existing staged or public file for that
version. Build, test and upload a new file to `main` once; retain producer evidence and
independently query the public poststate. A staged version must never enter this route:
its exact tested file is promoted with its SHA-256 instead. An unavailable or ambiguous
registry preflight fails closed. `uibcdf/molsyssuite#27` owns the reusable decision
criteria; SMonitor is a local noarch implementation pilot, not the policy authority.

## Why

SMonitor maintainers expect a routine tag and stable GitHub Release to publish Conda
automatically. The current workflows would leave a public GitHub Release without the
claimed Conda artifact until a maintainer noticed and manually staged and promoted it.
The change also imposes the cost of staging on releases for which no pre-public packaged
or coupled-consumer gate is required.

## What was refuted

- Re-uploading a staged filename under a different label is not an alternative: the
  0.16.0 release measured HTTP 409 for that shared coordinate (`uibcdf/smonitor#19`).
- Always staging every SMonitor release solves the collision but removes automatic
  routine publication without a corresponding release-safety requirement.
- Automatically choosing the newest staged build is unsafe: a version may have several
  builds or a candidate from a different source commit. Exact coordinate, tag SHA and
  digest remain required for promotion.

## Acceptance criteria

- A release-plan decision exists before tagging and identifies direct or staged mode,
  version, rationale and required gates; a mismatch fails before registry mutation.
- A stable routine Release with a direct plan automatically builds, tests and uploads
  only a new coordinate to `main`, retains evidence and verifies the public record.
- A staged plan or any same-version staged file cannot invoke the direct uploader;
  promotion retains its exact tag/coordinate/SHA-256 checks.
- Registry errors and occupied coordinates fail closed; no upload uses `--force`.
- Local tests exercise accepted and rejected decisions and the workflow wiring; no
  synthetic test claims that an actual 0.17.0 Release was published.

## Current implementation and remaining proof

The two-route workflow, exact-commit gate check, all-label preflight, public digest
postcheck, negative tests, and maintainer procedure are implemented locally. The
targeted local suite passes. This report remains active until the first future direct
GitHub Release demonstrates the complete hosted route; no 0.17.0 tag or Release has
been created as a synthetic proof. Central policy review remains with
`uibcdf/molsyssuite#27`.
