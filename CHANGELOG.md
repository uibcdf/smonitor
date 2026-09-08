# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- `hint` returns on `CatalogException` and `CatalogWarning`, as a read-only property re-resolved from `code` and `extra`. It stores nothing, so `args` still carries the message and nothing else — the invariant that makes `type(e)(*e.args)` reproduce an instance — and every rebuild reproduces the hint rather than dropping it. Being a property is also the enforcement the reserved-name rule needed: a subclass assigning `self.hint` now raises `AttributeError` at the offending line, which `__init_subclass__` could not do because it cannot see assignment order.

  It is read at access, so it answers for the active profile, while `message` remains the snapshot taken at construction. The two can disagree if the profile changes in between; the profile is set in `configure()` before any diagnostic is raised, so in practice they do not.

  This implements the decision in `devguide/archive/hint_ownership_on_catalog_instances.md`, landed after its precondition: ArgDigest migrated first (`uibcdf/argdigest@be23917`), so `exc.hint` changing from the call-site hint to the catalog one was a visible diff in its tests rather than a silent redefinition.

### Fixed
- A `CODES` entry that is not a mapping raised `AttributeError` from inside `resolve()`. A code pointing straight at a message string is the shape that does it, and one library in the ecosystem is written that way, so the first diagnostic it tried to report crashed the call reporting it. A malformed catalog now degrades to an uncoded diagnostic; `validate_project_config` already named the entry and `strict_config` still refuses to start on it.

### Added
- The machine payload is pinned as a whole, in `tests/snapshots/`, rather than field by field. `profile="agent"` exists so a triage agent reads structure instead of prose, and `normalized` is the section it reads; it is frozen for 1.0, where a key that disappears breaks every consumer and a key that appears is one we are then obliged to keep.

  Measured before writing it, by removing each field in turn: 23 of the 25 promoted `extra` keys were already guarded, but `form`, `requested_attribute`, `message`, `category` and `exception_type` could be deleted with the whole suite green — and a key could be *added* with nothing failing at all, verified by growing `normalized` an `internal_debug_state` holding `repr(event)`. Two snapshots close both directions: one event carrying every canonical field, one carrying nothing optional, so the fields that are always present are pinned too. Regenerating is explicit (`SMONITOR_UPDATE_SNAPSHOTS=1`) and the diff is the record of a contract change. All six previously silent changes now fail.

  The fingerprint is pinned as a value rather than masked, because it is deterministic across processes and pinning it guards the recipe that decides whether two occurrences are one incident.

