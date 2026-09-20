---
summary: A catalog hint interpolating a field cannot be re-rendered from args alone.
issue: uibcdf/smonitor#4
status: resolved
opened: 2026-08-15
closed: 2026-09-20
severity: low
verification: reproduced
area: [catalog, integrations]
guard: tests/test_catalog_instance_round_trip.py::test_state_dependent_hint_text_survives_an_args_only_rebuild
normative:
blocked_by: []
supersedes: []
---

# Catalog warnings are re-rendered when they are rebuilt

**Status:** resolved. The broad reconstruction defect was fixed in `0.13.0`; the
state-dependent visible-hint residue was removed locally on 2026-09-20.
**Reproduced:** 2026-08-15 under pytest-xdist. Root cause found 2026-08-17.

## Symptom

A catalog warning came back from a rebuild reading as its own template applied to
its own output:

```
Atom name 'Atom name 'Ar' is not recognized.' is not recognized.
GPU acceleration was requested but is not available: GPU acceleration was
requested but is not available: …
```

First seen in MolSysMT's suite under `-n 12` and absent serially, which is why it
was filed as an xdist problem. It was not one. `pickle` and `copy.deepcopy`
produced the same text, on any machine, with no test runner involved.

## Cause

Everything that rebuilds an exception calls `type(e)(*e.args)`: `pickle` and
`copy.deepcopy` through `BaseException.__reduce__`, `warnings.warn(text,
category)` when it builds the instance, and pytest-xdist when a warning crosses
from a worker to the controller.

`CatalogWarning.__init__` appended the resolved hint to the message and stored
the result as `args`. It therefore transformed its own input, and no call of that
form could reproduce the instance. Subclass parameter order was a second,
smaller half: a class naming a domain field first received the rendered sentence
as `atom_name` or `reason`.

## Resolution

`args` now holds the message *before* the hint; `__str__` renders the two
together, so the visible text is unchanged. Catalog classes across the ecosystem
take `message` first with their domain fields keyword-only. Section 3.3.1 of the
canonical guide carries the rule.

With that, `pickle`, `copy.deepcopy`, `warnings.warn(text, category)` and
released pytest-xdist all reproduce the instance, and three workarounds came out:
a `__reduce__` on the base classes, a patch in MolSysMT's `conftest.py`, and two
`isinstance(attributes, str)` branches inside its warning classes.

Guard: `tests/test_catalog_instance_round_trip.py`.

## What was refuted

Two rejections recorded in this document earlier were wrong, and both delayed the
fix:

- *"Reordering subclass parameters spreads a workaround across every library."*
  It is not a workaround; it is the shape Python's rebuild protocol requires.
  ArgDigest's classes already took the message first and doubled anyway, which is
  what finally located the defect in the base class rather than in the subclasses.
- *"Removing the subclasses' own `__init__` loses per-field argument checking, and
  classes that compute their message cannot be field-folded."* Both objected to a
  variant nobody proposed. Keeping the fields **keyword-only** preserves the
  checking exactly, and a class that computes its message renders it in a
  classmethod and hands the finished text to `__init__`.

A `__reduce__` on the base classes was also tried and removed. It made `pickle`
and `copy` exact by bypassing the constructor, but reached nothing that rebuilds
by calling the class — and a custom `__reduce__` forces the fix proposed in
`pytest-dev/pytest-xdist#1372` to fall back and drop the class outright.

The review on that pull request is what surfaced all of this. It is worth reading
before revisiting any of it.

## Former residue

A hint whose template interpolates a field cannot be re-rendered by a rebuilder
carrying only `args`, because the field is not there. ArgDigest's
`DigestNotDigestedWarning` shows it: `'unknown'` where the argument name should
be, and the quickstart's own example shows it too. No class shape fixes this —
the state has to travel, which is what `pytest-dev/pytest-xdist#1372` proposes.
`pickle` does carry the state and is unaffected, as are serial runs, scripts,
notebooks and services.

The repository originally kept this entry blocked until a released pytest-xdist
transferred warning state. That coupled truthful visible text to a stronger contract than
SMonitor needs from the transport.

## Resolution

Warnings created from structured catalog data now resolve their message and hint once and
store the complete visible text in `args`. An explicit message arriving without structured
inputs is treated as authoritative rebuild text, so an args-only transport does not try to
interpolate a state-dependent hint from fields it never received.

The boundary is explicit: released pytest-xdist still loses the warning's structured state,
and `pytest-dev/pytest-xdist#1372` remains valuable for preserving that state and the full
instance contract. SMonitor no longer waits on it to preserve correct user-visible text.

The new regression first failed with `Use '{suggestion}' instead.` where the original read
`Use 'AR' instead.` It now passes. On 2026-09-20 the three focused warning modules passed
35 tests, the complete suite passed 460 tests with 2 skips under 12 xdist workers, and Ruff
lint and formatting checks passed.

Guard:
`tests/test_catalog_instance_round_trip.py::test_state_dependent_hint_text_survives_an_args_only_rebuild`.
