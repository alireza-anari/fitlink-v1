import importlib
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from uuid import UUID, uuid4

import pytest
from django.apps import apps
from django.db import connections
from django.utils import timezone
from test_otp_issue import issue, modules, record

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]
PHONE = "+989123456789"


def verifier():
    otp = importlib.import_module("apps.accounts.otp")
    assert callable(getattr(otp, "verify_otp", None)), (
        "missing atomic proof consumption"
    )
    return otp


def sent(now, state="accepted"):
    otp, sms = modules()
    provider = sms.MockSmsProvider(state)
    result = issue(otp, provider, now)
    code = provider.drain()[0].code
    return result.challenge_id, code


def verify(challenge, code, at, recorder=record, **kwargs):
    return verifier().verify_otp(
        PHONE,
        challenge,
        code,
        "login",
        UUID(int=0),
        "127.0.0.1",
        at,
        recorder,
        birth_date=date(1990, 1, 1),
        adult_attested=True,
        **kwargs,
    )


@pytest.mark.parametrize("seconds,valid", [(299, True), (300, False)])
def test_expiry_exact_boundary_and_replay(limiter, seconds, valid):
    now = timezone.now()
    challenge, code = sent(now)
    result = verify(challenge, code, now + timedelta(seconds=seconds))
    assert result.valid is valid
    assert apps.get_model("accounts", "User").objects.count() == int(valid)
    assert not verify(challenge, code, now + timedelta(seconds=seconds)).valid


def test_wrong_attempts_commit_audit_lock_and_fifth_correct(limiter):
    now = timezone.now()
    challenge, code = sent(now)
    wrong = "000000" if code != "000000" else "111111"
    model = apps.get_model("accounts", "OTPChallenge")
    for attempt in range(1, 6):
        assert not verify(challenge, wrong, now).valid
        row = model.objects.get(pk=challenge)
        assert row.attempts == attempt
        assert (row.locked_at is not None) is (attempt == 5)
    assert not verify(challenge, code, now).valid
    assert (
        apps.get_model("governance", "AuditEvent")
        .objects.filter(action="otp.verification", result="failed")
        .count()
        == 6
    )
    assert not apps.get_model("accounts", "User").objects.exists()


def test_fifth_correct_consumes(limiter):
    now = timezone.now()
    challenge, code = sent(now)
    wrong = "000000" if code != "000000" else "111111"
    for _ in range(4):
        assert not verify(challenge, wrong, now).valid
    assert verify(challenge, code, now).valid


@pytest.mark.parametrize(
    "mutation", ["purpose", "context", "generation", "delivery", "unknown"]
)
def test_mismatched_and_unknown_proof_dummy_comparison(limiter, monkeypatch, mutation):
    now = timezone.now()
    challenge, code = sent(now)
    model = apps.get_model("accounts", "OTPChallenge")
    if mutation == "unknown":
        challenge = uuid4()
    elif mutation == "generation":
        apps.get_model("accounts", "OTPPhoneState").objects.update(generation=2)
    elif mutation == "delivery":
        model.objects.filter(pk=challenge).update(delivery_state="pending")
    otp = verifier()
    calls, compare = [], otp.hmac.compare_digest
    monkeypatch.setattr(
        otp.hmac, "compare_digest", lambda a, b: (calls.append(1), compare(a, b))[1]
    )
    result = otp.verify_otp(
        PHONE,
        challenge,
        code,
        "phone_change_new" if mutation == "purpose" else "login",
        uuid4() if mutation == "context" else UUID(int=0),
        "127.0.0.1",
        now,
        record,
        birth_date=date(1990, 1, 1),
        adult_attested=True,
    )
    assert not result.valid and len(calls) == 1
    assert not apps.get_model("accounts", "User").objects.exists()


def test_resend_retires_old_proof(limiter, monkeypatch):
    now = timezone.now()
    challenge, code = sent(now)
    monkeypatch.setattr(timezone, "now", lambda: now + timedelta(seconds=60))
    sent(now + timedelta(seconds=60))
    assert not verify(challenge, code, now + timedelta(seconds=60)).valid


def test_audit_rollback_leaves_no_identity_or_consumption(limiter):
    now = timezone.now()
    challenge, code = sent(now)

    def failed(outcome):
        raise RuntimeError("audit unavailable")

    with pytest.raises(RuntimeError):
        verify(challenge, code, now, recorder=failed)
    assert not apps.get_model("accounts", "User").objects.exists()
    assert (
        apps.get_model("accounts", "OTPChallenge").objects.get(pk=challenge).consumed_at
        is None
    )
    assert (
        apps.get_model("accounts", "SecurityRateEvent")
        .objects.filter(kind="verify_failure", outcome="pending")
        .count()
        == 1
    )


