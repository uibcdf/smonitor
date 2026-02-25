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

## You are done when

- each profile has explicit message/hint behavior in your catalog,
- user profile avoids unnecessary internal jargon,
- dev/qa/agent profiles preserve structured diagnostic detail.
