"""Explicit safe audience templates for metadata-only catalog resolution (#39)."""

import pytest

import smonitor
from smonitor.integrations import ProviderRegistrationError, register_provider

CATALOG = {
    "T-REF": {
        "user_message": "User found {count} references.",
        "dev_message": "Developer found {count} references.",
        "qa_message": "QA found {count} references.",
        "agent_message": "Agent found {count} references.",
        "user_hint": "Unsafe ordinary user hint.",
        "dev_hint": "Unsafe ordinary developer hint.",
        "metadata_messages": {
            "user": "Restore {count} references.",
            "dev": "Inspect {count} references.",
        },
        "metadata_hints": {
            "user": "Restore retained bytes.",
            "dev": "Inspect local index binding.",
        },
        "metadata_hint": "Review retained references.",
    }
}


@pytest.mark.parametrize(
    ("profile", "expected_message", "expected_hint"),
    [
        ("user", "Restore 2 references.", "Restore retained bytes."),
        ("dev", "Inspect 2 references.", "Inspect local index binding."),
        ("debug", "Inspect 2 references.", "Inspect local index binding."),
        ("unknown", "Inspect 2 references.", "Inspect local index binding."),
        ("qa", "QA found 2 references.", "Review retained references."),
        ("agent", "Agent found 2 references.", "Review retained references."),
    ],
)
def test_safe_audience_templates_are_pure_and_use_approved_facts(
    tmp_path, profile, expected_message, expected_hint
):
    manager = smonitor.get_manager()
    root = tmp_path / "provider"
    root.mkdir()
    root.joinpath("_smonitor.py").write_text(f"CODES = {CATALOG!r}\n")
    register_provider(root)
    config = manager.config

    with smonitor.diagnostic_scope(safe_extra={"count": 2}):
        assert smonitor.resolve(code="T-REF", profile=profile) == (
            expected_message,
            expected_hint,
        )

    assert manager.config is config
    assert manager._handlers == []
    assert manager.recent_events() == []
    assert not manager._policy_configured


def test_shared_metadata_templates_keep_existing_precedence():
    smonitor.get_manager().configure(
        codes={
            "T-SHARED": {
                "user_message": "Ordinary {count}",
                "metadata_message": "Shared {count}",
                "metadata_hint": "Shared hint {count}",
            }
        }
    )
    with smonitor.diagnostic_scope(safe_extra={"count": 3}):
        assert smonitor.resolve(code="T-SHARED", profile="user") == ("Shared 3", "Shared hint 3")


@pytest.mark.parametrize(
    "field,value",
    [
        ("metadata_hints", 42),
        ("metadata_hints", {"user": "Inspect {item.attr}"}),
        ("metadata_hints", {"user": "Inspect {item[0]}"}),
        ("metadata_hints", {"user": "Inspect {item!r}"}),
        ("metadata_hints", {"user": "Inspect {item:>10}"}),
        ("metadata_hints", {"operator": "Unsupported audience"}),
    ],
)
def test_invalid_safe_audience_declaration_rejects_whole_provider(tmp_path, field, value):
    root = tmp_path / "provider"
    root.mkdir()
    root.joinpath("_smonitor.py").write_text(
        f"CODES = {{'T-REF': {{'user_message': 'Known', {field!r}: {value!r}}}}}\n"
    )
    manager = smonitor.get_manager()

    with pytest.raises(ProviderRegistrationError) as caught:
        register_provider(root)

    assert caught.value.code == "SMONITOR-PROVIDER-INVALID"
    assert manager.get_codes() == {}
    assert manager.get_providers() == {}


def test_unsafe_direct_template_falls_back_without_rendering_opaque_values():
    class Opaque:
        def __str__(self):
            raise AssertionError("opaque conversion")

    manager = smonitor.get_manager()
    manager.configure(
        codes={
            "T-BAD": {
                "user_message": "Ordinary {secret}",
                "metadata_messages": {"user": "Unsafe {secret.attr}"},
                "metadata_hints": {"user": "Unsafe {secret!r}"},
            }
        }
    )
    with smonitor.diagnostic_scope(safe_extra={"count": 1}):
        assert smonitor.resolve(code="T-BAD", profile="user", extra={"secret": Opaque()}) == (
            "Diagnostic details omitted by capture policy.",
            None,
        )
