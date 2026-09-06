"""A catalog entry renders in every profile, not only in the one it named.

Message resolution consulted exactly one field per profile, so an entry defining
`user_message` alone — the shape the README, the shipped template and section 1
of the canonical guide all show — produced an empty message under every profile
but `user`. Measured across the ecosystem on 2026-09-06: ArgDigest and
PyUnitWizard emitted no message under `qa` and `agent`, DepDigest under `agent`.

The two libraries that were unaffected had each built a workaround: MolSysMT
writes all four fields by hand, MolSysViewer fans one template across them.
"""

from __future__ import annotations

import pytest

import smonitor
from smonitor.core.manager import _HINT_FALLBACKS, _MESSAGE_FALLBACKS

PROFILES = ["user", "dev", "qa", "agent", "debug"]
MESSAGE_FIELDS = ["user_message", "dev_message", "qa_message", "agent_message", "message"]
HINT_FIELDS = ["user_hint", "dev_hint", "qa_hint", "agent_hint"]


def _resolve(profile, entry, extra=None):
    smonitor.configure(profile=profile, handlers=[], codes={"C-1": entry}, level="DEBUG")
    return smonitor.resolve(code="C-1", extra=extra or {})


@pytest.mark.parametrize("profile", PROFILES)
def test_the_documented_minimal_entry_renders_in_every_profile(profile):
    """README, `smonitor/templates/_smonitor.py`, and guide section 1 all show this."""
    message, hint = _resolve(
        profile,
        {"user_message": "Selection {sel} is ambiguous.", "user_hint": "Be specific."},
        {"sel": "CA"},
    )
    assert message == "Selection CA is ambiguous."
    assert hint == "Be specific."


@pytest.mark.parametrize("profile", PROFILES)
@pytest.mark.parametrize("field", MESSAGE_FIELDS)
def test_any_single_message_field_renders_in_any_profile(profile, field):
    """The invariant: define one message field and no profile renders empty."""
    message, _ = _resolve(profile, {field: "the message"})
    assert message == "the message"


@pytest.mark.parametrize("profile", PROFILES)
@pytest.mark.parametrize("field", HINT_FIELDS)
def test_any_single_hint_field_renders_in_any_profile(profile, field):
    _, hint = _resolve(profile, {"message": "m", field: "the hint"})
    assert hint == "the hint"


@pytest.mark.parametrize(
    "profile,expected_message,expected_hint",
    [
        ("user", "U", "UH"),
        ("dev", "D", "DH"),
        ("qa", "Q", "QH"),
        ("agent", "A", "AH"),
        ("debug", "D", "DH"),
    ],
)
def test_a_profile_still_prefers_its_own_field(profile, expected_message, expected_hint):
    """A fallback must not change what a fully populated entry already did."""
    entry = {
        "user_message": "U", "dev_message": "D", "qa_message": "Q", "agent_message": "A",
        "message": "M",
        "user_hint": "UH", "dev_hint": "DH", "qa_hint": "QH", "agent_hint": "AH",
    }
    message, hint = _resolve(profile, entry)
    assert message == expected_message
    assert hint == expected_hint


@pytest.mark.parametrize("profile", ["qa", "agent"])
def test_qa_and_agent_still_reach_for_the_dev_hint_first(profile):
    """Precedence that already existed, kept: these two fell back to `dev_hint`."""
    _, hint = _resolve(profile, {"message": "m", "user_hint": "UH", "dev_hint": "DH"})
    assert hint == "DH"


@pytest.mark.parametrize("profile", PROFILES)
def test_nothing_is_invented_when_the_entry_defines_no_text(profile):
    message, hint = _resolve(profile, {"title": "Titled"})
    assert message == ""
    assert hint is None


def test_an_unknown_profile_resolves_as_dev():
    """Unknown profiles took the `dev` branch before these tables; they still do."""
    message, hint = _resolve("bespoke", {"dev_message": "D", "dev_hint": "DH", "user_message": "U"})
    assert (message, hint) == ("D", "DH")


@pytest.mark.parametrize("table,fields", [(_MESSAGE_FALLBACKS, MESSAGE_FIELDS),
                                          (_HINT_FALLBACKS, HINT_FIELDS)])
def test_every_chain_is_a_complete_ordering_of_the_fields(table, fields):
    """A chain that omits a field would leave that field unreachable as a fallback."""
    assert set(table) == set(PROFILES)
    for profile, chain in table.items():
        assert set(chain) == set(fields), profile
        assert len(chain) == len(set(chain)), profile
