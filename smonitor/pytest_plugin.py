"""Optional bridge from SMonitor events into Pytest Receptor evidence."""

from __future__ import annotations

from .core.manager import _add_event_observer, _remove_event_observer

_NAMESPACE = "uibcdf.smonitor@1"
_SAFE_EXTRA = (
    "incident_kind",
    "severity",
    "priority",
    "diagnostic_confidence",
    "retryable",
    "support_needed",
    "cause_code",
)


class _ReceptorObserver:
    def __init__(self, config, emit, mark_incomplete):
        self.config = config
        self.emit = emit
        self.mark_incomplete = mark_incomplete

    def __call__(self, event, *, profile):
        try:
            extra = event.get("extra") or {}
            payload = {
                "schema": "smonitor.pytest-event@1",
                "code": event.get("code"),
                "signal": event.get("source"),
                "level": event.get("level"),
                "category": event.get("category"),
                "exception_type": event.get("exception_type"),
                "fingerprint": event.get("fingerprint"),
                "run_id": event.get("run_id"),
                "session_id": event.get("session_id"),
                "correlation_id": event.get("correlation_id"),
                "profile": profile,
                "diagnostic": {key: extra[key] for key in _SAFE_EXTRA if key in extra},
            }
            self.emit(self.config, _NAMESPACE, payload)
        except Exception:
            self.mark_incomplete(self.config)


def pytest_configure(config):
    """Attach only when the receptor's canonical artifact was requested."""
    if not config.getoption("receptor_events", default=None):
        return
    try:
        from pytest_receptor.extensions import emit, mark_incomplete
    except ImportError:
        return
    observer = _ReceptorObserver(config, emit, mark_incomplete)
    _add_event_observer(observer)
    config._smonitor_receptor_observer = observer


def pytest_unconfigure(config):
    observer = getattr(config, "_smonitor_receptor_observer", None)
    if observer is not None:
        _remove_event_observer(observer)
