---
summary: Refresh client guidance for published SMonitor 0.21 and 0.22 contracts.
issue: uibcdf/smonitor#51
status: resolved
opened: 2026-10-22
closed: 2026-10-22
verification: inspected
area: [documentation, integration, ecosystem]
guard:
normative: standards/SMONITOR_GUIDE.md
blocked_by: []
supersedes: []
---

# Client guide for SMonitor 0.22

The canonical guide at `99d5c3d28e738b6ad6cde73f01c2f3f6d98f71ba`
identified SMonitor 0.20.0 and omitted already published 0.21.0 safe audience
metadata templates and identity bundles, plus 0.22.0 pytest policy. Those
omissions were inspected against the released APIs, maintained user/developer
documentation and their existing contract tests.

The source guide now identifies 0.22.0 and documents each optional capability's
own floor. It covers metadata template precedence and safe interpolation,
explicit approval and incomplete coverage of narrow identity exports, receptor
artifact ownership, independent pytest/policy exit statuses, catalog checks,
baseline stability limits, and required-diagnostic witnesses. Its support flow
now explicitly exports a memory-buffer bundle inside the producing process;
a later CLI process cannot recover a terminated pytest process's events.

The README points to the central registry instead of maintaining a stale local
client/integration inventory. No runtime API, dependency floor, policy caller,
tag or package is changed by this documentary update.

## Ownership and delivery

Advance notice was delivered to uibcdf/molsyssuite#106 before publishing the
guide. Its registered inventory lists eleven guide clients: ArgDigest,
DepDigest, PyUnitWizard, MolSysMT, MolSysViewer, TopoMT, PharmacophoreMT,
ElastNetMT, LindeLint, Ackredit and DockingMT. Central `suite_status.py` refreshed
their Git state; unrelated dirty, ahead and behind primary checkouts are
preserved. Official copies come from MolSysSuite's `sync_vendored_guides.py`.

The provider owns this canonical-content resolution. Published copy delivery
and review remain coordinated in uibcdf/molsyssuite#106, independently of
optional scoped receiving or adoption of the new pytest policy. Guide delivery
does not close an owner's runtime or scientific receiving decision.

## Validation

Use the existing metadata-template, identity-bundle, pytest bridge/policy,
guide-audit and developer-report contract tests. Review examples against their
released implementations, check Python snippet formatting, and verify generated
developer-guide indexes. Documentary content is maintained in the normative
guide rather than frozen by text-matching tests.

Local Python 3.14 validation passed 182 selected contract/report tests. The
canonical Markdown's Python snippets pass the owner's Ruff formatter, and
`git diff --check` and the generated archive index check pass.

## Delivery handoff, 2026-10-22

The maintainer selected a dedicated MolSysSuite delivery task:
uibcdf/molsyssuite#124. MolSysSuite developers have explicit permission to
commit and push this bounded guide-only rollout directly, without PRs.
uibcdf/molsyssuite#106 links the task and retains its independent receiving
decisions. No client commit, push or PR was created during provider preparation.
The eleven generated temporary copies were preparation evidence only; their
publication and final default-branch audit belong to the central delivery task.
