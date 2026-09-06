# Who owns `hint` on a catalog instance

**Status:** decided 2026-09-06, at the 1.0 API/contract freeze it was deferred to.
The three questions this document ends with are answered at the bottom, with the
measurements that answered them. Implementation is not started; the precondition
is stated below and belongs to ArgDigest.

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

## Decision (2026-09-06)

Everything above is the analysis as it stood. What follows is what was decided,
and the evidence that decided it. The three questions the proposal ended with are
answered in order.

### 1. Is an explicit `hint` an override or a field? — **Neither. There is no `hint=`.**

The question assumed a hint that cannot be keyed by a code. The inventory found
none. Across the nine libraries integrating SMonitor:

| library | catalog hints | call-site `hint=` | `self.hint` |
| --- | ---: | ---: | ---: |
| molsysmt | 200 | 0 | 0 |
| pyunitwizard | 22 | 0 | 0 |
| argdigest | 22 | ~12 | 3 |
| depdigest | 4 | 0 | 0 |
| molsysviewer | inline | 0 | 0 |
| topomt, pharmacophoremt, elastnetmt, lindelint | — | 0 | 0 |

ArgDigest is the only source of call-site hints, and the case that justified an
escape hatch — *"the text derives from a contract the user declared at runtime"* —
**does not describe the code**. `Violation.hint` has six construction sites: five
hardcoded English strings and one `_suggest()` computed from the function's own
signature. `FunctionContract` has `caller`, `caller_pattern`, `admits`,
`requires_any_of`, `mutually_exclusive`, `co_required` and `description`, and **no
hint field**: a user declaring a contract cannot supply hint text by any route.

What replaces the escape hatch is a template that is a bare placeholder, which
makes the dynamic part a **declared field** rather than an override:

```python
"ARG-ERR-CONTRACT-001": {
    "user_message": "'{caller}' does not accept the argument '{argname}'.",
    "user_hint": "{suggestion} Docs: {doc_url}",
    "dev_hint": "{suggestion} Extend the function contract if the argument is legitimate.",
}
```

The call site passes `suggestion=`. The catalog owns the framing, keeps the
per-profile variants, stays translatable, and the value reaches `report()`,
`events_by_fingerprint` and the bundle as data. Which codes accept a call-site
value is visible in the catalog, to a reviewer, instead of being discoverable only
by reading every raise site.

### 2. Documented or enforced? — **Enforced, by a static guard.**

`hint` returns as a **read-only derived property** on `CatalogException` and
`CatalogWarning`, re-resolved from `self.code` and `self.extra`:

```python
@property
def hint(self):
    if not self.code:
        return None
    _, hint = smonitor.resolve(code=self.code, extra=self.extra or {})
    return hint
```

It holds nothing, so the `args` invariant is untouched and
`tests/test_catalog_instance_round_trip.py` stays green — verified with a
prototype: `pickle` and `copy.deepcopy` reproduce the hint exactly.

The property is also the enforcement, at no cost: `self.hint = x` in a subclass
raises `AttributeError: property 'hint' ... has no setter`, at the exact line that
is wrong. No `__init_subclass__` is needed, which is fortunate, because it cannot
see assignment order at class creation.

For the names it cannot protect that way — `code`, `message`, `raw_message`,
`extra` — the rule is written **and** guarded by an AST check shipped in section 7
of the canonical guide, in the shape of this repository's own
`tests/test_no_package_attribute_reachthrough.py`. Documenting alone was rejected:
a hand-maintained rule in prose is exactly what drifted in the three configuration
key lists, in the guide sync list, and in the validator allowlist, all reconciled
the same day this was decided.

Run across the ecosystem, that guard finds **7 assignments, all in one file**:

