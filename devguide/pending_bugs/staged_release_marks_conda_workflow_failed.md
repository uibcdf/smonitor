---
summary: Staged release marks the automatic Conda workflow failed despite successful promotion
issue: uibcdf/smonitor#28
status: active
opened: 2026-09-26
closed:
severity: medium
verification: reproduced
area: [packaging, release, ci]
guard: tests/test_noarch_conda_publication.py
normative: devguide/conda_release_routes.md
blocked_by: []
supersedes: []
---

# Staged release marks the automatic Conda workflow failed

## What happened

The `0.17.0` staging build and its Windows installed-command check passed in
[run 36225638736](https://github.com/uibcdf/smonitor/actions/runs/36225638736).
The stable GitHub Release then started the automatic Conda workflow, whose direct
route check failed because the committed plan correctly selected `staged`
([run 36226014466](https://github.com/uibcdf/smonitor/actions/runs/36226014466)).
The exact-file promotion passed separately in
[run 36226026002](https://github.com/uibcdf/smonitor/actions/runs/36226026002).
The direct-route guard prevented a duplicate upload, but the release event left a
misleading failed run.

## Decision

Read and validate the committed route before the release job selects its steps.
For `staged`, verify the exact tag, plan and full-matrix gate, retain the route
receipt, and skip Conda setup, direct upload and the Windows job. The separate
promotion remains the publication gate. For `direct`, keep the all-label
registry preflight and public digest check. Invalid plans still fail before any
upload.

## Evidence and remaining proof

`tests/test_conda_release_route.py` checks route selection and rejects a
mismatched or noncanonical version. `tests/test_noarch_conda_publication.py`
guards both workflow paths, including the Windows job condition. Local tests
and hosted CI can verify the implementation without touching the occupied
`0.17.0` coordinate. The issue remains active until a later staged release
event shows a successful routing run and promotion; the historical run cannot
be changed.
