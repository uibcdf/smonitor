"""Tests for the support-tier protocol: SupportTierRegistry and support_tier decorator."""
from __future__ import annotations

from pathlib import Path

import pytest

import smonitor
from smonitor import integrations
from smonitor.integrations.diagnostic import DiagnosticBundle, SupportTierRegistry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_bundle(catalog=None):
    smonitor.configure(profile="user", handlers=[], event_buffer_size=20, enabled=True)
    return DiagnosticBundle(
        catalog=catalog or {},
        meta={"library": "testlib"},
        package_root=Path.cwd(),
    )


def _recent_events():
    return smonitor.get_manager().recent_events()


# ---------------------------------------------------------------------------
# SupportTierRegistry — registration
# ---------------------------------------------------------------------------

class TestSupportTierRegistryRegistration:

    def test_register_single(self):
        bundle = _make_bundle()
        reg = bundle.tier_registry()
        reg.register("mylib.FormA", 2)
        assert reg._tiers["mylib.FormA"] == 2

    def test_register_many(self):
        bundle = _make_bundle()
        reg = bundle.tier_registry()
        reg.register_many({"mylib.FormA": 1, "mylib.FormB": 2, "mylib.FormC": 3})
        assert reg._tiers["mylib.FormA"] == 1
        assert reg._tiers["mylib.FormB"] == 2
        assert reg._tiers["mylib.FormC"] == 3

    def test_tier_registry_is_lazy_and_persistent(self):
        bundle = _make_bundle()
        reg1 = bundle.tier_registry()
        reg2 = bundle.tier_registry()
        assert reg1 is reg2

    def test_registry_exported_from_integrations(self):
        assert "SupportTierRegistry" in dir(integrations)
        assert SupportTierRegistry is integrations.SupportTierRegistry


# ---------------------------------------------------------------------------
# SupportTierRegistry — check() / tier 1
# ---------------------------------------------------------------------------

class TestSupportTierRegistryTier1:

    def test_tier1_check_emits_nothing(self):
        smonitor.configure(profile="user", handlers=[], event_buffer_size=20, enabled=True)
        bundle = _make_bundle()
        reg = bundle.tier_registry()
        reg.register("mylib.FormA", 1)
        before = len(_recent_events())
        reg.check("mylib.FormA")
        assert len(_recent_events()) == before

    def test_unregistered_name_emits_nothing(self):
        smonitor.configure(profile="user", handlers=[], event_buffer_size=20, enabled=True)
        bundle = _make_bundle()
        reg = bundle.tier_registry()
        before = len(_recent_events())
        reg.check("not.registered")
        assert len(_recent_events()) == before


# ---------------------------------------------------------------------------
# SupportTierRegistry — check() / tier 2
# ---------------------------------------------------------------------------

class TestSupportTierRegistryTier2:

    def test_tier2_check_emits_warning(self):
        smonitor.configure(profile="user", handlers=[], event_buffer_size=20, enabled=True)
        bundle = _make_bundle()
        reg = bundle.tier_registry()
        reg.register("mylib.FormB", 2)
        before = len(_recent_events())
        reg.check("mylib.FormB")
        events = _recent_events()
        assert len(events) > before
        new_event = events[-1]
        assert new_event["level"] == "WARNING"

    def test_tier2_check_deduplicates_per_session(self):
        smonitor.configure(profile="user", handlers=[], event_buffer_size=20, enabled=True)
        bundle = _make_bundle()
        reg = bundle.tier_registry()
        reg.register("mylib.FormB", 2)
        reg.check("mylib.FormB")
        count_after_first = len(_recent_events())
        reg.check("mylib.FormB")
        reg.check("mylib.FormB")
        assert len(_recent_events()) == count_after_first

    def test_tier2_different_names_each_emit_once(self):
        smonitor.configure(profile="user", handlers=[], event_buffer_size=20, enabled=True)
        bundle = _make_bundle()
        reg = bundle.tier_registry()
        reg.register_many({"mylib.FormX": 2, "mylib.FormY": 2})
        before = len(_recent_events())
        reg.check("mylib.FormX")
        reg.check("mylib.FormY")
        assert len(_recent_events()) == before + 2

    def test_tier2_check_uses_catalog_entry_when_present(self):
        catalog = {
            "warnings": {
                "SupportTier2Warning": {
                    "code": "LIB-WARN-TIER-002",
                    "source": "testlib.warning.tier2",
                    "level": "WARNING",
                }
            }
        }
        smonitor.configure(
            profile="user",
            handlers=[],
            event_buffer_size=20,
            enabled=True,
            codes={"LIB-WARN-TIER-002": {"user_message": "Tier 2 form: {name}"}},
        )
        bundle = _make_bundle(catalog=catalog)
        reg = bundle.tier_registry()
        reg.register("mylib.FormB", 2)
        reg.check("mylib.FormB")
        events = _recent_events()
        assert any(e.get("code") == "LIB-WARN-TIER-002" for e in events)

    def test_tier2_extra_includes_name_kind_tier(self):
        smonitor.configure(profile="user", handlers=[], event_buffer_size=20, enabled=True)
        bundle = _make_bundle()
        reg = bundle.tier_registry()
        reg.register("mylib.FormB", 2)
        before = len(_recent_events())
        reg.check("mylib.FormB")
        event = _recent_events()[before]
        assert event["extra"]["name"] == "mylib.FormB"
        assert event["extra"]["kind"] == "form"
        assert event["extra"]["tier"] == 2


