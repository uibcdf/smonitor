CODES and Message Templates
===========================

`smonitor` can use `CODES` metadata to populate messages and hints by profile.

Example
-------

::

  CODES = {
    "MSM-W010": {
      "title": "Selection ambiguous",
      "user_message": "La selección '{selection}' es ambigua.",
      "user_hint": "Especifica la selección con más detalle (ejemplo: {example}).",
      "dev_message": "Selection parsing ambiguous.",
      "dev_hint": "Use explicit selectors.",
    }
  }

If `emit(..., code="MSM-W010")` is called with an empty message, smonitor will
use the profile-specific message and hint.

Templating
----------

`user_message`, `dev_message`, and hints can use `{placeholders}`. Placeholders
are resolved from `event.extra` at emit time.
