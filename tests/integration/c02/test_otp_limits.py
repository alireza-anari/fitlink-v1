import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import timedelta
from uuid import uuid4

import pytest
from django.apps import apps
from django.db import connections
from django.utils import timezone

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize(
    "kind,phone_limit,ip_limit",
    [("send", 5, 20), ("verify_failure", 10, 60), ("recovery_intake", 3, 10)],
)
def test_exact_phone_and_ip_rolling_limits(limiter, kind, phone_limit, ip_limit):
    now = timezone.now()
    for _ in range(phone_limit):
        assert limiter.reserve_admission(
            "۰۹۱۲۳۴۵۶۷۸۹", "::ffff:127.0.0.1", kind, now
        ).allowed
    assert not limiter.reserve_admission(
        "+989123456789", "127.0.0.1", kind, now
    ).allowed
    for index in range(ip_limit):
        phone = f"+989{index:09d}"
        assert limiter.reserve_admission(phone, "127.0.0.2", kind, now).allowed
    assert not limiter.reserve_admission(
        "+989999999999", "127.0.0.2", kind, now
    ).allowed
    if kind == "recovery_intake":
        for seconds in [3600, 86399]:
            assert not limiter.reserve_admission(
                "+989123456789", "127.0.0.1", kind, now + timedelta(seconds=seconds)
            ).allowed
    boundary = now + timedelta(seconds=86400 if kind == "recovery_intake" else 3600)
    assert limiter.reserve_admission(
        "+989123456789", "127.0.0.1", kind, boundary
    ).allowed


def test_only_proven_success_releases_failure_slot(limiter):
    now = timezone.now()
    for _ in range(10):
        slot = limiter.reserve_admission(
            "+989123456789", "127.0.0.1", "verify_failure", now
        )
        assert slot.allowed
        limiter.finalize_verification(slot.reservation_id, True, now)
    slots = [
        limiter.reserve_admission("+989123456789", "127.0.0.1", "verify_failure", now)
        for _ in range(10)
    ]
    assert all(slot.allowed for slot in slots)
    for slot in slots:
        limiter.finalize_verification(slot.reservation_id, False, now)
    assert not limiter.reserve_admission(
        "+989123456789", "127.0.0.1", "verify_failure", now
    ).allowed


@pytest.mark.parametrize("dimension,count,limit", [("phone", 24, 5), ("ip", 24, 20)])
def test_real_parallel_first_admission_never_overshoots(
    limiter, dimension, count, limit
):
    now, barrier = timezone.now(), threading.Barrier(count)

    def attempt(index):
        connections.close_all()
        try:
            barrier.wait(timeout=20)
            phone = "+989123456789" if dimension == "phone" else f"+989{index:09d}"
            ip = "127.0.0.1" if dimension == "ip" else f"127.0.0.{index + 1}"
            return limiter.reserve_admission(phone, ip, "send", now).allowed
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=count) as pool:
        results = list(pool.map(attempt, range(count)))
    assert sum(results) == limit
    anchor = apps.get_model("accounts", "SecurityRateAnchor")
    assert anchor.objects.count() == limit + 1
    event = apps.get_model("accounts", "SecurityRateEvent")
    assert event.objects.filter(kind="send").count() == limit


def test_actual_postgresql_guard_race_survives_absent_redis_keys(limiter):
    now, count = timezone.now(), 24
    barrier = threading.Barrier(count)

    def attempt(index):
        connections.close_all()
        try:
            barrier.wait(timeout=20)
            return limiter.durable_admission(
                "+989123456789", f"127.0.0.{index + 1}", "send", now, uuid4()
            ).allowed
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=count) as pool:
        results = list(pool.map(attempt, range(count)))
    assert sum(results) == 5
    assert apps.get_model("accounts", "SecurityRateEvent").objects.count() == 5


def test_retained_key_rotation_does_not_reset_quota(limiter, settings):
    from apps.accounts.security_keys import parse_key_ring

    now = timezone.now()
    original = settings.ACCOUNT_SECURITY
    for _ in range(5):
        assert limiter.reserve_admission(
            "+989123456789", "127.0.0.1", "send", now
        ).allowed
    ring = parse_key_ring(
        '{"development":"AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8=",'
        ' "next":"ERERERERERERERERERERERERERERERERERERERERERE="}',
        "next",
    )
    settings.ACCOUNT_SECURITY = replace(original, keys=ring)
    limiter.redis_client().flushdb()
    assert not limiter.reserve_admission(
        "+989123456789", "127.0.0.2", "send", now
    ).allowed


def test_unreviewed_key_removal_cannot_silently_reset_durable_quota(limiter, settings):
    from apps.accounts.security_keys import parse_key_ring

    now = timezone.now()
    for _ in range(5):
        assert limiter.reserve_admission(
            "+989123456789", "127.0.0.1", "send", now
        ).allowed
    settings.ACCOUNT_SECURITY = replace(
        settings.ACCOUNT_SECURITY,
        keys=parse_key_ring(
            '{"next":"ERERERERERERERERERERERERERERERERERERERERERE="}', "next"
        ),
    )
    limiter.redis_client().flushdb()
    with pytest.raises(limiter.LimiterUnavailable):
        limiter.reserve_admission("+989123456789", "127.0.0.2", "send", now)
