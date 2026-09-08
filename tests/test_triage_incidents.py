"""A triage aggregate named for incidents must not be filled with log lines.

A fingerprint is derived from `code`, `source`, `exception_type` and a subset of
`extra`. The message is excluded on purpose, so that a template rendering
different text does not split one incident. For a coded event that is right, and
it is why `events_by_fingerprint` groups usefully.

With no code, the reduction leaves only `source`, and every uncoded event from one
module collapses into a single bucket whatever it says. Measured against a real
suite on 2026-09-08 (`devguide/operability_evidence_2026-09-08.md`): 219 of 289
events in one bucket, carrying 102 distinct messages, presented by
`top_fingerprints` as the loudest recurring incident in the run.

The message spread does not separate the two cases -- a coded incident with a
templated message varies too; that same run had a coded fingerprint with six
events and six distinct messages. The presence of a code does.
"""

from __future__ import annotations

import smonitor

CODES = {"LIB-W001": {"user_message": "Resource {resource} is unavailable."}}


def _configured():
    return smonitor.configure(
        profile="user", handlers=[], level="DEBUG", event_buffer_size=200, codes=CODES
    )


def _report_rows(manager, name):
    return {row["key"]: row for row in manager.report()[name]}


def test_a_fingerprint_row_says_whether_it_is_an_incident():
    manager = _configured()
    for resource in ("a.pdb", "b.pdb", "c.pdb"):
        manager.emit("WARNING", "", code="LIB-W001", source="lib.io",
                     extra={"resource": resource})
    for text in ("started", "finished", "retrying"):
        manager.emit("DEBUG", text, source="lib.io")

    rows = _report_rows(manager, "top_fingerprints")
    coded = [row for row in rows.values() if row["code"]]
    uncoded = [row for row in rows.values() if not row["code"]]

    # Three coded events with different `resource` are three incidents; three
    # uncoded log lines from one source are one bucket carrying three messages.
    assert len(coded) == 3 and all(row["count"] == 1 for row in coded)
    assert len(uncoded) == 1 and uncoded[0]["count"] == 3


def test_recurrent_incidents_holds_only_coded_events():
    manager = _configured()
    for _ in range(4):
        manager.emit("WARNING", "", code="LIB-W001", source="lib.io",
                     extra={"resource": "a.pdb"})
    for text in ("started", "finished", "retrying", "done"):
        manager.emit("DEBUG", text, source="lib.io")

    recurrent = manager.report()["recurrent_incidents"]
    assert [row["code"] for row in recurrent] == ["LIB-W001"]
    assert recurrent[0]["count"] == 4

    # Nothing is hidden: the uncoded bucket is still reported, labelled.
    fingerprints = manager.report()["top_fingerprints"]
    assert any(row["code"] is None and row["count"] == 4 for row in fingerprints)


def test_the_message_spread_does_not_separate_the_two_cases():
    """Why the fix keys on the code and not on how varied the text is."""
    manager = _configured()
    for resource in ("a.pdb", "b.pdb"):
        for _ in range(2):
            manager.emit("WARNING", "", code="LIB-W001", source="lib.io",
                         extra={"resource": resource})

    rows = [row for row in manager.report()["top_fingerprints"] if row["code"]]
    messages = {e["message"] for e in manager.recent_events() if e.get("code")}

    # Two incidents, four events, two distinct messages: a coded fingerprint
    # varies its text as soon as its template interpolates a field.
    assert len(rows) == 2 and len(messages) == 2
    assert all(row["count"] == 2 for row in rows)


def test_an_uncoded_bucket_is_still_reachable_in_the_raw_counts():
    """`events_by_fingerprint` is the unfiltered count and stays that way."""
    manager = _configured()
    for text in ("one", "two"):
        manager.emit("DEBUG", text, source="lib.io")

    assert sum(manager.report()["events_by_fingerprint"].values()) == 2
