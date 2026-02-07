CODES and Message Templates
===========================

`smonitor` can use `CODES` metadata to populate messages and hints by profile.

Example
-------

::

  CODES = {
    "MSM-W010": {
      "title": "Selection ambiguous",
      "user_message": "Selection '{selection}' is ambiguous.",
      "user_hint": "Use a more specific selection (example: {example}).",
      "dev_message": "Selection parsing ambiguous.",
      "dev_hint": "Use explicit selectors.",
    }
  }

If `emit(..., code="MSM-W010")` is called with an empty message, smonitor will
use the profile-specific message and hint.

Templating
----------

``user_message``, ``dev_message``, and hints can use ``{placeholders}``. Placeholders
are resolved from ``event.extra`` at emit time.

Signal Contracts
----------------

You can define contracts for your signals using the ``SIGNALS`` dictionary in
your ``_smonitor.py``. This ensures that emitted events contain the required
structured data.

.. code-block:: python

  # _smonitor.py
  SIGNALS = {
    "molsysmt.select": {
        "extra_required": ["selection", "item_type"],
        "warnings": ["MSM-W010"],
    }
  }

If you enable ``strict_signals=True``, smonitor will raise a ``ValueError``
if a required field is missing from the ``extra`` dictionary.

.. code-block:: python

  import smonitor
  smonitor.configure(profile="dev", strict_signals=True)

  # This will raise if "selection" is missing in extra
  smonitor.emit("WARNING", "...", source="molsysmt.select", extra={})
