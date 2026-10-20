"""Atomic TTL quotas; only domain-separated HMACs reach Redis."""

import hashlib
import hmac

from django.conf import settings
from redis.exceptions import RedisError

from apps.accounts.client_ip import client_ip
from apps.accounts.limiter import canonical_ip, redis_client

from .contracts import MarketplaceUnavailable

LIMITS = {"search": 60, "origin": 120}
SCRIPT = """
local retry = 1
local denied = false
for _, key in ipairs(KEYS) do
    if tonumber(redis.call('GET', key) or '0') >= tonumber(ARGV[1]) then
        denied = true
        local ttl = redis.call('TTL', key)
        if ttl < 0 then ttl = 60; redis.call('EXPIRE', key, 60) end
        retry = math.max(retry, ttl)
    end
end
if denied then return {0, math.max(1, math.min(60, retry))} end
for _, key in ipairs(KEYS) do
    local count = redis.call('INCR', key)
    if count == 1 or redis.call('TTL', key) < 0 then redis.call('EXPIRE', key, 60) end
end
return {1, 0}
"""


class MarketplaceRateLimited(RuntimeError):
    def __init__(self, retry_after):
        super().__init__("Marketplace request limit reached")
        self.retry_after = max(1, min(60, int(retry_after)))


def rate_keys(kind, identity):
    if kind not in LIMITS:
        raise ValueError("Invalid marketplace quota")
    identity = canonical_ip(identity)
    ring = settings.ACCOUNT_SECURITY.keys
    payload = b"fitlink:c04:quota:" + kind.encode() + b"\x00" + identity.encode()
    return tuple(
        f"fitlink:c04:{kind}:{key_id}:"
        + hmac.new(ring.material[key_id], payload, hashlib.sha256).hexdigest()
        for key_id in ring.key_ids
    )


def admit(kind, identity):
    keys = rate_keys(kind, identity)
    try:
        with redis_client() as client:
            result = client.register_script(SCRIPT)(
                keys=list(keys), args=[LIMITS[kind]]
            )
        if (
            not isinstance(result, (tuple, list))
            or len(result) != 2
            or result[0] not in (0, 1)
        ):
            raise ValueError
        allowed, retry = map(int, result)
    except (RedisError, ValueError, TypeError):
        raise MarketplaceUnavailable("Marketplace temporarily unavailable") from None
    if not allowed:
        raise MarketplaceRateLimited(retry)


def admit_request(request, kind="search"):
    identity = client_ip(
        request.META.get("REMOTE_ADDR", ""),
        request.META.get("HTTP_X_FORWARDED_FOR"),
        settings.ACCOUNT_SECURITY.trusted_proxy_cidrs,
    )
    admit(kind, identity)
