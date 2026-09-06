from __future__ import annotations

from typing import Any


def configure_depdigest(**kwargs: Any):
    """Entry point for DepDigest integration.

    Intended usage: centralize DepDigest diagnostics via smonitor.configure.
    """
    # Deferred: `smonitor.configure` reaches through the package object, and
    # `smonitor/__init__.py` imports this package before it defines `configure`.
    # Importing the name goes through the import machinery, which waits on a
    # module still initializing in another thread (uibcdf/smonitor#3).
    from smonitor import configure

    return configure(**kwargs)
