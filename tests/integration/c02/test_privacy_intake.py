import importlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import timedelta
from threading import Barrier
from uuid import uuid4

import pytest
from django.apps import apps
from django.db import close_old_connections, transaction
from django.utils import timezone
from test_phone_change import actor_for
from test_recovery_authorization import owner

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def commands():
    assert importlib.util.find_spec("config.use_cases.privacy"), (
        "missing owned privacy composition"
    )
    return importlib.import_module("config.use_cases.privacy")


def test_export_replay_returns_owned_pending_intake_and_no_execution():
    module = commands()
    user = owner()
    actor, _ = actor_for(user)
    request_id = uuid4()
    at = timezone.now()
    result = module.request_privacy(actor, "export", request_id, at, confirmed=True)
    assert (
        module.request_privacy(actor, "export", request_id, at, confirmed=True)
        == result
    )
    assert (
        module.request_privacy(actor, "export", uuid4(), at, confirmed=True) == result
    )
    assert module.privacy_status(actor, result, at) == {
        "request_id": result,
        "kind": "export",
        "status": "pending_execution",
    }
    row = apps.get_model("governance", "PrivacyRequest").objects.get()
    assert row.user_id == user.pk and row.verified_at == at
    user.refresh_from_db()
    assert user.state == "active" and user.auth_version == 1
    assert (
        apps.get_model("governance", "OutboxEvent")
        .objects.filter(event_type="privacy.intake_recorded")
        .count()
        == 1
    )
    assert "ErasureMarker" not in {model.__name__ for model in apps.get_models()}
    # C03's private asset metadata exists, but privacy intake never creates assets.
    assert not apps.get_model("assets", "Asset").objects.exists()


@pytest.mark.parametrize(
    "defect", ["confirmation", "stale", "future", "revoked", "foreign", "kind"]
)
def test_intake_denies_unverified_stale_and_foreign_requests(defect):
    module = commands()
    user = owner()
    actor, _ = actor_for(user)
    at = timezone.now()
    request_id = uuid4()
    if defect == "foreign":
        module.request_privacy(actor, "export", request_id, at, confirmed=True)
        actor, _ = actor_for(owner("+989123456782"))
    elif defect == "stale":
        # Both the descriptor and authoritative control have an old proof.
        from apps.accounts.security_models import AccountSessionControl

        old = at - timedelta(seconds=601)
        AccountSessionControl.objects.filter(pk=actor.control_id).update(
            authenticated_at=old
        )
        actor = replace(actor, authenticated_at=old)
    elif defect == "future":
        actor = replace(actor, authenticated_at=at + timedelta(seconds=1))
    elif defect == "revoked":
        from apps.accounts.security_models import AccountSessionControl

        AccountSessionControl.objects.filter(pk=actor.control_id).update(revoked_at=at)
    with pytest.raises((PermissionError, ValueError)):
        module.request_privacy(
            actor,
            "bad" if defect == "kind" else "delete",
            request_id,
            at,
            confirmed=defect != "confirmation",
        )
    user.refresh_from_db()
    assert user.state == "active" and user.auth_version == 1


def test_delete_synchronously_revokes_sessions_challenges_and_owned_consents(limiter):
    from test_otp_issue import record
    from test_sessions import request_with_session

    from apps.accounts.sessions import issue_session, resolve_session
    from apps.governance.consents import validate_scope
    from config.use_cases.consent import grant_consent

    module = commands()
    user = owner()
    grantee = owner("+989123456782")
    actor, request = actor_for(user)
    now = timezone.now()
    scope = validate_scope(
        actor,
        grantee.public_id,
        "account_metadata",
        "account_metadata",
        user.public_id,
        1,
        now + timedelta(hours=1),
        now,
    )
    consent = grant_consent(actor, scope, "v1", "a" * 64, now)
    from test_otp_issue import issue

    from apps.accounts import otp
    from apps.accounts.sms import MockSmsProvider

    issued = issue(otp, MockSmsProvider(), now, phone=user.phone)
    assert (
        apps.get_model("accounts", "OTPChallenge")
        .objects.get(pk=issued.challenge_id)
        .retired_at
        is None
    )
    result = module.request_privacy(actor, "delete", uuid4(), now, confirmed=True)
    assert (
        apps.get_model("accounts", "OTPChallenge")
        .objects.get(pk=issued.challenge_id)
        .retired_at
        == now
    )
    user.refresh_from_db()
    assert (
        user.state == "pending_deletion"
        and user.auth_version == 2
        and user.state_version == 2
    )
    assert resolve_session(request, now) is None
    assert (
        apps.get_model("governance", "Consent").objects.get(pk=consent).revoked_at
        == now
    )
    assert (
        not apps.get_model("accounts", "AccountSessionControl")
        .objects.filter(user=user, revoked_at__isnull=True)
        .exists()
    )
    assert (
        not apps.get_model("accounts", "OTPChallenge")
        .objects.filter(target_user=user, retired_at__isnull=True)
        .exists()
    )
    control = request_with_session()
    with transaction.atomic():
        issue_session(control, user, "account_control", now, record)
    fresh = resolve_session(control, now)
    assert module.privacy_status(fresh, result, now)["status"] == "pending_deletion"
    assert (
        module.request_privacy(fresh, "delete", result, now, confirmed=True) == result
    )
    with pytest.raises(PermissionError):
        module.privacy_status(actor, result, now)


