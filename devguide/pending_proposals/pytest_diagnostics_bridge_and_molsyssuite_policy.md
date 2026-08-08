# Pytest Diagnostics Bridge and MolSysSuite Policy Layer

**Status:** exploratory proposal input; requires later digestion with the
existing exception/agent, pytest/CI, operability, and pytest-receptor proposals
before any implementation decision

**Recorded:** 2026-07-17

## Purpose

Define how SMonitor diagnostics should participate in pytest runs without
creating a second competing test reporter, and record the possible future role
of a lightweight `pytest-molsyssuite` package for shared development and CI
policy across the MolSysSuite repositories.

This proposal refines the post-1.0 "Project A — Pytest/CI Diagnostic
Integration" in `devguide/implementation_plan.md`. That plan correctly
identifies the need for pytest correlation, stable triage keys, redacted
artifacts, and CI integration. The appearance of pytest-receptor changes the
appropriate ownership boundaries: SMonitor should not independently recreate
pytest failure collection, grouping, terminal summaries, and test artifacts if
pytest-receptor already provides the evidence and rendering layer.

## Relationship to existing SMonitor agent communication

SMonitor already has a broader and more fundamental agent-communication path
that is independent of pytest. It includes:

- structured events emitted when instrumented code raises and re-raises an
  exception;
- catalog-backed exception and warning semantics;
- stable normalized payloads for the `agent` profile;
- codes, signals, fingerprints, evidence, causal metadata, confidence, and
  recommended next steps;
- local bundles, triage summaries, and bundle comparison;
- human/agent dual output;
- support and repair workflows consuming those diagnostics.

That path answers: "How should a scientific library communicate a runtime
diagnostic or raised exception to a human, agent, or support workflow?" It must
remain useful in scripts, notebooks, services, interactive sessions, and any
other environment where pytest is absent.

The pytest bridge proposed here answers a different and narrower question:
"When the runtime diagnostic occurs during a pytest session, how is it
correlated with the exact test, phase, worker, attempt, and pytest outcome?"

pytest-receptor answers a third question: "How is pytest execution evidence
preserved, grouped, budgeted, and rendered for its consumer?"

The future pytest-molsyssuite concept answers a fourth: "Which shared QA and CI
policies should MolSysSuite repositories apply to those existing contracts?"

These lines may share identifiers and artifacts, but none should subsume the
others accidentally. In particular:

- the general SMonitor agent/exception contract must not become pytest-only;
- pytest-receptor must not become a SMonitor-specific runtime diagnostic
  framework;
- the pytest bridge must not reinterpret every pytest failure as a new domain
  diagnostic when pytest already owns that evidence;
- pytest-molsyssuite must not become another event collector or renderer.

The pending proposal `catalog_signals_lose_structured_extra.md` is especially
relevant: structured exception and warning fields must survive at the raise and
catch boundary before pytest correlation can preserve them. A pytest bridge
cannot recover semantics already downgraded to prose.

## Provisional direction for later digestion

- A pytest–SMonitor integration is valuable and should be pursued.
- Initially implement it inside SMonitor, for example as
  `smonitor.pytest_plugin` or an optional `smonitor[pytest]` extra.
- Do not create a separate `pytest-smonitor` repository or distribution until
  the integration contract is stable and has external consumers.
- SMonitor should contribute structured diagnostic events and correlation
  context; it should not replace pytest-receptor's session collector or
  renderer.
- ArgDigest and DepDigest diagnostics should flow through SMonitor rather than
  require independent pytest reporters.
- A future `pytest-molsyssuite` package can compose policies, profiles,
  fixtures, validators, and artifacts across sibling projects.
- `pytest-molsyssuite` must remain a thin policy layer, not another terminal
  reporter, event store, or diagnostic framework.

## Ownership model

