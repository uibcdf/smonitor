Event Schema Validation
=======================

In `dev` and `qa` profiles, smonitor validates event schema and attaches
`schema_warning` to the event if required fields are missing or invalid.

Required fields:
- `timestamp`
- `level`
- `message`

Optional checks:
- `level` in DEBUG/INFO/WARNING/ERROR
- `code` or `category` present
