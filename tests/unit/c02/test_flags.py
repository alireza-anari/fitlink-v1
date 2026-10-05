import importlib
import importlib.util

import pytest
from django.db import DatabaseError

pytestmark = pytest.mark.unit

KEYS = {"marketplace", "professional_registration", "ai_insights", "ai_mirror"}


def contract():
    assert importlib.util.find_spec("apps.governance.flags"), (
        "missing operational flags"
    )
    return importlib.import_module("apps.governance.flags")


def test_exact_four_keys_without_permission_api():
    module = contract()
    assert set(module.FEATURE_KEYS) == KEYS
    assert callable(module.set_feature)
    assert not hasattr(module, "can_access_object")


def test_unknown_flag_does_not_query_database(monkeypatch):
    module = contract()
    monkeypatch.setattr(
        module.FeatureFlag.objects,
        "get",
        lambda **kw: pytest.fail("unknown flag queried"),
    )
    assert module.feature_enabled("unknown") is False


@pytest.mark.parametrize("key", sorted(KEYS))
def test_database_failure_disables_each_flag(monkeypatch, key):
    module = contract()

    def unavailable(**kw):
        raise DatabaseError("database unavailable")

    monkeypatch.setattr(module.FeatureFlag.objects, "get", unavailable)
    assert module.feature_enabled(key) is False


def test_professional_entry_reads_its_own_switch(monkeypatch):
    module = contract()
    seen = []
    monkeypatch.setattr(
        module, "feature_enabled", lambda key: seen.append(key) or False
    )
    assert module.professional_entry_enabled() is False
    assert seen == ["professional_registration"]
