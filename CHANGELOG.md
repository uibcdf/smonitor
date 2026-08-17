# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]
### Changed
- `DiagnosticBundle.warn()` now raises the Python warning **as well as** emitting the structured catalog event; on a catalog hit it used to emit and return. A diagnostic that exists only as an SMonitor event is invisible to `pytest.warns`, to `warnings.filterwarnings` and to `simplefilter("error")`, so adopting catalogs silently took those away from the library's own users and test suites. Downstream libraries responded by calling `warnings.warn` directly and losing the catalog instead: across MolSysMT and ArgDigest, 17 call sites did this against 2 using the structured path, and their events arrived with `code=None`, `source="py.warnings"`, no `category` and no structured fields.

  While the warning is in flight the capture emitters stand down, keyed on a `ContextVar`, so `capture_warnings` cannot feed the same incident back in without its catalog metadata — without that guard the incident lands twice, once coded and once stripped. A user filter that hides the warning does not suppress the event, and `simplefilter("error")` promotes it only after the event has been recorded.
- `CatalogWarning` and `CatalogException` accept `message` positionally. It was keyword-only, which made `warnings.warn(text, MyCatalogWarning)` fail with `TypeError` — Python builds the instance itself as `category(text)` — even though the guide documents that form. The early return had been hiding it.

### Performance
- `import smonitor` costs **43 ms instead of 67 ms** (medians of 21 runs, wheel installed into a clean venv). The version lookup tried `importlib.metadata` first — which pulls in `email.message`, `zipfile` and `inspect` — and fell back to `smonitor/_version.py` only on failure. The order is now reversed, and the metadata machinery is imported only when the tree has no build. Every library in the ecosystem paid this before doing any work. The string itself is unchanged: the build writes `_version.py`, so both sources report the same value in an installed distribution.

  Deferring `smonitor.bundle` behind PEP 562 was measured at the same time and **rejected**: it is worth 1.6 ms, not the 11.9 ms its cumulative `-X importtime` figure suggests, because `bundle`'s children (`pathlib`, `json`, `dataclasses`, `platform`) are imported by `core.manager` anyway. It is not worth a module-level `__getattr__` in the API being frozen for 1.0. The remaining ~42 ms is the core module graph itself, dominated by `pathlib` and `dataclasses`/`inspect` under `core.manager`; reducing it means moving imports between modules and is deferred to post-1.0.

### Fixed
- `CatalogWarning` and `CatalogException` survive `pickle` and `copy.deepcopy` unchanged. Python rebuilds an exception as `type(e)(*e.args)`, which assumes the first constructor argument is the message. These classes appended the resolved hint to the message before storing it, so rebuilding from `args` appended it a second time — `UnknownAtomNameWarning(atom_name="Ar")` came back from `pickle` reading `Atom name 'Atom name 'Ar' is not recognized…'`.

  `args` now carries the message *before* the hint, and `__str__` renders the two together, so the visible text is unchanged while the class became idempotent: `type(e)(*e.args)` reproduces it. The hint is also kept as `.hint` for callers that want it apart from the prose.

  This replaces a `__reduce__` added earlier in this same unreleased window, which made the round trip exact by bypassing the constructor. Rebuilders that call the class directly — pytest-xdist between a worker and the controller — never reach `__reduce__`, and a custom one makes them fall back and lose the class outright. Fixing the class is what fixes every rebuilder at once.

- `@signal` emitted the error event for a propagating `CatalogException` with `code=None`, so the coded identity the exception had already resolved never reached telemetry. The wrapper now carries a string `code` and merges the exception's structured `extra` onto the event, keeping its own provenance alongside. Non-catalog exceptions stay uncoded, and a non-string `code` attribute is ignored. Only the exception path changed.
- `emit()` stored the caller's `extra` dict by reference and then enriched it with `smonitor`, `title`, and the resolved `hint`. A dict reused across calls accumulated those keys, so a later event could carry a stale hint from an earlier, unrelated one. The event now works on a copy.
- `ruff check .` failed on the repository, and because the lint step runs before the test step, CI on `main` had not executed the test suite since 2026-08-14.
- `.gitignore` listed `.build/` and `.dist/`, which setuptools never creates. The real `build/` directory left by `pip install .` was therefore versioned-visible, and CI linted the copy of the sources inside it.

