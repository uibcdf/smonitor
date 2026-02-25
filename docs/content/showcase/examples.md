# Example Workflows

## User-facing warning

```python
import smonitor

smonitor.configure(profile="user", theme="rich")
smonitor.emit(
    "WARNING",
    "Selection string 'all' is broad",
    source="mylib.select",
    extra={"hint": "Use a more specific selector, for example atom_name == 'CA'."},
)
```

## Developer diagnostics with traceability

```python
import smonitor

smonitor.configure(profile="dev", theme="rich", args_summary=True)

@smonitor.signal(tags=["topology"])
def find_atoms(molsys, selection="*"):
    if not molsys:
        raise ValueError("Molecular system cannot be None")
```

## Policy-driven filtering

```python
import smonitor

smonitor.configure(
    filters=[
        {"when": {"code": "W001"}, "rate_limit": "1/100"},
    ]
)

for _ in range(1000):
    smonitor.emit("WARNING", "Repetitive warning", code="W001")
```

## Bundle export for support

```bash
smonitor export --out smonitor_bundle --max-events 500
```
