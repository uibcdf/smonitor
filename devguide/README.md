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
