# Showcase

This section provides three realistic integration showcases. Each example
targets a concrete use case so you can adapt the pattern that best matches
your library and your users.

## Example Catalog

| Showcase | What you will find |
|---|---|
| [Library Integration Contract](library-integration-contract.md) | How a developer of the host library wires `_smonitor.py`, `mylib/_private/smonitor`, and `@signal` with stable CODES/SIGNALS. |
| [End-User First Contact and Rescue](end-user-first-contact-rescue.md) | How an end user of the host library interprets messages, changes profile/verbosity, and follows a rescue flow with optional bundle export. |
| [QA + Agent Triage Pipeline](qa-agent-triage-pipeline.md) | How maintainers use strict checks, machine-readable outputs, and bundles for reproducible QA and AI-assisted triage. |

Use these showcases as copy-ready blueprints. Start with the one closest to your immediate need, then follow the full [Library Integrators](../user/library-integrators/index.md) route.

```{toctree}
:maxdepth: 1
:hidden:

library-integration-contract.md
end-user-first-contact-rescue.md
qa-agent-triage-pipeline.md
```
