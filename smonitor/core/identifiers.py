from __future__ import annotations

from uuid import uuid4


def new_identifier() -> str:
    """Returning a stable opaque runtime identifier string."""

    return uuid4().hex
