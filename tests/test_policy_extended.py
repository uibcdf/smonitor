from smonitor.policy.engine import PolicyEngine


class DummyHandler:
    def __init__(self, name):
        self.name = name


class NamedByClass:
    pass


def test_policy_send_to_by_handler_name_and_classname():
    engine = PolicyEngine()
    engine.set_routes([{"when": {"level": "ERROR"}, "send_to": ["json", "NamedByClass"]}])
    handlers = [DummyHandler("json"), DummyHandler("console"), NamedByClass()]
    ev, hs = engine.apply({"level": "ERROR"}, handlers)
    assert ev["level"] == "ERROR"
    assert len(hs) == 2


def test_policy_match_ops_in_contains_prefix_regex():
    engine = PolicyEngine()
    handlers = [DummyHandler("console")]
    engine.set_filters(
        [
            {
                "when": {
                    "source": {"prefix": "pkg."},
                    "message": {"contains": "needle"},
                    "code": {"regex": r"^X\d+$"},
                    "level": {"in": ["WARNING", "ERROR"]},
                },
                "drop": True,
            }
        ]
    )
    _, hs = engine.apply(
        {
            "source": "pkg.mod",
            "message": "has needle",
            "code": "X10",
            "level": "WARNING",
        },
        handlers,
    )
    assert hs == []


def test_policy_sample_fraction_blocks_when_random_high(monkeypatch):
    engine = PolicyEngine()
    handlers = [DummyHandler("console")]
    engine.set_filters([{"when": {"code": "X"}, "sample": 0.1}])
    monkeypatch.setattr("smonitor.policy.engine.random", lambda: 0.9)
    _, hs = engine.apply({"code": "X"}, handlers)
    assert hs == []


def test_policy_invalid_rate_limit_is_tolerated():
    engine = PolicyEngine()
    handlers = [DummyHandler("console")]
    engine.set_filters([{"when": {"code": "X"}, "rate_limit": "invalid"}])
    _, hs = engine.apply({"code": "X"}, handlers)
    assert hs


def test_policy_when_prefix_operator():
    engine = PolicyEngine()
    handlers = [DummyHandler("console")]
    engine.set_filters([{"when": {"source_prefix": "pkg."}, "drop": True}])
    _, hs = engine.apply({"source": "pkg.mod"}, handlers)
    assert hs == []
