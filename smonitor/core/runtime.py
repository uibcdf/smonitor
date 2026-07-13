from __future__ import annotations


signals_enabled = True


def set_signals_enabled(enabled: bool) -> None:
    global signals_enabled
    signals_enabled = bool(enabled)