```text
pytest lifecycle
    |
    v
pytest-receptor
    - session/test/phase/worker evidence
    - complete/incomplete execution state
    - reversible grouping and rendering
    - canonical pytest event artifact
    ^
    |
SMonitor pytest bridge
    - SMonitor event correlation
    - diagnostic codes, context, evidence, and hints
    - fixtures/markers for expected diagnostics
    - optional strict QA policy
    ^
    |
SMonitor integrations
    - ArgDigest, DepDigest, MolSysMT, MolSysViewer, PyUnitWizard, and others
    ^
    |
pytest-molsyssuite
    - shared profiles, baselines, policy, and ecosystem manifests
```

The same incident must not become unrelated pytest, SMonitor, warning, and
MolSysSuite records. Events need shared identifiers or explicit relationships
so consumers can present one causal chain rather than duplicate noise.

## SMonitor pytest bridge

### Primary responsibility

Associate structured SMonitor events emitted during a pytest run with the
pytest execution context in which they occurred.

The bridge should add or relate:

- pytest run identifier;
- node ID;
- phase (`setup`, `call`, `teardown`, collection, or session);
- xdist worker identifier;
- execution attempt or rerun;
- monotonic event sequence;
- receptor event identifier when available;
- SMonitor `run_id`, `session_id`, `correlation_id`, code, signal, fingerprint,
  severity, confidence, evidence, and recommended action.

### Context propagation

Do not store the current test in one mutable module global. Use `contextvars`
for in-process context and explicit worker/run identifiers for distributed
execution. Document that background threads and subprocesses may require
explicit context propagation.

The bridge must be correct for:

- setup, call, and teardown;
- async tests;
- threads that inherit or explicitly receive context;
- xdist workers;
- reruns;
- collection and session diagnostics;
- diagnostics emitted after a test call but during finalization.

### Diagnostics as first-class evidence

The bridge should transport the original normalized SMonitor payload rather
than rebuild it from the rendered message. Preserve stable structured fields,
including:

- `code`, `signal`, `source`, `category`, and level;
- event fingerprint and correlation identifiers;
- caller, operation, resource, provider, and form;
- incident kind, severity, priority, and confidence;
- expected/observed structured evidence;
- causal chain, cause code, and exception type;
- retry state and exhaustion;
- recommended action, next step, and support requirement;
- redaction metadata and human summary.

### Fixtures and markers

Potential test-facing capabilities include:

```python
@pytest.mark.expect_diagnostic(
    code="ARGDIGEST-WARN-MISSING-DIGESTER",
    count=1,
)
def test_legacy_argument():
    ...
```

Candidate fixtures:

- `smonitor_events`: events correlated with the current test;
- `smonitor_event_recorder`: bounded explicit recording context;
- `assert_smonitor_event`: structured code/payload assertion helper;
- `smonitor_profile`: controlled temporary profile with safe restoration;
- `smonitor_diagnostic_baseline`: comparison against an accepted fingerprint
  set.

Markers and fixtures must assert structured contracts, not rendered English
messages.

### Policy modes

Default behavior should observe without changing pytest outcomes. Strictness is
an explicit profile decision:

- `user`: ordinary library-facing diagnostics; no pytest policy mutation;
- `dev`: record and summarize diagnostic context;
- `qa`: fail or flag forbidden/invalid diagnostic contracts;
- `ci`: compare with baselines and expose new/disappeared/recurrent incidents;
- `agent`: compact structured context with evidence and verified next steps.

Possible QA violations include:

- unknown diagnostic code;
- missing catalog template;
- unresolved template placeholder;
- required structured field absent;
- SMonitor emission failure;
- unexpected error-level event;
- diagnostic explicitly forbidden by project policy;
- newly introduced warning fingerprint;
- redaction failure in an exportable artifact.

Whether a violation fails an individual test, marks the session as policy
failed, or only produces a report must be defined explicitly. A diagnostic
must not silently alter scientific test meaning under the default profile.

### Avoiding duplicate evidence

ArgDigest warnings may appear simultaneously as:

- a Python warning observed by pytest;
- an SMonitor event;
- captured stderr/logging;
- a later exception caused by the same contract violation.

The bridge and receptor need a correlation/deduplication policy based on stable
event identity and causal relationships. Do not deduplicate merely because two
rendered messages are equal. Preserve both records when they are independent,
and present one causal incident when one is a representation of the other.

