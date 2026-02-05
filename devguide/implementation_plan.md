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
Status: **Partial** (console/file/json implemented; rich handler added as optional)

## Phase 4 — Integration
- Add `@signal` to `arg_digest` and `dep_digest` entrypoints.
- Add `_smonitor.py` in MolSysMT root for hints and formatting.
- Replace MolSysMT logging setup with `smonitor.configure`.
- Update to `_smonitor.py` naming and profile-based output controls.
Status: **Started** (integration helpers added in `smonitor.integrations`; real adoption pending)

## Phase 5 — Docs & Examples
- Document the event model.
- Provide examples for warning interception and custom handlers.
- Add a cookbook for context chain visualization.
- Document `_smonitor.py` schema, policy engine, and communication styles by profile.
Status: **Partial** (Sphinx scaffold + config/policy/integration/docs/examples; catalog generator added)

## Additional Hardening
- Add CLI for validation/reporting and profile selection.
- Add environment variable support.
Status: **Done** (CLI + env config added)

## Additional QA
- Add event schema validation in dev/qa profiles.
- Add optional strict SIGNALS enforcement.
Status: **Done**

## Plan to 1.0 (Stable)

**H1 — Ecosystem integration (minimum)**
- Integrate with MolSysMT (replace logging setup with smonitor.configure).
- Integrate with ArgDigest or DepDigest (add @signal, emit codes).

**H2 — Emitter hardening**
- Prevent duplicate emissions (warnings/logging).
- Guard against handler feedback loops.

**H3 — Handler UX**
- Rich console formatting finalized for user/dev/qa.
- File/JSON outputs stabilized.

**H4 — Documentation**
- User guide with real examples.
- Developer guide for CODES/SIGNALS.
- Troubleshooting section.

**H5 — Release**
- Versioning, conda build, docs publish.

## Profiling (Developer Utility)
- Timeline buffer and sampling.
- Spans for manual blocks.
- Export to JSON/CSV.
Status: **Done**

## Milestones
- M1: Core MVP and a single console handler.
- M2: Warnings + logging emitters.
- M3: JSON/file handlers + integration hooks.
- M4: Documentation and polished UX.
