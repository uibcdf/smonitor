Visual Showcase
===============

smonitor features an exceptional visual interface when using the ``rich`` theme.
It transforms standard Python logs and warnings into structured, high-value
diagnostic cards.

Exceptional Rich Handler
------------------------

The ``RichConsoleHandler`` is the center of the UI/UX. It includes:

- **Iconography**: Distinct icons for gravity levels (⚙ DEBUG, ℹ INFO, ⚠ WARNING, ✘ ERROR).
- **Hierarchical Layout**: Meta-data (source, code, timestamp) is separated from the main message.
- **Breadcrumb Paths**: Call-chains are visualized using modern symbols (❯).
- **Profile-Driven Styles**: Elegant panels for users, and structured audit logs for developers.

User Profile
~~~~~~~~~~~~

Designed for clarity and calm. It hides technical noise and focuses on the
message and the solution (Hint).

.. image:: _static/showcase_user.png
   :align: center
   :alt: User profile showcase

Developer Profile
~~~~~~~~~~~~~~~~~

Designed for precision. It provides a structured report of every event, including
the exact call chain and structured extra data.

.. image:: _static/showcase_dev.png
   :align: center
   :alt: Developer profile showcase

Symmetry with the Ecosystem
---------------------------

smonitor provides a consistent look and feel across MolSysMT, ArgDigest, and DepDigest.
When an error occurs in a low-level library like PyUnitWizard, it is traced back
to the user-facing function in MolSysMT, providing a complete "Breadcrumb" trail.
