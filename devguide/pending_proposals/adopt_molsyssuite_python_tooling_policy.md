---
summary: Adopt the shared Python and Ruff development baseline.
issue: uibcdf/smonitor#12
status: active
opened: 2026-09-12
closed:
verification: measured
area: [ci, ecosystem]
guard:
normative:
blocked_by: []
supersedes: []
---

# Adopt the MolSysSuite Python tooling policy

## What

Align SMonitor with the Python-library contract governed by
`uibcdf/molsyssuite#6`: Python `>=3.11,<3.14`, Python 3.13 for development,
Ruff as formatter, import sorter, and linter, and the common `E4`, `E7`,
`E9`, `F`, and `I` rule baseline.

## How

Add the repository-local Ruff configuration and explicit exclusions for synchronized
root guides, pin the suite-tested Ruff release in the development environment, and
invoke the reusable MolSysSuite conformance workflow. Preserve SMonitor's broader test
matrix and repository-specific checks.

## Why

SMonitor is one of the six wave-1 libraries being stabilized first. Sharing the same
minimum Python range and quality gate reduces the cost and ambiguity of changes that
span SMonitor and its consumers.

## Evidence

The policy 1.0 checker on 2026-09-12 reported `PYTHON_RANGE`, `RUFF_CONFIG`,
`VENDORED_GUIDE_RUFF`, and `RUFF_CI`. Existing workflows already exercise Python
3.11, 3.12, and 3.13 and run Ruff linting, but do not enforce formatting or the complete
shared configuration.

## Acceptance criteria

- The central conformance checker reports no findings.
- Ruff lint and format checks pass with the suite-tested release.
- The existing SMonitor test suite passes.
- The local issue and this record close together after the guard is published.

