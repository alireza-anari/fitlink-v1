"""Atomic Redis admission plus PostgreSQL's authoritative durable quota guard."""

import math
import ssl
from dataclasses import dataclass
from datetime import datetime, timedelta
from ipaddress import IPv6Address, ip_address
from pathlib import Path
from uuid import UUID, uuid4

from django.conf import settings
from django.db import DatabaseError, transaction
from django.db.models import Q
from redis import Redis
from redis.exceptions import RedisError

from .contracts import AccountSecurityPolicy, AdmissionResult
from .phone import normalize_iranian_mobile
from .security_keys import SecurityKeyRing, security_digest
from .security_models import SecurityRateAnchor, SecurityRateEvent


class LimiterUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class RateKeys:
    phone: tuple[str, ...]
    ip: tuple[str, ...]
    active_position: int


def canonical_ip(value: str) -> str:
    if "%" in value:
        raise ValueError("Invalid admission address")
    address = ip_address(value)
    if isinstance(address, IPv6Address) and address.ipv4_mapped:
        address = address.ipv4_mapped
    return str(address)


def limits(kind: str, policy: AccountSecurityPolicy) -> tuple[int, int]:
    if kind == "send":
        return policy.send_phone, policy.send_ip
    if kind == "verify_failure":
        return policy.failure_phone, policy.failure_ip
    if kind == "recovery_intake":
        return policy.recovery_phone, policy.recovery_ip
    raise ValueError("Invalid admission kind")


def _key(kind: str, dimension: str, key_id: str, digest: str) -> str:
    return f"fitlink:otp:{kind}:{dimension}:{key_id}:{digest}"


def rate_keys(
    phone: str, ip: str, kind: str, *, ring: SecurityKeyRing | None = None
) -> RateKeys:
    limits(kind, settings.ACCOUNT_SECURITY.policy)
    phone, ip = normalize_iranian_mobile(phone), canonical_ip(ip)
    ring = ring or settings.ACCOUNT_SECURITY.keys
    return RateKeys(
        tuple(
            _key(
                kind,
                "phone",
                key_id,
                security_digest("phone", phone, key_id, ring=ring),
            )
            for key_id in ring.key_ids
        ),
        tuple(
            _key(kind, "ip", key_id, security_digest("ip", ip, key_id, ring=ring))
            for key_id in ring.key_ids
        ),
        ring.key_ids.index(ring.active_id) + 1,
    )


def redis_client() -> Redis:
    url = settings.OTP_RATE_REDIS_URL
    tls = (
        {"ssl_cert_reqs": ssl.CERT_REQUIRED, "ssl_check_hostname": True}
        if url.startswith("rediss://")
        else {}
    )
    return Redis.from_url(
        url,
        socket_connect_timeout=2,
        socket_timeout=2,
        retry_on_timeout=False,
        decode_responses=True,
        **tls,
    )


def _redis_admission(
    keys: RateKeys, kind: str, at: datetime, reservation: UUID
) -> AdmissionResult:
    policy = settings.ACCOUNT_SECURITY.policy
    phone_limit, ip_limit = limits(kind, policy)
    try:
        with redis_client() as client:
            script = client.register_script(
                Path(__file__)
                .with_name("lua")
                .joinpath("otp_admission.lua")
                .read_text()
            )
            allowed, retry = script(
                keys=[*keys.phone, *keys.ip],
                args=[
                    "reserve",
                    int(at.timestamp() * 1000),
                    policy.window_seconds * 1000,
                    phone_limit,
                    ip_limit,
                    len(keys.phone),
                    str(reservation),
                    keys.active_position,
                ],
            )
    except RedisError:
        raise LimiterUnavailable("Admission unavailable") from None
    return AdmissionResult(
        bool(allowed), math.ceil(retry / 1000), reservation if allowed else None
    )


def locked_rate_anchors(
    phone: str, ip: str
) -> tuple[list[SecurityRateAnchor], list[SecurityRateAnchor]]:
    """Caller holds atomic; create conflict-safely, then lock global sorted order."""
    if not transaction.get_connection().in_atomic_block:
        raise RuntimeError("Quota locks require a transaction")
    ring = settings.ACCOUNT_SECURITY.keys
    values = sorted(
        (dimension, key_id, security_digest(dimension, value, key_id))
        for dimension, value in [("phone", phone), ("ip", ip)]
        for key_id in ring.key_ids
    )
    ids = []
    for dimension, key_id, digest in values:
        anchor, _ = SecurityRateAnchor.objects.get_or_create(
            kind=dimension, key_id=key_id, key_digest=digest
        )
        ids.append(anchor.pk)
    locked = list(
        SecurityRateAnchor.objects.select_for_update()
        .filter(pk__in=ids)
        .order_by("kind", "key_id", "key_digest")
    )
    return [a for a in locked if a.kind == "phone"], [
        a for a in locked if a.kind == "ip"
    ]


