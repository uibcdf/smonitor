# Integrating Your Library

This chapter is the practical blueprint for migrating a real, existing package.

## First principle

Treat SMonitor integration as a refactor of diagnostics architecture, not a superficial logging replacement.

## Migration phases

## Phase 1: Create a stable diagnostics boundary

1. Add `_smonitor.py` in package root.
2. Add `A/_private/smonitor/catalog.py` and `A/_private/smonitor/meta.py`.
3. Add `A/_private/smonitor/emitter.py` with `DiagnosticBundle`.
4. Configure on import with `ensure_configured(PACKAGE_ROOT)`.

Checkpoint:
- your package imports cleanly,
- a test warning can be emitted from catalog.

## Phase 2: Move warnings/errors to catalog-driven flow

Replace direct message strings with catalog codes in key modules first:
- entry points,
- parser/validation layers,
- dependency/probing paths.

Checkpoint:
- no new warning/error strings are introduced outside catalog,
- emitted messages are profile-aware.

## Phase 3: Instrument function boundaries

Apply `@signal` to:
- public API functions,
- orchestration functions that cross subsystem boundaries.

Avoid high-frequency inner loops.

Checkpoint:
- call chain appears in diagnostics for failure scenarios.

## Phase 4: Harden and validate

1. Enable `strict_signals=True` in `qa` profile tests.
2. Run bundle export in a smoke test.
3. Verify fallback behavior if a handler fails.

Checkpoint:
- diagnostics are robust and reproducible.

## Practical migration order

Use this order to reduce risk:
1. one warning family,
2. one exception family,
3. one subsystem at a time,
4. then global rollout.

## Common concerns

### "Will this break users?"

Not if you keep code IDs stable and improve messages incrementally.

### "Do we need to migrate everything at once?"

No. Migrate by slices. Keep compatibility bridges during transition.

### "Should we expose SMonitor controls to end users?"

Usually no. Keep defaults safe for users; let developers/QA override in runtime/test/CI.

## Next

Read [Edge Cases](edge-cases.md) before broad rollout.
