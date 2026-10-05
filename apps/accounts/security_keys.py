"""Bounded environment key ring and domain-separated keyed identifiers."""

import base64
import hashlib
import hmac
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from django.core.exceptions import ImproperlyConfigured


@dataclass(frozen=True)
class SecurityKeyRing:
    active_id: str
    material: Mapping[str, bytes] = field(repr=False)

    @property
    def key_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self.material))


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError
        result[key] = value
    return result


def parse_key_ring(raw: str, active_id: str) -> SecurityKeyRing:
    try:
        if not isinstance(raw, str) or len(raw) > 2048:
            raise ValueError
        values = json.loads(raw, object_pairs_hook=_pairs)
        if not isinstance(values, dict) or not 1 <= len(values) <= 3:
            raise ValueError
        decoded = {}
        for key_id, value in values.items():
            if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", key_id):
                raise ValueError
            if not isinstance(value, str):
                raise ValueError
            key = base64.b64decode(value, validate=True)
            if not 32 <= len(key) <= 64:
                raise ValueError
            decoded[key_id] = key
    except (ValueError, TypeError):
        raise ImproperlyConfigured("Invalid ACCOUNT_SECURITY_KEYS_JSON") from None
    if active_id not in decoded:
        raise ImproperlyConfigured("Invalid ACCOUNT_SECURITY_ACTIVE_KEY_ID")
    return SecurityKeyRing(active_id, MappingProxyType(decoded))


def security_digest(
    kind: str, value: str, key_id: str, *, ring: SecurityKeyRing | None = None
) -> str:
    if ring is None:
        from django.conf import settings

        ring = settings.ACCOUNT_SECURITY.keys
    if kind not in {"otp", "phone", "ip", "receipt", "session", "referral"}:
        raise ValueError("invalid security domain")
    if key_id not in ring.material:
        raise ValueError("unknown security key")
    payload = b"fitlink:c02:" + kind.encode("ascii") + b"\x00" + value.encode("utf-8")
    return hmac.new(ring.material[key_id], payload, hashlib.sha256).hexdigest()
