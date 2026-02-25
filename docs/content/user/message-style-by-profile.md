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

## `agent`

- machine-readable and minimal fields.
