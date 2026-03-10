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
- shared collective E2E module added in `tests/e2e/test_collective_error_path.py` and validated locally.

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
- Latest snapshot (2026-03-04): CI green, pytest green, line coverage ~98%, branch-rate ~95%.
- CI stabilization gate: enforce branch-rate floor at 0.92 on the main CI workflow.

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

## Futurist Backlog (Agent-First + Scientific Libraries)

The following 25 ideas are recorded for strategic planning beyond current
stabilization work.

### A. Advanced diagnostics and ecosystem foresight (10)

1. `Contract Drift Radar`
- detect behavior drift by diagnostics patterns across versions/environments.

2. `Repro Packs Deterministic`
- export minimal, reproducible run packs (env + seed + synthetic inputs).

3. `Diagnostics Policy-as-Code`
- versioned, testable, auditable policy profiles per context (CI/user/HPC).

4. `Semantic Incident Fingerprints`
- robust grouping resilient to message/stack textual variability.

5. `Auto-Playbooks by Code`
- standardized remediation flows per diagnostic code.

6. `Dependency Early-Warning`
- correlate incident spikes with dependency/version changes.

7. `Experiment Observability Bridge`
- diagnostics tied to scientific workflow units (notebooks/pipelines/runs).

8. `Human+Agent Co-Debug Protocol`
- explicit collaboration trace for agent proposals and human decisions.

9. `Privacy Grades`
- formal export classes (`internal`, `external`, `public`) with verifiable redaction.

10. `Dynamic Quality Gates`
- release gates adapting to incident risk signals and recurrence trends.

### B. Agent-native automation and autonomy roadmap (15)

11. `Agent Intent Channel`
- runtime intent declaration (`explore`, `optimize`, `repair`) to tune diagnostics.

12. `Machine-Action Hints`
- structured action directives (`try_command`, `rerun_test`, `open_doc`, `edit_file`).

13. `Fix Verification Contracts`
- mandatory evidence checks before accepting automated patches.

14. `Agent Memory Bridge`
- privacy-aware short/medium-term memory of incidents, fixes, and outcomes.

15. `Counterfactual Diagnostics`
- expected-outcome modeling for candidate fixes ("if X, then Y should clear").

16. `Cost-Aware Triage`
- optimization by CI/runtime cost, regression risk, and user impact.

17. `Multi-Agent Coordination Protocol`
- role-separated triage/patch/review handoff with explicit contracts.

18. `Confidence Scoring`
- confidence + evidence scoring for each diagnosis and suggested action.

19. `Synthetic Failure Injection`
- contract-driven failure generation to train and validate repair agents.

20. `Autonomous Canary Mode`
- pre-release autonomous scenario runs with regression thresholds.

21. `Doc Sync Guardian`
- automatic doc-contract drift detection and update enforcement.

22. `Runtime Negotiation API`
- capability negotiation between library and agent (strictness/privacy/profiling).

23. `Trust Ledger`
- historical quality ledger of agent proposals and human acceptance outcomes.

24. `Incident Graph`
- causal graph linking codes/signals/dependencies for root-cause prioritization.

25. `Policy Sandbox for Agents`
- safe simulation environment for agent diagnostic strategies before real execution.

## Execution Plan (Proposed)

Objective:
- move from ideas to validated impact with a focused subset of high-leverage initiatives.

Selected bets (first wave):
1. `Machine-Action Hints`
2. `Fix Verification Contracts`
3. `Semantic Incident Fingerprints`
4. `Doc Sync Guardian`
5. `Autonomous Canary Mode` (scoped MVP)

### Phase A — Foundation (post-1.0.0, short term)

Scope:
- define machine-action hint schema and contract versioning;
- define verification contract schema for automated fixes;
- define incident fingerprint v1 algorithm and stability constraints.

Deliverables:
- schema docs + examples;
- initial API/contracts in SMonitor;
- baseline tests for payload compatibility.

Success criteria:
- contracts are stable and test-covered;
- no regression in current user/developer diagnostics UX.

### Phase B — CI and Workflow Integration

Scope:
- integrate hints + verification contracts into pytest/CI diagnostics flow;
- add doc drift checks tied to diagnostics contract changes;
- expose fingerprint grouping in CLI/report outputs.

Deliverables:
- CI-ready triage summaries using stable fingerprints;
- PR/release checks for documentation drift;
- actionable hint output in machine-readable form.

