from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from django.apps import apps
from django.contrib.sessions.models import Session
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.utils import timezone

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def require_security_schema():
    names = {model.__name__ for model in apps.get_app_config("accounts").get_models()}
    assert "OTPChallenge" in names, "missing C02 durable security schema"
    return apps.get_model("accounts", "User")


def test_populated_c01_upgrade_preserves_identity_and_sessions():
    require_security_schema()
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    assert targets != [("accounts", "0001_initial")]
    original = [("accounts", "0001_initial")]
    try:
        executor.migrate(original)
        historical = executor.loader.project_state(original).apps
        user = historical.get_model("accounts", "User")
        session = Session
        ids = [
            UUID("aaaaaaaa-0000-4000-8000-000000000001"),
            UUID("aaaaaaaa-0000-4000-8000-000000000002"),
        ]
        for index, active in enumerate((True, False)):
            user.objects.create(
                phone=f"+98912345678{index}",
                public_id=ids[index],
                is_active=active,
                password="!legacy",
            )
        session.objects.create(
            session_key="c01-legacy-session",
            session_data="legacy",
            expire_date=timezone.now() + timedelta(days=1),
        )
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        current = executor.loader.project_state(targets).apps
        rows = list(current.get_model("accounts", "User").objects.order_by("phone"))
        assert [row.public_id for row in rows] == ids
        assert [row.phone for row in rows] == ["+989123456780", "+989123456781"]
        assert [row.password for row in rows] == ["!legacy", "!legacy"]
        assert all(
            row.birth_date is None and row.adult_attested_at is None for row in rows
        )
        assert [row.state for row in rows] == ["active", "suspended"]
        assert [row.is_active for row in rows] == [True, False]
        assert all(row.auth_version == 1 for row in rows)
        assert (
            current.get_model("sessions", "Session")
            .objects.get(session_key="c01-legacy-session")
            .session_data
            == "legacy"
        )
        assert "auth_user" not in connection.introspection.table_names()
    finally:
        MigrationExecutor(connection).migrate(targets)


def reject(model, **values):
    with pytest.raises(IntegrityError), transaction.atomic():
        model.objects.create(**values)


def test_user_constraints_preserve_legacy_denial():
    user = require_security_schema()
    for extras in [
        dict(auth_version=0),
        dict(state_version=0),
        dict(state="suspended", is_active=True),
        dict(state="active", is_active=False),
        dict(state="invented"),
        dict(adult_attested_at=timezone.now()),
        dict(adult_attestation_version="declared"),
    ]:
        reject(user, phone="+989123456789", **extras)
    inactive = user.objects.create_user("+989123456788", is_active=False)
    assert inactive.state == "suspended" and not inactive.is_active
    assert inactive.birth_date is None and not inactive.has_usable_password()


def test_anchor_uniqueness_and_bounds():
    require_security_schema()
    phone = apps.get_model("accounts", "OTPPhoneState")
    anchor = apps.get_model("accounts", "SecurityRateAnchor")
    phone.objects.create(phone="+989123456789")
    reject(phone, phone="+989123456789")
    reject(phone, phone="09123456789")
    reject(phone, phone="+989123456788", generation=-1)
    anchor.objects.create(kind="phone", key_id="v1", key_digest="a" * 64)
    reject(anchor, kind="phone", key_id="v1", key_digest="a" * 64)
    reject(anchor, kind="arbitrary", key_id="v1", key_digest="b" * 64)


def test_challenge_and_session_constraints():
    user = require_security_schema().objects.create_user("+989123456789")
    phone = apps.get_model("accounts", "OTPPhoneState").objects.create(phone=user.phone)
    challenge = apps.get_model("accounts", "OTPChallenge")
    now = timezone.now()
    base = dict(
        phone_state=phone,
        generation=1,
        purpose="login",
        context_uuid=UUID(int=0),
        key_id="v1",
        code_digest="a" * 64,
        issued_at=now,
        expires_at=now + timedelta(seconds=300),
    )
    challenge.objects.create(**base)
    reject(challenge, **base)
    for changes in [
        dict(generation=2, expires_at=now),
        dict(generation=2, attempts=6),
        dict(generation=2, purpose="unknown"),
        dict(generation=2, consumed_at=now, delivery_state="pending"),
        dict(generation=2, proof_applied_at=now),
        dict(generation=2, target_user=user, target_auth_version=None),
    ]:
        reject(challenge, **{**base, **changes})
    session = apps.get_model("accounts", "AccountSessionControl")
    values = dict(
        user=user,
        key_id="v1",
        session_digest="b" * 64,
        auth_version=1,
        scope="normal",
        authenticated_at=now,
        created_at=now,
        expires_at=now + timedelta(days=1),
    )
    session.objects.create(**values)
    reject(session, **values)
    reject(session, **{**values, "session_digest": "c" * 64, "scope": "admin"})
    reject(session, **{**values, "session_digest": "c" * 64, "auth_version": 0})
    reject(session, **{**values, "session_digest": "c" * 64, "expires_at": now})


def test_reservation_is_unique_and_protected():
    require_security_schema()
    anchor = apps.get_model("accounts", "SecurityRateAnchor")
    event = apps.get_model("accounts", "SecurityRateEvent")
    phone = anchor.objects.create(kind="phone", key_id="v1", key_digest="a" * 64)
    ip = anchor.objects.create(kind="ip", key_id="v1", key_digest="b" * 64)
    values = dict(
        reservation_id=uuid4(),
        phone_anchor=phone,
        ip_anchor=ip,
        kind="send",
        outcome="pending",
        at=timezone.now(),
    )
    event.objects.create(**values)
    reject(event, **values)
    reject(event, **{**values, "reservation_id": uuid4(), "kind": "arbitrary"})
    reject(event, **{**values, "reservation_id": uuid4(), "outcome": "arbitrary"})
