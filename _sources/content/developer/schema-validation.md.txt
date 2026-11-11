# Schema Validation

In `dev` and `qa` profiles, SMonitor validates event schema and can attach `schema_warning`.

Required event fields:
- `timestamp`
- `level`
- `message`

Additional checks:
- `level` in `DEBUG/INFO/WARNING/ERROR/CRITICAL`
- valid ISO `timestamp`
- `tags` is list of strings
- `extra` and `context` are dictionaries

Enable strict mode to fail fast:

```python
import smonitor

smonitor.configure(profile="qa", strict_schema=True)
```
