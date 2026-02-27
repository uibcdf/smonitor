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
- Add deterministic triage examples keyed by stable contracts (`code` + context signature). **Done**
- Add redaction policy examples for bundle sharing in automated pipelines. **Done**
- Add a compact "agent-ready checklist" to release gates. **Done**

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
1. Add release-gate CI checks for package build/install smoke + docs build. **Done**
2. Add explicit public API contract tests (top-level exports + integrations API). **Done**
3. Add agent-profile payload contract tests and snapshot fixtures. **In Progress**
4. Add a short operational runbook in docs for weekly maintenance loops. **Done**

## 1.0.0 Operational Checklist

1. Stabilization window
- Duration: 2-4 weeks on top of `0.11.x`.
- Scope: bugfixes, hardening, tests/docs consistency only.
- Status: **Active** (started 2026-02-27).

2. Weekly control loop
- Check CI health for SMonitor and integrated ecosystem libraries.
- Review repeated warning/error codes and incident trends.
- Review support bundles for reproducibility quality.

3. PR acceptance rules
- `pytest` passes.
- `make -C docs html` passes.
- QA CI smoke passes (`sdist`/`wheel` build + wheel install + CLI smoke).
- No breaking public API change unless explicitly approved for post-1.0.

4. Release-candidate freeze
- Freeze public export surface.
- Freeze semantics of published diagnostic codes/signals.
- Update release notes with any contract-relevant change.

5. Exit criteria for 1.0.0
- No open high-severity defects in SMonitor.
- CI stable across supported matrix for a sustained period.
- Ecosystem smoke validations completed.

## 1.0.0 Adoption & Discovery Plan

1. Ecosystem visibility
- Add a visible “Diagnostics powered by SMonitor” section in sibling libraries:
  MolSysMT, MolSysViewer, ArgDigest, DepDigest, and PyUnitWizard.

2. Proof by examples
- Publish short “before vs after” examples showing clearer user guidance and
  improved developer diagnostics.

3. Fast onboarding
- Keep a “5-minute integration” path as the main entry point in docs.

4. Packaging discoverability
- Improve project metadata (PyPI/conda/readme keywords and summary) focused on
  diagnostics, warnings, telemetry, and scientific Python.

5. Communication
- Announce releases and integration outcomes in project channels
  (GitHub discussions + lab communication channels).

6. Default adoption in new projects
- Require `_smonitor.py` + catalog wiring in all new ecosystem packages.

7. Trust through stability
- Keep CI status, coverage trend, and release notes visible and updated.

8. Reusable integration kit
- Maintain and promote `standards/SMONITOR_GUIDE.md` and standards templates as
  the official copy/adapt toolkit for third-party adopters.

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

## Post-1.0 Roadmap (towards 2.0)

### Project A — Pytest/CI Diagnostic Integration

Goal:
- enrich test-failure triage in local runs and CI without replacing native pytest output.

Scope:
- pytest plugin/hooks to emit SMonitor events on failed tests;
- stable triage keys (`code` + context signature);
- terminal summary section for grouped failures and actionable hints;
- optional JUnit enrichment (`user_properties`) for CI tooling;
- bundle export on failed CI jobs for reproducible support/triage.

Constraints:
- low-noise defaults (emit on failures, not on passing tests);
- explicit redaction policy for exported diagnostics artifacts;
- maintain compatibility with current pytest workflows.

Target window:
- start after 1.0.0 stabilization;
- mature before 2.0.0 as the default CI triage path.

Implementation design (agreed baseline):

Objective:
- keep pytest as the primary failure source;
- add an SMonitor layer for reproducible CI triage with stable keys.

How it should work:
1. pytest runs normally and keeps its native report.
2. a pytest plugin/hook emits SMonitor events only for failures.
3. at end of run, export a bundle (`bundle.json` + `events.jsonl`).
4. CI uploads that bundle as an artifact.
5. automated/human triage groups incidents by `code` + context signature.

Per-failure event payload:
- `level`: `ERROR`
- `code`: for example `TEST-FAIL-ASSERT`, `TEST-FAIL-EXC`, `TEST-FAIL-TIMEOUT`
- `source`: `tests.path::test_name`
- `message`: short normalized failure summary
- `extra`:
  - `nodeid`
  - `exception_type`
  - `assert_excerpt` (truncated)
  - `phase` (`setup`/`call`/`teardown`)
  - `duration`