def test_status_list_and_count_are_owned():
    module = commands()
    actor, _ = actor_for(owner())
    other, _ = actor_for(owner("+989123456782"))
    at = timezone.now()
    result = module.request_privacy(actor, "export", uuid4(), at, confirmed=True)
    with pytest.raises(PermissionError):
        module.privacy_status(other, result, at)
    with pytest.raises(PermissionError):
        module.privacy_status(actor, uuid4(), at)
    assert module.visible_requests(other, at).count() == 0
    assert module.visible_requests(actor, at).count() == 1


@pytest.mark.parametrize("failure", ["audit", "outbox"])
def test_failed_recorder_rolls_back_delete_intake_and_identity(monkeypatch, failure):
    module = commands()
    user = owner()
    actor, _ = actor_for(user)

    def fail(*args, **kwargs):
        raise RuntimeError("metadata unavailable")

    monkeypatch.setattr(
        module, "append_event" if failure == "audit" else "append_outbox", fail
    )
    with pytest.raises(RuntimeError):
        module.request_privacy(actor, "delete", uuid4(), timezone.now(), confirmed=True)
    user.refresh_from_db()
    assert user.state == "active" and user.auth_version == 1
    assert not apps.get_model("governance", "PrivacyRequest").objects.exists()
    assert (
        apps.get_model("accounts", "AccountSessionControl")
        .objects.get(pk=actor.control_id)
        .revoked_at
        is None
    )


def test_concurrent_export_intakes_preserve_one_open_request():
    module = commands()
    actor, _ = actor_for(owner())
    barrier = Barrier(2)

    def intake(_):
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            return module.request_privacy(
                actor, "export", uuid4(), timezone.now(), confirmed=True
            )
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as pool:
        result = list(pool.map(intake, range(2)))
    assert result[0] == result[1]
    assert apps.get_model("governance", "PrivacyRequest").objects.count() == 1


def test_global_logout_racing_deletion_never_restores_normal_access():
    from test_otp_issue import record

    from apps.accounts.sessions import resolve_session, revoke_sessions

    module = commands()
    user = owner()
    actor, request = actor_for(user)
    barrier = Barrier(2)

    def run(kind):
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            try:
                if kind == "delete":
                    module.request_privacy(
                        actor, "delete", uuid4(), timezone.now(), confirmed=True
                    )
                else:
                    revoke_sessions(user, "all", timezone.now(), record)
                return True
            except PermissionError:
                return False
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as pool:
        result = list(pool.map(run, ["delete", "logout"]))
    assert any(result)
    user.refresh_from_db()
    assert user.auth_version >= 2 and resolve_session(request, timezone.now()) is None
    assert user.state in {"active", "pending_deletion"}


def test_concurrent_delete_intakes_revoke_once():
    module = commands()
    actor, _ = actor_for(owner())
    barrier = Barrier(2)

    def intake(_):
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            try:
                return module.request_privacy(
                    actor, "delete", uuid4(), timezone.now(), confirmed=True
                )
            except PermissionError:
                return None
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as pool:
        result = list(pool.map(intake, range(2)))
    assert sum(value is not None for value in result) == 1
    assert apps.get_model("governance", "PrivacyRequest").objects.count() == 1
    assert (
        apps.get_model("accounts", "User")
        .objects.get(public_id=actor.user_uuid)
        .auth_version
        == 2
    )


def test_grant_racing_deletion_leaves_no_current_owned_grant():
    from apps.governance.consents import validate_scope
    from config.use_cases.consent import grant_consent

    module = commands()
    user = owner()
    actor, _ = actor_for(user)
    grantee = owner("+989123456782")
    now = timezone.now()
    scope = validate_scope(
        actor,
        grantee.public_id,
        "account_metadata",
        "account_metadata",
        user.public_id,
        1,
        now + timedelta(hours=1),
        now,
    )
    barrier = Barrier(2)

    def run(kind):
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            try:
                if kind == "delete":
                    module.request_privacy(
                        actor, "delete", uuid4(), timezone.now(), confirmed=True
                    )
                else:
                    grant_consent(actor, scope, "v1", "a" * 64, now)
                return True
            except PermissionError:
                return False
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as pool:
        result = list(pool.map(run, ["delete", "grant"]))
    assert result[0]
    user.refresh_from_db()
    assert user.state == "pending_deletion"
    assert (
        not apps.get_model("governance", "Consent")
        .objects.filter(subject=user, revoked_at__isnull=True)
        .exists()
    )


def test_recovery_racing_delete_preserves_restriction_or_rejects_stale_delete(
    limiter, settings
):
    from test_recovery_apply import approved, prove

    from apps.accounts.sessions import resolve_session

    module = commands()
    user = owner()
    actor, request = actor_for(user)
    values = approved(settings)
    _, recovery, receipt, staff_actor, _, _, step, case = values
    prove(recovery, receipt)
    case.refresh_from_db()
    barrier = Barrier(2)

    def run(kind):
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            try:
                if kind == "delete":
                    module.request_privacy(
                        actor, "delete", uuid4(), timezone.now(), confirmed=True
                    )
                else:
                    recovery.apply_recovery(
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
        result = list(pool.map(run, ["delete", "recovery"]))
    assert any(result)
    user.refresh_from_db()
    if result[0]:
        assert user.state == "pending_deletion"
    assert user.auth_version >= 2 and resolve_session(request, timezone.now()) is None
