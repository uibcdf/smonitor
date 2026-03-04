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


def test_policy_sample_fraction_keeps_when_random_low(monkeypatch):
    engine = PolicyEngine()
    handlers = [DummyHandler("console")]
    engine.set_filters([{"when": {"code": "X"}, "sample": 0.5}])
    monkeypatch.setattr("smonitor.policy.engine.random", lambda: 0.1)
    _, hs = engine.apply({"code": "X"}, handlers)
    assert hs


def test_policy_set_extra_with_non_dict_extra_creates_dict():
    engine = PolicyEngine()
    handlers = [DummyHandler("console")]
    engine.set_routes([{"when": {"code": "X"}, "set_extra": {"k": "v"}}])
    event, _ = engine.apply({"code": "X", "extra": "bad"}, handlers)
    assert event["extra"] == {"k": "v"}


def test_policy_match_false_paths_cover_ops_and_lists():
    engine = PolicyEngine()
    assert engine._match({"source": "pkg.mod"}, {"source_prefix": "other."}) is False
    assert engine._match({"level": "INFO"}, {"level": {"eq": "ERROR"}}) is False
    assert engine._match({"tags": ["a", "b"]}, {"tags": "z"}) is False
    assert engine._op_prefix(None, "x") is False


def test_policy_rename_missing_field_and_non_list_tags_are_tolerated():
    engine = PolicyEngine()
    engine.set_routes(
        [
            {
                "when": {"level": "WARNING"},
                "rename": {"missing": "renamed"},
                "add_tags": ["extra"],
            }
        ]
    )
    event, _ = engine.apply(
        {"level": "WARNING", "source": "s", "tags": "not-a-list"},
        [DummyHandler("console")],
    )
    assert "renamed" not in event
    assert event["tags"] == "not-a-list"
