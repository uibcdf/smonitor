import json

import smonitor
from smonitor.handlers.console import ConsoleHandler
from smonitor.handlers.json import JsonHandler


class _Buffer:
    def __init__(self):
        self.parts = []

    def write(self, text):
        self.parts.append(text)

    def flush(self):
        return None

    def getvalue(self):
        return "".join(self.parts)


def test_agent_profile_prefers_agent_templates():
    smonitor.configure(
        profile="agent",
        handlers=[],
        codes={
            "AG-001": {
                "agent_message": "AGENT {x}",
                "agent_hint": "HINT {x}",
                "dev_message": "DEV {x}",
                "dev_hint": "DEVH {x}",
            }
        },
    )
    event = smonitor.emit("WARNING", "", code="AG-001", extra={"x": "ok"})
    assert event["message"] == "AGENT ok"
    assert event["extra"]["hint"] == "HINT ok"


def test_agent_console_output_is_machine_oriented():
    stream = _Buffer()
    handler = ConsoleHandler(stream=stream)
    handler.handle(
        {
            "level": "ERROR",
            "source": "mylib.core",
            "message": "broken",
            "code": "AG-ERR-1",
        },
        profile="agent",
    )
    line = stream.getvalue().strip()
    assert line == "code=AG-ERR-1 level=ERROR source=mylib.core message=broken"


def test_agent_json_payload_contains_stable_fields(tmp_path):
    path = tmp_path / "agent.jsonl"
    handler = JsonHandler(str(path), mode="w")
    handler.handle(
        {
            "level": "WARNING",
            "message": "warn",
            "source": "mylib.select",
            "code": "AG-W1",
            "category": "diagnostics",
            "extra": {"hint": "use filter"},
        },
        profile="agent",
    )
    payload = json.loads(path.read_text(encoding="utf-8").strip())
    assert payload["profile"] == "agent"
    assert payload["level"] == "WARNING"
    assert payload["source"] == "mylib.select"
    assert payload["code"] == "AG-W1"
    assert payload["category"] == "diagnostics"
