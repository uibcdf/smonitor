---
summary: The 0.17.1 citation version lags its immutable release tag.
issue: uibcdf/smonitor#30
status: active
opened: 2026-09-26
closed:
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
