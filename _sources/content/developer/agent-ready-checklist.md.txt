# Agent-Ready Checklist

Use this checklist before release candidates and during stabilization.

## 1. Contracts and payload stability

- [ ] `agent` profile messages are machine-oriented and deterministic.
- [ ] Stable fields are present in payloads (`code`, `level`, `source`, `category` when available).
- [ ] Contract tests for agent payloads pass.

## 2. Deterministic triage

- [ ] Triage groups incidents by stable keys (`code` + context signature), not free text.
- [ ] Grouping rules are documented in the QA triage workflow.
- [ ] Repeated incidents from different runs map to the same group key.

## 3. Redaction and sharing policy

- [ ] Bundle export examples include explicit redaction fields.
- [ ] Team has a default redaction profile for internal sharing.
- [ ] Team has a stricter redaction profile for external sharing.

## 4. CI and release gate

- [ ] QA flow exports bundle artifacts for failed runs.
- [ ] Human review remains mandatory for agent-proposed fixes.
- [ ] Release notes mention any contract-relevant diagnostics changes.

## 5. Definition of done

- [ ] Agent workflow is reproducible from documented commands.
- [ ] No unresolved high-severity diagnostics regressions remain.
- [ ] Checklist review completed in the release PR.
