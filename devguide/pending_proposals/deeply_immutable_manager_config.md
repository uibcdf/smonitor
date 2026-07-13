# Deeply immutable ManagerConfig containers

## Status

Postponed implementation refinement. The scalar configuration contract is
already safe: `ManagerConfig` is a frozen dataclass and runtime mutation goes
through `Manager.configure(...)` or `Manager.enabled`.

## Remaining limitation

`frozen=True` prevents attribute assignment, but it is shallow. Container
fields such as `silence` and `profiling_hooks` can still hold lists, so code
that obtains `manager.config` could mutate those lists in place and thereby
alter the active configuration without going through the manager.

## Proposed resolution

Store container-valued configuration as immutable tuples and normalize public
list inputs in `Manager.configure(...)`. Preserve the current public input
forms and verify that `dataclasses.replace`, `dataclasses.asdict`, bundle JSON
serialization, routing, profiling hooks, and warning silencing retain their
current behavior.

## Acceptance criteria

- `manager.config.silence.append(...)` is impossible.
- `manager.config.profiling_hooks` cannot be changed in place.
- `configure(silence=[...], profiling_hooks=[...])` remains accepted.
- Bundle exports continue to serialize these fields as JSON arrays.
- Construction or copying of `ManagerConfig` has no runtime side effects.
