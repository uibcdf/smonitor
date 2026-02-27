from smonitor.handlers.console import ConsoleHandler


class _Buffer:
    def __init__(self):
        self.parts = []

    def write(self, text):
        self.parts.append(text)

    def flush(self):
        return None

    def getvalue(self):
        return "".join(self.parts)


def test_console_user_includes_hint():
    stream = _Buffer()
    handler = ConsoleHandler(stream=stream)
    handler.handle(
        {"level": "WARNING", "message": "problem", "extra": {"hint": "fix it"}},
        profile="user",
    )
    text = stream.getvalue().strip()
    assert "WARNING: problem" in text
    assert "Hint: fix it" in text


def test_console_qa_includes_code_and_source():
    stream = _Buffer()
    handler = ConsoleHandler(stream=stream)
    handler.handle(
        {
            "level": "ERROR",
            "message": "boom",
            "source": "pkg.mod",
            "code": "E-1",
        },
        profile="qa",
    )
    text = stream.getvalue().strip()
    assert text.startswith("[E-1] ERROR pkg.mod | boom")


def test_console_dev_adds_context_chain_and_error_args():
    stream = _Buffer()
    handler = ConsoleHandler(stream=stream)
    handler.handle(
        {
            "level": "ERROR",
            "message": "failed",
            "source": "pkg.mod",
            "code": "E-2",
            "context": {
                "chain": ["a", "b"],
                "frames": [
                    {"module": "m", "function": "f", "args": {"x": 1}},
                    {"module": "n", "function": "g", "args": None},
                ],
            },
            "extra": {"hint": "inspect input"},
        },
        profile="dev",
    )
    text = stream.getvalue()
    assert "[E-2] ERROR pkg.mod | failed | a ❯ b | Hint: inspect input" in text
    assert "m.f({'x': 1})" in text


def test_console_agent_without_code_is_still_machine_readable():
    stream = _Buffer()
    handler = ConsoleHandler(stream=stream)
    handler.handle(
        {"level": "INFO", "message": "ok", "source": "pkg.mod"},
        profile="agent",
    )
    text = stream.getvalue().strip()
    assert text == "code=None level=INFO source=pkg.mod message=ok"