### Artifact ownership

SMonitor may continue to export its standalone support bundle for workflows
outside pytest. Within a pytest-receptor run:

- pytest-receptor owns the canonical pytest event artifact;
- SMonitor events are embedded or referenced as namespaced extension events;
- an optional SMonitor bundle may be linked rather than silently duplicated;
- artifact paths, hashes, schema versions, completeness, and redaction policy
  must be explicit;
- neither system uploads evidence implicitly.

## ArgDigest and DepDigest behavior

Do not create a separate pytest reporter for each diagnostic-producing library.
ArgDigest and DepDigest already integrate through SMonitor and should emit
complete structured context there.

Useful ArgDigest fields include:

- decorated callable;
- argument name;
- safe value type/shape summary;
- selected or missing digester;
- digestion status and reason;
- strictness policy;
- passport/validated-payload use;
- double-digestion or bypass information;
- stable code, confidence, and evidence.

Useful MolSysSuite QA policies include:

- no new `DigestNotDigestedWarning` on stable public APIs;
- no missing digester for a documented public argument;
- no invalid passport reuse;
- no unexpected repeated validation on declared hot paths;
- no swallowed diagnostic emission failure;
- no top-level soft dependency import or dependency-policy violation.

Dependency and performance policies remain owned by their source validators;
pytest integration should compose their results rather than copy their logic.

## Possible pytest-molsyssuite package

### Product role

`pytest-molsyssuite` would standardize how MolSysSuite repositories configure
and evaluate pytest-receptor, SMonitor, ArgDigest, DepDigest, PyUnitWizard, and
repository-specific validators.

It is an ecosystem policy and composition package, not a general community
pytest reporter.

### Candidate capabilities

#### Shared profiles

- `molsyssuite-dev` for local diagnostics;
- `molsyssuite-qa` for contract enforcement;
- `molsyssuite-ci` for baselines and durable artifacts;
- `molsyssuite-agent` for compact structured triage.

Profiles should configure existing components through supported APIs. They must
not mutate unrelated global state invisibly.

#### Diagnostic policy

- accepted, forbidden, and severity-escalated diagnostic codes;
- warning/diagnostic fingerprint baselines;
- new, disappeared, and recurrent incident classification;
- policy for unresolved templates and missing structured fields;
- per-repository exceptions with owner, reason, and expiry;
- strictness by support tier or API stability.

#### Ecosystem manifest

Record, with privacy-aware defaults:

- package versions and source commit identifiers;
- Python, pytest, and plugin versions;
- active SMonitor and receptor profiles;
- optional dependency availability relevant to the test selection;
- xdist worker count and execution mode;
- relevant validator/schema versions;
- CI workflow/job identifiers when explicitly available.

The manifest should explain the environment without dumping arbitrary secrets
or the complete process environment.

#### Shared fixtures and markers

- standard demo molecular systems and small scientific fixtures where
  cross-repository use is justified;
- diagnostic expectation helpers;
- optional-dependency capability markers;
- cross-library version-compatibility fixtures;
- local artifact directory and cleanup fixtures;
- deterministic ecosystem health-check fixture.

Avoid moving domain-specific fixtures out of their owning repositories merely
for centralization.

#### CI artifact policy

- consistent artifact names and schemas;
- receptor event artifact plus optional linked SMonitor bundle;
- warning/diagnostic baseline diff;
- ecosystem manifest;
- redaction and restrictive-permission defaults;
- retention recommendations;
- no implicit remote telemetry.

#### Quality gates

- required repository validators discovered through declared entry points;
- public diagnostic catalog integrity;
- new diagnostic debt and missing ArgDigest policy detection;
- version compatibility between sibling packages;
- explicit complete/incomplete suite status;
- optional no-regression gates for diagnostic noise and validation overhead.

### Explicit non-responsibilities

`pytest-molsyssuite` must not:

