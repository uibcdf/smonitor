"""Immutable, task-local restrictions applied before automatic collection."""

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from math import isfinite

from .._diagnostics import CapturePolicyError


@dataclass(frozen=True, slots=True)
class CapturePolicy:
    """Allowed capture operations; nested scopes combine permissions with AND."""

    arguments: bool = True
    exception_text: bool = True
    inherited_context: bool = True
    extra: bool = True

    def __post_init__(self):
        if any(
            type(value) is not bool
            for value in (self.arguments, self.exception_text, self.inherited_context, self.extra)
        ):
            raise CapturePolicyError()


DETAILED = CapturePolicy()
METADATA_ONLY = CapturePolicy(False, False, False, False)


@dataclass(frozen=True, slots=True)
class _CaptureState:
    policy: CapturePolicy = DETAILED
    facts: tuple = ()


_capture: ContextVar[_CaptureState] = ContextVar("smonitor_capture", default=_CaptureState())


def get_capture_policy() -> CapturePolicy:
    """Return active permissions for consumers that construct diagnostic data."""
    return _capture.get().policy


def capture_state() -> _CaptureState:
    """Snapshot for deferred diagnostics; contains no arbitrary payloads."""
    return _capture.get()


def capture_key() -> str:
    """Separate deferred aggregation across capture permissions and safe facts."""
    state = _capture.get()
    if state.policy == DETAILED and not state.facts:
        return ""
    import json

    policy = state.policy
    return json.dumps(
        [
            policy.arguments,
            policy.exception_text,
            policy.inherited_context,
            policy.extra,
            dict(state.facts),
        ],
        sort_keys=True,
        separators=(",", ":"),
    )


def safe_metadata(extra=None) -> dict:
    """Copy explicitly approved flat primitives without invoking user methods."""
    if extra is None:
        return {}
    if type(extra) is not dict or len(extra) > 32:
        raise CapturePolicyError()
    for key, value in extra.items():
        if type(key) is not str or not key or len(key) > 80:
            raise CapturePolicyError()
        kind = type(value)
        valid = (
            value is None
            or kind is bool
            or (kind is str and len(value) <= 256)
            or (kind is int and value.bit_length() <= 64)
            or (kind is float and isfinite(value))
        )
        if not valid:
            raise CapturePolicyError()
    return extra.copy()


def capture_facts(extra=None) -> dict:
    return safe_metadata({**dict(_capture.get().facts), **safe_metadata(extra)})


def derived_metadata(extra) -> dict:
    """Keep automatic primitive facts within the caller's aggregate budget."""
    approved = {}
    for key, value in extra.items():
        approved.update(safe_metadata({key: value}))
    existing = dict(_capture.get().facts)
    budget = 32 - len(existing)
    result = {}
    for key, value in approved.items():
        if key in existing:
            result[key] = value
        elif budget:
            result[key] = value
            budget -= 1
    return result


@contextmanager
def diagnostic_scope(policy: CapturePolicy = METADATA_ONLY, *, safe_extra=None):
    """Restrict capture locally; token restoration works across awaits and errors.

    Safe facts are caller-approved, bounded primitives, not a redaction service.
    Place this scope before any provider call whose automatic collection is forbidden.
    """
    if type(policy) is not CapturePolicy:
        raise CapturePolicyError()
    previous = _capture.get()
    active = previous.policy
    combined = CapturePolicy(
        active.arguments and policy.arguments,
        active.exception_text and policy.exception_text,
        active.inherited_context and policy.inherited_context,
        active.extra and policy.extra,
    )
    facts = capture_facts(safe_extra)
    token = _capture.set(_CaptureState(combined, tuple(facts.items())))
    try:
        yield combined
    finally:
        _capture.reset(token)