## [0.12.0] - 2026-08-08

Releases `0.11.1` through `0.11.6` were tagged without changelog entries; this
section covers the work merged after `0.11.6` and does not restate them.

### Added
- Support-tier protocol: `SupportTierRegistry`, the `DiagnosticBundle.support_tier(tier, ...)` decorator, and tier-aware catalog signals. Tier 1 is contractual and silent, tier 2 emits a WARNING once per name per session, tier 3 an INFO. `experimental()` is now an alias for `support_tier(3)`.
- `CatalogException` and `CatalogWarning` instances now retain `code`, `extra`, `raw_message`, and `message`, so catch sites can branch on structured state instead of parsing rendered text.
- `FormatError` and `InconsistencyError` are listed in `smonitor.integrations.__all__`. They existed since `0.11.5` but were never exported, so `import *` missed them.

### Changed
- Pre-`1.0.0` stabilization window started on 2026-02-27.
- Repository PR process now includes explicit stabilization release gates (`pytest`, docs build, QA smoke).
- `DiagnosticBundle.warn(instance)` now re-emits using the instance's structured `extra`, so catalog templates may interpolate their own placeholders and the fields reach `report()` and event fingerprints. Explicit `extra=` still wins; `{message}` is unchanged for string callers.
- `ManagerConfig` is a frozen dataclass replaced wholesale by `configure()` rather than mutated in place, and is deeply immutable: `silence` and `profiling_hooks` are normalized to tuples so a caller's list cannot alter live configuration.
- Catalog message templates are interpolated by an explicit formatter that supports `!r`/`!s`/`!a` conversions and format specs, and leaves unknown placeholders untouched instead of raising.
- `@signal` resolves a method's source module from the runtime class of the bound instance, so classes assembled from mixins across modules report their logical owner. Free functions are unaffected.
- `@signal` guards each step it performs; a failure inside the instrumentation degrades to a `RuntimeWarning` and the decorated call still runs.

### Performance
- A decorated call on the enabled path is **3.1x cheaper** overall (53.5x a bare call down to 17.0x), and a nested operation of the kind sibling libraries actually produce — 16 stacked `@signal` calls — went from **74.9 us to 19.9 us**. No capability was traded away: catalogs, profiles, policy, contracts and the per-step error guards all behave as before. The disabled fast path is unchanged. Reproduce with `benchmarks/signal_enabled.py`.
  - Frames no longer format an ISO-8601 timestamp on every decorated call; the wall clock is stored raw and rendered only when an event is emitted. This alone was over half the wrapper cost.
  - The breadcrumb stack is a linked list, so `push_frame`/`pop_frame` are O(1) instead of copying the stack twice per call. Cost no longer grows with nesting depth.
  - A frame is a compact list rather than a dataclass instance, roughly a third of the allocation cost. It is the hottest allocation in the library: one per decorated call, built whether or not anything is ever emitted.
  - `@signal` caches the configuration-derived decisions it makes per call, keyed on config object identity. `ManagerConfig` is frozen and replaced wholesale by `configure()`, so identity is an exact invalidation signal.
  - `@signal` decides at decoration time whether a callable can resolve its module from a bound instance, so free functions skip that lookup per call.
- A decorated call with telemetry disabled returns through a module-level flag, without reaching the manager at all.
- What remains is close to the floor for this design: roughly 1240 ns of overhead per enabled call, of which the two `ContextVar` writes that buy correct isolation across asyncio tasks and threads are inherent. Further gains would come from decorating fewer functions on hot paths, not from a cheaper decorator.

### Fixed
- Catalog warnings whose template interpolates `{message}` were rendered twice, duplicating both the message prefix and the hint. `warn()` no longer re-injects an instance's already-rendered text as the `message` field.
- An emitted event's `context.frames` is now a snapshot. It previously aliased the live frame objects, so `duration_ms` appeared in the dict returned by `emit()` after handlers had already received, formatted, and buffered the same event with `None` there.
- Assigning `manager.enabled = True` did not update the module-level flag that the decorated fast path consults, so already-decorated callables kept taking the disabled bypass. The setter now keeps the two in sync, and mutating a *copy* of the configuration no longer affects live telemetry.

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
