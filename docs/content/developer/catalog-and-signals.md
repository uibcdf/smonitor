# Catalog and Signals

SMonitor resolves profile-specific messages and hints from `CODES`, and validates contracts from `SIGNALS`.

## CODES template model

```python
CODES = {
  "MYLIB-W010": {
    "title": "Selection ambiguous",
    "user_message": "Selection '{selection}' is ambiguous.",
    "user_hint": "Use a more specific selector.",
    "dev_message": "Selection parser ambiguity.",
    "dev_hint": "Review selector normalization.",
  }
}
```

Each profile reads its own field first and falls back through the nearest
audience to the `user_*` field when its own is absent; a generic `message` sits
in the middle of every message chain. So the entry above renders under `qa` and
`agent` too, using `dev_message` and `dev_hint`, and an entry carrying only
`user_message` renders everywhere.

The invariant is that **an entry defining any message field renders empty in no
profile**. Define the variants that genuinely differ for their audience; there
is no need to repeat one sentence four times.


## SIGNALS contracts

```python
SIGNALS = {
  "mylib.select": {
      "extra_required": ["selection"],
      "warnings": ["MYLIB-W010"],
  }
}
```

With `strict_signals=True`, missing required `extra` fields raise `ValueError`.

## Generated catalog tables

### CODES

```{include} ../../_generated_codes.md
```

### SIGNALS

```{include} ../../_generated_signals.md
```