Success criteria:
- reduced triage time for repeated incidents;
- reduced false-positive grouping noise across runs;
- documentation drift caught before merge.

### Phase C — Controlled Autonomy

Scope:
- introduce Autonomous Canary Mode for pre-release scenarios only;
- enforce verification contracts before any patch recommendation is considered valid;
- require explicit human approval for merge/release decisions.

Deliverables:
- canary scenario runner with thresholds;
- evidence-driven pass/fail gates;
- audit trace for agent suggestion -> verification -> human decision.

Success criteria:
- earlier detection of release regressions;
- measurable reduction of failed release candidates;
- zero unverified autonomous changes merged.

### Phase D — Adoption and Hardening (towards 2.0)

Scope:
- roll out selected capabilities across integrated ecosystem libraries;
- collect quality metrics and tune policies by context (CI, local dev, support);
- finalize 2.0 readiness based on operational evidence.

Deliverables:
- integration playbooks per library;
- dashboard/summary metrics for triage and verification quality;
- hardening pass on privacy/redaction defaults.

Success criteria:
- repeated-incident handling becomes deterministic and faster;
- agent suggestions show stable acceptance quality;
- maintainers report lower support/triage burden.

## Operating Rules for This Plan

1. Keep local-first behavior as default; remote/centralized features remain opt-in.
2. Preserve human ownership of merge/release decisions.
3. Version every machine-facing contract and test compatibility continuously.
4. Ship thin vertical slices; avoid large speculative implementations.

## Milestones
- M1: Core MVP and a single console handler.
- M2: Warnings + logging emitters.
- M3: JSON/file handlers + integration hooks.
- M4: Documentation and polished UX.

## 1.0.x Diagnostic Operability Addendum
- Add structured `extra_factory` support to `@signal` for low-friction QA/developer context on profiled calls. **Implemented**
- Surface `tags` in timeline exports and add `timings_by_tag` to `report()`. **Implemented**
- Evaluate slow-call threshold events as an opt-in pre-1.0/1.0.x feature. **Implemented (opt-in core support added)**


## 1.0.x Slow-signal event checkpoint

The profiling layer now supports opt-in slow-signal events via `slow_signal_ms` and `slow_signal_level`.

- Slow-signal events are disabled by default.
- When enabled, `@signal` measures call duration even if sampling-based profiling is disabled.
- Calls crossing the threshold emit `SMONITOR-SIGNAL-SLOW` with structured payload including duration, threshold, tags, and user-supplied `extra_factory` context.
- This is intended for developer and QA workflows rather than default user-facing output.

## 1.0.x Human-readable payload truncation checkpoint

Human-readable handlers now apply profile-aware truncation to large structured payload fragments.

- `console` and `file` handlers truncate oversized structured values for `qa`, `dev`, and `debug` profiles.
- Machine-oriented payloads remain unchanged in the routed event and JSON handler output.
- The goal is to keep QA and developer output actionable without flooding terminals or log lines.

## Immediate next implementation slices (checkpoint)

The current recommended execution order for the next sessions is:

1. Add optional coalescing for repeated transient warnings.
   - Goal: reduce retry noise while preserving total attempt count and final failure reason.
   - Expected output: opt-in policy/config support and regression tests.

2. Reassess machine-oriented output normalization after the coalescing slice lands.
   - Goal: decide whether explicit normalized fields are needed for cross-library QA automation.
   - Expected output: either a minimal normalized machine payload contract or an explicit decision to keep current JSON/event structure unchanged.

This order is the active checkpoint for the next development sessions unless a higher-priority regression appears.


## 1.0.x Structured context helper checkpoint

SMonitor now exposes `integrations.context_extra(...)` for common structured diagnostic fields (`caller`, `form`, `requested_attribute`, `resource`, `provider`, `operation`).

- The helper is intended to reduce repeated local payload assembly across MolSysSuite libraries.
- Additional helper expansion should remain conservative and keyword-only to preserve payload stability.


## 1.0.x Bundle/report triage summary checkpoint

SMonitor now exposes triage-oriented summaries in `report()` and bundle exports.

- `report()` includes counts by event code and category.
- `report()` includes a compact `slow_signals_recent` list for the most recent slow-signal events.
- `collect_bundle()` mirrors those fields under `triage` so QA can inspect summarized artifacts without reading raw event streams first.


