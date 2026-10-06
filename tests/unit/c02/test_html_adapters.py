from uuid import uuid4

import pytest
from django.test import Client
from django.utils import timezone

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("old,new", [(False, False), (True, False), (True, True)])
def test_phone_change_display_reads_actual_proof_fields(monkeypatch, old, new):
    from apps.accounts import sessions
    from apps.accounts.models import User
    from apps.accounts.recovery_models import PhoneChangeIntent
    from config.use_cases.identity import phone_change_display

    owner = User(phone="+989123456789")
    change = PhoneChangeIntent(
        user=owner,
        old_phone_verified_at=timezone.now() if old else None,
        new_phone_verified_at=timezone.now() if new else None,
    )

    # The DB boundary returns a real model, retaining its actual field contract.
    class Result:
        def first(self):
            return change

    def owned_filter(**kwargs):
        assert kwargs == {"pk": change.id, "user": owner}
        return Result()

    monkeypatch.setattr(sessions, "actor_user", lambda *args: owner)
    monkeypatch.setattr(PhoneChangeIntent.objects, "filter", owned_filter)
    assert phone_change_display(object(), change.id, timezone.now()) == {
        "change_uuid": change.id,
        "old_verified": old,
        "new_verified": new,
    }


def test_staff_html_post_requires_csrf_before_any_case_access():
    response = Client(enforce_csrf_checks=True).post(
        f"/staff/recovery/{uuid4()}/", {"action": "apply"}
    )
    assert response.status_code == 403
    assert response["Cache-Control"] == "no-store"


def test_staff_read_outage_returns_generic_unavailable_without_private_case(
    monkeypatch,
):
    from django.db import DatabaseError

    from apps.accounts import staff_views

    monkeypatch.setattr(staff_views, "current_actor", lambda *args: object())

    def unavailable(*args):
        raise DatabaseError("private database detail")

    monkeypatch.setattr(staff_views.recovery, "recovery_detail", unavailable)
    response = Client().get(
        f"/staff/recovery/{uuid4()}/",
        {"step_up_id": str(uuid4()), "reason_code": "identity_verified"},
    )
    assert response.status_code == 503
    assert response["Cache-Control"] == "no-store"
    assert b"private database detail" not in response.content


@pytest.mark.parametrize(
    "path",
    [
        "/accounts/entry/",
        "/accounts/verify/",
        "/accounts/me/",
        "/accounts/phone-change/",
        "/accounts/recovery/",
        "/privacy/requests/",
    ],
)
def test_native_html_csrf_precedes_any_identity_or_provider_effect(path):
    response = Client(enforce_csrf_checks=True).post(path, {"action": "verify"})
    assert response.status_code == 403
    assert response["Cache-Control"] == "no-store"
