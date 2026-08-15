"""The catalog path must keep ordinary Python warning semantics.

`DiagnosticBundle.warn()` emits a structured, catalog-backed event. It must also
raise the warning through `warnings.warn`, because a diagnostic that exists only
as an SMonitor event cannot be seen by `pytest.warns`, by
`warnings.filterwarnings`, or by `simplefilter("error")`.

That gap is why MolSysMT and ArgDigest between them route 17 call sites through
`warnings.warn` directly: keeping those semantics cost them the catalog, so the
events arrived with `code=None`, `source="py.warnings"` and no structured
fields. Both halves have to work at once.
"""

from __future__ import annotations

import inspect
import logging
import warnings
from pathlib import Path

import pytest

import smonitor
from smonitor.handlers.memory import MemoryHandler
from smonitor.integrations.diagnostic import CatalogWarning, DiagnosticBundle


class AtomWarning(CatalogWarning):
    catalog_key = "AtomWarning"


CATALOG = {
    "warnings": {
        "AtomWarning": {
            "code": "T-ATOM",
            "source": "lib.atom.unknown_name",
            "category": "data_quality",
            "level": "WARNING",
        }
    }
}

CODES = {
    "T-ATOM": {
        "title": "Unknown atom name",
        "user_message": "Atom name '{atom_name}' is not recognized.",
        "user_hint": "Provide an explicit atom type.",
    }
}


def _bundle(**config):
    logging.getLogger().handlers.clear()
    handler = MemoryHandler()
    smonitor.configure(
        profile="user",
        handlers=[handler],
        codes=CODES,
        event_buffer_size=10,
        **config,
    )
    return DiagnosticBundle(catalog=CATALOG, meta={}, package_root=Path.cwd()), handler


def test_catalog_warning_is_visible_to_pytest_warns():
    bundle, _ = _bundle()
    with pytest.warns(AtomWarning, match="XXX"):
        bundle.warn(AtomWarning(code="T-ATOM", extra={"atom_name": "XXX"}))


def test_catalog_warning_still_emits_the_structured_event():
    bundle, handler = _bundle()
    with pytest.warns(AtomWarning):
        bundle.warn(AtomWarning(code="T-ATOM", extra={"atom_name": "XXX"}))

    (event,) = handler.events
    assert event["code"] == "T-ATOM"
    assert event["source"] == "lib.atom.unknown_name"
    assert event["category"] == "data_quality"
    assert event["extra"]["atom_name"] == "XXX"
    assert event["message"] == "Atom name 'XXX' is not recognized."


@pytest.mark.parametrize(
    ("capture_logging", "capture_warnings"),
    [(True, True), (False, True), (True, False), (False, False)],
)
def test_the_re_raised_warning_is_not_captured_a_second_time(capture_logging, capture_warnings):
    """Whichever capture emitter is installed must stand down during the replay.

    Without the guard the incident lands twice: once as `T-ATOM` with its
    fields, and once as an uncoded event whose message is Python's formatted
    warning text, file path and source line included.
    """
    bundle, handler = _bundle(
        capture_logging=capture_logging, capture_warnings=capture_warnings
    )
    warnings.simplefilter("always")

    if capture_warnings:
        # A capture emitter owns `showwarning`; leave it in place, since standing
        # it down is exactly what is under test here.
        bundle.warn(AtomWarning(code="T-ATOM", extra={"atom_name": "XXX"}))
    else:
        # Nothing is installed to capture it, so collect the warning rather than
        # letting it escape into the test report.
        with pytest.warns(AtomWarning):
            bundle.warn(AtomWarning(code="T-ATOM", extra={"atom_name": "XXX"}))

    assert [event["code"] for event in handler.events] == ["T-ATOM"]


def test_error_filter_raises_but_the_event_is_kept():
    """`simplefilter("error")` must promote the warning, without losing telemetry."""
    bundle, handler = _bundle()
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        with pytest.raises(AtomWarning):
            bundle.warn(AtomWarning(code="T-ATOM", extra={"atom_name": "XXX"}))

    assert [event["code"] for event in handler.events] == ["T-ATOM"]


def test_ignore_filter_silences_the_user_but_not_the_telemetry():
    """The user's filter governs their console, not what SMonitor records."""
    bundle, handler = _bundle()
    with warnings.catch_warnings(record=True) as raised:
        warnings.simplefilter("ignore")
        bundle.warn(AtomWarning(code="T-ATOM", extra={"atom_name": "XXX"}))

    assert raised == []
    assert [event["code"] for event in handler.events] == ["T-ATOM"]


def test_string_caller_keeps_the_requested_category():
    bundle, handler = _bundle()
    with pytest.warns(AtomWarning, match="plain text"):
        bundle.warn("plain text", AtomWarning)

    assert [event["code"] for event in handler.events] == ["T-ATOM"]


def test_warning_without_catalog_entry_is_unaffected():
    """No catalog entry means no emission, and the warning behaves as always."""
    bundle, handler = _bundle()
    with pytest.warns(UserWarning, match="uncatalogued"):
        bundle.warn("uncatalogued", UserWarning)

    assert handler.events == []


def _library_function(bundle):
    """Stands in for a library function that notices a problem."""
    bundle.warn(AtomWarning(code="T-ATOM", extra={"atom_name": "XXX"}))


def _library_function_once(bundle):
    bundle.warn_once(AtomWarning(code="T-ATOM", extra={"atom_name": "XXX"}))


def test_stacklevel_blames_the_calling_user_code():
    """`stacklevel` must mean what it means at a plain `warnings.warn`.

    The default of 2 blames the caller of the library function, i.e. the user's
    own line — not the library file that noticed the problem, and not a frame
    inside SMonitor. `warn()` occupies a frame of its own, so it adds that back
    rather than leaving every call site to compensate.
    """
    bundle, _ = _bundle()
    with pytest.warns(AtomWarning) as record:
        expected_line = inspect.currentframe().f_lineno + 1
        _library_function(bundle)

    assert Path(record[0].filename).name == Path(__file__).name
    assert record[0].lineno == expected_line


def test_warn_once_keeps_the_same_attribution():
    bundle, _ = _bundle()
    with pytest.warns(AtomWarning) as record:
        expected_line = inspect.currentframe().f_lineno + 1
        _library_function_once(bundle)

    assert Path(record[0].filename).name == Path(__file__).name
    assert record[0].lineno == expected_line
