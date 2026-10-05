import importlib
import importlib.util
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import UUID

import pytest
from django.apps import apps
from django.db import connections, transaction
from django.utils import timezone

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def modules():
    assert importlib.util.find_spec("apps.accounts.otp"), (
        "missing durable digest-only issuance"
    )
    return importlib.import_module("apps.accounts.otp"), importlib.import_module(
        "apps.accounts.sms"
    )


def record(outcome):
    from apps.governance.audit import append_event

    append_event(outcome)


def issue(otp, provider, at, phone="+989123456789", recorder=record):
    return otp.request_otp(
        phone, "127.0.0.1", "login", UUID(int=0), at, recorder, provider=provider
    )


def test_cooldown_exact_boundary_resend_and_no_user(limiter, monkeypatch):
    otp, sms = modules()
    now = timezone.now()
    monkeypatch.setattr(timezone, "now", lambda: now)
    provider = sms.MockSmsProvider()
    first = issue(otp, provider, now)
    assert first.status == "accepted"
    challenge = apps.get_model("accounts", "OTPChallenge")
    old = challenge.objects.get(pk=first.challenge_id)
    assert old.delivery_state == "sent" and old.generation == 1
    assert not apps.get_model("accounts", "User").objects.exists()
    with pytest.raises(otp.OtpThrottled):
        issue(otp, provider, now + timedelta(seconds=59))
    now += timedelta(seconds=60)
    second = issue(otp, provider, now)
    old.refresh_from_db()
    assert old.retired_at is not None
    assert challenge.objects.get(pk=second.challenge_id).generation == 2
    assert len(provider.drain()) == 2


@pytest.mark.parametrize("state", ["failed", "unknown"])
def test_failed_or_unknown_delivery_never_sent(limiter, state):
    otp, sms = modules()
    result = issue(otp, sms.MockSmsProvider(state), timezone.now())
    challenge = apps.get_model("accounts", "OTPChallenge").objects.get(
        pk=result.challenge_id
    )
    assert result.status == "accepted" and challenge.delivery_state == "failed"
    assert challenge.consumed_at is None
    assert not apps.get_model("accounts", "AccountSessionControl").objects.exists()


def test_crash_pending_cannot_be_verifiable(limiter):
    otp, sms = modules()

    class Crash:
        def send_otp(self, *args):
            raise SystemExit("simulated process death")

    with pytest.raises(SystemExit):
        issue(otp, Crash(), timezone.now())
    challenge = apps.get_model("accounts", "OTPChallenge").objects.get()
    assert challenge.delivery_state == "pending" and challenge.consumed_at is None
    assert not apps.get_model("accounts", "User").objects.exists()


def test_late_ack_does_not_resurrect_prior_generation(limiter, monkeypatch):
    otp, sms = modules()
    now = timezone.now()
    clock = [now]
    monkeypatch.setattr(timezone, "now", lambda: clock[0])
    entered, release = threading.Event(), threading.Event()

    class Delayed:
        def send_otp(self, *args):
            entered.set()
            assert release.wait(timeout=5)
            return sms.DeliveryResult("accepted")

    def first_request():
        connections.close_all()
        try:
            return issue(otp, Delayed(), now)
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=1) as pool:
        pending = pool.submit(first_request)
        assert entered.wait(timeout=5)
        clock[0] = now + timedelta(seconds=60)
        second = issue(otp, sms.MockSmsProvider(), clock[0])
        release.set()
        first = pending.result(timeout=5)
    model = apps.get_model("accounts", "OTPChallenge")
    assert model.objects.get(pk=first.challenge_id).delivery_state != "sent"
    assert model.objects.get(pk=second.challenge_id).delivery_state == "sent"
    assert not apps.get_model("accounts", "User").objects.exists()


def test_audit_failure_rolls_back_before_provider_io(limiter):
    otp, sms = modules()
    provider = sms.MockSmsProvider()

    def failed(outcome):
        raise RuntimeError("audit unavailable")

    with pytest.raises(RuntimeError):
        issue(otp, provider, timezone.now(), recorder=failed)
    assert not provider.drain()
    assert not apps.get_model("accounts", "OTPChallenge").objects.exists()
    assert apps.get_model("accounts", "SecurityRateEvent").objects.count() == 1


def test_provider_private_values_never_persist_or_log(limiter, monkeypatch, caplog):
    otp, sms = modules()
    monkeypatch.setattr(otp, "generate_code", lambda: "001234")

    class Broken:
        def send_otp(self, *args):
            raise RuntimeError("private-sms-001234-+989123456789")

    result = issue(otp, Broken(), timezone.now())
    challenge = apps.get_model("accounts", "OTPChallenge").objects.get(
        pk=result.challenge_id
    )
    assert "001234" not in challenge.code_digest + caplog.text
    for name in ["AuditEvent", "OutboxEvent"]:
        rows = list(apps.get_model("governance", name).objects.values())
        assert "001234" not in repr(rows)
        assert "+989123456789" not in repr(rows)


def test_existing_and_restricted_phone_get_same_public_attempt_result(limiter):
    otp, sms = modules()
    users = apps.get_model("accounts", "User")
    users.objects.create_user("+989123456788", state="restricted")
    users.objects.create_user("+989123456787", is_active=False)
    provider, now = sms.MockSmsProvider("failed"), timezone.now()
    results = [
        issue(otp, provider, now, phone=phone)
        for phone in ["+989123456789", "+989123456788", "+989123456787"]
    ]
    assert all(
        result.status == "accepted" and result.resend_after_seconds == 60
        for result in results
    )
    assert len(provider.drain()) == 3 and users.objects.count() == 2


def test_ambient_transaction_rejected_before_admission_and_provider_io(limiter):
    otp, sms = modules()
    provider = sms.MockSmsProvider()
    with transaction.atomic(), pytest.raises(otp.OtpUnavailable):
        issue(otp, provider, timezone.now())
    assert not provider.drain()
    for app, name in [
        ("accounts", "OTPChallenge"),
        ("accounts", "SecurityRateEvent"),
        ("accounts", "OTPPhoneState"),
        ("governance", "AuditEvent"),
    ]:
        assert not apps.get_model(app, name).objects.exists()
