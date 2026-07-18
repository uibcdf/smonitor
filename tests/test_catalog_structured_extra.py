"""Regressions for catalog warnings/exceptions retaining structured state.

Covers `devguide/pending_bugs/catalog_warning_messages_are_rendered_twice.md`
and `devguide/pending_proposals/catalog_signals_lose_structured_extra.md`, which
are two symptoms of one defect: `DiagnosticBundle.warn()` used to discard the
instance's structured `extra` and re-emit its already-rendered message.
"""

from pathlib import Path

import pytest

import smonitor
from smonitor.handlers.memory import MemoryHandler
from smonitor.integrations.diagnostic import CatalogException, CatalogWarning, DiagnosticBundle


class GpuNotAvailableWarning(CatalogWarning):
    catalog_key = "GpuNotAvailableWarning"


class UnknownAtomNameWarning(CatalogWarning):
    catalog_key = "UnknownAtomNameWarning"


class MultipleMolecularSystemsError(CatalogException):
    catalog_key = "MultipleMolecularSystemsError"


CODES = {
    # Template keyed on {message} — the pattern the SMonitor guide pushes
    # integrators toward, and the one that produced the doubled rendering.
    "T-W-GPU": {
        "user_message": "GPU not available: {message}",
        "user_hint": "Falls back to the CPU kernel.",
    },
    # Template keyed on a domain placeholder.
    "T-W-ATOM": {
        "user_message": "Atom name '{atom_name}' is not recognized.",
        "user_hint": "Provide an explicit atom type.",
    },
    "T-E-MULTI": {"user_message": "Several molecular systems: {count}."},
}

CATALOG = {
    "warnings": {
        "GpuNotAvailableWarning": {"code": "T-W-GPU", "source": "demo.gpu"},
        "UnknownAtomNameWarning": {"code": "T-W-ATOM", "source": "demo.atom"},
    },
    "exceptions": {"MultipleMolecularSystemsError": {"code": "T-E-MULTI"}},
}


@pytest.fixture
def bundle_and_events():
    handler = MemoryHandler()
    smonitor.configure(profile="user", codes=CODES, handlers=[handler], enabled=True)
    bundle = DiagnosticBundle(catalog=CATALOG, meta={}, package_root=Path.cwd())
    return bundle, handler.events


def test_warn_instance_interpolates_domain_placeholder(bundle_and_events):
    """The proposal's core ask: a template may use its own placeholders."""
    bundle, events = bundle_and_events
    bundle.warn(UnknownAtomNameWarning(code="T-W-ATOM", extra={"atom_name": "Ar"}))
    assert events[-1]["message"] == "Atom name 'Ar' is not recognized."


def test_warn_instance_does_not_render_message_twice(bundle_and_events):
    """The bug: a {message}-keyed template rendered its own output again."""
    bundle, events = bundle_and_events
    bundle.warn(
        GpuNotAvailableWarning(code="T-W-GPU", extra={"message": "no CUDA GPU is accessible"})
    )
    emitted = events[-1]
    assert emitted["message"] == "GPU not available: no CUDA GPU is accessible"
    assert emitted["message"].count("GPU not available") == 1
    # The hint travels in `extra`; it must not also be baked into the message.
    assert "Falls back to the CPU kernel." not in emitted["message"]
    assert emitted["extra"]["hint"] == "Falls back to the CPU kernel."


@pytest.mark.parametrize(
    "warning_cls, code, field, value",
    [
        (GpuNotAvailableWarning, "T-W-GPU", "message", "no CUDA GPU is accessible"),
        (UnknownAtomNameWarning, "T-W-ATOM", "atom_name", "Ar"),
    ],
)
def test_field_and_hint_appear_exactly_once(warning_cls, code, field, value):
    """The regression the bug report asked for, across the warning family."""
    smonitor.configure(profile="user", codes=CODES, handlers=[])
    rendered = str(warning_cls(code=code, extra={field: value}))
    assert rendered.count(value) == 1
    hint = CODES[code]["user_hint"]
    assert rendered.count(hint) == 1


def test_structured_extra_reaches_telemetry(bundle_and_events):
    """Fingerprints and counters must see typed fields, not rendered prose."""
    bundle, events = bundle_and_events
    bundle.warn(
        UnknownAtomNameWarning(
            code="T-W-ATOM", extra={"atom_name": "Ar", "resource": "traj.h5"}
        )
    )
    extra = events[-1]["extra"]
    assert extra["atom_name"] == "Ar"
    assert extra["resource"] == "traj.h5"


def test_instance_retains_code_and_extra():
    """Catch sites should branch on `code`, not pattern-match English."""
    smonitor.configure(profile="user", codes=CODES, handlers=[])
    with pytest.raises(MultipleMolecularSystemsError) as excinfo:
        raise MultipleMolecularSystemsError(code="T-E-MULTI", extra={"count": 3})
    assert excinfo.value.code == "T-E-MULTI"
    assert excinfo.value.extra["count"] == 3

    warning = GpuNotAvailableWarning(code="T-W-GPU", extra={"message": "no GPU"})
    assert warning.code == "T-W-GPU"
    assert warning.extra["message"] == "no GPU"


def test_explicit_extra_overrides_instance_extra(bundle_and_events):
    bundle, events = bundle_and_events
    bundle.warn(
        UnknownAtomNameWarning(code="T-W-ATOM", extra={"atom_name": "Ar"}),
        extra={"atom_name": "Xe"},
    )
    assert events[-1]["message"] == "Atom name 'Xe' is not recognized."


def test_plain_string_message_still_populates_message_placeholder(bundle_and_events):
    """The {message} contract for string callers is unchanged."""
    bundle, events = bundle_and_events
    bundle.warn("no CUDA GPU is accessible", GpuNotAvailableWarning)
    assert events[-1]["message"] == "GPU not available: no CUDA GPU is accessible"


def test_caller_is_preserved_from_instance(bundle_and_events):
    bundle, events = bundle_and_events
    bundle.warn(UnknownAtomNameWarning(code="T-W-ATOM", extra={"atom_name": "Ar"}))
    # CatalogWarning.__init__ defaults `caller` to the catalog key.
    assert events[-1]["extra"]["caller"] == "UnknownAtomNameWarning"
