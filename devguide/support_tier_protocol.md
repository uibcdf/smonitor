# Support Tier Protocol

## Purpose

This document describes the support-tier protocol added to SMonitor in March 2026
as part of the MolSysSuite 1.0.0 stabilization effort.

The protocol lets any library in the MolSysSuite ecosystem communicate to users
which parts of its API carry a formal support guarantee (Tier 1), which are
best-effort (Tier 2), and which are experimental or niche (Tier 3) — using
SMonitor's structured diagnostics rather than ad-hoc warnings or comments.

---

## Tier semantics

| Tier | Meaning | Runtime signal |
|------|---------|----------------|
| **1** — Contractual | Regressions are patch-priority. API is stable for the 1.x line. | None (silence) |
| **2** — Best-effort | Supported and maintained, but not contractually guaranteed for all workflows. | `WARNING` once per name per session |
| **3** — Experimental / niche | Available but outside the contractual core. | `INFO` once per name per session |

"Once per name per session" means the signal fires at most once regardless of
how many times the item is used.  This prevents log pollution in loops or
batch workflows.

---

## API added to `DiagnosticBundle`

### `support_tier(tier, *, message=None, key=None)` — function decorator

Marks a **function** with its support tier.

```python
@bundle.support_tier(2)
def solvate(molecular_system, ...):
    ...

@bundle.support_tier(3)
def run_NPT_equilibration(...):
    ...
```

- **Tier 1**: returns the original function unchanged (zero overhead, no wrapper).
- **Tier 2**: wraps the function; emits a `WARNING` on the first call per session.
- **Tier 3**: wraps the function; emits an `INFO` on the first call per session.

The `key` parameter overrides the catalog lookup key
(`"SupportTier2Warning"` or `"SupportTier3Info"` by default).
If the catalog key is absent, a built-in fallback message is emitted directly.

### `tier_registry()` — form/object registry

Returns a `SupportTierRegistry` bound to the bundle.  Created lazily on first
access and persistent for the bundle's lifetime.

```python
registry = bundle.tier_registry()
registry.register("MDAnalysis.Universe", 2)
registry.register_many({
    "networkx.Graph": 3,
    "pytraj.Trajectory": 3,
})
registry.check("MDAnalysis.Universe")   # emits WARNING once
registry.check("molsysmt.MolSys")       # unregistered → silence
```

`check()` is the call-site method: place it wherever the form/object name is
first resolved in the public API.

### `SupportTierRegistry` class

| Method | Description |
|--------|-------------|
| `register(name, tier)` | Register a single name with its tier. |
| `register_many(mapping)` | Register a `{name: tier}` dict at once. |
| `check(name)` | Emit the tier signal for `name`, at most once per session. |

### `experimental(message=None, *, key="ExperimentalPath")` — backward-compatible alias

`experimental()` is now an alias for `support_tier(3, key=key)`.  Existing
code using `@bundle.experimental()` continues to work.  The behavior changes
slightly: signals are now **deduplicated per function per session** rather than
emitted on every call.  This is strictly an improvement for the use cases
`experimental()` was designed for.

---

## Catalog keys

Libraries can add the following entries to their SMonitor catalog to provide
customized messages.  If absent, built-in fallback messages are used.

| Catalog key | Group | Default level | Purpose |
|---|---|---|---|
| `SupportTier2Warning` | `warnings` | `WARNING` | Emitted for Tier 2 items |
| `SupportTier3Info` | `info` | `INFO` | Emitted for Tier 3 items |
| `ExperimentalPath` | `info` | `INFO` | Legacy key; used as fallback for Tier 3 |

Example catalog entry for a library:

```python
CATALOG = {
    "warnings": {
        "SupportTier2Warning": {
            "code": "MSM-WARN-TIER-002",
            "source": "molsysmt.warning.tier2",
            "category": "support_tier",
            "level": "WARNING",
        },
    },
    "info": {
        "SupportTier3Info": {
            "code": "MSM-INFO-TIER-003",
            "source": "molsysmt.info.tier3",
            "category": "support_tier",
            "level": "INFO",
        },
    },
}
```

---

## Deduplication

All tier signals use a per-bundle `_tier_dedup_cache` (a `set[str]` keyed on
`"tier:{tier}:{name}"`).  This cache is independent of the `_warned_once_cache`
used by `warn_once()`.

Signals emitted via `support_tier()` on functions and via
`SupportTierRegistry.check()` share the same cache, so a form registered in
the registry and decorated with `@support_tier` will not double-fire.

---

## Why `experimental()` is now an alias

The original `experimental()` emitted on **every call** with no deduplication.
For long-running workflows or loops this could produce hundreds of identical
signals.  Routing it through `support_tier(3)` gives consistent dedup behavior
across all tier signals.  The semantic meaning is unchanged: Tier 3 items are
experimental.

Libraries that genuinely need "emit on every single call" behavior can call
`self.info("ExperimentalPath", extra={...})` directly without the decorator.

---

## Adoption across MolSysSuite

The protocol is designed to be adopted uniformly:

- **MolSysMT**: forms classified by tier via `_private/form_tier.py`; check
  injected in `basic/get_form.py`; `molecular_dynamics` functions use
  `@support_tier(3)`.
- **Other libraries** (argdigest, depdigest, pyunitwizard, molsysviewer): can
  adopt the same pattern for their own forms and experimental functions.

---

## Pending / future ideas

- **`support_tier` on classes**: the decorator currently wraps functions.
  A class-level variant could wrap `__init__` or use `__init_subclass__`.
- **Tier introspection**: `bundle.tier_registry().get_tier(name)` could allow
  tooling to query registered tiers programmatically.
- **CLI / report integration**: a `smonitor report` section listing which
  Tier 2/3 items were used in a session would help QA workflows.
- **Auto-population from module attributes**: if every library module exposes a
  `form_tier` attribute, the registry could be auto-populated without a
  centralized dict.
- **`support_tier` as a class decorator**: for marking entire modules or
  sub-packages (e.g., `molecular_dynamics`) as Tier 3 without decorating
  every function individually.