# ---------------------------------------------------------------------------
# SupportTierRegistry — check() / tier 3
# ---------------------------------------------------------------------------

class TestSupportTierRegistryTier3:

    def test_tier3_check_emits_info(self):
        smonitor.configure(profile="user", level="INFO", handlers=[], event_buffer_size=20, enabled=True)
        bundle = _make_bundle()
        reg = bundle.tier_registry()
        reg.register("mylib.FormC", 3)
        before = len(_recent_events())
        reg.check("mylib.FormC")
        events = _recent_events()
        assert len(events) > before
        assert events[-1]["level"] == "INFO"

    def test_tier3_check_deduplicates_per_session(self):
        smonitor.configure(profile="user", level="INFO", handlers=[], event_buffer_size=20, enabled=True)
        bundle = _make_bundle()
        reg = bundle.tier_registry()
        reg.register("mylib.FormC", 3)
        reg.check("mylib.FormC")
        count_after_first = len(_recent_events())
        reg.check("mylib.FormC")
        assert len(_recent_events()) == count_after_first

    def test_tier3_falls_back_to_experimental_path_catalog_key(self):
        catalog = {
            "info": {
                "ExperimentalPath": {
                    "code": "LIB-INFO-EXP-001",
                    "source": "testlib.info.experimental",
                    "level": "INFO",
                }
            }
        }
        smonitor.configure(
            profile="user",
            level="INFO",
            handlers=[],
            event_buffer_size=20,
            enabled=True,
            codes={"LIB-INFO-EXP-001": {"user_message": "Experimental: {name}"}},
        )
        bundle = _make_bundle(catalog=catalog)
        reg = bundle.tier_registry()
        reg.register("mylib.FormC", 3)
        reg.check("mylib.FormC")
        events = _recent_events()
        assert any(e.get("code") == "LIB-INFO-EXP-001" for e in events)


# ---------------------------------------------------------------------------
# support_tier decorator — tier 1
# ---------------------------------------------------------------------------

class TestSupportTierDecoratorTier1:

    def test_tier1_returns_original_function(self):
        bundle = _make_bundle()

        @bundle.support_tier(1)
        def my_func():
            return 42

        assert my_func() == 42

    def test_tier1_is_exact_same_object(self):
        bundle = _make_bundle()
        original = lambda: None  # noqa: E731
        decorated = bundle.support_tier(1)(original)
        assert decorated is original

    def test_tier1_emits_nothing(self):
        smonitor.configure(profile="user", handlers=[], event_buffer_size=20, enabled=True)
        bundle = _make_bundle()

        @bundle.support_tier(1)
        def my_func():
            return 1

        before = len(_recent_events())
        my_func()
        assert len(_recent_events()) == before


# ---------------------------------------------------------------------------
# support_tier decorator — tier 2
# ---------------------------------------------------------------------------

