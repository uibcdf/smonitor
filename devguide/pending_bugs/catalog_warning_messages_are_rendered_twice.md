# Catalog Warning Messages Are Rendered Twice

**Reported:** 2026-07-18
**Reported by:** pytest-receptor, from evidence gathered in the MolSysMT pilot
**Severity:** Medium — messages are wrong and roughly twice as long; no
behavioural impact on the warning itself

## Summary

Some `CatalogWarning` subclasses produce a message that contains an
already-rendered message nested inside its own template. The catalog text is
applied twice and, where a hint exists, the hint is appended twice.

This was found while analysing warning output from a full MolSysMT run
(9,336 tests, 216 warnings). It reproduces outside pytest — the duplication is
present in the warning instance itself, not in any reporting layer.

## Evidence

Two examples from the MolSysMT suite, quoted verbatim from
`str(warning_instance)`.

`UnknownAtomNameWarning`, where the template is roughly
`Atom name '{atom_name}' is not recognized; atom type 'UNK' will be used. …`:

```text
Atom name 'Atom name 'Ar' is not recognized; atom type 'UNK' will be used.
Provide an explicit atom type when the name uses a non-standard convention.' is
not recognized; atom type 'UNK' will be used. Provide an explicit atom type when
the name uses a non-standard convention.
```

The field `{atom_name}` has been filled with a fully rendered message rather
than with `Ar`.

`GpuNotAvailableWarning` shows the same shape, and additionally duplicates the
hint:

```text
GPU acceleration was requested but is not available: GPU acceleration was
requested but is not available: no CUDA GPU is accessible The calculation falls
back to the CPU kernel and the result is unchanged. Set
molsysmt.configure.gpu_mode = False to stop requesting the GPU. Docs:
https://www.uibcdf.org/MolSysMT The calculation falls back to the CPU kernel and
the result is unchanged. Set molsysmt.configure.gpu_mode = False to stop
requesting the GPU. Docs: https://www.uibcdf.org/MolSysMT
```

Both the prefix and the trailing hint appear twice. That the *hint* is
duplicated is the useful detail: it points at the composition step rather than
at the template.

Affected in this sample: `UnknownAtomNameWarning` (4 groups, 56 occurrences) and
`GpuNotAvailableWarning` (1 group, 18 occurrences). Other catalog warnings in the
same run — `MemoryPressureWarning`, `SelectionWarning` — were clean, so this is
not universal.

## Hypothesis

Offered as a hypothesis, not a diagnosis: it comes from reading the code, not
from instrumenting it.

Two separate places perform "resolve, then append the hint":

- `CatalogWarning.__init__`, in `smonitor/integrations/diagnostic.py:69`:

  ```python
  resolved_msg, hint = smonitor.resolve(message=message, code=target_code, extra=resolved_extra)
  full_message = resolved_msg
  if hint:
      full_message = f"{full_message} {hint}" if full_message else hint
  ```

- `DiagnosticBundle.resolve`, in the same module around line 398, which does the
  same combination and returns a single string.

If a caller uses `DiagnosticBundle.resolve(...)` to build a message and then
passes the result into a `CatalogWarning` — directly as `message=`, or indirectly
by placing it in `extra` under the field the template interpolates — the second
resolution renders the already-rendered text again and appends the hint a second
time. That accounts for both observed symptoms in one step, including the
duplicated hint, which a template applied twice would not by itself explain.

Worth checking first: what `extra["atom_name"]` actually holds at the point
`UnknownAtomNameWarning(atom_name)` is constructed in
`molsysmt/element/atom/get_atom_type_from_atom_name.py`. If it is already a
sentence rather than `Ar`, the duplication happens before SMonitor is reached and
this is a MolSysMT call-site bug rather than an SMonitor one.

## Why it is worth fixing

- The message is factually wrong: it claims an atom is named
  `Atom name 'Ar' is not recognized; …` rather than `Ar`.
- Any consumer grouping or fingerprinting on message text sees a longer and
  noisier string. In our case it roughly doubles the cost of those lines, but
  the same applies to logs, support bundles, and anything reading
  `str(warning)`.
- It is invisible in ordinary use: pytest's own warning summary truncates, so
  this survived until something printed the untruncated text.

## Suggested regression

Construct each catalog-backed warning class directly, with a short scalar field
value, and assert that the field appears exactly once in `str(instance)` and
that any hint appears exactly once. A parametrized test over every registered
`catalog_key` would catch the whole family rather than the two found here.

## Provenance

Full untruncated evidence, including all 60 warning groups from the run, is in
`pytest-receptor/devguide/molsysmt_warning_group_evidence_2026-07-18.md`.

pytest-receptor takes no position on how SMonitor renders its catalog; this is
reported because the pilot's data happened to expose it, and because it is not
visible in normal test output.
