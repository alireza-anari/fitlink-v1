"""Access ends synchronously; effects retain history and reconcile private jobs."""

from datetime import timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from django.db import transaction
from django.utils import timezone

from apps.assets.models import AssetProcessingAttempt
from apps.governance.audit_models import AuditEvent
from apps.governance.outbox import dispatch_event
from apps.governance.outbox_models import OutboxEvent
from apps.professionals.models import AssistantMembership
from apps.professionals.selectors import own_professional_profile
from config.event_handlers import HANDLERS
from config.use_cases import profile_assets
from config.use_cases.privacy import request_privacy

from .processing_helpers import Scanner, prepared
from .processing_helpers import api as processing
from .test_asset_holds import (
    absent,
    api,
    cleanup,
    hold,
    media,
    policy,
    revoke,
    subject,
)
from .test_professional_setup import owner

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize(
    "defect",
    [
        "missing",
        "draft",
        "approved",
        "wrong_class",
        "wrong_purpose",
        "future",
        "not_due",
        "wrong_version",
        "live",
        "selected",
    ],
)
def test_cleanup_without_effective_policy_or_eligibility_denied(defect):
    s = owner()
    asset, store = media(s)
    revoke(asset)
    rule = policy(s, asset)
    if defect == "missing":
        rule.id = uuid4()
    elif defect in {"draft", "approved"}:
        rule.status = defect
        rule.save()
    elif defect == "wrong_class":
        rule.data_class = "account_metadata"
        rule.save()
    elif defect == "wrong_purpose":
        rule.purpose = "cover"
        rule.save()
    elif defect == "future":
        rule.effective_at = timezone.now() + timedelta(days=1)
        rule.save()
    elif defect == "not_due":
        rule.duration_seconds = 86400
        rule.save()
    elif defect == "live":
        asset.state, asset.revoked_at = "ready", None
        asset.save()
    elif defect == "selected":
        s.profile.avatar_id = asset.id
        s.profile.save()
    version = asset.version + 1 if defect == "wrong_version" else asset.version
    result = api(
        "cleanup_asset", asset.id, version, rule.id, timezone.now(), store=store
    )
    assert result in {"denied", "policy_required", "not_due", "in_use", "conflict"}
    assert store.head(asset.source_key).size > 0
    assert store.head(asset.derivatives.get().key).size > 0
    asset.refresh_from_db()
    assert asset.state not in {"deleted", "deletion_pending"}


def test_cleanup_without_effective_policy_denied():
    s = owner()
    asset, store = media(s)
    revoke(asset)
    assert cleanup(asset, None, store) == "policy_required"
    assert store.head(asset.source_key).size > 0


def test_private_delete_failure_is_bounded_and_retry_is_idempotent():
    s = owner()
    asset, store = media(s)
    revoke(asset)
    rule = policy(s, asset)

    class Broken:
        def delete(self, key):
            if key == asset.source_key:
                store.delete(key)
            else:
                raise RuntimeError("PRIVATE_SENTINEL https://private.invalid/key")

        def head(self, key):
            return store.head(key)

    assert cleanup(asset, rule, Broken()) == "retry"
    asset.refresh_from_db()
    assert asset.state == "deletion_pending"
    assert store.head(asset.derivatives.get().key).size > 0
    assert cleanup(asset, rule, store) == "deleted"
    assert cleanup(asset, rule, store) == "deleted"
    absent(store, asset.source_key)
    absent(store, asset.derivatives.get().key)
    assert (
        AuditEvent.objects.filter(action="asset.deleted", subject_uuid=asset.id).count()
        == 1
    )
    assert "PRIVATE_SENTINEL" not in repr(asset.__dict__)


