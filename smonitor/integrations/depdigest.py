from __future__ import annotations

from typing import Any

import smonitor


def configure_depdigest(**kwargs: Any):
    """Entry point for DepDigest integration.

    Intended usage: centralize DepDigest diagnostics via smonitor.configure.
    """
    return smonitor.configure(**kwargs)
