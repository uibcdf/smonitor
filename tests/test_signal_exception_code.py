"""Regression: a raised CatalogException must keep its code on the event.

`CatalogException` resolves and stores `code` and a structured `extra`, but it
does not emit; emission happens in the `@signal` wrapper when the exception
propagates. That wrapper used to emit with `code=None` and only its own
`source_module`, so the coded identity the exception had already resolved never
reached telemetry. Downstream contract tests that assert "the error path emits
a coded signal" could then only be satisfied by unrelated events.
"""


import pytest

import smonitor
from smonitor.handlers.memory import MemoryHandler
from smonitor.integrations.diagnostic import CatalogException


class OutOfRangeError(CatalogException):
    catalog_key = "OutOfRangeError"


CODES = {"T-E-RANGE": {"user_message": "Value {value} is out of range."}}

CATALOG = {
    "exceptions": {"OutOfRangeError": {"code": "T-E-RANGE", "source": "demo.range"}}
}

META = {"doc_url": "https://example.invalid/docs"}


@pytest.fixture
def events():
    handler = MemoryHandler()
    smonitor.configure(profile="user", codes=CODES, handlers=[handler], enabled=True)
    return handler.events


def _raise_out_of_range():
    raise OutOfRangeError(catalog=CATALOG, meta=META, extra={"value": 42})


def test_signal_event_carries_the_exception_code(events):
    decorated = smonitor.signal(tags=["demo"])(_raise_out_of_range)

    with pytest.raises(OutOfRangeError):
        decorated()

    assert events[-1]["code"] == "T-E-RANGE"


def test_signal_event_carries_the_exception_structured_extra(events):
    decorated = smonitor.signal(tags=["demo"])(_raise_out_of_range)

    with pytest.raises(OutOfRangeError):
        decorated()

    extra = events[-1]["extra"]
    assert extra["value"] == 42
    assert extra["doc_url"] == "https://example.invalid/docs"
    # The wrapper's own provenance must survive alongside the catalog fields.
    assert "source_module" in extra


def test_plain_exception_still_emits_without_a_code(events):
    """Only catalog codes are propagated; a bare exception stays uncoded."""

    def boom():
        raise ValueError("no catalog behind this one")

    decorated = smonitor.signal(tags=["demo"])(boom)

    with pytest.raises(ValueError):
        decorated()

    assert events[-1]["code"] is None
    assert events[-1]["exception_type"] == "ValueError"


def test_non_string_code_attribute_is_ignored(events):
    """`code` is common on unrelated exceptions; only strings are trusted."""

    class WeirdError(Exception):
        code = 7

    def boom():
        raise WeirdError("carries an int code")

    decorated = smonitor.signal(tags=["demo"])(boom)

    with pytest.raises(WeirdError):
        decorated()

    assert events[-1]["code"] is None
