---
summary: The 0.17.1 citation version lags its immutable release tag.
issue: uibcdf/smonitor#30
status: resolved
opened: 2026-09-26
closed: 2026-09-26
severity: medium
verification: reproduced
area: [release, metadata, ci]
guard: tests/test_citation_metadata.py::test_citation_version_matches_committed_release_plan
normative:
blocked_by: []
supersedes: []
---

# Release citation version lags its tag

The immutable `0.17.1` tag declares `version: 0.17.0` in `CITATION.cff`.
The Conda package and GitHub Release are correctly identified as `0.17.1`,
but citation metadata in that source release is stale. Post-tag QA run
`36230082851` failed its exact-tag-or-next-candidate citation test.

Before the tag, that test compared against the latest *existing* tag,
`0.17.0`, and accepted the stale version. It did not compare against the
committed `0.17.1` release plan. The new guard
`tests/test_citation_metadata.py::test_citation_version_matches_committed_release_plan`
reproduced the mismatch locally: `0.17.0 != 0.17.1`.

The `0.17.1` tag and occupied Conda coordinate must remain immutable.
Correct the citation version in a new `0.17.2` release, keep the guard in the
pre-tag full matrix, and verify its public Conda file and Windows installed
command. The release plan chooses the direct route because only source
citation metadata and its test change; runtime code and package dependencies
are unchanged.

## Resolution and verification

The `0.17.2` tag contains `CITATION.cff` with `version: 0.17.2` and the
committed release plan has the same version. The new guard first reproduced
the `0.17.0 != 0.17.1` mismatch, then passed on the corrected candidate.
Local citation, release and report tests passed with 108 passed and four
skipped. Hosted CI, QA, documentation and policy checks passed at candidate
commit `fbb0d401942fa229c60afddc3e98b5b6bba386be`; full-matrix run
`36230288183` passed all twelve cells.

Stable Release `0.17.2` triggered direct Conda run `36230424438`. Its receipt
records the exact matrix run, an unoccupied pre-upload coordinate, and public
file `noarch/smonitor-0.17.2-py_0.tar.bz2` with SHA-256
`9471ccfd2067cd1fe5916689af02a9ac4662803cbeb9bcc79967347cec5354ef`.
The public Conda index independently returned the same file and digest.
The Windows job installed the new package and ran its CLI command.

The original `0.17.1` tag and package remain immutable; its Release notes
point readers to the corrected version. The guard checks the candidate
citation before the next tag is made.
