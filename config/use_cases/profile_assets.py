"""Explicit professional subject, private-store and immutable metadata wiring."""

from apps.assets import delivery, uploads
from apps.assets.contracts import UploadQuota as UploadQuota
from apps.assets.storage import get_private_store as get_private_store
from apps.governance.audit import append_event
from apps.governance.audit_models import AuditEvent
from apps.governance.outbox import append_outbox
from apps.professionals.policies import owned_asset_subject


def hooks(actor):
    def record(outcome):
        append_event(outcome, actor_uuid=actor.user_uuid, subject_type="asset")

    def lookup(operation_id):
        # Only server-written successful command metadata, serialized by User lock.
        row = AuditEvent.objects.filter(
            actor_uuid=actor.user_uuid,
            correlation_id=operation_id,
            subject_type="asset",
            result="succeeded",
            action__in=["asset.begun", "asset.finalized", "asset.revoked"],
        ).first()
        return (row.action, row.subject_uuid) if row else None

    return record, lookup


def begin_profile_upload(
    actor,
    purpose,
    subject_uuid,
    operation_id,
    at,
    *,
    declared_size,
    declared_type,
):
    record, lookup = hooks(actor)
    return uploads.begin_profile_upload(
        actor,
        purpose,
        subject_uuid,
        operation_id,
        at,
        declared_size=declared_size,
        declared_type=declared_type,
        subject=owned_asset_subject,
        record=record,
        lookup=lookup,
    )


def receive_profile_upload(actor, asset_uuid, expected_version, stream, at):
    record, _ = hooks(actor)
    return uploads.receive_profile_upload(
        actor,
        asset_uuid,
        expected_version,
        stream,
        at,
        subject=owned_asset_subject,
        record=record,
        store=get_private_store,
    )


def finalize_profile_upload(actor, asset_uuid, expected_version, operation_id, at):
    record, lookup = hooks(actor)

    def source_bound(row):
        return AuditEvent.objects.filter(
            actor_uuid=actor.user_uuid,
            subject_uuid=row.id,
            subject_type="asset",
            action="asset.uploaded",
            result="succeeded",
            correlation_id=uploads.source_receipt(row),
        ).exists()

    def emit(row):
        append_outbox(
            "asset.processing_requested",
            row.id,
            row.processing_version,
            {"asset_uuid": str(row.id), "user_uuid": str(actor.user_uuid)},
            f"asset.processing_requested:{row.id}:{row.processing_version}",
        )

    return uploads.finalize_profile_upload(
        actor,
        asset_uuid,
        expected_version,
        operation_id,
        at,
        subject=owned_asset_subject,
        record=record,
        lookup=lookup,
        source_bound=source_bound,
        store=get_private_store,
        emit=emit,
    )


def abandon_profile_upload(actor, asset_uuid, expected_version, operation_id, at):
    record, lookup = hooks(actor)
    return uploads.abandon_profile_upload(
        actor,
        asset_uuid,
        expected_version,
        operation_id,
        at,
        subject=owned_asset_subject,
        record=record,
        lookup=lookup,
    )


def authorized_profile_download(actor, asset_uuid, purpose, at, staff_context=None):
    return delivery.authorized_profile_download(actor, asset_uuid, purpose, at)
