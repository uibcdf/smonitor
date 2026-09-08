# Policy Engine

The policy engine applies routing and filtering rules to normalized events before handler dispatch.

## Rule matching (`when`)

Supported fields:
- `level`, `source`, `source_prefix`, `category`, `code`, `tags`, `exception_type`, `library`

Supported operators:
- `eq` (default), `in`, `prefix`, `contains`, `regex`

## Example

```python
ROUTES = [
    {"when": {"level": "WARNING", "source_prefix": "mylib."}, "send_to": ["console", "json"]}
]

FILTERS = [
    {"when": {"code": "MYLIB-W010"}, "rate_limit": "1/100@60"},
    {"when": {"level": "INFO"}, "sample": 0.1},
]
```

## Advanced transforms

```python
ROUTES = [
    {
      "when": {"level": "WARNING"},
      "rename": {"source": "origin"},
      "drop_fields": ["exception_type"],
      "add_tags": ["review"],
      "set": {"category": "validation"},
      "set_extra": {"owner": "qa"},
    }
]
```
