# About

SMonitor (Signal Monitor) is a diagnostics and telemetry layer for scientific Python libraries.

It centralizes:
- warnings,
- logging-derived events,
- exception diagnostics,
- structured telemetry for QA and automation.

## Why it exists

Scientific libraries often evolve in small teams. Diagnostics become fragmented quickly:
- messages are inconsistent,
- support is expensive,
- debugging context is lost across package boundaries.

SMonitor provides one operational model so user-facing messages remain clear while developers and QA keep deep traceability.

## Why adopt it now

- You can improve end-user guidance without rewriting all internals.
- You can keep diagnostics contracts stable for QA and automation.
- You can reduce support turnaround with reproducible bundles.

## Core ideas

- **Catalog-driven diagnostics**: warnings/errors are declared as codes with profile-specific messages.
- **Boundary instrumentation**: `@signal` captures breadcrumbs across layers and sibling packages.
- **Profile-aware output**: `user`, `dev`, `qa`, `agent`, `debug`.
- **Local-first operations**: export bundles for reproducible diagnosis without mandatory remote telemetry.
- **Lightweight profiling**: decorator timing, spans, and timeline export for QA/debug observability.

## Ecosystem integration

SMonitor is already integrated across the current UIBCDF stack:
- MolSysMT
- MolSysViewer
- ArgDigest
- DepDigest
- PyUnitWizard

## Read next

- [Showcase](../showcase/index.md)
- [User Guide](../user/index.md)
- [Developer Guide](../developer/index.md)
