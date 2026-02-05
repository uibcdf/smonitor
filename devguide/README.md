# smonitor Developer Guide

This folder collects the initial developer documentation for `smonitor`.

## Recommended Reading Order
1) `architecture.md` — High-level architecture and goals.
2) `event_model.md` — The event schema and handler contract.
3) `api.md` — Public API sketch and expected behavior.
4) `implementation_plan.md` — Phased implementation checklist.
5) `integration_notes.md` — How to integrate with arg_digest, dep_digest, and MolSysMT.

## Scope
These documents define the initial plan and interfaces. They are not a finalized specification and may evolve as implementation starts.
The authoritative checkpoint for v0.2 decisions is `SPEC_SMONITOR.md` (section v0.2 Draft).

## Current Status (Checkpoint)
- Core scaffold, manager/context, and `@signal` implemented.
- Emitters for warnings/logging/exceptions implemented (initial).
- Policy engine core implemented (routing/filtering with rate limit stub).
- Console/file/json handlers implemented (plain) + optional rich handler.
- Config discovery + merging implemented for `_smonitor.py`.
- Sphinx docs scaffold + config/policy/integration stubs added.
- CLI added for report/validate and env var support.
- Event schema validation (dev/qa) added.
- CODES templating and SIGNALS soft enforcement added.
- Catalog generation utilities added for docs.
- Profiling expanded (timeline, sampling, spans, export).