class TestSupportTierDecoratorTier2:

    def test_tier2_emits_warning_on_first_call(self):
        smonitor.configure(profile="user", handlers=[], event_buffer_size=20, enabled=True)
        bundle = _make_bundle()

        @bundle.support_tier(2)
        def best_effort_func():
            return "ok"

        before = len(_recent_events())
        best_effort_func()
        events = _recent_events()
        assert len(events) > before
        assert events[-1]["level"] == "WARNING"

    def test_tier2_deduplicates_across_calls(self):
        smonitor.configure(profile="user", handlers=[], event_buffer_size=20, enabled=True)
        bundle = _make_bundle()

        @bundle.support_tier(2)
        def best_effort_func():
            return "ok"

        best_effort_func()
        count_after_first = len(_recent_events())
        best_effort_func()
        best_effort_func()
        assert len(_recent_events()) == count_after_first

    def test_tier2_function_still_returns_value(self):
        smonitor.configure(profile="user", handlers=[], event_buffer_size=20, enabled=True)
        bundle = _make_bundle()

        @bundle.support_tier(2)
        def compute(x):
            return x * 2

        assert compute(5) == 10

    def test_tier2_extra_includes_function_context(self):
        smonitor.configure(profile="user", handlers=[], event_buffer_size=20, enabled=True)
        bundle = _make_bundle()

        @bundle.support_tier(2)
        def my_tier2():
            pass

        before = len(_recent_events())
        my_tier2()
        event = _recent_events()[before]
        assert event["extra"]["kind"] == "function"
        assert event["extra"]["tier"] == 2
        assert "my_tier2" in event["extra"]["name"]

    def test_tier2_different_functions_each_emit_once(self):
        smonitor.configure(profile="user", handlers=[], event_buffer_size=20, enabled=True)
        bundle = _make_bundle()

        @bundle.support_tier(2)
        def func_alpha():
            pass

        @bundle.support_tier(2)
        def func_beta():
            pass

        before = len(_recent_events())
        func_alpha()
        func_beta()
        assert len(_recent_events()) == before + 2

    def test_tier2_preserves_function_metadata(self):
        bundle = _make_bundle()

        @bundle.support_tier(2)
        def documented_func():
            """My docstring."""

        assert documented_func.__name__ == "documented_func"
        assert documented_func.__doc__ == "My docstring."


# ---------------------------------------------------------------------------
# support_tier decorator — tier 3
# ---------------------------------------------------------------------------

class TestSupportTierDecoratorTier3:

    def test_tier3_emits_info_on_first_call(self):
        smonitor.configure(profile="user", level="INFO", handlers=[], event_buffer_size=20, enabled=True)
        bundle = _make_bundle()

        @bundle.support_tier(3)
        def experimental_func():
            return "x"

        before = len(_recent_events())
        experimental_func()
        events = _recent_events()
        assert len(events) > before
        assert events[-1]["level"] == "INFO"

    def test_tier3_deduplicates_across_calls(self):
        smonitor.configure(profile="user", level="INFO", handlers=[], event_buffer_size=20, enabled=True)
        bundle = _make_bundle()

        @bundle.support_tier(3)
        def experimental_func():
            pass

        experimental_func()
        count_after_first = len(_recent_events())
        experimental_func()
        experimental_func()
        assert len(_recent_events()) == count_after_first

    def test_tier3_function_still_executes(self):
        smonitor.configure(profile="user", level="INFO", handlers=[], event_buffer_size=20, enabled=True)
        bundle = _make_bundle()

        @bundle.support_tier(3)
        def experimental_func(x):
            return x + 1

        assert experimental_func(7) == 8


# ---------------------------------------------------------------------------
# Isolation: separate bundles have independent dedup caches
# ---------------------------------------------------------------------------

class TestSupportTierIsolation:

    def test_two_bundles_deduplicate_independently(self):
        smonitor.configure(profile="user", handlers=[], event_buffer_size=40, enabled=True)
        bundle_a = _make_bundle()
        bundle_b = _make_bundle()
        reg_a = bundle_a.tier_registry()
        reg_b = bundle_b.tier_registry()
        reg_a.register("mylib.FormX", 2)
        reg_b.register("mylib.FormX", 2)

        before = len(_recent_events())
        reg_a.check("mylib.FormX")
        reg_b.check("mylib.FormX")
        # Each bundle emits once independently
        assert len(_recent_events()) == before + 2

    def test_registry_and_decorator_share_bundle_dedup_cache(self):
        """A name checked via registry won't fire again via _emit_tier_signal."""
        smonitor.configure(profile="user", handlers=[], event_buffer_size=20, enabled=True)
        bundle = _make_bundle()
        reg = bundle.tier_registry()
        reg.register("mylib.FormX", 2)
        reg.check("mylib.FormX")
        count_after_first = len(_recent_events())
        # Calling _emit_tier_signal directly with same name should be a no-op
        bundle._emit_tier_signal(tier=2, name="mylib.FormX", kind="form")
        assert len(_recent_events()) == count_after_first
