import uuid

import pytest
from django.core.cache import cache

from config.health import redis_available

pytestmark = pytest.mark.integration


def test_cache_roundtrip_and_prefix():
    key = "probe-" + str(uuid.uuid4())
    try:
        cache.set(key, "ok", timeout=30)
        assert cache.get(key) == "ok"
        assert cache.make_key(key).startswith("fitlink:")
    finally:
        cache.delete(key)
    assert cache.get(key) is None


def test_redis_probe_success():
    assert redis_available()