## 1.0.x Warning coalescing checkpoint

SMonitor now supports opt-in coalescing of repeated transient warnings via `warning_coalesce_window_s`.

- The first warning in a coalescing window is emitted normally.
- Repeated matching warnings inside the window are suppressed from handlers and event buffering.
- Suppressed duplicates are tracked in `report()["coalesced_warnings"]` and mirrored in bundle triage output.
- Finalized coalescing windows also emit `SMONITOR-WARNING-COALESCED` summary events so CI/event streams keep the aggregate retry outcome.


## 1.0.x Machine-output normalization checkpoint

SMonitor now exposes a normalized machine-oriented payload in JSON handler output.

- The `normalized` section contains stable core fields and selected structured-context keys.
- Canonical retry/causal keys are now reserved in `context_extra(...)` and promoted into `normalized` output for cross-library QA ingestion.
- This is intended to simplify cross-library QA ingestion without changing the underlying event schema.
- Further normalization should remain incremental and backward compatible.


## Pre-1.0 Diagnostic Operability Completion Plan

Goal:
- turn SMonitor into a clearly superior diagnostic/triage layer before `1.0.0`;
- make repeated incidents easier to group, compare, prioritize, and hand off;
- reduce log noise without losing decision-grade information;
- keep all additions backward compatible and local-first by default.

Constraint:
- no public contract breakage in existing event fields;
- additions should be additive, opt-in where appropriate, and covered by API/contract tests.

### Slice 1 — Stable incident fingerprints [implemented]

Scope:
- add a deterministic `fingerprint` field for emitted events and normalized payloads;
- base it on stable contracts only:
  - `code`
  - `source`
  - `exception_type`
  - selected normalized extra fields
- expose fingerprint counts in `report()` and bundle triage.

Deliverables:
- fingerprint helper in core;
- `fingerprint` in routed event / JSON normalized payload;
- `events_by_fingerprint` in `report()` and bundle `triage`;
- tests for determinism and grouping behavior.

Success criteria:
- repeated incidents can be grouped without custom downstream logic;
- fingerprint stays stable across runs for semantically identical incidents.

### Slice 2 — Run/session/correlation identifiers [implemented]

Scope:
- add canonical identifiers for reproducibility:
  - `run_id`
  - `session_id`
  - `correlation_id`
- allow explicit injection and safe defaults;
- preserve local-first behavior.

Deliverables:
- manager/session-level identifiers;
- event propagation for correlation metadata;
- bundle metadata including run/session identifiers;
- tests covering explicit IDs and default generation.

Success criteria:
- QA can reconstruct which events belong to the same run/session/operation;
- bundles become easier to compare and hand off.

### Slice 3 — Incident classification and decision metadata [implemented]

Scope:
- add additive machine-oriented fields for decision support:
  - `incident_kind`
  - `severity`
  - `priority`
  - `diagnostic_confidence`
  - `recommended_action`
  - `next_step`
  - `retryable`
  - `support_needed`
- keep existing `level` semantics unchanged.

Deliverables:
- canonical helper support (`context_extra(...)` or equivalent additive path);
- normalized JSON promotion of those fields;
- contract tests for stable serialization.

Success criteria:
- users and agents can distinguish “what happened” from “what to do next”;
- triage can prioritize incidents without parsing prose hints.

### Slice 4 — Evidence-first payload structure [implemented]

Scope:
- add canonical `evidence` support for compact observed/expected/resource facts;
- define a conservative shape suitable for support and CI triage.

Deliverables:
- event payload convention for `evidence`;
- normalized JSON inclusion;
- docs/tests/examples showing minimal and rich evidence payloads.

Success criteria:
- support bundles capture decision-grade evidence without ad hoc key sprawl;
- handlers can present short evidence summaries without losing raw structure.

### Slice 5 — Stronger noise-reduction policies [implemented]

Scope:
- generalize beyond current warning coalescing toward policy-driven duplicate handling;
- support additive policies such as:
  - `emit_first`
  - `emit_last`
  - `emit_summary`
  - `emit_every_n`
- keep the current warning coalescing behavior backward compatible.

Deliverables:
- policy/config design for duplicate handling;
- summary-event strategy compatible with bundles and reports;
- regression tests for high-noise retry loops.

