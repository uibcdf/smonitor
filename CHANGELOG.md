# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]
### Added
- Placeholder for post-`0.11.0` changes.
- Pre-`1.0.0` stabilization window started on 2026-02-27.
- `CatalogException` and `CatalogWarning` instances now retain `code`, `extra`, `raw_message`, and `message`, so catch sites can branch on structured state instead of parsing rendered text.

### Changed
- Repository PR process now includes explicit stabilization release gates (`pytest`, docs build, QA smoke).
- `DiagnosticBundle.warn(instance)` now re-emits using the instance's structured `extra`, so catalog templates may interpolate their own placeholders and the fields reach `report()` and event fingerprints. Explicit `extra=` still wins; `{message}` is unchanged for string callers.

### Performance
- A decorated call on the enabled path is **3.1x cheaper** overall (53.5x a bare call down to 17.0x), and a nested operation of the kind sibling libraries actually produce — 16 stacked `@signal` calls — went from **74.9 us to 19.9 us**. No capability was traded away: catalogs, profiles, policy, contracts and the per-step error guards all behave as before. The disabled fast path is unchanged. Reproduce with `benchmarks/signal_enabled.py`.
  - Frames no longer format an ISO-8601 timestamp on every decorated call; the wall clock is stored raw and rendered only when an event is emitted. This alone was over half the wrapper cost.
  - The breadcrumb stack is a linked list, so `push_frame`/`pop_frame` are O(1) instead of copying the stack twice per call. Cost no longer grows with nesting depth.
  - A frame is a compact list rather than a dataclass instance, roughly a third of the allocation cost. It is the hottest allocation in the library: one per decorated call, built whether or not anything is ever emitted.
  - `@signal` caches the configuration-derived decisions it makes per call, keyed on config object identity. `ManagerConfig` is frozen and replaced wholesale by `configure()`, so identity is an exact invalidation signal.
  - `@signal` decides at decoration time whether a callable can resolve its module from a bound instance, so free functions skip that lookup per call.
- What remains is close to the floor for this design: roughly 1240 ns of overhead per enabled call, of which the two `ContextVar` writes that buy correct isolation across asyncio tasks and threads are inherent. Further gains would come from decorating fewer functions on hot paths, not from a cheaper decorator.

### Fixed
- Catalog warnings whose template interpolates `{message}` were rendered twice, duplicating both the message prefix and the hint. `warn()` no longer re-injects an instance's already-rendered text as the `message` field.
- An emitted event's `context.frames` is now a snapshot. It previously aliased the live frame objects, so `duration_ms` appeared in the dict returned by `emit()` after handlers had already received, formatted, and buffered the same event with `None` there.

## [0.11.0] - 2026-02-26
### Added
- Pre-1.0 stabilization plan in `devguide/implementation_plan.md`.
- API contract tests for public exports and core API behavior.
- Integrations API contract tests (`smonitor.integrations` public exports + behavior).
- Agent-profile contract tests for machine-oriented output and payload stability.

### Changed
- Documentation terminology standardized from placeholder library naming to host-library wording.
- Documentation path consistency for canonical guide references.
- CI matrix extended to Python `3.13` (including docs/QA/conda workflows updates).
- GitHub Actions references updated (`checkout@v6`, `setup-python@v6`, `setup-micromamba@v2`).
- QA CI now builds `sdist`/`wheel` and runs wheel install + CLI smoke checks.
- Conda recipe metadata updated with lab homepage plus `dev_url`/`doc_url`.

## [0.10.0] - 2026-02-06
### Documentation
- Updated README, SPEC, and devguide to reflect 0.10 status and completed ecosystem integration.
- Clarified smonitor name (Signal Monitor) and next steps beyond 0.10.0.

## [0.9.0] - 2026-02-06
### Added
- Strict config validation (`strict_config`, `SMONITOR_STRICT_CONFIG`) and full project validation.
- Catalog and signals contract validation helpers.
- Policy rules: sampling (`sample`), `set`, and `set_extra`.
- `MemoryHandler` for in-memory event buffering.
- CLI validation tests and config precedence tests.

### Changed
- Configuration precedence clarified: runtime `configure()` > env vars > `_smonitor.py`.
- CLI uses full project validation.
- Profiling spans now respect `profiling_sample_rate` and reuse timeline recording.

### Fixed
- Timeline recording duplication for spans.

### Documentation
- Expanded policy, profiling, and CLI documentation.

## [0.2.0] - 2026-02-06
- Initial public draft with core manager, emitters, handlers, policy engine, and profiling tools.
