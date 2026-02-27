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
