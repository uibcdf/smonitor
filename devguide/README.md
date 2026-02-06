# smonitor Developer Guide

This folder collects developer documentation for `smonitor`.

## Recommended Reading Order
1) `architecture.md` — High-level architecture and goals.
2) `event_model.md` — The event schema and handler contract.
3) `api.md` — Public API sketch and expected behavior.
4) `implementation_plan.md` — Phased implementation checklist.
5) `integration_notes.md` — How to integrate with arg_digest, dep_digest, and MolSysMT.

## Scope
These documents track the evolving implementation. The authoritative checkpoint
for v0.10 decisions is `SPEC_SMONITOR.md` (section v0.2 Draft).

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
- Ecosystem integration completed (MolSysMT, ArgDigest, DepDigest, PyUnitWizard).
