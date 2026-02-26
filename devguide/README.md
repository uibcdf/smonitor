# smonitor Developer Guide

This folder collects developer documentation for `smonitor`.

## Recommended Reading Order
0) `../SPEC_SMONITOR.md` — Product scope, architecture, and roadmap decisions.
1) `architecture.md` — High-level architecture and goals.
2) `event_model.md` — The event schema and handler contract.
3) `api.md` — Public API sketch and expected behavior.
4) `implementation_plan.md` — Phased implementation checklist.
5) `integration_notes.md` — How to integrate with arg_digest, dep_digest, and MolSysMT.
6) `../standards/SMONITOR_GUIDE.md` — Canonical guide to sync into ecosystem repos.
7) `../SUPPORT.md` — Project support and incident-handling policy.
8) `../docs/content/user/library-integrators/ai-agents-workflow.md` — Integrator contract for AI/LLM-enabled workflows.

## Scope
These documents track implementation details. Product-level decisions and
historical context live in `SPEC_SMONITOR.md`.

## Current Status (Checkpoint)
- Core scaffold, manager/context, and `@signal` implemented.
- Emitters for warnings/logging/exceptions implemented.
- Policy engine implemented with routing, filtering, rate limits, sampling,
  and transforms (`set`, `set_extra`).
- Console/file/json handlers implemented (plain) + optional rich handler.
- `MemoryHandler` added for in-memory buffering.
- Config discovery + merging for `_smonitor.py` implemented.
- CLI added for validate/report/export; config validation hardened.
- Event schema validation (dev/qa) and strict SIGNALS enforcement.
- CODES templating and SIGNALS soft enforcement.
- Profiling expanded (timeline, sampling, spans, export).
- Local bundle export (CLI + event buffer).
- Ecosystem integration completed (MolSysMT, MolSysViewer, ArgDigest, DepDigest, PyUnitWizard).
- Documentation architecture migrated to MyST with role-based routes:
  integrators, end users, showcase scenarios, and contributor path.
- Standards pack published for ecosystem adoption (`standards/`), including
  end-user rescue/docs templates and sync policy.
- Version `0.11.0` released as pre-1.0 stabilization checkpoint.

## Operational Stabilization Plan (Toward 1.0.0)
1. Stabilization window (2-4 weeks): only bugfixes, hardening, and docs/test corrections.
2. Weekly operation loop:
   - review CI failures in SMonitor and integrated libraries,
   - review recurring incident codes/signals,
   - review quality of support bundles.
3. Required PR gates:
   - `pytest` full suite,
   - docs build (`make -C docs html`),
   - QA CI package smoke (`sdist`/`wheel` + install + CLI check).
4. Freeze rules:
   - no breaking API changes in public exports,
   - no semantic repurposing of existing diagnostic codes.
5. Exit criteria for `1.0.0`:
   - no open high-severity bugs in SMonitor,
   - sustained CI stability across defined matrix,
   - ecosystem smoke checks validated.

## Remaining Focus (Pre-1.0)
- Raise focused coverage on critical low-coverage modules (`cli`, rich console handler, profiling, integration adapters).
- Final consistency sweep across `README`, `SPEC`, `devguide`, and Sphinx docs.
- Post-1.0 roadmap preparation: opt-in telemetry client and Sentinel integration.
