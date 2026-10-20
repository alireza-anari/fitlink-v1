"""Search admission is a separate HMAC namespace and fails closed."""

import importlib
import importlib.util

import pytest
from redis.exceptions import ConnectionError

pytestmark = pytest.mark.unit


def limiter():
    assert importlib.util.find_spec("apps.marketplace.limiter") is not None, (
        "Missing marketplace admission"
    )
    return importlib.import_module("apps.marketplace.limiter")


def test_search_limiter_outage_does_not_expose_provider_detail(monkeypatch):
    module = limiter()

    def unavailable():
        raise ConnectionError("PRIVATE-REDIS-HOST-SENTINEL")

    monkeypatch.setattr(module, "redis_client", unavailable)
    with pytest.raises(RuntimeError) as error:
        module.admit("search", "203.0.113.8")
    assert str(error.value) == "Marketplace temporarily unavailable"


def test_namespace_uses_only_digest_and_retained_key_identifiers():
    keys = limiter().rate_keys("search", "203.0.113.8")
    assert keys and all(key.startswith("fitlink:c04:search:") for key in keys)
    assert all("203.0.113.8" not in key and "otp" not in key for key in keys)


def test_unknown_quota_and_invalid_ip_rejected():
    for kind, ip in [("otp", "203.0.113.8"), ("search", "PRIVATE-NOT-IP")]:
        with pytest.raises(ValueError):
            limiter().admit(kind, ip)
