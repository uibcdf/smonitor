# End-User First Contact and Rescue

This showcase targets people using a host library that embeds SMonitor.

## Problem

A task fails or warns, and the user needs a clear path to continue without
reading internal implementation details.

## Pattern

Use profile-aware messages with explicit hint fields and a short rescue flow.

```python
import A
import smonitor

smonitor.configure(profile="user", verbosity="normal")

# A emits a user-facing warning through SMonitor:
# "Selection is ambiguous. Hint: use atom_name == 'CA'."
mylib.select(query="all")
```

Rescue flow for end users:
1. read the message and apply the hint;
2. retry with a safer input;
3. if needed, switch to `profile="dev"` temporarily;
4. optionally export a redacted bundle for support.

```bash
smonitor export --out smonitor_bundle --drop-extra --redact extra.password
```

## Why this works

- the message explains both cause and next step;
- profile escalation is available only when needed;
- support receives reproducible context with less back-and-forth.

## Where to apply

- notebooks and interactive scripts;
- CLI workflows used by non-expert users;
- support and issue-reporting templates in the host library.
