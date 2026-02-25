# AI Agents Workflow for Library Integrators

This page defines the minimum contract so AI agents can safely consume SMonitor
signals from your library `A` without breaking human workflows.

## Why this matters

If your team uses agents for triage, QA, or patch proposals, the agent needs:
- stable machine-readable identifiers (`code`, `signal`),
- deterministic structure in events,
- reproducible artifacts (bundles),
- explicit safety limits.

Without this, agent output is noisy and difficult to trust.

## Required operational contract in `A`

1. Keep `code` values stable once published.
2. Keep `signal` names stable and descriptive.
3. Emit actionable `hint` for human users in `user` profile.
4. Ensure `agent` profile keeps compact, structured output.
5. Enable local bundle export in support flows.
6. Keep strict validation enabled in CI:
   - `strict_signals=True`
   - `strict_schema=True`

## Recommended profile usage

- `user`: clear natural language, actionable next step.
- `dev`: richer context for implementation debugging.
- `qa`: strict checks + explicit contract failures.
- `agent`: concise machine-oriented payload with low ambiguity.

## CI pattern for agent-readiness

Add these checks in CI:
- tests run with strict signal/schema settings,
- a smoke test that exports a bundle,
- snapshot/assertions for representative emitted events.

This ensures agents always receive a stable data contract.

## Guardrails for autonomous tooling

- Never auto-merge fixes produced from agent triage.
- Require human review for any patch suggested from SMonitor output.
- Prefer deterministic triage keys (`code`, `trace_hash`) before free-text matching.
- Redact sensitive fields before sharing bundles externally.

## Practical flow

1. User or CI run emits SMonitor events.
2. Bundle is exported locally.
3. Agent consumes bundle/event stream and proposes diagnosis.
4. Human reviews diagnosis and proposed patch.
5. Fix is validated with tests and strict checks.

## Related references

- [Bundles and Export](../bundles-and-export.md)
- [Profile Decision Matrix](profile-decision-matrix.md)
- [Integration Testing Template](integration-testing-template.md)
- [Message Style by Profile](../message-style-by-profile.md)
- [SMONITOR_GUIDE.md](https://github.com/uibcdf/smonitor/blob/main/standards/SMONITOR_GUIDE.md)
