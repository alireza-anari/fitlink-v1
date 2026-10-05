import importlib
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta

import pytest
from django.apps import apps
from django.db import connections, transaction
from django.utils import timezone
from test_otp_consume import PHONE, sent
from test_otp_issue import record
from test_sessions import login, request_with_session, service

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def change(user, state):
    module = importlib.import_module("apps.accounts.state")
    return module.transition_account_state(
        user.public_id, user.auth_version, state, timezone.now(), record
    )


@pytest.mark.parametrize("state", ["restricted", "pending_deletion", "suspended"])
def test_state_change_revokes_current_session_and_requires_control(limiter, state):
    request, _ = login(limiter)
    actor = service().resolve_session(request, timezone.now())
    user = apps.get_model("accounts", "User").objects.get(public_id=actor.user_uuid)
    change(user, state)
    assert service().resolve_session(request, timezone.now()) is None
    if state != "suspended":
        import apps.accounts.sessions as sessions

        user.refresh_from_db()
        apps.get_model("accounts", "OTPPhoneState").objects.update(
            next_send_at=timezone.now() - timedelta(seconds=1)
        )
        request, _ = login(limiter, user)
        actor = sessions.resolve_session(request, timezone.now())
        assert actor.scope == "account_control"
        with pytest.raises(PermissionError), transaction.atomic():
            sessions.locked_actor(actor, "referral.create", timezone.now())


def test_mutation_rechecks_stale_actor_under_user_lock(limiter):
    request, _ = login(limiter)
    actor = service().resolve_session(request, timezone.now())
    user = apps.get_model("accounts", "User").objects.get(public_id=actor.user_uuid)
    change(user, "restricted")
    with transaction.atomic(), pytest.raises(PermissionError):
        service().locked_actor(actor, "consent.grant", timezone.now())


@pytest.mark.parametrize("first", ["login", "suspension"])
def test_login_suspension_serializations_have_no_surviving_auth(limiter, first):
    sessions = service()
    otp = importlib.import_module("apps.accounts.otp")
    user = apps.get_model("accounts", "User").objects.create_user(
        PHONE,
        birth_date=date(1990, 1, 1),
        adult_attested_at=timezone.now(),
        adult_attestation_version="adult-v1",
    )
    now = timezone.now()
    challenge, code = sent(now)
    request = request_with_session()
    entered, release = threading.Event(), threading.Event()

    def issued(locked):
        sessions.issue_session(request, locked, "normal", now, record)
        entered.set()
        assert release.wait(timeout=5)

    def consume():
        connections.close_all()
        try:
            return otp.verify_otp(
                PHONE,
                challenge,
                code,
                "login",
                otp.LOGIN_CONTEXT,
                "127.0.0.1",
                now,
                record,
                on_login=issued,
            )
        finally:
            connections.close_all()

    def suspend():
        connections.close_all()
        try:
            change(user, "suspended")
        finally:
            connections.close_all()

    if first == "suspension":
        suspend()
        release.set()
        assert not consume().valid
    else:
        with ThreadPoolExecutor(max_workers=2) as pool:
            login_future = pool.submit(consume)
            assert entered.wait(timeout=5)
            suspension_future = pool.submit(suspend)
            release.set()
            assert login_future.result(timeout=5).valid
            suspension_future.result(timeout=5)
    assert sessions.resolve_session(request, timezone.now()) is None
    user.refresh_from_db()
    assert user.state == "suspended" and not user.is_active
