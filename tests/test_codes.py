import smonitor
from smonitor.core.manager import get_manager


def test_codes_fill_message_and_hint(tmp_path):
    # Create a temporary _smonitor.py
    cfg_path = tmp_path / "_smonitor.py"
    cfg_path.write_text(
        "CODES = {\n"
        "  'X001': {\n"
        "    'title': 'Test',\n"
        "    'user_message': 'User msg',\n"
        "    'user_hint': 'User hint'\n"
        "  }\n"
        "}\n"
    )

    # Configure using that config
    smonitor.configure(profile="user")
    manager = get_manager()
    manager.configure(
        codes={
            "X001": {
                "title": "Test",
                "user_message": "User msg",
                "user_hint": "User hint",
            }
        }
    )

    event = smonitor.emit("WARNING", "", code="X001")
    assert event["message"] == "User msg"
    assert event["extra"]["hint"] == "User hint"


def test_codes_template_with_extra():
    manager = get_manager()
    manager.configure(
        codes={"X002": {"user_message": "Value {v} is bad", "user_hint": "Use {alt}"}}
    )
    event = smonitor.emit("WARNING", "", code="X002", extra={"v": "X", "alt": "Y"})
    assert event["message"] == "Value X is bad"
    assert event["extra"]["hint"] == "Use Y"


def test_contract_warning_missing_extra():
    manager = get_manager()
    manager.configure(profile="dev", signals={"mod.fn": {"extra_required": ["foo"]}})
    event = smonitor.emit("WARNING", "msg", source="mod.fn", extra={})
    assert "contract_warning" in event["extra"]


def test_strict_signals_raises():
    manager = get_manager()
    manager.configure(
        profile="dev",
        strict_signals=True,
        signals={"mod.fn": {"extra_required": ["foo"]}},
    )
    try:
        smonitor.emit("WARNING", "msg", source="mod.fn", extra={})
    except ValueError as exc:
        assert "Missing extra fields" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_a_malformed_codes_entry_degrades_instead_of_raising():
    """A code mapped to a string used to raise `AttributeError` from `resolve()`.

    Found by running the guide's section 7 checks across the ecosystem: one
    library maps its codes straight to message strings. Diagnostics must not be
    the thing that breaks the call reporting a problem; `validate_project_config`
    is where a malformed entry is named.
    """
    smonitor.configure(profile="user", handlers=[], codes={"X-BAD": "just a string"})

    message, hint = smonitor.resolve(code="X-BAD", extra={})
    assert (message, hint) == ("", None)

    event = smonitor.emit("WARNING", "still reported", code="X-BAD")
    assert event["message"] == "still reported"
    assert event["code"] == "X-BAD"
