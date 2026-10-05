import importlib
import importlib.util
import threading
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from django.apps import apps
from django.db import close_old_connections, transaction
from django.utils import timezone
from test_otp_issue import record
from test_recovery_apply import approved, prove
from test_recovery_authorization import NEW, OLD, owner
from test_sessions import request_with_session

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def contract():
    assert importlib.util.find_spec("apps.accounts.phone_change"), (
        "missing owned dual-proof command"
    )
    return importlib.import_module(
        "apps.accounts.phone_change"
    ), importlib.import_module("config.use_cases.identity")


def actor_for(user):
    from apps.accounts.sessions import issue_session, resolve_session

    request = request_with_session()
    with transaction.atomic():
        issue_session(request, user, "normal", timezone.now(), record)
    return resolve_session(request, timezone.now()), request


def started(new=NEW, user=None):
    module, commands = contract()
    user = user or owner()
    actor, request = actor_for(user)
    intent_id = commands.begin_phone_change(actor, new, timezone.now())
    intent = apps.get_model("accounts", "PhoneChangeIntent").objects.get(pk=intent_id)
    return module, commands, user, actor, request, intent


def phone_proof(commands, actor, intent, kind):
    from apps.accounts.sms import MockSmsProvider

    provider = MockSmsProvider()
    challenge = commands.request_phone_change_otp(
        actor, intent.id, kind, "127.0.0.1", timezone.now(), provider=provider
    )
    result = commands.verify_phone_change_otp(
        actor,
        intent.id,
        kind,
        challenge.challenge_id,
        provider.drain()[0].code,
        "127.0.0.1",
        timezone.now(),
    )
    assert result.valid
    return challenge.challenge_id


def fully_proved(values):
    module, commands, user, actor, request, intent = values
    phone_proof(commands, actor, intent, "old")
    phone_proof(commands, actor, intent, "new")
    intent.refresh_from_db()
    return values


def test_dual_proof_changes_existing_user_and_requires_new_login(limiter):
    from apps.accounts.sessions import resolve_session

    module, commands, user, actor, request, intent = fully_proved(started())
    original = user.public_id, user.password, user.birth_date
    result = commands.apply_phone_change(actor, intent.id, timezone.now())
    user.refresh_from_db()
    assert (user.public_id, user.password, user.birth_date) == original
    assert user.phone == NEW and user.auth_version == 2
    assert resolve_session(request, timezone.now()) is None
    assert (
        apps.get_model("accounts", "PhoneChangeHistory").objects.get().change_context
        == intent.id
    )
    assert (
        apps.get_model("accounts", "OTPChallenge")
        .objects.filter(context_uuid=intent.id, proof_applied_at__isnull=False)
        .count()
        == 2
    )
    with pytest.raises(PermissionError):
        commands.apply_phone_change(actor, intent.id, timezone.now())
    new_actor, _ = actor_for(user)
    assert commands.apply_phone_change(new_actor, intent.id, timezone.now()) == result
    assert apps.get_model("accounts", "PhoneChangeHistory").objects.count() == 1


@pytest.mark.parametrize(
    "defect",
    [
        "only_old",
        "only_new",
        "same_proof",
        "wrong_purpose",
        "wrong_context",
        "foreign",
        "stale",
        "expired",
        "destination_owned",
    ],
)
def test_every_dual_proof_and_owner_binding_is_rechecked(limiter, defect):
    module, commands, user, actor, request, intent = started()
    if defect != "only_new":
        phone_proof(commands, actor, intent, "old")
    if defect != "only_old":
        phone_proof(commands, actor, intent, "new")
    intent.refresh_from_db()
    at = timezone.now()
    proof_model = apps.get_model("accounts", "OTPChallenge")
    if defect == "same_proof":
        type(intent).objects.filter(pk=intent.pk).update(
            new_phone_challenge_id=intent.old_phone_challenge_id
        )
    elif defect == "wrong_purpose":
        proof_model.objects.filter(pk=intent.new_phone_challenge_id).update(
            purpose="recovery_new_phone"
        )
    elif defect == "wrong_context":
        proof_model.objects.filter(pk=intent.new_phone_challenge_id).update(
            context_uuid=uuid4()
        )
    elif defect == "foreign":
        actor, request = actor_for(owner("+989123456786"))
    elif defect == "stale":
        from apps.accounts.sessions import revoke_sessions

        revoke_sessions(user, "all", timezone.now(), record)
    elif defect == "expired":
        at = proof_model.objects.get(pk=intent.old_phone_challenge_id).expires_at
    elif defect == "destination_owned":
        owner(NEW)
    with pytest.raises(PermissionError):
        commands.apply_phone_change(actor, intent.id, at)
    user.refresh_from_db()
    assert (
        user.phone == OLD
        and not apps.get_model("accounts", "PhoneChangeHistory").objects.exists()
    )