- replace pytest or own a terminal reporter;
- duplicate pytest-receptor's event collector or renderers;
- duplicate SMonitor's event manager, catalogs, handlers, or bundles;
- implement ArgDigest, DepDigest, or PyUnitWizard validation internally;
- convert every warning into a failure without explicit policy;
- force all sibling libraries to release in lockstep;
- import every optional scientific dependency at plugin startup;
- upload artifacts or telemetry without explicit consent;
- make ordinary library tests depend on MolSysMT.

### Packaging and dependency boundaries

The package should depend on protocols or narrow supported versions, not on the
entire scientific stack. Optional integrations must be lazy. Repository
validators and domain fixtures should be discovered through entry points or
explicit configuration.

Circular dependency constraints:

- pytest-receptor remains neutral and cannot depend on SMonitor or MolSysSuite;
- SMonitor may optionally integrate with pytest-receptor's public extension
  protocol;
- pytest-molsyssuite may depend on or configure both;
- ArgDigest and other libraries emit through SMonitor but do not depend on
  pytest-molsyssuite at runtime.

### Extraction criteria

Do not create the package until the same needs are demonstrated in at least
three repositories. Before extraction, require:

- stable pytest-receptor extension/event contract;
- working SMonitor pytest bridge;
- successful MolSysMT and MolSysViewer dogfooding;
- at least one additional sibling repository confirming the policy set;
- no unresolved ownership duplication;
- measured startup, runtime, and memory overhead;
- a maintainer and compatibility policy.

Until then, prototype the policy in fixtures/configuration close to the owning
repositories and keep this proposal as the shared design record.

## Recommended implementation order

1. Complete pytest-receptor's correctness floor and extension event protocol.
2. Revise SMonitor Project A ownership to consume that protocol.
3. Implement the SMonitor bridge as an internal optional plugin.
4. Correlate SMonitor events with node ID, phase, worker, and attempt.
5. Dogfood on the known MolSysViewer ArgDigest-warning workflow.
6. Dogfood on MolSysMT with twelve-worker execution and Scientific Truth tests.
7. Establish diagnostic baselines and strict QA policy experimentally.
8. Validate the same policy in a third sibling repository.
9. Decide whether to extract `pytest-molsyssuite`.
10. Consider a separate `pytest-smonitor` distribution only after external
   adoption justifies an independent lifecycle.

## Acceptance criteria for the bridge

- SMonitor events are associated with the correct test, phase, worker, and
  attempt in serial and xdist runs.
- Default observation does not change pytest outcomes.
- Strict policy changes outcomes only through documented, tested rules.
- ArgDigest warnings are not presented multiple times as unrelated incidents.
- Unknown and plugin-defined events remain recoverable.
- Redaction occurs before export to a shared artifact.
- Receptor and SMonitor artifacts reference one another without silent
  duplication or conflicting session outcomes.
- Failure of the bridge never fabricates pytest success or swallows the original
  diagnostic.

## Future proposal digestion

Before accepting this proposal, perform a dedicated digestion across at least:

- SMonitor's general exception/raise and `agent` profile contracts;
- `catalog_signals_lose_structured_extra.md`;
- the implemented event, normalized payload, bundle, and comparison contracts;
- Project A's existing pytest/CI proposal in `implementation_plan.md`;
- pytest-receptor's critical audit, evidence architecture, trust criteria, and
  extension proposal;
- real ArgDigest/MolSysViewer and MolSysMT diagnostic examples;
- possible MolSysSuite policy needs observed in a third repository.

The digestion should classify every idea as:

- already implemented under a different name;
- valid general SMonitor responsibility;
- valid pytest bridge responsibility;
- valid pytest-receptor responsibility;
- possible pytest-molsyssuite policy;
- duplicate or conflicting proposal;
- rejected or deferred work.

It must also identify authoritative schemas and prevent parallel identifiers,
fingerprints, artifacts, or renderers from representing the same fact without
an explicit relationship.

## Proposal checkpoint

The capability appears valuable, but no implementation or ownership decision
is accepted by this document. First preserve all proposal information, then
digest it against the existing SMonitor exception/agent architecture and the
pytest-receptor boundary. Only the resulting consolidated decision should
revise normative roadmaps or start implementation.
