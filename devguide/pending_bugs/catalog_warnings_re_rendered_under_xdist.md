# Catalog warnings are re-rendered when a suite runs under pytest-xdist

**Status:** diagnosed, not ours to fix. Reproduced 2026-08-15.
**Owner:** pytest-xdist (upstream). MolSysMT and any library with catalog
warning subclasses that take a domain field positionally are affected.

## Symptom

Running MolSysMT's suite with `-n 12` reports warnings whose text is nested
inside itself:

```
UnknownAtomNameWarning x50 | Atom name 'Atom name 'Ar' is not recognized; atom
                             type 'UNK' will be used. Provide an explicit...
GpuNotAvailableWarning x15 | GPU acceleration was requested but is not
                             available: GPU acceleration was requested but is
                             not available: MolSysMT 1.0...
```

A second shape appears in the same run, with the class path glued to the front:

```
CrossChainCovalentBondsWarning x1 | molsysmt._private.smonitor.warnings.
                                    CrossChainCovalentBondsWarning: Cross-chain
                                    covalent bonds were detected...
```

This is the report previously filed as "catalog warning messages are rendered
twice". It was investigated twice and never reproduced, because both attempts
ran serially.

## It is not SMonitor, and not the call site

Two earlier hypotheses were wrong. It is not two competing resolve+append sites
inside `DiagnosticBundle.warn` (fixed in `0c556d8`, a real but different
defect), and it is not a call site pre-rendering the sentence: MolSysMT passes
`extra={"atom_name": atom_name}`, exactly as the guide prescribes.

Serial and parallel runs of the same four warnings differ by exactly this:

| run | text |
|---|---|
| `pytest --receptor=llm` | `Atom name 'Ar' is not recognized; ...` |
| `pytest --receptor=llm -n 2` | `Atom name 'Atom name 'Ar' is not recognized; ...'` |

pytest-receptor is not the cause either; its `pytest_warning_recorded` hook only
takes `str(warning_message.message)`.

## Mechanism

`xdist/workermanage.py::unserialize_warning_message` rebuilds the warning on the
controller from what the worker sent:

```python
cls = getattr(mod, data["message_class_name"])
message = cls(*data["message_args"])          # message_args is the original .args
except TypeError:
    message = Warning(f"{module}.{cls}: {message_str}")
```

`CatalogWarning.__init__` ends in `super().__init__(full_message)`, so `.args`
is `(rendered_message,)`. On the controller that becomes:

- `UnknownAtomNameWarning(rendered_message)` — whose signature is
  `__init__(self, atom_name)`, so the rendered text lands in `atom_name` and the
  catalog template wraps it a second time;
- `GpuNotAvailableWarning(rendered_message)` — same, via `reason`;
- `CrossChainCovalentBondsWarning(rendered_message)` — signature takes three
  required arguments, so `TypeError` sends it to the generic fallback, which is
  the prefixed shape above.

Confirmed directly: `UnknownAtomNameWarning("<rendered text>")` reproduces the
doubled string character for character.

## Why it surfaced now

Before `dd54a9b`, `DiagnosticBundle.warn()` emitted the catalog event and
returned without raising a Python warning at all, so there was nothing for xdist
to marshal. Restoring standard warning semantics is what made this visible. The
diagnostics themselves are correct; only the controller's reconstruction of them
is wrong, and only under xdist.

## Options, none taken

1. Report upstream. The reconstruction is unsound for any `Warning` subclass
   whose `__init__` is not `(message)`, which is not a MolSysSuite peculiarity.
2. Give catalog warning subclasses signatures that tolerate a single positional
   rendered message. Spreads a workaround across every library.
3. Have `CatalogWarning` control what `.args` carries so the round trip is
   either exact or cleanly refused. Worth weighing before 1.0, since it is the
   only one of the three inside SMonitor's own contract.

Nothing here blocks the diagnostics contract: serial runs, scripts, notebooks
and services are unaffected.
