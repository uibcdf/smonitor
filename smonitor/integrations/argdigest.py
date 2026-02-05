from __future__ import annotations

from typing import Any

import smonitor


def configure_argdigest(**kwargs: Any):
    """Entry point for ArgDigest integration.

    Intended usage: centralize ArgDigest diagnostics via smonitor.configure.
    """
    return smonitor.configure(**kwargs)
