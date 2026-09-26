---
summary: Resolve ArgDigest and DepDigest dependency cycles at SMonitor boundaries.
issue: uibcdf/smonitor#29
status: resolved
opened: 2026-09-26
closed: 2026-09-26
verification: measured
area: [architecture, ecosystem, dependencies]
guard: tests/test_support_library_bootstrap.py
normative: MOLSYSSUITE_GUIDE.md
blocked_by: []
supersedes: []
---

# Resolve support-library dependency cycles

## Resolution on 2026-09-26

MOLI commit [`15b38fb`](https://github.com/uibcdf/moli/commit/15b38fbe17b6ee9fa9aac2a8e21b80d76a8da70f)
adopted a narrow bootstrap-provider rule: while ArgDigest or DepDigest has a
required runtime dependency on SMonitor, local validation at that public
boundary is structurally applicable and must have behavior, diagnostic,
installation, and import-order tests. The rule requires reassessment if the
reverse dependency disappears. MolSysSuite
[`policy-v1.4.12`](https://github.com/uibcdf/molsyssuite/tree/policy-v1.4.12)
pins that MOLI decision and records SMonitor `support-libraries=adopted` with
the guard and clean-install evidence below. The temporary exception and its
expiry were removed from the central inventory.

The guard passed in hosted collective QA run
[`36233454261`](https://github.com/uibcdf/smonitor/actions/runs/36233454261)
with fresh provider source checkouts (three passed, none skipped). A clean
Linux/Python 3.13 Conda install of the published packages passed all six
import orders, public configuration and validation, and the missing-optional-
backend diagnostic. The policy guide copy is synchronized from the central
snapshot. These observations satisfy the scoped applicability rule on the
tested platforms; they do not assert all-platform installation coverage.

The historical checkpoint and exception rationale below record the state
before the normative decision. The exception is now closed.

## 2026-09-26 governance checkpoint

The dependency graph still has `argdigest -> depdigest -> smonitor` and a direct
`argdigest -> smonitor` edge. The alternative of retaining SMonitor diagnostics
inside those providers while adding either as a required SMonitor dependency
cannot satisfy the cycle-free acceptance criterion. SMonitor's existing local
validation and lazy backend handling remain the bounded exception, with no
claim that the inherited policy has changed.

MOLI owns cross-component applicability. `uibcdf/moli#29` now asks whether a
narrow rule for diagnostic bootstrap providers is appropriate, or whether the
providers must remove the reverse runtime edges. The central MolSysSuite
inventory remains `excepted` until that normative decision is effective and
the public-boundary, installation and import-order evidence below passes.
This report is blocked on that decision; neither closing it nor advancing the
inventory would be accurate yet.

The preparatory guard reads installed provider metadata and rejects a required
SMonitor dependency that would close a reverse edge. With ArgDigest and
DepDigest installed, it also exercises all six import orders in subprocesses
and checks that SMonitor's public configuration and event validation still
work. These tests protect the current bootstrap boundary; they do not settle
MOLI applicability or prove a clean Conda installation on every claimed
platform.

Commit `21fd597` runs the guard in the hosted QA collective job against fresh
ArgDigest and DepDigest source checkouts, with missing siblings treated as a
failure. QA run `36233454261` passed both jobs; the collective job reported
three passed (the existing cross-library path plus both bootstrap tests), with
no skipped test. Routine CI and the MolSysSuite policy workflow also passed at
that commit. This proves the source checkout dependency and import-order
contract on hosted Linux.

A separate clean Linux `linux-64` Conda environment installed the published
`smonitor=0.17.3`, `argdigest=0.13.0`, and `depdigest=0.11.1` together with
Python 3.13 from `uibcdf` and `conda-forge` using strict channel priority:

```bash
conda create --prefix /tmp/smonitor-bootstrap-conda-proof \
  --override-channels -c uibcdf -c conda-forge --strict-channel-priority \
  python=3.13 smonitor=0.17.3 argdigest depdigest -y
```

Using that environment's Python with `-I` and working directory `/tmp`, all
six permutations of importing the three installed packages passed. Each
process also called public `smonitor.configure(handlers=[])` and verified
`validate_event` rejected an incomplete event. The environment did not contain
`rich`; `smonitor.configure(theme="rich")` produced an `ImportError` naming
the missing backend. This is installed-package and optional-backend evidence
for Linux/Python 3.13. The policy decision and other claimed platforms remain
outstanding.

The completed member review in `uibcdf/smonitor#24` found two applicable
support-library boundaries. Public configuration and event validation are
ArgDigest-shaped; the optional `rich` console backend is DepDigest-shaped.
ArgDigest depends on DepDigest and SMonitor, while DepDigest depends on
SMonitor. A runtime dependency in the reverse direction would create a cycle.

The temporary exception keeps SMonitor's bootstrap validation and lazy
optional-backend handling local. Its owner is the SMonitor maintainers and its
expiry is 2027-03-26. The central MolSysSuite inventory tracks the same
exception as `support-libraries=excepted`; this is not an adoption claim.

Before expiry, choose a cycle-free dependency structure or obtain a revised
applicability rule through MOLI and MolSysSuite governance. Verify the chosen
contract with public validation, optional-backend, installation and import-order
tests. Remove the exception only after that evidence is published and the
central inventory is updated.
