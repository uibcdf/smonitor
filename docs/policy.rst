Policy Engine
=============

The policy engine applies routing and filtering rules to normalized events
before handler dispatch.

Rule matching (`when`)
----------------------

Fields:
- `level`, `source`, `source_prefix`, `category`, `code`, `tags`, `exception_type`, `library`

Operators:
- `eq` (default), `in`, `prefix`, `contains`, `regex`

Examples
--------

::

  ROUTES = [
    {"when": {"level": "WARNING", "source_prefix": "molsysmt."},
     "send_to": ["console", "json"]}
  ]

  FILTERS = [
    {"when": {"code": "MSM-W010"}, "rate_limit": "1/100"}
  ]