def durable_admission(
    phone: str, ip: str, kind: str, at: datetime, reservation_id: UUID
) -> AdmissionResult:
    phone, ip = normalize_iranian_mobile(phone), canonical_ip(ip)
    policy = settings.ACCOUNT_SECURITY.policy
    phone_limit, ip_limit = limits(kind, policy)
    with transaction.atomic():
        phones, ips = locked_rate_anchors(phone, ip)
        existing = SecurityRateEvent.objects.filter(pk=reservation_id).first()
        if existing:
            if (
                existing.phone_anchor_id not in {a.pk for a in phones}
                or existing.ip_anchor_id not in {a.pk for a in ips}
                or existing.kind != kind
            ):
                raise LimiterUnavailable("Admission unavailable")
            return AdmissionResult(True, 0, reservation_id)
        events = SecurityRateEvent.objects.filter(
            kind=kind, at__gt=at - timedelta(seconds=policy.window_seconds)
        )
        if kind == "verify_failure":
            events = events.filter(outcome__in=["pending", "failed"])
        phone_events = events.filter(phone_anchor__in=phones)
        ip_events = events.filter(ip_anchor__in=ips)
        if phone_events.count() >= phone_limit or ip_events.count() >= ip_limit:
            first = (
                events.filter(Q(phone_anchor__in=phones) | Q(ip_anchor__in=ips))
                .order_by("at")
                .first()
            )
            retry = (
                max(
                    1,
                    math.ceil(
                        (
                            first.at + timedelta(seconds=policy.window_seconds) - at
                        ).total_seconds()
                    ),
                )
                if first
                else policy.window_seconds
            )
            return AdmissionResult(False, retry, None)
        key_id = settings.ACCOUNT_SECURITY.keys.active_id
        SecurityRateEvent.objects.create(
            reservation_id=reservation_id,
            phone_anchor=next(a for a in phones if a.key_id == key_id),
            ip_anchor=next(a for a in ips if a.key_id == key_id),
            kind=kind,
            at=at,
        )
        return AdmissionResult(True, 0, reservation_id)


def reserve_admission(phone: str, ip: str, kind: str, at: datetime) -> AdmissionResult:
    if at.tzinfo is None:
        raise ValueError("Server time required")
    phone, ip = normalize_iranian_mobile(phone), canonical_ip(ip)
    reservation = uuid4()
    admitted = _redis_admission(rate_keys(phone, ip, kind), kind, at, reservation)
    if not admitted.allowed:
        return admitted
    try:
        return durable_admission(phone, ip, kind, at, reservation)
    except DatabaseError:
        raise LimiterUnavailable("Admission unavailable") from None


def finalize_verification(reservation_id: UUID, valid: bool, at: datetime) -> None:
    candidate = SecurityRateEvent.objects.select_related(
        "phone_anchor", "ip_anchor"
    ).get(pk=reservation_id)
    if candidate.kind != "verify_failure":
        raise ValueError("Invalid verification reservation")
    with transaction.atomic():
        # These locks must precede identity/phone/challenge locks in callers.
        list(
            SecurityRateAnchor.objects.select_for_update()
            .filter(pk__in=[candidate.phone_anchor_id, candidate.ip_anchor_id])
            .order_by("kind", "key_id", "key_digest")
        )
        event = SecurityRateEvent.objects.select_for_update().get(pk=reservation_id)
        desired = "succeeded" if valid else "failed"
        if event.outcome == desired:
            return
        if event.outcome != "pending":
            raise LimiterUnavailable("Admission unavailable")
        if valid:
            keys = [
                _key("verify_failure", anchor.kind, anchor.key_id, anchor.key_digest)
                for anchor in [candidate.phone_anchor, candidate.ip_anchor]
            ]
            try:
                with redis_client() as client:
                    script = client.register_script(
                        Path(__file__)
                        .with_name("lua")
                        .joinpath("otp_admission.lua")
                        .read_text()
                    )
                    script(
                        keys=keys,
                        args=["release", 0, 0, 0, 0, 1, str(reservation_id), 1],
                    )
            except RedisError:
                raise LimiterUnavailable("Admission unavailable") from None
        event.outcome = desired
        event.save(update_fields=["outcome"])
