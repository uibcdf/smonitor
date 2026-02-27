# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]
### Added
- Placeholder for post-`0.11.0` changes.
- Pre-`1.0.0` stabilization window started on 2026-02-27.

### Changed
- Repository PR process now includes explicit stabilization release gates (`pytest`, docs build, QA smoke).

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
