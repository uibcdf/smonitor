---
summary: Release upload collides with a staged Conda build coordinate
issue: uibcdf/smonitor#19
status: active
opened: 2026-09-21
closed:
severity: high
verification: reproduced
area: [packaging, release, conda]
guard:
normative:
blocked_by: []
supersedes: []
---

# Release upload collides with a staged Conda build coordinate

**Reported:** 2026-09-21 during the public SMonitor 0.16.0 release.

## What

GitHub Release `0.16.0` was published and independently archived by Zenodo, but the
release-triggered Conda workflow `35587726937` failed to upload its otherwise built and
tested `noarch/smonitor-0.16.0-py_0.tar.bz2` package to `uibcdf` main. Anaconda returned
`409 Conflict`: that exact owner/package/version/subdirectory/filename coordinate was
already uploaded under the staging label by candidate run `35585670456`.

## How

Anaconda labels change discoverability; they do not create independent namespaces for
file uploads. The staging and main workflows both used build number 0. Consequently,
the second upload was rejected even though it requested a different label. The action
correctly reported `1 of 1 uploads failed`; GH Run Receptor preserved the failure and
its producer evidence. A green GitHub Release or Zenodo record does not imply Conda
publication.

The corrected lifecycle follows `uibcdf/molsyssuite#27`: every candidate is first
uploaded to staging under an immutable version/build coordinate, and public publication
adds the `main` label to that *same* file after verifying its SHA-256. No build number is
reserved for a second upload. A defective candidate gets a higher build number, never
an overwrite. For this already-published release, the exact candidate
`noarch/smonitor-0.16.0-py_1.tar.bz2` from SHA
`7daac74c6641e6003df8bbcc6cca91709ec891b9` was built in run `35587197005` and
installed successfully in a clean Python 3.14 environment. The shared promotion Action
`uibcdf/action-build-and-upload-conda-packages/promote@v2.2.2`, already piloted in
`uibcdf/pytest-receptor`, can add `main` only to this exact staged file after verifying
its source label, checksum, and target state. SMonitor's dispatch additionally checks
the published GitHub Release tag and commit. It must never copy the entire staging
label or overwrite a distribution.

## Why

MolSysViewer, DepDigest, and other consumers cannot resolve SMonitor 0.16.0 from the
normal `uibcdf` channel until the exact file is visible under `main`. The same collision
would recur at later releases if they rebuild and re-upload a staged coordinate. Central
issue `uibcdf/molsyssuite#27` already owns the reusable policy; this case provides
another independent noarch-publisher validation.

## What was refuted

- The build itself did not fail; Conda build and package tests completed before upload.
- A label is not an upload namespace: uploading a second file with the same coordinate
  under `main` returns 409.
- Reserving build 0 for a later release upload would avoid this particular 409 but
  distribute a different, untested file and abandon exact candidate identity.
- Deleting the entire version from Anaconda would discard the tested candidate and
  would not repair the lifecycle design.

## Acceptance criteria

- The staging workflow cannot directly upload to `main` on a release event; a separate
  post-release dispatch promotes only one exact staged file.
- Promotion checks release, coordinate, and checksum identity, preserves the staging
  label, and refuses broad or mismatched promotion.
- The 0.16.0 file appears under the public `uibcdf` main label and installs in a clean
  Python 3.14 environment with correct version, origin, and CLI behavior.
- Workflow-contract tests guard staging/public separation and exact-file promotion.
  `uibcdf/molsyssuite#27` records the reusable policy and SMonitor's measured outcome.

## Resolution

Pending exact-file promotion, public-channel verification, and central handoff.
