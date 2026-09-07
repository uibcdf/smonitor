---
summary: One line, present tense. Becomes the issue title.
issue: uibcdf/smonitor#000
status: open
opened: 2026-01-01
closed:
severity: medium
verification: asserted
area: []
guard:
normative:
blocked_by: []
supersedes: []
---

# <Title: the defect, or what is proposed — not the fix>

**Reported:** <date, and how it surfaced — a suite run, a downstream report, an
ecosystem sweep, a design question that turned out to be a defect.>

<!--
One template for both queues. The directory decides which this is:

  pending_bugs/       a defect. `severity` is required.
  pending_proposals/  work not yet part of the contract. Remove `severity`.

Open the issue first, to obtain the number — `issue:` must not stay at #000.

The three sections below are the same spine the issue carries, expanded. Delete
this comment and any section that genuinely does not apply, but do not delete a
section because it is hard to fill: an empty "What was refuted" and a missing one
say different things.
-->

## What

**Bug:** the behaviour that is wrong, with the command that produces it pasted,
not paraphrased.

**Proposal:** what is proposed, in a paragraph. If it does not fit in a
paragraph, it is more than one proposal.

```python
import smonitor
...
```

## How

**Bug:** where it goes wrong, with `file.py:line`. If the cause is not yet known,
say so — an unfinished diagnosis is a fact, and `verification: asserted` records
it honestly.

**Proposal:** how it would be done, at the level of which seam changes. Not a
patch.

## Why

Which public surface is affected and who hits it. For a proposal, the problem it
solves and the evidence behind it — a measurement, a downstream report, a
workflow that is awkward. Not enthusiasm.

## What was refuted

The paths that looked right and were not, and how they were ruled out. This is
the section that saves the next person a day, and the one most often skipped.

<!--
Two habits worth keeping, both from things that cost us:

- Say which layer you verified at. A claim read in the source is `inspected`; a
  claim that was run is `reproduced`. Mislabelling that is how a wrong diagnosis
  reaches a sibling repository, and it has.
- A diagnostics library is consumed by other libraries. Where a claim is about
  how a downstream library behaves, say which one and at which commit: their
  catalogues change under us.
-->

## Resolution

<!--
Filled at close, not before. Then: set `status`, `closed`, and `guard` — the test
that fails if the defect returns. For a proposal whose outcome is a rule rather
than a behaviour, set `normative` instead: the document that absorbed the durable
rules.

Move this file to `devguide/archive/` and close the issue.

Once archived this document is immutable evidence. A claim that turns out to be
false gets an appended, dated correction note — never an edit to the original
claim.
-->