def test_deletion_owner_denies_release_preview_and_stale_task(settings, monkeypatch):
    s = prepared(monkeypatch)
    worker = processing()
    worker.request_processing(s.event, timezone.now())
    assert worker.scan_due_assets(timezone.now(), 1, enqueue=lambda *args: None) == 1
    attempt = AssetProcessingAttempt.objects.get(asset=s.asset, state="running")
    request_privacy(s.actor, "delete", uuid4(), timezone.now(), confirmed=True)
    # Denied before dispatch, including a caller holding an old lease/receipt.
    with pytest.raises(PermissionError):
        own_professional_profile(s.actor, timezone.now())
    with pytest.raises((PermissionError, LookupError)):
        profile_assets.authorized_profile_download(
            s.actor, s.asset.id, "avatar", timezone.now()
        )
    assert (
        worker.process_asset(
            s.asset.id,
            1,
            attempt.lease_uuid,
            timezone.now(),
            store=s.store,
            scanner=Scanner(),
        )
        != "ready"
    )
    event = OutboxEvent.objects.get(event_type="account.security_changed")
    event.state, event.lease_uuid, event.lease_until = (
        "leased",
        uuid4(),
        timezone.now() + timedelta(seconds=60),
    )
    event.save()
    assert dispatch_event(event.id, timezone.now(), lease_uuid=event.lease_uuid)
    s.asset.refresh_from_db()
    attempt.refresh_from_db()
    assert s.asset.state in {"abandoned", "revoked"} and s.asset.revoked_at is not None
    assert attempt.state == "failed" and attempt.lease_uuid is None
    assert not s.asset.derivatives.filter(state="ready").exists()
    assert s.store.head(s.asset.source_key).size > 0


def test_retained_evidence_not_normal_access(settings):
    s = owner()
    asset, store = media(s)
    hold(settings, s, subject(asset))
    request_privacy(s.actor, "delete", uuid4(), timezone.now(), confirmed=True)
    # Retention inventory is still available without an owner access session.
    inventory = api("inventory_c03_owner", s.user.public_id, timezone.now())
    assert asset.id in {row.record_uuid for row in inventory.records}
    with pytest.raises(PermissionError):
        own_professional_profile(s.actor, timezone.now())
    with pytest.raises((PermissionError, LookupError)):
        profile_assets.authorized_profile_download(
            s.actor, asset.id, "avatar", timezone.now()
        )
    assert store.head(asset.source_key).size > 0


def test_current_security_effect_revokes_only_owner_and_inert_membership():
    s, other = owner(), owner("+989123456789")
    a, _ = media(s)
    b, _ = media(other)
    member = AssistantMembership.objects.create(profile=s.profile, assistant=other.user)
    request_privacy(s.actor, "delete", uuid4(), timezone.now(), confirmed=True)
    s.user.refresh_from_db()
    event = SimpleNamespace(
        aggregate_uuid=s.user.public_id,
        aggregate_version=s.user.auth_version,
        payload={"user_uuid": str(s.user.public_id)},
        event_type="account.security_changed",
    )
    with transaction.atomic():
        assert HANDLERS[event.event_type](event, timezone.now()) == "applied"
    a.refresh_from_db()
    b.refresh_from_db()
    member.refresh_from_db()
    assert a.state == "revoked" and b.state == "ready"
    assert member.state == "revoked" and member.revoked_at is not None
    old_version = a.version
    with transaction.atomic():
        assert HANDLERS[event.event_type](event, timezone.now()) == "applied"
    a.refresh_from_db()
    assert a.version == old_version


def test_stale_security_event_cannot_revoke_active_current_owner():
    s = owner()
    asset, _ = media(s)
    event = SimpleNamespace(
        aggregate_uuid=s.user.public_id,
        aggregate_version=999,
        payload={"user_uuid": str(s.user.public_id)},
        event_type="account.security_changed",
    )
    with transaction.atomic():
        assert HANDLERS[event.event_type](event, timezone.now()) == "skipped"
    asset.refresh_from_db()
    assert asset.state == "ready" and asset.revoked_at is None


def test_cleanup_outbox_receipt_never_performs_storage_io(monkeypatch):
    from apps.assets import storage

    s = owner()
    asset, _ = media(s)
    revoke(asset)

    def fail(*args, **kwargs):
        raise AssertionError("I/O inside outbox")

    monkeypatch.setattr(storage, "get_private_store", fail)
    assert "asset.cleanup_requested" in HANDLERS
    event = SimpleNamespace(
        aggregate_uuid=asset.id,
        aggregate_version=asset.version,
        payload={"asset_uuid": str(asset.id), "user_uuid": str(s.user.public_id)},
    )
    with transaction.atomic():
        assert HANDLERS["asset.cleanup_requested"](event, timezone.now()) == "applied"
    asset.refresh_from_db()
    assert asset.state == "revoked"