def test_simultaneous_first_registration_one_consume_one_user(limiter):
    now = timezone.now()
    challenge, code = sent(now)
    barrier = threading.Barrier(2)

    def run():
        connections.close_all()
        try:
            barrier.wait(timeout=5)
            return verify(challenge, code, now).valid
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: run(), range(2)))
    assert sorted(results) == [False, True]
    assert apps.get_model("accounts", "User").objects.count() == 1
    assert (
        apps.get_model("accounts", "OTPChallenge").objects.get(pk=challenge).consumed_at
        is not None
    )


def bound_proof(now):
    otp, sms = modules()
    user = apps.get_model("accounts", "User").objects.create_user(PHONE)
    binding = otp.OtpBinding(
        "phone_change_old", uuid4(), user.public_id, user.auth_version, PHONE
    )
    provider = sms.MockSmsProvider()
    result = otp.request_otp(
        PHONE,
        "127.0.0.1",
        binding.purpose,
        binding.context_uuid,
        now,
        record,
        provider=provider,
        binding=binding,
        validate_context=lambda value: None,
    )
    code = provider.drain()[0].code
    return user, binding, result.challenge_id, code


def test_nonlogin_consume_replay_version_and_application_rollback(limiter):
    now = timezone.now()
    user, binding, challenge, code = bound_proof(now)
    otp = verifier()
    result = otp.verify_otp(
        PHONE,
        challenge,
        code,
        binding.purpose,
        binding.context_uuid,
        "127.0.0.1",
        now,
        record,
        binding=binding,
        validate_context=lambda value: None,
    )
    assert result.valid
    assert not otp.verify_otp(
        PHONE,
        challenge,
        code,
        binding.purpose,
        binding.context_uuid,
        "127.0.0.1",
        now,
        record,
        binding=binding,
        validate_context=lambda value: None,
    ).valid

    def failed(locked):
        locked.locale = "en"
        locked.save(update_fields=["locale"])
        raise RuntimeError("effect rollback")

    with pytest.raises(RuntimeError):
        otp.apply_verified_proof(
            challenge,
            binding,
            now,
            record,
            effect=failed,
            validate_context=lambda value: None,
        )
    user.refresh_from_db()
    row = apps.get_model("accounts", "OTPChallenge").objects.get(pk=challenge)
    assert user.locale == "fa" and row.proof_applied_at is None
    user.auth_version += 1
    user.save(update_fields=["auth_version"])
    with pytest.raises(otp.OtpUnavailable):
        otp.apply_verified_proof(
            challenge,
            binding,
            now,
            record,
            effect=lambda locked: None,
            validate_context=lambda value: None,
        )
    assert not apps.get_model("accounts", "AccountSessionControl").objects.exists()


def test_concurrent_application_yields_one_effect(limiter):
    now = timezone.now()
    user, binding, challenge, code = bound_proof(now)
    otp = verifier()
    assert otp.verify_otp(
        PHONE,
        challenge,
        code,
        binding.purpose,
        binding.context_uuid,
        "127.0.0.1",
        now,
        record,
        binding=binding,
        validate_context=lambda value: None,
    ).valid
    barrier = threading.Barrier(2)

    def effect(locked):
        locked.locale = "en"
        locked.save(update_fields=["locale"])

    def run():
        connections.close_all()
        try:
            barrier.wait(timeout=5)
            try:
                otp.apply_verified_proof(
                    challenge,
                    binding,
                    now,
                    record,
                    effect=effect,
                    validate_context=lambda value: None,
                )
                return True
            except otp.OtpUnavailable:
                return False
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: run(), range(2)))
    assert sorted(results) == [False, True]
    assert (
        apps.get_model("accounts", "OTPChallenge")
        .objects.get(pk=challenge)
        .proof_applied_at
        is not None
    )
    user.refresh_from_db()
    assert (
        user.locale == "en"
        and not apps.get_model("accounts", "AccountSessionControl").objects.exists()
    )


def test_stale_bound_version_verification_fails(limiter):
    now = timezone.now()
    user, binding, challenge, code = bound_proof(now)
    user.auth_version += 1
    user.save(update_fields=["auth_version"])
    result = verifier().verify_otp(
        PHONE,
        challenge,
        code,
        binding.purpose,
        binding.context_uuid,
        "127.0.0.1",
        now,
        record,
        binding=binding,
        validate_context=lambda value: None,
    )
    assert not result.valid
    assert (
        apps.get_model("accounts", "OTPChallenge").objects.get(pk=challenge).consumed_at
        is None
    )


def test_malformed_code_rejects_before_quota(limiter):
    otp = verifier()
    with pytest.raises(ValueError):
        otp.verify_otp(
            PHONE,
            uuid4(),
            "12345\u202e",
            "login",
            UUID(int=0),
            "127.0.0.1",
            timezone.now(),
            record,
        )
    assert not apps.get_model("accounts", "SecurityRateEvent").objects.exists()
