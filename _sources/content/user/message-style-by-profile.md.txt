# Message Style by Profile

Use profile-specific communication so diagnostics help the right audience.

## `user`

- clear and calm,
- explain what happened,
- show concrete fix.

Template:

```text
Error: <what happened>.
Solution: <what to do>.
Example: <short example>.
```

## `dev`

- technical precision,
- include context and code.

Template:

```text
Error [CODE]: <message>
Context: function=..., arg=..., value=...
Hint: ...
```

## `qa`

- reproducible and structured.

Template:

```text
[CODE] <message> | source=<module.func> | input=<summary>
Expected: <expected-behavior>
Observed: <observed-behavior>
```

## `agent`

- machine-readable and minimal fields.

Template:

```text
code=MYLIB-E101 level=ERROR source=mylib.core.analysis.run action=fix_input extra.argument=format
```

## Which field each profile reads

| profile | message | hint |
| --- | --- | --- |
| `user` | `user_message` | `user_hint` |
| `dev`, `debug` | `dev_message` | `dev_hint` |
| `qa` | `qa_message` | `qa_hint` |
| `agent` | `agent_message` | `agent_hint` |

When a profile's own field is absent, resolution falls back through the nearest
audience and ends at the `user_*` field; a generic `message` sits in the middle
of every message chain. An entry that defines any message field therefore
renders in every profile, and writing all four is a choice rather than a
requirement.

Write a variant where the audiences genuinely need different wording — the end
user told what happened, the developer given the exception type — and write one
sentence once where they do not.


## Shared event structure

- exported events and JSON payloads now preserve both:
  - `human_summary`: concise human-facing handoff fields,
  - `normalized`: machine-oriented stable fields for QA/agents.
- this avoids forcing support tooling to reconstruct the human view from raw machine payloads.

## You are done when

- each profile has explicit message/hint behavior in your catalog,
- user profile avoids unnecessary internal jargon,
- dev/qa/agent profiles preserve structured diagnostic detail,
- exported artifacts keep human and machine views explicit.
