---
summary: Emit catalog diagnostics without bootstrapping application policy.
issue: uibcdf/smonitor#48
status: active
opened: 2026-10-13
closed:
severity: medium
verification: reproduced
area: [integration, registration, policy]
guard: tests/test_declaration_only_bundle.py
normative:
blocked_by: []
supersedes: []
---

# Declaration-only DiagnosticBundle

## What

ArgDigest's registration-only public route (uibcdf/argdigest#32) must preserve
an unconfigured application during catalog warnings as well as imports.
Recorda is the concrete receiving application; uibcdf/moli#62 owns its wider
diagnostic-policy coordination.

## How

Add the keyword-only `bootstrap_policy=False` choice to DiagnosticBundle.
The bundle registers declarations through register_provider, then uses the
existing emit_from_catalog boundary without a package_root. Its original
package_root remains available as provenance. Warning, info and support-tier
calls therefore do not enter ensure_configured. The default True retains
first-use bootstrap and configured-application precedence.

The public emit wrapper also selects the console fallback on an unconfigured
manager. Add the same per-call option there and in emit_from_catalog; explicit
False preserves the caller's handler set. Preserve the default True for existing
callers, including catalog fallbacks without a matching entry.

Local source validation on Python 3.14.7: 182 focused checks pass (two unrelated
skips); the complete SMonitor suite passes 665 checks with three justified
existing skips. The source-integrated ArgDigest suite passes all 391 checks with
registration-only qualification required, including fresh manager, actual
warning and failure-path controls. These are source results, not installed or
public delivery. The shared development environment's unrelated #82 conflicts
remain visible and unchanged.

Tests execute real catalog registration, warnings, info and tier calls under
restrictive scopes with fresh unconfigured and explicitly configured managers.
They check config identity, warning hooks, root and manager handlers, scope
identity, Python warning behavior and actual catalog events. The default path
is separately checked for its original bootstrap.

## Why

Removing ArgDigest's initial ensure_configured alone leaves a later hidden
bootstrap through DiagnosticBundle. This operation belongs in SMonitor rather
than copying its warning, replay, deduplication or stacklevel implementation into
the consumer. This is a proposed public capability, not a released guarantee.

## Acceptance criteria

- Preserve default bundle behavior and all existing integration contracts.
- Declaration-only emission preserves both unconfigured and configured callers.
- Owner-reviewed provider PR, then separately qualified provider publication
  before ArgDigest claims a public capability or Recorda adopts it.
