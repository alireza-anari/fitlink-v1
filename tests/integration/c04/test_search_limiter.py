"""Real Redis atomically enforces separate expiring search quotas."""

from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest

pytestmark = pytest.mark.integration


def test_real_redis_sixty_admissions_and_atomic_concurrent_boundary():
    from apps.marketplace.limiter import (
        MarketplaceRateLimited,
        admit,
        rate_keys,
        redis_client,
    )

    # Unique synthetic documentation IP, never a user address or query.
    value = int(uuid4()) % 65536
    ip = f"198.18.{value // 256}.{value % 256}"
    keys = rate_keys("search", ip)
    with redis_client() as client:
        client.delete(*keys)
    try:
        for _ in range(59):
            admit("search", ip)

        def attempt():
            try:
                admit("search", ip)
                return True
            except MarketplaceRateLimited as error:
                assert 1 <= error.retry_after <= 60
                return False

        with ThreadPoolExecutor(max_workers=4) as pool:
            assert sum(pool.map(lambda _: attempt(), range(4))) == 1
        admit("origin", ip)
        with redis_client() as client:
            assert all(0 < client.ttl(key) <= 60 for key in keys)
            assert all(int(client.get(key)) == 60 for key in keys)
    finally:
        with redis_client() as client:
            client.delete(*keys, *rate_keys("origin", ip))


@pytest.mark.parametrize("milliseconds", [500, None])
def test_limit_stays_closed_at_subsecond_or_missing_ttl(milliseconds):
    from apps.marketplace.limiter import (
        MarketplaceRateLimited,
        admit,
        rate_keys,
        redis_client,
    )

    ip = "198.19.0.14"
    keys = rate_keys("search", ip)
    try:
        with redis_client() as client:
            for key in keys:
                client.set(key, 60, px=milliseconds)
        with pytest.raises(MarketplaceRateLimited):
            admit("search", ip)
    finally:
        with redis_client() as client:
            client.delete(*keys)


def test_actual_redis_connection_loss_fails_closed_and_restoration_recovers(settings):
    import socket

    from apps.marketplace.contracts import MarketplaceUnavailable
    from apps.marketplace.limiter import admit, rate_keys, redis_client

    original = settings.OTP_RATE_REDIS_URL
    ip = "198.19.0.15"
    keys = rate_keys("search", ip)
    with redis_client() as client:
        client.delete(*keys)
    try:
        with socket.socket() as unavailable:
            unavailable.bind(("127.0.0.1", 0))
            settings.OTP_RATE_REDIS_URL = (
                f"redis://127.0.0.1:{unavailable.getsockname()[1]}/4"
            )
            with pytest.raises(
                MarketplaceUnavailable, match="^Marketplace temporarily unavailable$"
            ):
                admit("search", ip)
        settings.OTP_RATE_REDIS_URL = original
        admit("search", ip)
    finally:
        settings.OTP_RATE_REDIS_URL = original
        with redis_client() as client:
            client.delete(*keys)
