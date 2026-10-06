---
summary: Provider registration preserves application diagnostic policy.
issue: uibcdf/smonitor#38
status: resolved
opened: 2026-10-06
closed: 2026-10-06
severity: high
verification: reproduced
area: [integration, configuration, catalog]
guard: tests/test_provider_registration.py
normative: docs/content/user/library-integrators/integration-api-advanced.md
blocked_by: []
supersedes: []
---

# Provider registration preserves application diagnostic policy

Before the fix, configuring CRITICAL/qa with capture disabled, then importing
ArgDigest, DepDigest or PyUnitWizard reset policy to WARNING/user with capture
enabled. Fresh subprocesses reproduced this against local editable consumers.

`register_provider()` now loads the exact package declaration, validates it, and
commits a detached catalog/signal/provenance record atomically under a lock. It
retains recommendations without applying them. Equal shared definitions are
accepted; conflicts reject the complete operation, independently of import order.
Explicit application catalog overrides keep their existing semantics.

`ensure_configured()` registers declarations and only bootstraps before policy
has been selected. A discovered application project takes precedence over
provider defaults. Applications can explicitly request provider policy with
`use_provider_policy=True`. Memoization belongs to the manager, not process-global
test state. Explicit audience rendering uses `resolve(profile=...)` without
changing policy. Bundles retain provider provenance and declaration names.

The guard covers all three-provider permutations and repeated registration,
first-use bootstrap, explicit opt-in, concurrent registration, atomic rejection,
detached records, bundles and pure audience rendering. Published distribution
qualification and adoption of declaration-only initialization remain release and
consumer work; this checkout does not claim new PyPI/Conda publication.

Coordination remains in uibcdf/molsyssuite#106, uibcdf/moli#62 and
uibcdf/argdigest#29; consumer code is not copied into SMonitor.