def test_forged_storage_inventory_cannot_erase_another_asset():
    from apps.assets.models import Asset

    s, other = owner(), owner("+989123456789")
    foreign, store = media(other)
    at = timezone.now()
    forged = Asset.objects.create(
        owner=s.user,
        subject_kind="professional_profile",
        subject_uuid=s.profile.id,
        purpose="avatar",
        source_key=foreign.source_key,
        state="abandoned",
        revoked_at=at - timedelta(minutes=5),
        upload_expires_at=at,
    )
    rule = policy(s, forged)
    rule.data_class = "asset_quarantine"
    rule.save()
    assert cleanup(forged, rule, store) == "denied"
    assert store.head(foreign.source_key).size > 0


def test_security_effect_failure_rolls_back_asset_and_metadata_receipt(monkeypatch):
    import apps.governance.outbox as outbox

    s = owner()
    asset, _ = media(s)
    request_privacy(s.actor, "delete", uuid4(), timezone.now(), confirmed=True)
    s.user.refresh_from_db()

    def fail(*args, **kwargs):
        raise RuntimeError("outbox unavailable")

    monkeypatch.setattr(outbox, "append_outbox", fail)
    event = SimpleNamespace(
        aggregate_uuid=s.user.public_id,
        aggregate_version=s.user.auth_version,
        payload={"user_uuid": str(s.user.public_id)},
        event_type="account.security_changed",
    )
    with pytest.raises(RuntimeError), transaction.atomic():
        HANDLERS[event.event_type](event, timezone.now())
    asset.refresh_from_db()
    assert asset.state == "ready"
    assert not AuditEvent.objects.filter(
        action="asset.revoked", subject_uuid=asset.id
    ).exists()


def test_held_case_evidence_never_restores_assigned_staff_access(settings):
    from .verification_helpers import assign, reviewer, selectors, submitted

    s = submitted()
    staff = reviewer(settings, s.case.id)
    s.case = assign(s, staff)
    asset, credential = s.assets["coach"]
    from apps.governance.retention import ValidatedRecordSubject

    row = s.profile.credentials.get(pk=credential.id)
    hold(
        settings,
        s,
        ValidatedRecordSubject(
            "professional_credential", row.id, s.user.public_id, row.version
        ),
        s.case.id,
        staff,
    )
    request_privacy(s.actor, "delete", uuid4(), timezone.now(), confirmed=True)
    with pytest.raises((PermissionError, LookupError)):
        selectors().assigned_verification_detail(
            staff.actor, s.case.id, staff.step, "verification_review", timezone.now()
        )
    assert AssetProcessingAttempt.objects.filter(asset=asset).exists()


def test_security_reconciliation_survives_accumulated_asset_tombstones():
    from apps.assets.models import Asset

    s = owner()
    asset, _ = media(s)
    Asset.objects.bulk_create(
        [
            Asset(
                owner=s.user,
                subject_kind="professional_profile",
                subject_uuid=s.profile.id,
                purpose="avatar",
                state="deleted",
                revoked_at=timezone.now(),
                upload_expires_at=timezone.now(),
            )
            for _ in range(1001)
        ]
    )
    request_privacy(s.actor, "delete", uuid4(), timezone.now(), confirmed=True)
    s.user.refresh_from_db()
    event = SimpleNamespace(
        aggregate_uuid=s.user.public_id,
        aggregate_version=s.user.auth_version,
        payload={"user_uuid": str(s.user.public_id)},
        event_type="account.security_changed",
    )
    with transaction.atomic():
        assert HANDLERS[event.event_type](event, timezone.now()) == "applied"
    asset.refresh_from_db()
    assert asset.state == "revoked"


def test_storage_delete_acknowledgement_without_erasure_stays_pending():
    s = owner()
    asset, store = media(s)
    revoke(asset)

    class NoEffect:
        def delete(self, key):
            return None

        def head(self, key):
            return store.head(key)

    assert cleanup(asset, policy(s, asset), NoEffect()) == "retry"
    asset.refresh_from_db()
    assert asset.state == "deletion_pending"
    assert not AuditEvent.objects.filter(
        action="asset.deleted", subject_uuid=asset.id
    ).exists()
