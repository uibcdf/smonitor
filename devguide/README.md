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
9) `discovery_and_adoption_strategy.md` — Strategy to maximize third-party discovery and adoption (humans + agents).
10) `collective_evidence_pack.md` — Cross-repo evidence handoff for collective 1.0 closure.

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
- Signal profiling now carries optional structured frame context and tag-aware timing summaries in reports/timeline, plus opt-in slow-signal events for QA/developer workflows.
- Human-readable handlers now apply profile-aware truncation to large structured payload fragments.
- Local bundle export (CLI + event buffer).
- Test suite expanded with sensitive-path coverage for manager/policy/handlers/CLI.
- Ecosystem integration completed (MolSysMT, MolSysViewer, ArgDigest, DepDigest, PyUnitWizard).
- Shared collective E2E module added: `tests/e2e/test_collective_error_path.py` (cross-repo error-path baseline).
- Documentation architecture migrated to MyST with role-based routes:
  integrators, end users, showcase scenarios, and contributor path.
- Standards pack published for ecosystem adoption (`standards/`), including
  end-user rescue/docs templates and sync policy.
- Version `0.11.4` released as pre-1.0 stabilization checkpoint.
- Current quality snapshot (2026-03-04): remote CI green, full pytest suite green, line coverage ~98% and branch-rate ~95%.

## Operational Stabilization Plan (Toward 1.0.0)
1. Extended stabilization window (until diagnostic operability closure): only bugfixes, hardening, docs/test corrections, and pre-1.0 diagnostic operability work explicitly tracked in `implementation_plan.md`.
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
   - ecosystem smoke checks validated,
   - diagnostic operability plan below implemented and validated in at least one real cross-library workflow.

## Remaining Focus (Pre-1.0)
- Keep coverage >=90% while prioritizing correctness/contract stability over percentage gains.
- Keep branch-rate >=92% in CI as stabilization floor.
- Final consistency sweep across `README`, `SPEC`, `devguide`, and Sphinx docs.
- Complete the pre-1.0 diagnostic operability plan:
  - validate the now-complete operability stack together in at least one real support/CI workflow,
  - keep docs/standards/user guides synchronized while the feature set stabilizes.
- Post-1.0 roadmap preparation: opt-in telemetry client and Sentinel integration.

## Version 1.0 Emphasis
- Operational stability and compatibility are release blockers.
- Adoption/discovery execution is tracked in `implementation_plan.md` under:
  `1.0.0 Adoption & Discovery Plan`.

## Stabilization closure checklist

Pre-`1.0.0` stabilization should only be considered closed when all of the following are true:

1. `main` is clean and internally consistent.
   - no relevant pending core changes;
   - `README`, `docs`, `devguide`, and `standards` are synchronized.
2. Full local validation remains green.
   - `ruff check .`
   - `PYTHONPATH=. pytest -q`
   - `PYTHONPATH=. pytest -q --cov-config=.coveragerc --cov=smonitor --cov-report=term --cov-report=xml`
3. Remote CI is green in a sustained way.
   - several consecutive successful runs on the main workflows;
   - no new flaky failures in primary gates.
4. No open high-severity bugs remain in SMonitor.
   - nothing breaking public contracts, bundles, profiles, CLI, or support/triage flows.
5. Operability is confirmed in at least one real workflow.
   - a real CI/support flow demonstrates value from fingerprints, runtime identifiers, triage summaries, bundle comparison, and dual human/agent output.
6. No further API changes are clearly required.
   - no missing canonical fields;
   - no public signatures that need redesign before freeze.
7. A short observation period passes without structural friction.
   - real usage does not reveal new design-level issues.

## Next-session checkpoint
- The current pre-1.0 profiling/diagnostics checkpoint includes: structured `extra_factory` signal context, `timings_by_tag`, opt-in slow-signal events, and profile-aware truncation in human-readable handlers.
- Integration helpers now include a canonical `context_extra(...)` builder for common structured diagnostic fields.
- `report()` and bundle exports now expose triage-oriented summaries for event codes, categories, and recent slow-signal activity.
- Optional coalescing for repeated transient warnings is now available via `warning_coalesce_window_s`.
- Machine-oriented JSON output now includes a normalized payload section for stable cross-library QA ingestion.
- Retry and causal metadata now have canonical fields in `context_extra(...)`, normalized JSON output, and coalesced warning summary events.
- The current pre-1.0 focus is no longer only observation: it is to complete the diagnostic operability plan before `1.0.0` so SMonitor feels decisively useful for developers, QAs, users, and automation agents.
- Runtime identifiers are now explicit and tested: managers generate stable opaque `run_id` and `session_id` values by default, allow explicit overrides, and expose them for bundle/report correlation workflows.
- Incident classification and decision metadata are now canonical in `context_extra(...)` and promoted through normalized JSON payloads.
- Structured `evidence` is now first-class in canonical payloads for support and CI triage.
- Duplicate-policy noise reduction is now available by incident fingerprint via `duplicate_policy`.
- Local bundle comparison is now available through `compare_bundles(...)` and `smonitor compare ...`, including new/disappeared/recurrent fingerprint summaries and count deltas.
- Events and JSON exports now carry an explicit `human_summary` block alongside the normalized machine payload so support handoff stays readable without weakening agent determinism.
- Full local operational validation has been rerun after these additions and is green:
  - `ruff check .`
  - `PYTHONPATH=. pytest -q`
  - `PYTHONPATH=. pytest -q --cov-config=.coveragerc --cov=smonitor --cov-report=term --cov-report=xml`
