# Who owns `hint` on a catalog instance

**Status:** proposal. Deliberately deferred to the 1.0 API/contract freeze, which
is the moment to decide which attribute names belong to the base classes.

**Recorded:** 2026-08-17

**Origin:** a `self.hint` added to `CatalogWarning` during the `0.13.0` round-trip
fix and removed the same day (`81bb6dd`) because it broke two ArgDigest tests.

## What happened

`CatalogWarning.__init__` briefly stored the resolved catalog hint on
`self.hint`. ArgDigest's `DigestError` and `DigestNotDigestedWarning` set their
own `self.hint` *before* calling `super().__init__()`, so the base overwrote the
caller's hint with the catalog's. `exc.hint == "fix this"` stopped holding.

The attribute was unnecessary — `__str__` reads `self.message`, which already
carries the hint — so removing it cost nothing and the matter was closed.

It should not stay closed. Two things it exposed are still true.

### The instance is poorer than the event

On the event the hint travels as its own field: `Manager.emit` does
`event["extra"].setdefault("hint", hint)`. On the instance it exists only fused
into `self.message`. A caller that catches a `CatalogWarning` and wants to render
the hint separately — dimmed in a console, dropped from a log line, shown in a
tooltip — cannot get at it. Nothing in the design intends that asymmetry; it is
just where the code landed.

### `code` has the identical collision, already shipped

ArgDigest sets `self.code` before `super().__init__()` too, and
`CatalogException.__init__` reassigns it (`self.code = target_code`). Today both
sides compute the same value, so the overwrite is invisible. It is the same
hazard as `hint`, live in released code, waiting for the first consumer whose
code differs from what the catalog resolves.

The general shape: `CatalogException`/`CatalogWarning` claim `code`, `message`,
`raw_message` and `extra` on instances they do not exclusively own, and no
document says so.

## Two hints, not two implementations of one

They are genuinely different, and the distinction is what makes "just use
SMonitor's" unworkable.

The **catalog hint** is declared per code and per profile in `CODES`, resolved by
`Manager._resolve_message_and_hint`, and interpolated with the event's fields. It
is data: translatable, stable, reviewable in one place. It is what the canonical
guide means when it forbids hardcoded user-facing strings in library logic.

The **call-site hint** is computed where the diagnostic is raised. ArgDigest's
`FunctionContractError(violation.message, context=ctx, hint=violation.hint)` is
the honest case: the text derives from a contract the *user* declared at runtime,
so it cannot be keyed by a static code without inventing one code per contract
shape. Other call sites (`hint="A standardizer takes (caller, kwargs) and
returns…"`) are simply hardcoded strings that belong in a catalog, and should
move there regardless of what this proposal decides.

## Proposal

**One concept, owned by SMonitor, with a written precedence.** Not one hint per
library.

1. The catalog hint is the norm and the default.
2. An explicit `hint=` is a documented escape hatch and **wins** when present.
3. SMonitor exposes the result; consumers stop assigning `self.hint` themselves.
4. The same rule is written for `code`, `message`, `raw_message` and `extra`:
   these names belong to the base classes, and a subclass that assigns them
   before `super().__init__()` is writing into a variable the base will
   overwrite.

### The constraint that is not negotiable

`hint` must come back as a **derived property**, not as stored state.

`args` carries the raw message and nothing else — that is precisely the
invariant that made `pickle`, `copy.deepcopy`, `warnings.warn(text, category)`
and released pytest-xdist all reproduce an instance correctly. A stored
`self.hint` is new state outside `args`, so every rebuild would drop it, and the
defect closed in `0.13.0` would reopen in a new place.

A property that re-resolves from `self.code` and `self.extra` survives any
`type(w)(*w.args)` because it holds nothing. An explicit override is the hard
part: to survive a rebuild it has to reach `extra`, which means it is no longer
purely an override but a field. Deciding that is the substance of this proposal,
not a detail of it.

See `devguide/pending_bugs/catalog_warnings_re_rendered_under_xdist.md` for why
the `args` invariant is load-bearing, and for the related residue: a hint whose
template interpolates a field cannot be re-rendered by a rebuilder carrying only
`args`.

### An inconsistency to fix along the way

The two paths resolve hints in opposite directions.

On the event, the caller wins: `emit` calls `setdefault`, so an
`extra["hint"]` supplied by the caller survives and the catalog hint only fills a
gap. In `CatalogWarning.__init__`, the catalog wins: `smonitor.resolve()` reads
the code entry and never consults `extra["hint"]`, so a caller-supplied hint
reaches the event but never the rendered text.

ArgDigest passes `hint` into `extra` and hits exactly this: its hints show up in
structured output and are invisible in what the user reads.

## Why not now

It touches the base classes two days after `0.13.0`, and nothing is broken. The
`hint` collision is gone, the `code` collision is latent and currently harmless,
and the round-trip guards are green across the ecosystem.

The right moment is the 1.0 API freeze, where the question "which names do the
base classes own?" has to be answered anyway.

## What a decision needs

- Whether an explicit `hint` is an override (lost on rebuild) or a field (carried
  in `extra`, and then subject to the interpolation residue).
- Whether the reserved-name rule is documented only, or enforced — a base
  `__init_subclass__` could reject a subclass that assigns reserved names before
  `super().__init__()`, though it cannot see assignment order at class creation.
- Whether ArgDigest's hardcoded call-site hints move into its catalog first, which
  would shrink the escape hatch to the contract-violation case alone and might
  change the answer to the first question.

## Guards that already exist

`tests/test_catalog_instance_round_trip.py` fails if anything reintroduces state
outside `args`, including a stored `hint`. Any implementation of this proposal
has to keep it green.