- `devtools/verify_integration.py` runs section 7's checks 1, 2, 3 and 5 over one library or over every sibling carrying the canonical guide, and exits non-zero on any failure. The section gives each library a test file to copy, which answers "is this library correct"; the sweep answers "where does every library stand", which is what a stabilization pass needs. It reads a catalog without importing its library, under a synthetic package chain, so a library whose `__init__` pulls the scientific stack is still checkable. Check 4 is not covered: it needs one builder per catalog class in the shape a call site uses, which only the library can supply.

  Its first run found the `resolve()` crash above, and independently rediscovered a catalog that is wired but not connected (uibcdf/topomt#15).

## [0.14.0] - 2026-09-06

*Published on 2026-09-08 as a GitHub source release and through the UIBCDF Conda channel
for Python 3.11--3.13 on `linux-64`, `osx-64`, `osx-arm64`, and `win-64`.*

Three notes for integrators, in the order they are likely to matter:

- **A catalog entry that defines only `user_message` now renders in every
  profile.** It previously rendered an empty message under `dev`, `qa`, `agent`
  and `debug` — the shape the README, the shipped template and section 1 of the
  canonical guide all show. ArgDigest and PyUnitWizard were emitting no message
  at all under `qa` and `agent`, DepDigest under `agent`. Nothing to change on
  your side; a profile whose own field is present resolves exactly as before.
- **An unrecognised key in `_smonitor.py` no longer raises.** It is reported by
  `smonitor --validate-config` and ignored, because that file is read during your
  package's import and a typo must not take the library down. `strict_config`
  still turns the report into an error.
- **`_smonitor.py` belongs inside the package**, at `mylib/_smonitor.py`. The
  canonical guide said "relative to the repository root", which is found in a
  development checkout and is not packaged into the wheel. If yours is at the
  repository root, it is absent for everyone who installed your library.

The canonical guide gained two sections worth reading once: **3.5**, what to
write in a diagnostic and what each choice buys downstream, and **7**, five
checks that catch an integration that is wired correctly and silently useless.

### Fixed
- `ensure_configured()` could fail with `AttributeError: partially initialized module 'smonitor' has no attribute 'configure'` when two threads imported different packages that use SMonitor. `smonitor/__init__.py` imports `integrations` before it defines `configure`, `emit` and `resolve`, so a module that binds the package with `import smonitor` and reads the attribute at call time depends on the package body having progressed past that definition. That holds single-threaded and fails the moment a second top-level package, with its own import lock, enters through another thread. Reproduced 24 times out of 25 from `uibcdf/molsysviewer#76`; never serially.

  The eleven call sites now import the name inside the function. `from smonitor import configure` goes through the import machinery, which waits on a module still initializing elsewhere; an attribute read on an already-bound module object waits for nothing. Isolating the two halves of the change on that reproduction says which one matters: attribute access *with* the new lock still failed 14 of 15 times, the deferred import *without* the lock failed 0 of 15. The lock stays regardless, because `_configured_packages` is a check-then-act between the membership test and the `add` — a second and quieter defect on the same lines, which that reproduction does not exercise.

  `tests/test_no_package_attribute_reachthrough.py` guards the invariant rather than the race: it parses `__init__.py`, collects the names bound after the `integrations` import, and fails on any `smonitor.<name>` attribute read of one of them. That is what found the seven sites beyond the one in the traceback. A race test for this window could not be made to reproduce standalone — it needs two real downstream packages — and a green test that never opens the window would certify the defect instead of catching it.

  Shipped in `31da6a4` (uibcdf/smonitor#3); recorded here after the fact.

- `ruff check .` was failing on `main`, and the lint step runs before the test step, so the test suite had not executed in CI since 2026-09-04 (runs `33929972827`, `33929972830`, `33930563670`, all failing at `Run linter`; every commit since was `[skip ci]`). Five `import smonitor` bindings under `integrations/` became unused in `31da6a4`, when those call sites deferred their imports into function bodies (uibcdf/smonitor#3); `F401` flagged them and the suite stopped running behind the lint gate. This is the second occurrence of the failure shape recorded under `0.13.0`, and the gate order is what makes it silent.

  Removing them is not only lint hygiene: a module-level binding of the package inside `integrations/` is the raw material of that bug, and `tests/test_no_package_attribute_reachthrough.py` guards the attribute read rather than the binding. Three tests reached the package through `argdigest.smonitor` and three more through `smonitor.integrations.core.smonitor`; those aliases *were* the package object, so they now name it directly.

  `ruff check .` also depended on whether the tree had been built. `tests/test_integrations_entrypoints.py` did `import smonitor._version`, and ruff's isort resolves that dotted path against the filesystem: `smonitor/_version.py` is written by the build and kept out of the tree by `.gitignore`, so the module was first-party after a build and third-party before one — and the two import orderings that satisfies are mutually exclusive. CI never saw it because `pip install .` runs before the lint step. The test now reaches the module as `from smonitor import _version`, which keys on `smonitor` and is stable either way; `ruff check .` is clean on an unbuilt checkout for the first time.

- A key in `_smonitor.py` that `Manager.configure` does not accept reached it as a keyword argument and raised `TypeError`. `ensure_configured()` runs during the host library's import, so a typo in a config file — or a copy of SMonitor's own shipped template — took the whole library down at import time.

  Three lists of configuration keys had drifted apart, in all three directions at once. `silence`, `duplicate_policy` and `duplicate_every_n` were accepted by the manager and rejected by the validator; `silence` appears in the canonical guide's **first example**, so a `_smonitor.py` copied from the guide reported `Unknown SMONITOR key: silence` and raised under `strict_config`. `style` went the other way: it sat in `smonitor/templates/_smonitor.py` and in `SPEC_SMONITOR.md`, was accepted by nobody, and produced `TypeError: Manager.configure() got an unexpected keyword argument 'style'` from the shipped template verbatim.

  The keyword set is now derived from `Manager.configure`'s signature (`CONFIGURE_PARAMETERS`), the `SMONITOR` allowlist is derived from that in turn, and keys arriving from a config file or the environment are dropped rather than forwarded — `validate_project_config` already names them and `strict_config` still raises. Keys passed directly to `smonitor.configure(...)` keep raising, because there a typo is the caller's own and immediate. `style` is gone from the template and the SPEC: a profile block's keys are the same keys as the `SMONITOR` block, and the profile *name* already selects the output style. Guarded by `tests/test_config_surface_agreement.py`, which fails on the shape of the drift rather than on the individual keys.

- `CRITICAL` was rejected by event schema validation, though `Manager` scores it above `ERROR` in `_LEVEL_ORDER` and routes it, and `docs/content/developer/schema-validation.md` publishes it as valid. Only `validation.py` disagreed, so in the `dev` and `qa` profiles every `CRITICAL` event carried a `schema_warning` and `strict_schema` refused it outright — making the highest severity the one severity those profiles could not emit.

- A catalog message resolved in one profile and rendered **empty** in the others. Message lookup consulted exactly one field per profile, so an entry defining `user_message` alone — the shape the README, the shipped template and section 1 of the canonical guide all show — produced an empty message under `dev`, `qa`, `agent` and `debug`. Hints already fell back (`qa_hint` to `dev_hint`); messages did not.

  Measured across the ecosystem on 2026-09-06: ArgDigest and PyUnitWizard emitted no message at all under `qa` and `agent`, DepDigest under `agent` — the profile whose entire purpose is machine triage, arriving with nothing to triage. The two libraries that were unaffected were unaffected because each had built its own workaround: MolSysMT writes all four fields by hand, MolSysViewer fans one template across them in `_code_entry`, whose docstring records the limitation. Both workarounds are now optional.

  Each profile prefers its own field, then the nearest audience, and ends at the `user_*` field, which is the one every published example defines. The invariant is that an entry defining any message field renders empty in no profile. A profile whose own field is present resolves exactly as before, so no working configuration changes. Guarded by `tests/test_profile_message_fallback.py`.

- The canonical guide told integrators to place `_smonitor.py` "relative to the repository root". Every library in the ecosystem places it at `mylib/_smonitor.py`, and the guide's own location does not survive packaging: configuration discovery walks upward, so a file at the repository root is found in a development checkout and then is simply not in the wheel. The failure is silent — diagnostics fall back to defaults, every catalog code resolves against no template, and messages come out empty for everyone who installed the library.

### Documentation
- Canonical guide section **3.5**, "What to write, and what it buys you": which of `code`, message, hint and `extra` owns what, the same diagnostic written with prose and with data, how to choose a code, and what each field buys in `report()` and in bundles. It ends with two facts that are not guessable from the API and were written down nowhere — which twelve `extra` keys take part in the incident fingerprint, and that `retry_attempt` is one of them, so fingerprints do not collapse retries and `duplicate_policy` cannot either; `warning_coalesce_window_s` is what does.
- Canonical guide section **7**, "Verify the integration": five checks, one assertion each, as a copy-pasteable test file. Each corresponds to a defect that reached a released library in this ecosystem.
- `devguide/decisions/` records decisions that shape a public contract, with the evidence that decided them and what was rejected. The first is `hint_ownership_on_catalog_instances.md`, decided at the 1.0 API freeze it was deferred to: there is no `hint=`, `hint` returns as a read-only derived property, the reserved-name rule is guarded by a static check rather than only documented, and `FunctionContract` does not gain a `violation_code`. The decision is recorded; it is not implemented in this release.
- `devtools/sync_smonitor_guide.py` syncs to consumers found on disk rather than only to a hand-maintained list. It named five repositories while nine carried the guide, and the four it had forgotten were six months stale.

## [0.13.0] - 2026-08-17

Catalog exceptions and warnings changed shape. Three notes for integrators:

- `warn()` now raises the Python warning as well as emitting the event. Code
  running under `simplefilter("error")` sees an exception where it previously
  saw none; `pytest.warns` and `filterwarnings` start working on catalog
  diagnostics, which is the point.
- `stacklevel` counts from the caller of `warn()`, as it does at a plain
  `warnings.warn`. A call site that had compensated for the old off-by-one
  should drop the compensation.
- A catalog class must take `message` as its first parameter, with its domain
  fields keyword-only. Section 3.3.1 of the canonical guide explains why and
  what breaks otherwise. `args` no longer carries the appended hint; `str()` is
  unchanged.

### Changed
- `DiagnosticBundle.warn()` now raises the Python warning **as well as** emitting the structured catalog event; on a catalog hit it used to emit and return. A diagnostic that exists only as an SMonitor event is invisible to `pytest.warns`, to `warnings.filterwarnings` and to `simplefilter("error")`, so adopting catalogs silently took those away from the library's own users and test suites. Downstream libraries responded by calling `warnings.warn` directly and losing the catalog instead: across MolSysMT and ArgDigest, 17 call sites did this against 2 using the structured path, and their events arrived with `code=None`, `source="py.warnings"`, no `category` and no structured fields.

  While the warning is in flight the capture emitters stand down, keyed on a `ContextVar`, so `capture_warnings` cannot feed the same incident back in without its catalog metadata — without that guard the incident lands twice, once coded and once stripped. A user filter that hides the warning does not suppress the event, and `simplefilter("error")` promotes it only after the event has been recorded.
- `CatalogWarning` and `CatalogException` accept `message` positionally. It was keyword-only, which made `warnings.warn(text, MyCatalogWarning)` fail with `TypeError` — Python builds the instance itself as `category(text)` — even though the guide documents that form. The early return had been hiding it.

### Performance
- `import smonitor` costs **43 ms instead of 67 ms** (medians of 21 runs, wheel installed into a clean venv). The version lookup tried `importlib.metadata` first — which pulls in `email.message`, `zipfile` and `inspect` — and fell back to `smonitor/_version.py` only on failure. The order is now reversed, and the metadata machinery is imported only when the tree has no build. Every library in the ecosystem paid this before doing any work. The string itself is unchanged: the build writes `_version.py`, so both sources report the same value in an installed distribution.

  Deferring `smonitor.bundle` behind PEP 562 was measured at the same time and **rejected**: it is worth 1.6 ms, not the 11.9 ms its cumulative `-X importtime` figure suggests, because `bundle`'s children (`pathlib`, `json`, `dataclasses`, `platform`) are imported by `core.manager` anyway. It is not worth a module-level `__getattr__` in the API being frozen for 1.0. The remaining ~42 ms is the core module graph itself, dominated by `pathlib` and `dataclasses`/`inspect` under `core.manager`; reducing it means moving imports between modules and is deferred to post-1.0.

### Fixed
- `CatalogWarning` and `CatalogException` survive `pickle` and `copy.deepcopy` unchanged. Python rebuilds an exception as `type(e)(*e.args)`, which assumes the first constructor argument is the message. These classes appended the resolved hint to the message before storing it, so rebuilding from `args` appended it a second time — `UnknownAtomNameWarning(atom_name="Ar")` came back from `pickle` reading `Atom name 'Atom name 'Ar' is not recognized…'`.

  `args` now carries the message *before* the hint, and `__str__` renders the two together, so the visible text is unchanged while the class became idempotent: `type(e)(*e.args)` reproduces it.

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
