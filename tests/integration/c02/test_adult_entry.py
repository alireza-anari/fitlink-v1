from datetime import date
from uuid import UUID

import pytest
from django.apps import apps
from django.utils import timezone
from test_otp_consume import PHONE, sent, verifier
from test_otp_issue import record

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize(
    "birth,attested",
    [(date(2015, 1, 1), True), (None, True), (date(1990, 1, 1), False)],
)
def test_no_adult_declaration_no_identity(limiter, birth, attested):
    now = timezone.now()
    challenge, code = sent(now)
    result = verifier().verify_otp(
        PHONE,
        challenge,
        code,
        "login",
        UUID(int=0),
        "127.0.0.1",
        now,
        record,
        birth_date=birth,
        adult_attested=attested,
    )
    assert not result.valid
    assert not apps.get_model("accounts", "User").objects.exists()
    assert not apps.get_model("accounts", "AccountSessionControl").objects.exists()


@pytest.mark.parametrize(
    "state,active,valid",
    [("active", True, True), ("restricted", True, True), ("suspended", False, False)],
)
def test_legacy_entry_records_adult_without_reactivation(limiter, state, active, valid):
    users = apps.get_model("accounts", "User")
    user = users.objects.create_user(PHONE, state=state, is_active=active)
    now = timezone.now()
    challenge, code = sent(now)
    result = verifier().verify_otp(
        PHONE,
        challenge,
        code,
        "login",
        UUID(int=0),
        "127.0.0.1",
        now,
        record,
        birth_date=date(1990, 1, 1),
        adult_attested=True,
    )
    assert result.valid is valid
    user.refresh_from_db()
    assert (
        users.objects.count() == 1 and user.state == state and user.is_active is active
    )
    assert (user.adult_attested_at is not None) is valid
    assert not apps.get_model("accounts", "AccountSessionControl").objects.exists()
