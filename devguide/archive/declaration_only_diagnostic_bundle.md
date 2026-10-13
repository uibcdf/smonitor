---
summary: Emit catalog diagnostics without bootstrapping application policy.
issue: uibcdf/smonitor#48
status: resolved
opened: 2026-10-13
closed: 2026-10-13
severity: medium
verification: reproduced
area: [integration, registration, policy]
guard: tests/test_declaration_only_bundle.py
normative:
blocked_by: []
supersedes: []
---

# Declaration-only DiagnosticBundle

## Maintainer disposition — 2026-10-13

Diego approved the implementation and explicitly authorized direct commit/push
to main under the internal-maintainer route. The reviewed implementation is
`986175de7a4456e977183f5dad361b541edfa6fd`; its hosted CI, docs, QA and policy
checks passed. At this review stage, provider publication and receiving installed
qualification were pending.

## Resolution — 2026-10-13

The final source candidate is `f6230af431a7fc185209fa44364c017d711cc2b7`.
Its [full twelve-cell source matrix](https://github.com/uibcdf/smonitor/actions/runs/38463960174)
and policy gate passed. The staged `smonitor-0.20.0-py_1.tar.bz2` was built in
[run 38464211188](https://github.com/uibcdf/smonitor/actions/runs/38464211188),
independently hashed, and qualified through the
[twelve-cell installed gate](https://github.com/uibcdf/smonitor/actions/runs/38465021847).
The [exact-file promotion](https://github.com/uibcdf/smonitor/actions/runs/38466664766)
verified every required installed step and published the same file to `uibcdf/main`.
Its SHA-256 is `887cbbe8fa9056388ee1344c8244138af2c06371846584dc234de1d994335ebf`.
The stable [0.20.0 release](https://github.com/uibcdf/smonitor/releases/tag/0.20.0)
and public Conda package now provide this opt-in API. The default bootstrap behavior
remains guarded by `tests/test_declaration_only_bundle.py`.

ArgDigest's receiving installed qualification remains owned by
uibcdf/argdigest#32; provider publication alone does not establish consumer adoption.

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
