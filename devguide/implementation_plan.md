# smonitor Developer Guide — Implementation Plan

## Phase 0 — Scaffold
- Create package layout: `core/`, `emitters/`, `handlers/`, `config/`.
- Add empty `__init__.py` in each subpackage.
- Add a small `__version__` and `__all__` definition in the top-level package.
- Add `policy/` package for policy engine.
Status: **Done** (structure + package scaffold committed)

## Phase 1 — Core MVP
- Implement `core.context` with contextvars:
  - `push_frame(frame)`
  - `pop_frame()`
  - `get_context()`
- Implement `core.manager`:
  - singleton via module-level instance
  - `configure(...)`
  - `emit(event)`
  - `add_handler(handler)` / `remove_handler(handler)`
- Add profile support in manager (`profile`, `style`) with runtime override.
- Implement `core.decorator`:
  - `@signal` that wraps functions
  - ensures push/pop
  - on exception: emit error event and re-raise
Status: **Done** (core context, manager, @signal; args_summary flag added)

## Phase 2 — Emitters
- `emitters.warn`:
  - wrap `warnings.showwarning`
  - turn warnings into events
- `emitters.log`:
  - implement a `logging.Handler` that forwards logs
  - optionally `LoggerAdapter` with extra context
- `emitters.error`:
  - optional `sys.excepthook` integration
- Implement policy engine (routing/filtering/transforms) and integrate before handler dispatch.
- Add `_smonitor.py` discovery in `config.discovery`.
Status: **Done (initial)** (warnings/logging/exceptions emitters; policy engine core; discovery stub; logging captureWarnings integration)

## Phase 3 — Handlers
- `handlers.console`:
  - Rich output (optional dependency)
  - fallback plain formatting
- `handlers.file`:
  - text logs with timestamps
- `handlers.json`:
  - JSON lines for telemetry
- Ensure handlers honor active `profile` for formatting.
Status: **Done** (console/file/json implemented; rich handler optional; memory handler added)

## Phase 4 — Integration
- Add `@signal` to `arg_digest` and `dep_digest` entrypoints.
- Add `_smonitor.py` in MolSysMT root for hints and formatting.
- Replace MolSysMT logging setup with `smonitor.configure`.
- Update to `_smonitor.py` naming and profile-based output controls.
Status: **Done** (integration helpers + adoption across MolSysMT, ArgDigest, DepDigest, PyUnitWizard)

## Phase 5 — Docs & Examples
- Document the event model.
- Provide examples for warning interception and custom handlers.
- Add a cookbook for context chain visualization.
- Document `_smonitor.py` schema, policy engine, and communication styles by profile.
Status: **Done** (MyST docs migrated; role-based user routes, showcase scenarios, and standards-based adoption guides completed)

## Additional Hardening
- Add CLI for validation/reporting and profile selection.
- Add environment variable support.
Status: **Done** (CLI + env config added)

## Additional QA
- Add event schema validation in dev/qa profiles.
- Add optional strict SIGNALS enforcement.
Status: **Done**

## Plan to 0.10 (Stable)

**H1 — Ecosystem integration (minimum)** (Done)
- MolSysMT, ArgDigest, DepDigest, PyUnitWizard integrated.

**H2 — Emitter hardening**
- Prevent duplicate emissions (warnings/logging).
- Guard against handler feedback loops.

**H3 — Handler UX** (Done)
- Rich console formatting finalized for user/dev/qa (Exceptional visual style implemented).
- File/JSON outputs stabilized.
- Memory handler added.

**H4 — Documentation**
- User guide with real examples.
- Developer guide for CODES/SIGNALS.
- Troubleshooting section.

**H5 — Release**
- Versioning, conda build, docs publish.

## 0.10 Status
- Feature complete; hardening and docs polish remain before 0.10.0 finalization.

## 0.11 Plan (Pre-1.0 Stabilization)
- Align all docs (`README`, `SPEC`, `devguide`, Sphinx pages) with actual behavior.
- Validate release gates in clean environments:
  - `pytest`
  - docs build (`make -C docs html`)
  - package build and CLI smoke checks
- Freeze and document public API surface (and keep internals private-by-default).
- Add API contract tests for exported symbols and core behavior.
- Run integration smoke checks in ecosystem repositories.
Status: **In Progress**

Progress checkpoint:
- docs/routes largely stabilized and aligned with runtime behavior,
- integrator guidance expanded (handlers, advanced integration API, AI-agent workflow),
- end-user rescue flow and adoption templates published.
- QA CI now includes package artifact build (`sdist`/`wheel`) and wheel install + CLI smoke checks.
- Agent-profile contract tests added for template resolution and machine-oriented handler payloads.

## AI-Agent Readiness Plan (Integrator-Facing)

Done:
- `agent` profile documented and available in user docs.
- Bundles/events provide machine-readable inputs for triage pipelines.
- Standards include integration contract and end-user support artifacts.

Pending hardening before 1.0:
- Add explicit contract tests for machine-readability in `agent` profile outputs.
- Add deterministic triage examples keyed by `code` + `trace_hash`.
- Add redaction policy examples for bundle sharing in automated pipelines.
- Add a compact "agent-ready checklist" to release gates.

## Profiling (Developer Utility)
- Timeline buffer and sampling.
- Spans for manual blocks.
- Export to JSON/CSV.
Status: **Done**

## Future: Telemetry & Sentinel (Post‑0.10)
- Phase A: Local export bundles (privacy‑first). **Done**
- Phase B: Opt‑in telemetry client with rate limits.
- Phase C: Sentinel server + public dashboard.
- Phase D: LLM triage on aggregated reports.

## Next Concrete Steps
1. Add release-gate CI checks for package build/install smoke + docs build.
2. Add explicit public API contract tests (top-level exports + integrations API).
3. Add agent-profile payload contract tests and snapshot fixtures.
4. Add a short operational runbook in docs for weekly maintenance loops.

## Future: Project Metadata (Post‑0.10)
- Load `doc_url`, `issues_url`, `api_url` from `pyproject.toml` under `[tool.smonitor]`.
- Inject metadata into emitted events for consistent user hints.

## Future: smonitor ↔ smonitor-sentinel UX
- User opt‑in with clear consent.
- Local‑first bundles for manual sharing.
- Public health dashboard by library/version.
- Developer workflow: codes → docs → fixes.

## Future: AI Support & Repair (Post‑0.10)
- Structured outputs (CODES/SIGNALS, bundles) for agents.
- Triage + dedup pipelines based on `code` and `trace_hash`.
- Suggested fixes with human approval.

## Milestones
- M1: Core MVP and a single console handler.
- M2: Warnings + logging emitters.
- M3: JSON/file handlers + integration hooks.
- M4: Documentation and polished UX.
