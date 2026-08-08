# Contract Versioning (CODES and SIGNALS)

SMonitor contracts are operational APIs. Treat `CODES` and `SIGNALS` as
versioned interfaces.

## Stability rules

1. Do not repurpose an existing `code` with a different meaning.
2. Do not silently remove `signal` names used in QA/automation.
3. Prefer deprecation windows over immediate removals.
4. Keep message text evolvable, but keep semantic intent stable.

## Safe evolution pattern

- Add new code/signal first.
- Keep old code/signal working during a transition window.
- Mark old contract as deprecated in docs and changelog.
- Remove only after downstream libraries and tests are updated.

## Deprecation metadata (recommended)

In catalog entries, include optional metadata such as:
- `deprecated_since`
- `replacement_code`
- `replacement_signal`

This helps tooling and agents generate precise migration hints.

## CI checks

- strict contract tests for required signals/codes;
- snapshot tests for representative emitted payloads;
- changelog entry when contract-affecting changes are introduced.

## Release guidance

Any breaking contract change should be explicit in release notes and reflected
in ecosystem integration checklists before tagging.
