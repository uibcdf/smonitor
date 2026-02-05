from __future__ import annotations

from typing import Any

import smonitor


def configure_molsysmt(**kwargs: Any):
    """Entry point for MolSysMT integration.

    Intended usage: replace molsysmt.logging_setup with smonitor.configure.
    """
    return smonitor.configure(**kwargs)
