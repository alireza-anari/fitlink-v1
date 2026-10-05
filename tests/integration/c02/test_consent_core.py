import importlib
import importlib.util
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import timedelta
from uuid import uuid4

import pytest
from django.apps import apps
from django.db import DatabaseError, close_old_connections, connection, transaction
from django.utils import timezone
from test_phone_change import actor_for
from test_recovery_authorization import owner

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def contract():
    assert importlib.util.find_spec("apps.governance.consents"), (
        "missing purpose-limited consent core"
    )
    return importlib.import_module("apps.governance.consents"), importlib.import_module(
        "config.use_cases.consent"
    )


def prepared():
    module, commands = contract()
    user, grantee = owner(), owner("+989123456780")
    actor, _ = actor_for(user)
    at = timezone.now()
    scope = module.validate_scope(
        actor,
        grantee.public_id,
        "account_metadata",
        "account_metadata",
        user.public_id,
        user.state_version,
        at + timedelta(hours=1),
        at,
    )
    return module, commands, user, grantee, actor, scope, at


def granted():
    values = prepared()
    consent_id = values[1].grant_consent(
        values[4], values[5], "metadata-v1", "a" * 64, values[6]
    )
    return (*values, consent_id)


def test_exact_subject_grantee_purpose_scope_revision_and_expiry():
    module, commands, user, grantee, actor, scope, at, consent_id = granted()
    assert module.has_current_grant(
        user.public_id, grantee.public_id, scope.purpose, scope, at
    )
    for altered in (
        replace(scope, grantee_uuid=uuid4()),
        replace(scope, subject_uuid=uuid4()),
        replace(scope, object_uuid=uuid4()),
        replace(scope, object_version=2),
        replace(scope, purpose="archive_sharing"),
    ):
        assert not module.has_current_grant(
            altered.subject_uuid, altered.grantee_uuid, altered.purpose, altered, at
        )
    assert not module.has_current_grant(
        user.public_id, grantee.public_id, scope.purpose, scope, scope.expires_at
    )
    row = apps.get_model("governance", "Consent").objects.get(pk=consent_id)
    assert row.text_version == "metadata-v1" and row.content_hash == "a" * 64
    assert (
        apps.get_model("governance", "ConsentScope")
        .objects.filter(consent_id=consent_id)
        .count()
        == 1
    )


@pytest.mark.parametrize(
    "defect",
    [
        "foreign",
        "stale",
        "restricted",
        "suspended",
        "deleted",
        "forged_scope",
        "terms",
        "health",
        "expired",
        "bad_hash",
        "bad_text",
    ],
)
def test_forged_future_or_current_authority_denies_without_grant(defect):
    module, commands, user, grantee, actor, scope, at = prepared()
    if defect == "foreign":
        actor, _ = actor_for(owner("+989123456781"))
    elif defect == "stale":
        type(user).objects.filter(pk=user.pk).update(auth_version=2)
    elif defect in {"restricted", "suspended", "deleted"}:
        type(user).objects.filter(pk=user.pk).update(
            state=defect, is_active=defect == "restricted"
        )
    elif defect == "forged_scope":
        scope = replace(scope, object_uuid=uuid4())
    elif defect == "terms":
        scope = replace(scope, purpose="account_terms")
    elif defect == "health":
        scope = replace(scope, kind="health")
    elif defect == "expired":
        at = scope.expires_at
    with pytest.raises((PermissionError, ValueError)):
        commands.grant_consent(
            actor,
            scope,
            "" if defect == "bad_text" else "metadata-v1",
            "x" if defect == "bad_hash" else "a" * 64,
            at,
        )
    assert not apps.get_model("governance", "Consent").objects.exists()


def test_guessed_uuid_foreign_list_count_and_revoke_deny():
    module, commands, user, grantee, actor, scope, at, consent_id = granted()
    stranger, _ = actor_for(grantee)
    assert module.visible_consents(stranger, at).count() == 0
    assert not module.visible_consents(stranger, at).filter(pk=consent_id).exists()
    assert module.visible_consents(actor, at).count() == 1
    for foreign in (consent_id, uuid4()):
        with pytest.raises(PermissionError):
            commands.revoke_consent(stranger, foreign, 1, at)


def test_terminal_revoke_version_and_outbox():
    module, commands, user, grantee, actor, scope, at, consent_id = granted()
    commands.revoke_consent(actor, consent_id, 1, at)
    assert not module.has_current_grant(
        user.public_id, grantee.public_id, scope.purpose, scope, at
    )
    with pytest.raises(PermissionError):
        commands.revoke_consent(actor, consent_id, 1, at)
    assert (
        apps.get_model("governance", "OutboxEvent")
        .objects.filter(event_type="consent.revoked")
        .count()
        == 1
    )
    row = apps.get_model("governance", "Consent").objects.get(pk=consent_id)
    assert row.revoked_at == at and row.version == 2
    with (
        pytest.raises(DatabaseError),
        transaction.atomic(),
        connection.cursor() as cursor,
    ):
        cursor.execute(
            "UPDATE governance_consent SET revoked_at = NULL WHERE id = %s",
            [consent_id],
        )


@pytest.mark.parametrize(
    "operation,failure",
    [
        ("grant", "audit"),
        ("grant", "outbox"),
        ("revoke", "audit"),
        ("revoke", "outbox"),
    ],
)
def test_consent_scope_audit_and_outbox_rollback_together(
    monkeypatch, operation, failure
):
    module, commands, user, grantee, actor, scope, at, consent_id = granted()
    initial_count = apps.get_model("governance", "Consent").objects.count()

    def failed(*args, **kwargs):
        raise RuntimeError("persistence unavailable")

    monkeypatch.setattr(
        commands, "append_event" if failure == "audit" else "append_outbox", failed
    )
    with pytest.raises(RuntimeError):
        if operation == "grant":
            commands.grant_consent(actor, scope, "metadata-v1", "a" * 64, at)
        else:
            commands.revoke_consent(actor, consent_id, 1, at)
    assert apps.get_model("governance", "Consent").objects.count() == initial_count
    assert (
        apps.get_model("governance", "Consent").objects.get(pk=consent_id).revoked_at
        is None
    )


def test_concurrent_revoke_accepts_one_current_version():
    module, commands, user, grantee, actor, scope, at, consent_id = granted()
    barrier = threading.Barrier(2)

    def revoke(_):
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            try:
                commands.revoke_consent(actor, consent_id, 1, at)
                return True
            except PermissionError:
                return False
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert list(pool.map(revoke, range(2))).count(True) == 1
    assert (
        apps.get_model("governance", "OutboxEvent")
        .objects.filter(event_type="consent.revoked")
        .count()
        == 1
    )


@pytest.mark.parametrize("target", ["subject", "grantee"])
def test_current_restriction_never_reuses_old_consent(target):
    module, commands, user, grantee, actor, scope, at, consent_id = granted()
    type(user).objects.filter(pk=(user if target == "subject" else grantee).pk).update(
        state="restricted"
    )
    assert not module.has_current_grant(
        user.public_id, grantee.public_id, scope.purpose, scope, at
    )
