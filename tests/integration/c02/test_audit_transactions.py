import importlib
from uuid import uuid4

import pytest
from django.apps import apps
from django.db import DatabaseError, connection, transaction

from apps.accounts.contracts import SecurityOutcome

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def modules():
    assert apps.is_installed("apps.governance"), (
        "missing transactional governance schema"
    )
    return importlib.import_module("apps.governance.audit"), importlib.import_module(
        "apps.governance.outbox"
    )


def outcome():
    return SecurityOutcome("otp.requested", "accepted", uuid4(), uuid4())


def test_audit_and_outbox_share_transaction_and_dedup():
    audit, outbox = modules()
    event = apps.get_model("governance", "AuditEvent")
    effects = apps.get_model("governance", "OutboxEvent")
    with pytest.raises(RuntimeError), transaction.atomic():
        audit.append_event(outcome())
        outbox.append_outbox("account.security_changed", uuid4(), 1, {}, "rollback:1")
        raise RuntimeError("rollback probe")
    assert not event.objects.exists() and not effects.objects.exists()
    subject = uuid4()
    with transaction.atomic():
        first = outbox.append_outbox(
            "account.security_changed", subject, 1, {}, "same:1"
        )
        assert first == outbox.append_outbox(
            "account.security_changed", subject, 1, {}, "same:1"
        )
        with pytest.raises(ValueError):
            outbox.append_outbox("account.security_changed", uuid4(), 1, {}, "same:1")
    assert effects.objects.count() == 1


def test_audit_model_queryset_and_owner_sql_are_append_only():
    audit, _ = modules()
    model = apps.get_model("governance", "AuditEvent")
    with transaction.atomic():
        pk = audit.append_event(outcome())
    row = model.objects.get(pk=pk)
    for operation in [
        lambda: row.save(),
        lambda: row.delete(),
        lambda: model.objects.filter(pk=pk).update(result="denied"),
        lambda: model.objects.filter(pk=pk).delete(),
    ]:
        with pytest.raises(ValueError, match="append-only"):
            operation()
    for sql in [
        "UPDATE governance_auditevent SET result='denied'",
        "DELETE FROM governance_auditevent",
    ]:
        with (
            pytest.raises(DatabaseError),
            transaction.atomic(),
            connection.cursor() as cursor,
        ):
            cursor.execute(sql)
    assert model.objects.get(pk=pk).result == "accepted"


def test_runtime_role_can_append_and_read_but_not_mutate():
    audit, _ = modules()
    role = "c02_audit_" + uuid4().hex
    q = connection.ops.quote_name
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE ROLE {q(role)} NOLOGIN")
        cursor.execute(f"GRANT USAGE ON SCHEMA public TO {q(role)}")
        cursor.execute(f"GRANT SELECT, INSERT ON governance_auditevent TO {q(role)}")
    try:
        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute(f"SET LOCAL ROLE {q(role)}")
            audit.append_event(outcome())
            cursor.execute("SELECT count(*) FROM governance_auditevent")
            assert cursor.fetchone()[0] == 1
        for sql in [
            "UPDATE governance_auditevent SET result='denied'",
            "DELETE FROM governance_auditevent",
            "TRUNCATE governance_auditevent",
        ]:
            with (
                pytest.raises(DatabaseError),
                transaction.atomic(),
                connection.cursor() as cursor,
            ):
                cursor.execute(f"SET LOCAL ROLE {q(role)}")
                cursor.execute(sql)
    finally:
        with connection.cursor() as cursor:
            cursor.execute(f"DROP OWNED BY {q(role)}")
            cursor.execute(f"DROP ROLE {q(role)}")
