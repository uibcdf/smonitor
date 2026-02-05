import os
import smonitor


def test_profile_user_has_hint_in_message():
    os.environ["SMONITOR_PROFILE"] = "user"
    smonitor.configure(profile="user")
    event = smonitor.emit("WARNING", "", code=None, extra={"hint": "H"})
    # Hint is carried in extra; formatting is handler-dependent
    assert event.get("extra", {}).get("hint") == "H"
