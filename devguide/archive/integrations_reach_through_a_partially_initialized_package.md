---
summary: The integrations reach through a package that is not finished being imported.
issue: uibcdf/smonitor#3
status: resolved
opened: 2026-09-04
closed: 2026-09-04
severity: high
verification: reproduced
area: [integrations, imports]
guard: tests/test_no_package_attribute_reachthrough.py
normative:
blocked_by: []
supersedes: []
---

# The integrations reach through a package that is not finished being imported

**Status:** resolved in `31da6a4`. Guarded by
`tests/test_no_package_attribute_reachthrough.py`.
**Reproduced:** 2026-09-04, 24 times out of 25, from `uibcdf/molsysviewer#76`.

## Symptom

```
AttributeError: partially initialized module 'smonitor' from '.../smonitor/__init__.py'
has no attribute 'configure' (most likely due to a circular import).
Did you mean: 'config'?
  File "smonitor/integrations/core.py", line 15, in ensure_configured
    smonitor.configure(config_path=package_root)
```

Two threads, each importing a different package that uses smonitor. Never serially.

## Cause

`smonitor/__init__.py` imports `integrations` on line 23 and defines `configure` on
line 58. Between those two lines `sys.modules['smonitor']` exists and `configure` does
not.

`integrations/core.py` binds the package at module level and reaches through it at call
time:

```python
import smonitor                                     # line 6

def ensure_configured(package_root: Path) -> None:
    ...
    smonitor.configure(config_path=package_root)    # line 15
```

Single-threaded that window is unreachable: nothing calls `ensure_configured` while the
package body is still running. With two threads it is reachable, because two top-level
packages have two different import locks and nothing serializes them. One is executing
the smonitor body; the other, entering through its own package, calls `ensure_configured`
and reads the attribute off the half-built module.

**The module-level `import smonitor` provides no synchronization.** It completed when
*core.py* itself was imported, and all it does now is hand out the module object.

## Fix

Import the name inside the function:

```python
from smonitor import configure
configure(config_path=package_root)
```

This is not a style preference. `from smonitor import configure` goes through the import
machinery, which waits on a module still initializing in another thread. An attribute
read on an already-bound module object does not wait for anything.

Eleven sites had the shape, not one. `configure` in `core.py`, `molsysmt.py`,
`argdigest.py` and `depdigest.py` is the import-time-reachable one; `emit` and `resolve`
in `core.py` and `diagnostic.py` are runtime rather than import-time and were deferred
too, rather than left as the next occurrence.

## What the measurements say, against what was assumed

The change added a lock *and* deferred the import. Isolating them on the cross-package
reproduction says which one matters:

| change | failures |
| --- | ---: |
| attribute access + `_CONFIGURE_LOCK` | 14 of 15 |
| deferred import, no lock | **0 of 15** |
| both | 0 of 15 |

The lock is not the fix. It stays because `_configured_packages` is a check-then-act with
nothing between the membership test and the `add`, so two threads can both pass the test
and both configure — a second and quieter defect on the same lines, and one this
reproduction does not exercise.

## The guard is static, on purpose

A race test for this window could not be made to reproduce standalone. The reproduction
needs two real downstream packages, which this repository cannot depend on, and a
synthetic pair that imports `smonitor.integrations` directly never opens the window at
all: importing the submodule forces the parent to finish first.

Such a test was written and deleted. It passed with the fix reverted, which makes it worse
than nothing — a green test that never opens the window certifies the defect instead of
catching it.

So the guard checks the invariant instead. It parses `__init__.py`, collects the names
bound after the `integrations` import, and fails on any `smonitor.<name>` attribute read
of one of them. That is what found the seven sites beyond `configure`; reading the
traceback had only shown the first.

## Refuted

- *"Move `configure` into a leaf module and re-export it from `__init__`."* Proposed in the
  issue and not taken. It fixes `configure` and leaves `emit` and `resolve`, and it moves
  the hazard rather than making it visible where it would reappear. The guard covers all
  of them and says what to do when it fires.
- *"The lock is the fix."* Measured above: 14 of 15 still fail with the lock alone.

## Residue

`smonitor/__init__.py` still defines its public entry points below the `integrations`
import, so the window still exists — the guard makes it non-load-bearing rather than
closing it. Anything added to `integrations/` that reaches through the package will be
caught at test time, not at 3 a.m. in someone else's suite.

Distinct from [`catalog_warnings_re_rendered_under_xdist.md`](catalog_warnings_re_rendered_under_xdist.md),
which is about the *state* a rebuilt warning carries. This one is about the *import*
performed to find its class. They are neighbours inside xdist's
`unserialize_warning_message`, and that function's own defect — an arbitrary import in the
receiver thread, guarded only against `TypeError` — is tracked in `uibcdf/molsysviewer#80`.
