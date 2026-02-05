from smonitor.policy.engine import PolicyEngine


class DummyHandler:
    def __init__(self, name):
        self.name = name


def test_policy_rate_limit():
    engine = PolicyEngine()
    engine.set_filters([{"when": {"code": "X"}, "rate_limit": "1/2"}])
    handlers = [DummyHandler("console")]
    event = {"code": "X"}

    # First allowed
    _, hs1 = engine.apply(event, handlers)
    assert hs1

    # Second allowed (1/2 -> allow 1 of each 2, so 2nd blocked)
    _, hs2 = engine.apply(event, handlers)
    assert hs2 == []

    # Third allowed again
    _, hs3 = engine.apply(event, handlers)
    assert hs3


def test_policy_tags_membership():
    engine = PolicyEngine()
    engine.set_filters([{"when": {"tags": "io"}, "rate_limit": "1/1"}])
    handlers = [DummyHandler("console")]
    event = {"tags": ["io", "selection"]}
    _, hs = engine.apply(event, handlers)
    assert hs
