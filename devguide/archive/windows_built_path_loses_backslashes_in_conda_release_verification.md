---
summary: Windows built path loses backslashes in Conda release verification.
issue: uibcdf/smonitor#25
status: resolved
opened: 2026-09-24
closed: 2026-09-24
severity: medium
verification: reproduced
area: [ci, packaging]
guard: tests/test_conda_release_route.py::test_windows_built_paths_preserve_backslashes_and_quoted_spaces
normative:
blocked_by: []
supersedes: []
---

# Windows built path loses backslashes in Conda release verification

**Reported:** 2026-09-24 from the SMonitor 12-cell hosted matrix
`36025853813` run against the pytest-receptor adoption commit.

## What

All four Windows/Python jobs failed the same two tests in
`tests/test_conda_release_route.py`, while eight Linux and macOS jobs passed.
The Windows jobs each reported 504 passing tests, four skips and two failures.
`test_public_poststate_matches_the_exact_built_file` raised
`ReleaseRouteError: built package is not the expected noarch release file`;
`test_public_poststate_rejects_checksum_mismatch` then observed that early
error instead of its expected checksum mismatch. The preceding matrix
`35662669121` had the same Windows-only split.

## How

`verify_public()` passed `built_paths` to `shlex.split()` with its POSIX
default. Windows `tmp_path` values contain backslashes, which POSIX shell
parsing treats as escapes. The resulting path is not the built file. Parse
Windows action output with non-POSIX shell rules and strip only balanced
outer quotes; retain the existing exactly-one-file and filename checks.

## Why

The false failure makes the full supported-platform gate red and prevents the
developer-tool review in `uibcdf/smonitor#24` from citing a passing hosted
matrix. The production release verifier would also reject a valid Windows
built path before checking its public hash.

## What was refuted

The pytest-receptor profile reported the failures accurately; GitHub's
authoritative job conclusions and the native failed-step logs agree.
Changing the checksum assertion would hide the earlier path parsing error.

## Resolution

Commit `a470286` adds a parser that retains Windows backslashes and strips
balanced outer quotes while preserving the one-file release invariant. The
new test exercises both an unquoted Windows path and a quoted path with
spaces; the old POSIX parsing rule loses backslashes in the first case, so
the test guards the reported mechanism. Local pytest-receptor passed 510
tests with five skips, Ruff and the component checker passed. The manual
hosted full matrix `36032583387` passed all twelve jobs across Linux, macOS
and Windows with Python 3.11 through 3.14. The defect is resolved.