- `context`:
  - `python_version`
  - `platform`
  - `git_sha`
  - `workflow`/`job` (in CI)

Deterministic grouping key:
- compute hash from:
  - `code`
  - normalized `source`
  - `exception_type`
  - normalized first failure line
- result stored as stable `triage_key` across runs.

Pytest technical integration:
- primary hook: `pytest_runtest_makereport`
  - when `report.failed` in relevant phase, emit event.
- end hook: `pytest_sessionfinish`
  - emit aggregate summary (`passed`/`failed`/`skipped`, top codes).
- optional bootstrap fixture/session setup for `smonitor.configure(profile="qa")`.

Recommended configuration:
- activate only in CI or behind flag:
  - `SMONITOR_TEST_REPORT=1`
- profile policy:
  - `qa` in CI
  - optional `dev` locally
- event buffer baseline:
  - `event_buffer_size` around `1000`.

CI pipeline expectations:
1. run pytest with plugin enabled.
2. always export bundle at end (even when pytest fails).
3. apply default redaction policy:
  - `--redact extra.local_path`
  - `--redact extra.env`
  - `--drop-context` for sensitive environments.
4. upload diagnostics artifact.

Phasing:
- Phase 1 (MVP):
  - capture failed tests (`call.failed`) only
  - 2-3 failure codes
  - bundle export + CI artifact
  - no complex traceback parsing.
- Phase 2:
  - better failure classifier (`assert`, `import`, `dependency`, `timeout`)
  - stronger `triage_key`
  - automatic markdown summary for PR/checks.
- Phase 3:
  - cross-run diff (new vs recurrent incidents)
  - prioritization rules by severity/frequency.

Useful pytest output channels:
1. `pytest_runtest_logreport` + `terminalreporter`
  - print short per-failure SMonitor line (`code`, `hint`, `triage_key`, bundle path).
2. `pytest_terminal_summary`
  - append `SMonitor Triage Summary` with top codes, groups by `triage_key`, frequent hints.
3. test report metadata (`user_properties`)
  - store `smonitor_code`, `triage_key`, etc. for JUnit/CI consumers.

Output design recommendation:
- per-test output minimal (single extra line on failure);
- final summary rich in `terminal_summary`;
- verbosity controlled by `--smonitor-report=off|minimal|full` and profile policy.

### Project B — HTML Diagnostics Support

Goal:
- provide a user-facing, readable diagnostics report (local and CI artifacts).

Scope:
- static HTML report generated from bundles/events;
- sections for summary, grouped incidents, warnings/errors timeline, and actionable hints;
- links between stable codes/signals and contract-aware guidance;
- run-to-run comparison view (incremental phase).

Extension path:
- optional remote web service (sentinel-style) for team-level aggregation and support workflows, opt-in and privacy-first.

Constraints:
- local-first operation must remain fully functional offline;
- remote mode must enforce redaction, access control, and retention policy.

Target window:
- static report MVP after 1.0.0;
- optional hosted aggregation considered on the path to 2.0.0.

Implementation design (agreed baseline):

Phase 1 — Immediate static local HTML (no server):
- generate `smonitor_report.html` at end of test/diagnostics execution.
- minimum report content:
  - global summary (`failed`/`warn`/`error`);
  - incidents table (`code`, `source`, `hint`, `triage_key`);
  - recurrence grouping;
  - links to traceback/context sections.
- usage model:
  - local: open file directly;
  - CI: upload as artifact.

Phase 2 — Navigable report with short history:
- keep per-run snapshots under `reports/<timestamp>/`.
- provide an index HTML with comparison:
  - current run vs previous run.
- use for regression/recurrence visibility between runs.

Phase 3 — Optional remote web service (sentinel-style):
- backend ingests bundles (opt-in only).
- team UI provides filters by `code`, version, and environment.
- include guided diagnostics interpretation and remediation playbooks.
- enforce privacy requirements:
  - redaction,
  - retention rules,
  - access control.

Architecture decision:
- local-first by default (always exportable and useful offline).
- remote server remains an optional layer for teams needing centralization.

MVP command-line target:
- add command in the spirit of:
  - `smonitor report --from smonitor_bundle --html out/report.html`
- same data source for local and CI workflows.
- keep implementation lightweight (simple template + minimal JavaScript, no heavy frontend stack).

## Milestones
- M1: Core MVP and a single console handler.
- M2: Warnings + logging emitters.
- M3: JSON/file handlers + integration hooks.
- M4: Documentation and polished UX.