Success criteria:
- noisy workflows remain readable;
- aggregate information remains preserved and machine-usable.

### Slice 6 — Operational report improvements [implemented]

Scope:
- make `report()` immediately useful as an action surface;
- add:
  - top codes
  - top sources
  - top fingerprints
  - most noisy resources
  - most expensive tags/sources
  - blocking/actionable/recurrent summaries

Deliverables:
- additive `report()` sections;
- mirrored bundle triage sections;
- tests for ranking and summary determinism.

Success criteria:
- a maintainer can decide what to inspect first without scanning raw events;
- agents can consume ranked incident summaries directly.

### Slice 7 — Bundle comparison workflow [implemented]

Scope:
- add a first local diff workflow for support and CI:
  - compare two bundles
  - show new/disappeared/recurrent fingerprints
  - show count deltas and slow-signal deltas

Deliverables:
- initial local comparison API/CLI surface;
- Markdown/text summary suitable for issue/PR comments;
- tests for stable diff semantics.

Success criteria:
- repeated regressions become visible immediately;
- support handoff can answer “what changed?” reproducibly.

### Slice 8 — Human/agent dual-output hardening [implemented]

Scope:
- keep profile-based behavior, but harden the explicit separation between:
  - human-facing concise summaries
  - agent-facing machine payloads
- evaluate whether to expose a stable `human_summary` block without changing core event semantics.

Deliverables:
- docs + tests for dual-output expectations;
- optional additive summary field if needed.

Success criteria:
- handlers stay readable for humans while JSON/bundles stay deterministic for agents.

## Recommended execution order before 1.0.0

1. Stable incident fingerprints
2. Run/session/correlation identifiers
3. Incident classification and decision metadata
4. Evidence-first payload structure
5. Operational report improvements
6. Stronger noise-reduction policies
7. Bundle comparison workflow
8. Human/agent dual-output hardening

Status on 2026-03-10:
- slices 1-8 are implemented and covered by targeted tests;
- docs, standards, and Sphinx user docs have been refreshed for the new dual human/agent contract;
- remaining pre-`1.0.0` work is validation in real CI/support workflows, not new operability scope.
- full local operational validation was rerun after the slice-8 landing and is green:
  - `ruff check .`
  - `PYTHONPATH=. pytest -q`
  - `PYTHONPATH=. pytest -q --cov-config=.coveragerc --cov=smonitor --cov-report=term --cov-report=xml`

Future design note:
- `smonitor/integrations/core.py` currently acts as a contract kernel for canonical structured payloads.
- its branch count is acceptable as long as those branches keep encoding explicit contract rules rather than ad hoc behavior.
- after `1.0.0`, revisit internal decomposition only if real maintenance pain appears; until then, prefer small changes, contract tests, and synchronized docs for every semantic change.

Reasoning:
- slices 1-4 define the machine contract;
- slices 5-7 define the operator workflow;
- slice 8 consolidates UX without destabilizing the contract layer early.

## Revised 1.0.0 exit criteria

`1.0.0` should not be cut until all conditions below are true:

1. core/test/CI stability criteria remain satisfied;
2. existing public contracts remain backward compatible;
3. slices 1-6 are implemented and covered by tests;
4. at least an initial bundle comparison workflow exists;
5. at least one cross-library diagnostic workflow validates the new operability model end to end.

Operational closure checklist for the stabilization window:

1. `main` remains clean and internally consistent.
   - no relevant pending core changes;
   - `README`, `docs`, `devguide`, and `standards` stay synchronized.
2. full local validation remains green.
   - `ruff check .`
   - `PYTHONPATH=. pytest -q`
   - `PYTHONPATH=. pytest -q --cov-config=.coveragerc --cov=smonitor --cov-report=term --cov-report=xml`
3. remote CI remains green in a sustained way.
   - multiple consecutive successful runs on primary workflows;
   - no new flakiness in the main gates.
4. no open high-severity SMonitor bugs remain.
   - nothing breaking public contracts, bundles, profiles, CLI, or support/triage flows.
5. operability is confirmed in at least one real CI/support workflow.
   - fingerprints, runtime identifiers, triage summaries, bundle comparison, and dual human/agent output are all exercised.
6. no further pre-`1.0.0` API changes are clearly required.
   - no missing canonical fields;
   - no public signatures needing redesign before freeze.
7. a short observation period passes without structural friction.