def test_old_new_or_recovery_code_cannot_verify_other_purpose(limiter):
    from apps.accounts.sms import MockSmsProvider

    module, commands, user, actor, request, intent = started()
    provider = MockSmsProvider()
    issued = commands.request_phone_change_otp(
        actor, intent.id, "old", "127.0.0.1", timezone.now(), provider=provider
    )
    result = commands.verify_phone_change_otp(
        actor,
        intent.id,
        "new",
        issued.challenge_id,
        provider.drain()[0].code,
        "127.0.0.1",
        timezone.now(),
    )
    assert not result.valid
    assert (
        not apps.get_model("accounts", "OTPChallenge")
        .objects.get(pk=issued.challenge_id)
        .consumed_at
    )


def test_begin_is_owned_and_retires_previous_intent(limiter):
    module, commands, user, actor, request, first = started()
    old_proof = phone_proof(commands, actor, first, "old")
    second = commands.begin_phone_change(actor, "+989123456781", timezone.now())
    first.refresh_from_db()
    assert first.retired_at is not None and second != first.id
    with pytest.raises(PermissionError):
        commands.apply_phone_change(actor, first.id, timezone.now())
    assert (
        apps.get_model("accounts", "OTPChallenge").objects.get(pk=old_proof).retired_at
        is not None
    )


@pytest.mark.parametrize("failure", ["audit", "outbox", "history"])
def test_identity_proofs_history_and_events_rollback_together(
    limiter, monkeypatch, failure
):
    module, commands, user, actor, request, intent = fully_proved(started())

    def failed(*args, **kwargs):
        raise RuntimeError("persistence unavailable")

    if failure == "audit":
        monkeypatch.setattr(commands, "record_security_outcome", failed)
    elif failure == "outbox":
        monkeypatch.setattr(commands, "append_outbox", failed)
    else:
        monkeypatch.setattr(
            apps.get_model("accounts", "PhoneChangeHistory"), "save", failed
        )
    with pytest.raises(RuntimeError):
        commands.apply_phone_change(actor, intent.id, timezone.now())
    user.refresh_from_db()
    assert user.phone == OLD and user.auth_version == 1
    assert not apps.get_model("accounts", "PhoneChangeHistory").objects.exists()
    assert (
        not apps.get_model("accounts", "OTPChallenge")
        .objects.filter(context_uuid=intent.id, proof_applied_at__isnull=False)
        .exists()
    )


def test_two_owned_changes_race_for_one_phone(limiter):
    first = fully_proved(started())
    second = started(user=owner("+989123456786"))
    apps.get_model("accounts", "OTPPhoneState").objects.filter(phone=NEW).update(
        next_send_at=timezone.now()
    )
    fully_proved(second)
    barrier = threading.Barrier(2)

    def apply(values):
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            try:
                values[1].apply_phone_change(values[3], values[5].id, timezone.now())
                return True
            except PermissionError:
                return False
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(apply, [first, second]))
    assert outcomes.count(True) == 1
    assert apps.get_model("accounts", "User").objects.filter(phone=NEW).count() == 1
    assert apps.get_model("accounts", "PhoneChangeHistory").objects.count() == 1


def test_recovery_and_owned_change_serialize_without_two_effects(limiter, settings):
    values = fully_proved(started())
    module, commands, user, actor, request, intent = values
    recovery_values = approved(settings, OLD, "+989123456781")
    recovery, recovery_commands, receipt, staff_actor, staff, grant, step, case = (
        recovery_values
    )
    prove(recovery_commands, receipt)
    case.refresh_from_db()
    barrier = threading.Barrier(2)

    def run(kind):
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            try:
                if kind == "owned":
                    commands.apply_phone_change(actor, intent.id, timezone.now())
                else:
                    recovery_commands.apply_recovery(
                        staff_actor,
                        case.id,
                        case.version,
                        step,
                        "identity_verified",
                        timezone.now(),
                    )
                return True
            except PermissionError:
                return False
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(run, ["owned", "recovery"]))
    assert outcomes.count(True) == 1
    user.refresh_from_db()
    assert user.phone in {NEW, "+989123456781"} and user.auth_version == 2
    assert apps.get_model("accounts", "PhoneChangeHistory").objects.count() == 1
