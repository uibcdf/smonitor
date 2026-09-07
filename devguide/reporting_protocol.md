# Reporting protocol

How a defect or a proposal enters this project, is worked on, and is closed.

This document is normative. It governs `pending_bugs/`, `pending_proposals/`,
`archive/`, and the GitHub issue board.

The vocabulary below is **not ours**. It is the MolSysSuite reporting vocabulary,
defined in [`uibcdf/molsysmt`'s `devguide/reporting_protocol.md`][msm] and adopted
here without adapting a word, which is the only thing that makes
`uibcdf/<repo>#<number>` a reliable reference in every direction. Where we differ
is stated at the end, and it is about tooling, not vocabulary.

[msm]: https://github.com/uibcdf/molsysmt/blob/main/devguide/reporting_protocol.md

## The rule

**If it deserves a document in `devguide/`, it deserves an issue.**

The document is already the significance filter — nobody writes a pending
document for a typo — so no second filter is needed.

The two records have different jobs:

| | holds | changes |
|---|---|---|
| the document | the analysis, the measurements, the refuted paths | continuously |
| the issue | state, and the settled facts a reader outside the repository needs | at two moments only |

The issue is written when it opens and when it closes, and is not maintained in
between. If the analysis changes on the way, the document is corrected; the
closing comment states the final truth.

## Identity

The issue number is the stable identity of a theme. Filenames are local names and
may change; issue numbers may not.

Cross-repository references use `uibcdf/<repo>#<number>`, never a path into
another repository's `devguide/`. A path breaks silently when the other side
renames or archives.

This is not theoretical here. On 2026-09-06 a decision record was filed at
`devguide/decisions/hint_ownership_on_catalog_instances.md` and referenced by
that path from a comment on `uibcdf/argdigest#2`. Adopting this protocol the next
day moved it, and the reference broke — which is the argument for issue numbers,
demonstrated at our own expense.

## Front matter

Every document under `pending_bugs/`, `pending_proposals/` or `archive/` begins
with YAML front matter:

```yaml
---
summary: A catalog message renders empty in every profile but its own.
issue: uibcdf/smonitor#12
status: open
opened: 2026-09-06
closed:
severity: high
verification: measured
area: [catalog, profiles]
guard:
normative:
blocked_by: []
supersedes: []
---
```

| field | required | meaning |
|---|---|---|
| `summary` | always | One line. Feeds the generated indexes and the issue title. |
| `issue` | always | `uibcdf/<repo>#<number>`. |
| `status` | always | See below. |
| `opened` | always | ISO date the document was filed. |
| `closed` | when not open | ISO date the status left the open set. |
| `severity` | bugs | `critical`, `high`, `medium`, `low`. |
| `verification` | always | How the report itself was verified. See below. |
| `area` | always | One or more free tags matching repository areas. |
| `guard` | see closing | Test that fails if the defect returns. |
| `normative` | see closing | Document that absorbed the durable rules. |
| `blocked_by` | optional | Issue references this waits on. |
| `supersedes` | optional | Issue references this replaces. |

`README.md` files carry no front matter; they are indexes, not reports.

### `status`

| value | meaning |
|---|---|
| `open` | Filed, not started. |
| `active` | Being worked on now. |
| `blocked` | Waiting on something named in `blocked_by`. |
| `partial` | Some phases done, the rest pending. |
| `resolved` | Done, with the guard or the normative document named. |
| `withdrawn` | The premise died. |
| `superseded` | Replaced by the theme named in the replacing document's `supersedes`. |

The first four are the **open set**; the last three are the **closed set**, and a
document in the closed set belongs under `archive/`.

### `verification`

How solid the report's own diagnosis is:

| value | meaning |
|---|---|
| `reproduced` | Run, and it failed as described. |
| `measured` | Numbers in the document, with the command that produces them. |
| `inspected` | Read in the source, not executed. |
| `upstream` | Confirmed to originate outside this repository. |
| `asserted` | Believed, not checked. |

`asserted` is permitted and is the honest label for a report filed before it is
verified. It makes the debt visible instead of letting a claim read as a finding.

## Filing

1. **Open the issue first**, to obtain the number.
2. **Write the document** from [`templates/report.md`](templates/report.md), with
   `issue:` filled in. One template serves both queues; the directory decides
   whether it is a defect or a proposal.
3. **Commit and push**, so the path the issue names exists on `main`.

The issue body at open is telegraphic — the reasoning belongs in the document:

```
What  — A catalog defining only `user_message` renders an empty message under
        every other profile.
How   — smonitor.resolve(code=..., extra={}) under profile="agent" returns ('', None).
Why   — Three libraries in the suite emit no message at all under `agent`, the
        profile whose whole purpose is machine triage.
Record — devguide/pending_bugs/<file>.md
```

For a proposal the three fields keep their names: **What** is what is proposed,
**How** is how it would be done in two lines, **Why** is the problem it solves.

### The asymmetry

It holds in one direction only:

- **Every document in a queue has an `issue`.** Always. The test checks this.
- **Not every issue has a document.** One awaiting triage has none, and one that
  cannot be reproduced closes with the reason and never gets one.

## Closing

An entry closes when three things exist: the change, the record, and something
that fails if the defect returns.

1. Set `status`, `closed`, and **`guard`** — the test that fails if it comes
   back. For a proposal whose outcome is a rule rather than a behaviour, set
   **`normative`** instead: the document that absorbed the durable rules. One of
   the two is mandatory for `resolved`; neither is for `withdrawn` or
   `superseded`.
2. Move the document to `archive/`.
3. Close the issue with a three-line comment:

```
Fixed in 25eb18e — fix(core): resolve a catalog message in every profile

For users — a catalog defining one message field now renders everywhere; a
            profile whose own field is present is unchanged.
Guard  — tests/test_profile_message_fallback.py
Record — devguide/archive/<file>.md
```

*For users* is the line that belongs in the issue more than in the document: the
document is written for us, the issue is read by them.

**Archive, never delete.** This is the one alignment the ecosystem protocol
requires, and the one we were breaking: closed documents used to be removed
outright, which silently breaks every reference into them.

## Corrections

A claim that turns out to be false is corrected, not left standing.

- **In the open set:** correct in place. The document is live.
- **Archived:** append a dated correction note. Do not edit the original claim —
  rewriting destroys the record of what we believed and when. A stale measurement
  needs no correction; it was true on its date. A claim that was *never* true
  does.

## Labels

| group | labels | who sets them |
|---|---|---|
| kind, exactly one | `bug`, `proposal`, `enhancement`, `documentation` | by hand, at open |
| state, zero or one | `in-progress`, `blocked`, `partial` | derived from `status` |
| triage | `needs-triage` | by hand, on arrival from outside |

No state label means open and unstarted. There is no `done` label: GitHub closes
issues.

## Indexes are generated

Each queue's `README.md` has a hand-written head — how to read the directory,
what it demands — and a generated block rendered from front matter:

```markdown
<!-- generated: devguide_index -->
...
<!-- /generated -->
```

The head is judgement and is written. The block is data. Maintaining a
hand-written list of documents that already describe themselves is two
authoritative lists, which is the drift this repository has spent its time
removing elsewhere.

```bash
python devtools/devguide_index.py           # write
python devtools/devguide_index.py --check   # fail if stale
```

## Where we differ

Three differences, all about tooling. The vocabulary is unmodified.

1. **The validator is a test, not a script.** MolSysMT runs
   `validate_devguide.py` from its release gate. Our gate is `pytest`, so the
   same checks live in `tests/test_devguide_reports.py` and run on every PR with
   no extra wiring. The checks are the same ones: front matter present and
   parseable, vocabularies respected, `issue` well formed, `severity` on bugs,
   `closed` consistent with `status`, `resolved` naming a `guard` that exists in
   the test tree or a `normative` document that exists, and the generated index
   blocks up to date.
2. **The archive is flat**, as in MolSysViewer. We have few documents, and moving
   them later breaks references — the argument this protocol makes for issue
   numbers over paths applies to our own files too.
3. **The board is worked by hand.** No script writes the opening or closing
   comment: that is where the judgement is, and a script would write it badly.

## Security

An exploitable finding is not opened as a public issue. It goes to a private
security advisory, and the local document stays out of the queues until a fix is
released. The protocol resumes at that point.