```
argdigest/core/errors.py:22   DigestError.self.raw_message       (before super().__init__)
argdigest/core/errors.py:26   DigestError.self.code              (before super().__init__)
argdigest/core/errors.py:27   DigestError.self.hint              (before super().__init__)
argdigest/core/errors.py:76   DigestNotDigestedWarning.self.code (before super().__init__)
argdigest/core/errors.py:77   DigestNotDigestedWarning.self.hint (before super().__init__)
argdigest/core/errors.py:125  FunctionContractWarning.self.code  (before super().__init__)
argdigest/core/errors.py:126  FunctionContractWarning.self.hint  (before super().__init__)
```

Every other library: zero.

### 3. Do ArgDigest's hardcoded hints move to its catalog first? — **Yes, and it is a precondition, not a preference.**

`exc.hint` today means the *call-site* hint. The derived property returns the
*catalog* hint. Same name, different value. If the property lands before
ArgDigest's prose is in its catalog, three tests and one health check do not fail —
they keep passing while asserting something else. The migration has to come first
so the change is a rename with a visible diff rather than a silent redefinition.

It is also ArgDigest's own bug: it puts `hint` into `extra`, `Manager.emit` does
`setdefault("hint", ...)` so the value reaches the event, and
`_resolve_message_and_hint` never consults `extra["hint"]` — so its hints appear in
telemetry and are invisible in what the user reads.

The work is smaller than it sounds, and none of it depends on SMonitor changing:

| | size |
| --- | --- |
| catalog templates edited (`{message}` stops being the user template) | ~4 entries |
| hardcoded user-facing strings moved into the catalog | 5 call sites |
| `_suggest()` becomes the `{suggestion}` field | 1 call site |
| assignments to base-owned names removed | 7, one file |

## What was rejected, and why

**A `violation_code` on `FunctionContract`.** Proposed here during the same
session and withdrawn on measurement. It would let a host library give its own
wording to a contract violation, which sounds right and is not supported by the
demand:

- A contract can be violated in **five** ways (`unknown_domain`,
  `unknown_argument`, `missing_argument`, `mutually_exclusive`, `co_required`), and
  MolSysMT's `get_neighbors` contract can fail in two of them. One code per
  contract would render "use one or the other, not both" at a caller who passed
  neither, so it would have to be per kind — more surface still.
- Counting the real `(contract, kind)` pairs across the suite gives **14**, of
  which **13 are `unknown_argument`**, where ArgDigest already computes a
  did-you-mean from the real signature with `difflib`. No static host string beats
  it.
- MolSysViewer's own contract docstring says it is satisfied: *"Declaring the rule
  turns it into a catalogued `MissingArgumentError` carrying the caller and the
  accepted names."*
- MolSysMT's docstring — *"a catalogued diagnostic that names both arguments"* — is
  **already met**: the generic message names both arguments and is catalogued. An
  earlier reading of this document claimed otherwise; it was wrong.

That leaves one contract in the whole suite that might want its own wording. Adding
API to a pre-1.0 library at a freeze, for one case, is not a trade worth making.

**What would reopen it:** a host library demonstrating a contract whose violation
genuinely needs wording ArgDigest cannot produce, with the kind identified. The
shape is then `codes={<kind>: <code>}`, validated at contract-registration time —
which is possible, because `ensure_configured` runs at line 23 of
`molsysmt/__init__.py`, before any contract module is imported, so the host's codes
are loaded by the time a contract is declared. Verified: codes from two packages
merge into one manager, and a middle library resolves a host's code correctly.

**Making `message` a derived property too, for symmetry with `hint`.** Rejected.
`hint` re-resolves at access while `message` is a snapshot from construction, so
the two can disagree if the profile changes between them. Deriving `message` would
make them consistent and would touch `args`, which is the invariant that cost the
`0.13.0` round-trip work. The profile is set in `configure()`, before any
diagnostic is raised; in practice they do not diverge. Documented as a bounded
consequence instead.

## Guards that already exist

`tests/test_catalog_instance_round_trip.py` fails if anything reintroduces state
outside `args`, including a stored `hint`. Any implementation of this decision has
to keep it green; the prototype does.
