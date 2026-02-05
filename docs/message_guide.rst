User Message Guide
==================

This guide defines how messages should be written for each profile.

User
----

- Clear and calm.
- Always state what happened and how to fix it.
- Avoid internal jargon.

Template::

  Error: <what happened>.
  Solution: <what to do>.
  Example: <short example>.
  More help: <optional URL>.

Dev
---

- Technical and precise.
- Include context and hints.

Template::

  Error [CODE]: <message>
  Context: function=..., arg=..., value=...
  Hint: ...

QA
--

- Reproducible and structured.

Template::

  [CODE] <message> | function=... | input=...
  Expected: yes/no

Agent
-----

- Machine-readable and minimal.

Template::

  code=... category=... action=... extra.foo=...
