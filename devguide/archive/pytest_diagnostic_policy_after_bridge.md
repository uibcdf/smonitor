---
summary: Evaluate opt-in pytest diagnostic policy after the observational bridge.
issue: uibcdf/smonitor#32
status: resolved
opened: 2026-09-26
closed: 2026-10-22
verification: measured
area: [pytest, ci, ecosystem]
guard: tests/test_pytest_policy.py
normative: docs/content/developer/pytest-diagnostic-policy.md
blocked_by: []
supersedes: []
---

# Pytest diagnostic policy after the bridge

SMonitor 0.18.0 completed the observational bridge recorded in
[`../archive/pytest_diagnostics_bridge_and_molsyssuite_policy.md`](../archive/pytest_diagnostics_bridge_and_molsyssuite_policy.md).
Pytest Receptor owns the execution outcome and canonical artifact, while
SMonitor contributes bounded diagnostic identities through its neutral
extension protocol. The current bridge does not alter pytest outcomes.

The archived proposal contains broader design inputs that now need their own
evidence and adoption decision:

- opt-in strict QA rules and stable diagnostic-identity baselines;
- fixtures or markers only where they add value without duplicating receptor;
- integrity links to optional standalone SMonitor support bundles;
- dogfooding on MolSysViewer, MolSysMT and a third sibling repository before
  considering a separate `pytest-molsyssuite` policy package.

The default xdist load distribution makes warning counts and credited test
nodes unstable for process-cached warnings. Baselines should compare a set of
`(code, source, fingerprint)` identities; see
[`../warning_baselines_under_parallel_test_runs.md`](../warning_baselines_under_parallel_test_runs.md).

This issue is exploratory. No strict policy, fixtures, markers, bundle links or
new package are part of the 0.18.0 release contract.

## Resolution, 2026-10-22

SMonitor now offers an opt-in policy reader and CLI for Pytest Receptor's
canonical artifact: `smonitor.pytest_policy.evaluate_pytest_artifact`,
`smonitor pytest-check`, and `smonitor pytest-baseline`. The reader checks
finalization, SHA-256 integrity through the receptor reader, execution
completeness, artifact truncation, extension gaps, SMonitor payload shape,
optional provider `CODES` membership, forbidden codes, and new warning/error
identity against a versioned baseline. It reports disappeared identities for
review but does not fail them. Its gate uses a set of `(code, source,
fingerprint)`, never event counts or node assignment. Default pytest behavior
remains observational; this separate command changes no pytest outcome.

Baseline creation requires a passing, complete run and explicit opt-in for an
empty set. `--require-diagnostics` detects a missing producer in smoke tests
that should emit a diagnostic. A zero-diagnostic artifact alone cannot prove
that the SMonitor plugin was active. Provider catalog checks use explicit
trusted `_smonitor.py` roots and the existing structural validator; they do
not certify every runtime template substitution. Consumer tests remain
responsible for representative rendered messages and structured fields.

### Measured adoption evidence

All probes used the Python 3.14 MolSysSuite environment, receptor `llm` profile,
an explicit JSONL path under `/tmp`, and read-only consumer checkouts:

| Probe | Pytest result | SMonitor identity evidence | Policy result |
|---|---|---|---|
| Three-consumer fixture, serial | 3 passed | Viewer init warning, MolSysMT unknown atom, ArgDigest missing digester | complete, integrity-valid, 3 records, 0 dropped |
| Same fixture, `-n 2` | 3 passed | Exact same three `(code, source, fingerprint)` identities | complete, integrity-valid, 3 records, 0 dropped |
| MolSysViewer `test_core_public_api_does_not_emit_missing_digester_warnings` | 1 passed | `MSM-WARN-H5MSM-001`; no `ARG-WARN-MISS-001` | forbidden ArgDigest code absent; policy passed |
| MolSysMT `test_get_atom_type_from_atom_name.py`, `-n 2` | 3 passed | `MSM-WARN-ATOM-001` | catalog and required-diagnostic checks passed |
| ArgDigest `test_missing_digester_warning_has_readable_message` | 1 passed | `ARG-WARN-MISS-001` | catalog and required-diagnostic checks passed |

The artificial three-consumer fixture was run from `/tmp/smonitor-issue32`;
its serial baseline matched its distributed artifact. Changing policy to
forbid `ARG-WARN-MISS-001` made `pytest-check` exit 1 while the recorded pytest
outcome remained `PASS`. This proves the rule is opt-in and independent of the
runner outcome. The real MolSysViewer test checks absence of that warning on a
large public API workflow; the separate ArgDigest test proves the producer can
record it. The real MolSysMT test verifies worker transport on a scientific
function. These are focused probes, not a claim of continuous adoption in the
sibling CI pipelines.

Fingerprint inputs include selected structured extra fields (`caller`,
`resource`, retry fields and others). The tuple is deterministic for equal
inputs, but a baseline over data-dependent values can still change between
runs. This gate does not promise stability for arbitrary diagnostics; code-level
forbidden rules are available where the fingerprint varies legitimately.

The SMonitor repository gate passed: `python -m pytest --receptor=llm` reported
725 passed. `tests/test_pytest_policy.py` guards duplicate
occurrence collapse, forbidden and unknown catalog identities, baseline
round-trip, incomplete artifacts, missing expected diagnostics, and invalid
provider declarations.

### Scope decisions

- Keep test-local assertions in `pytest.warns`, `pytest.raises`, and existing
  SMonitor contract tests. A SMonitor fixture or marker would add a second
  test-evidence surface for no demonstrated gain.
- Keep the standalone bundle separate. A future paired-bundle manifest must
  specify relative paths, hashes, schemas, completeness, redaction settings,
  and coverage limits. Rich bundles have no versioned schema or guaranteed
  complete history, so an automatic link would imply guarantees they lack.
- Do not create `pytest-molsyssuite` yet. Three repositories were exercised,
  but only as bounded dogfood probes. There is no sustained cross-repository
  policy configuration or maintainer demand to extract into another package.
  The reusable policy remains in its diagnostic owner, SMonitor.
