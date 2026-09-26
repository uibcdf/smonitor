---
summary: Evaluate opt-in pytest diagnostic policy after the observational bridge.
issue: uibcdf/smonitor#32
status: open
opened: 2026-09-26
closed:
verification: asserted
area: [pytest, ci, ecosystem]
guard:
normative:
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
