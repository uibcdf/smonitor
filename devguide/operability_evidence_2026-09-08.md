# Operability confirmed in a real workflow — 2026-09-08

Evidence for exit criterion 5 of `implementation_plan.md`: *operability is
confirmed in at least one real CI/support workflow, exercising fingerprints,
runtime identifiers, triage summaries, bundle comparison, and dual human/agent
output.*

The workflow chosen is the one a maintainer actually has, rather than a scenario
written to make the tooling look good: **what diagnostics does this component
emit, and what changed?** It was run against ArgDigest's suite, and it produced
two findings about SMonitor that no test had.

## The workflow

Nothing was added to ArgDigest. The event buffer and the level arrive through the
environment, which the component's own `ensure_configured()` reads on import:

```bash
SMONITOR_EVENT_BUFFER=5000 SMONITOR_LEVEL=DEBUG pytest -q tests
```

That a component can be instrumented from outside, with no change to its code, is
itself worth recording: a support workflow rarely gets to edit the library it is
diagnosing.

The harness runs the suite in-process, then `smonitor.export_bundle(...)`. Two
bundles were taken — the component before and after `uibcdf/argdigest@5d3825e`,
each against the matching SMonitor — and compared with `smonitor compare`.

## What one run produced

226 tests, **289 events, 31 distinct fingerprints**, with `run_id` and
`session_id` on every event.

```
top_codes                          top_sources
  13  ARG-ERR-VAL-001               219  argdigest
   9  ARG-WARN-MISS-001              21  argdigest.core.registry.run
   8  ARG-ERR-CONTRACT-001           17  argdigest.core.decorator.wrapper
   4  ARG-ERR-MISS-001                9  argdigest.warning.missing
   4  ARG-ERR-TYPE-001                2  pyunitwizard.parse.parse
```

`recurrent_incidents: 5`, `blocking_incidents: 10`. The cross-library line —
`pyunitwizard.parse.parse` appearing in ArgDigest's run — is the breadcrumb
working.

## Finding A — a fingerprint is only meaningful for a coded event

**219 of the 289 events, 76% of the run, share one fingerprint. They carry 102
distinct messages.**

They are `logging` calls captured by the logging bridge: `level=DEBUG`,
`code=None`, `category=None`, `extra={module, funcName, smonitor}`. The
fingerprint is derived from `code`, `source`, `exception_type` and a fixed subset
of `extra`, and the message is deliberately excluded so that a varying message
does not split one incident. When `code` is absent, that reduction degenerates:
every uncoded event from one source becomes the same incident.

The consequence is not academic. `top_fingerprints` reports its top entry as one
incident seen 219 times, when it is 102 different things. A reader triaging that
bundle is told the loudest thing in the run is a single recurring problem, and it
is not.

This is a limitation of the fingerprint contract, not a defect in this component.
Filed as `uibcdf/smonitor#11`.

## Finding B — the comparison caught a broken integration without a traceback

The first comparison paired ArgDigest *before* its catalogue migration with
SMonitor *after* the `hint` property landed — a pairing the coordinated change
had made invalid, and one nobody would deliberately construct.

The bundle said so at a glance: **234 events, 0 with a code, 16 at ERROR.** A
catalogue-driven component emitting no coded diagnostics and sixteen errors is a
signature, and it needs no stack trace to read.

That is bundle comparison doing what it is for, on a case that was not staged.

## Finding C — the fair comparison detected the semantic change, and nothing else

Pairing each side with its matching SMonitor:

```
## Fingerprints
- new: 2      - disappeared: 1      - recurrent: 29

## Code delta
- `ARG-ERR-OPTDEP-001`: 0 -> 3 (+3)
- `ARG-ERR-TYPE-001`:   7 -> 4 (-3)
```

Three events moved from "wrong type" to "optional dependency missing", which is
exactly the reclassification `5d3825e` made and the only semantic change in it.
The comparison reported it with no other noise: two new fingerprints, one gone,
twenty-nine recurrent.

## Finding D — prose leaving the machine payload, measured

Counting the keys of `extra` on coded events, before and after the migration:

| key | before | after |
| --- | ---: | ---: |
| `message` (a pre-rendered sentence) | 44 | 9 |
| `detail` (the typed fact) | 0 | 41 |
| `argname`, `caller` | 44 | 44 |
| `hint` | 44 | 44 |

The nine remaining `message` entries are **not** unconverted call sites: they are
the empty string, injected by SMonitor's own `DiagnosticBundle.warn()`, which
does `payload.setdefault("message", msg)` with an empty `msg` for a warning
rendered from its catalog. `hint` is unchanged for the same reason — `emit()`
puts the resolved catalog hint there deliberately.

## What this closes, and what it does not

Exercised: **fingerprints** (31 of them, and their limit), **runtime identifiers**
(`run_id`/`session_id` on every event), **triage summaries** (`top_codes`,
`top_sources`, `top_fingerprints`, recurrent and blocking), **bundle comparison**
(twice, once on an invalid pairing and once on a real change), and **dual output**
(the human line at DEBUG in the terminal, the coded payload in the bundle).

Not exercised: the `agent` profile end to end through a component, and
`correlation_id`, which stayed `None` because nothing set it. Both are available
and neither is load-bearing for this criterion.

## Reproducing

`devtools/operability_evidence.py` runs the whole thing: two bundles, the
comparison, and the counts above.
