import subprocess
import sys

import pytest
from django.apps import apps
from django.db import transaction
from django.utils import timezone

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_redis_loss_never_falls_back_to_database(limiter, settings):
    settings.OTP_RATE_REDIS_URL = "redis://127.0.0.1:1/4"
    with pytest.raises(limiter.LimiterUnavailable):
        limiter.reserve_admission("+989123456789", "127.0.0.1", "send", timezone.now())
    assert not apps.get_model("accounts", "SecurityRateEvent").objects.exists()


def test_noscript_and_key_reset_preserve_durable_quota(limiter):
    now = timezone.now()
    client = limiter.redis_client()
    for _ in range(5):
        client.script_flush()
        assert limiter.reserve_admission(
            "+989123456789", "127.0.0.1", "send", now
        ).allowed
    for reset in [lambda: client.delete(*client.keys("fitlink:otp:*")), client.flushdb]:
        reset()
        assert not limiter.reserve_admission(
            "+989123456789", "127.0.0.2", "send", now
        ).allowed


def test_successful_cleanup_failure_keeps_pending_slot_and_no_identity(
    limiter, settings
):
    now = timezone.now()
    slot = limiter.reserve_admission(
        "+989123456789", "127.0.0.1", "verify_failure", now
    )
    settings.OTP_RATE_REDIS_URL = "redis://127.0.0.1:1/4"
    with pytest.raises(limiter.LimiterUnavailable), transaction.atomic():
        limiter.finalize_verification(slot.reservation_id, True, now)
    event = apps.get_model("accounts", "SecurityRateEvent").objects.get(
        pk=slot.reservation_id
    )
    assert event.outcome == "pending"
    assert not apps.get_model("accounts", "User").objects.exists()
    assert not apps.get_model("accounts", "AccountSessionControl").objects.exists()


def test_aborted_database_admission_leaves_redis_spent(limiter, monkeypatch):
    now = timezone.now()
    original = limiter.durable_admission

    def interrupted(*args, **kwargs):
        raise limiter.LimiterUnavailable("Admission unavailable")

    monkeypatch.setattr(limiter, "durable_admission", interrupted)
    for _ in range(5):
        with pytest.raises(limiter.LimiterUnavailable):
            limiter.reserve_admission("+989123456789", "127.0.0.1", "send", now)
    monkeypatch.setattr(limiter, "durable_admission", original)
    assert not limiter.reserve_admission(
        "+989123456789", "127.0.0.1", "send", now
    ).allowed
    assert not apps.get_model("accounts", "SecurityRateEvent").objects.exists()


def test_real_process_exit_after_redis_admission_keeps_quota_spent(limiter):
    script = """
import os, django
django.setup()
from django.utils import timezone
from apps.accounts import limiter
def terminate(*args, **kwargs):
    os._exit(71)
limiter.durable_admission = terminate
limiter.reserve_admission('+989123456789', '127.0.0.1', 'send', timezone.now())
"""
    for _ in range(5):
        result = subprocess.run(
            [sys.executable, "-c", script], capture_output=True, timeout=10, check=False
        )
        assert result.returncode == 71
    assert not limiter.reserve_admission(
        "+989123456789", "127.0.0.1", "send", timezone.now()
    ).allowed
    assert not apps.get_model("accounts", "SecurityRateEvent").objects.exists()
