from __future__ import annotations

from contextvars import ContextVar, Token

signals_enabled = True


def set_signals_enabled(enabled: bool) -> None:
    global signals_enabled
    signals_enabled = bool(enabled)


# A catalog-backed warning is emitted as a structured event and *also* re-raised
# as an ordinary Python warning, so `pytest.warns`, `filterwarnings` and
# `simplefilter("error")` keep working on it. While it is being re-raised the
# warning-capture emitters stand down: otherwise `capture_warnings` would feed
# the same diagnostic back in a second time, stripped of its code, source,
# category and structured fields, and the incident would be counted twice in
# `report()` and in every fingerprint summary.
#
# A ContextVar rather than a plain flag, so the stand-down cannot leak across
# asyncio tasks or threads that happen to warn at the same moment.
_replaying_catalog_warning: ContextVar[bool] = ContextVar(
    "smonitor_replaying_catalog_warning", default=False
)


def replaying_catalog_warning() -> bool:
    """Whether this context is re-raising a warning it has already emitted."""
    return _replaying_catalog_warning.get()


def begin_catalog_warning_replay() -> Token[bool]:
    return _replaying_catalog_warning.set(True)


def end_catalog_warning_replay(token: Token[bool]) -> None:
    _replaying_catalog_warning.reset(token)
