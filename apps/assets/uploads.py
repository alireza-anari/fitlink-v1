"""Short owned reservations, bounded private I/O, then fresh commit authority."""

import json
from dataclasses import astuple
from datetime import timedelta
from hashlib import sha256
from uuid import UUID, uuid4

from django.conf import settings
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.accounts.contracts import SecurityOutcome
from apps.accounts.sessions import locked_actor

from .contracts import UploadConflict, UploadDTO, UploadQuota
from .models import Asset
from .policies import owned_asset, validate_context
from .storage import limited_spool
from .validation import (
    MAX_BYTES,
    raster_signature,
    validate_declaration,
    validate_filename,
)


def dto(row):
    return UploadDTO(row.id, row.version, row.state, row.purpose, row.upload_expires_at)


def own_profile_upload_status(actor, asset_uuid, at, *, subject):
    """Read one exact owned reservation after current subject authority."""
    from .contracts import AssetNotFound

    validate_context(actor, at)
    with transaction.atomic():
        user = locked_actor(actor, "asset.owner_read", max(at, timezone.now()))
        try:
            row = owned_asset(user, asset_uuid, subject)
        except (ValueError, LookupError):
            raise AssetNotFound("Asset unavailable") from None
        return dto(row)


def binding(row):
    return (
        row.id,
        row.owner_id,
        row.subject_kind,
        row.subject_uuid,
        row.purpose,
        row.source_key,
        row.classification,
        row.declared_size,
        row.declared_type,
    )


def source_receipt(row):
    """Opaque UUID attestation; no key, hash, filename or bytes enter audit."""
    facts = (*binding(row), row.actual_size, row.detected_type, row.sha256)
    return UUID(bytes=sha256(json.dumps(facts, default=str).encode()).digest()[:16])


def version(expected_version):
    if type(expected_version) is not int or expected_version < 1:
        raise ValueError("Invalid upload version")


def operation(operation_id):
    if not isinstance(operation_id, UUID):
        raise ValueError("Invalid upload operation")


def live(row, expected_version, at, state):
    if (
        row.version != expected_version
        or row.state != state
        or row.accepted_at is not None
        or row.upload_expires_at <= at
    ):
        raise UploadConflict("Upload conflict")


def record_change(record, row, action, correlation):
    record(
        SecurityOutcome(
            action,
            "succeeded",
            row.id,
            correlation,
            ("state", "version"),
            "user_requested",
        )
    )


def replay(row, expected_version, operation_id, action, lookup):
    receipt = lookup(operation_id)
    if receipt is None:
        return False
    if (
        receipt != (action, row.id)
        or row.version != expected_version + 1
        or (
            action == "asset.finalized"
            and (
                row.state != "quarantined"
                or row.accepted_at is None
                or row.finalized_at is None
            )
        )
        or (action == "asset.revoked" and row.state != "abandoned")
    ):
        raise UploadConflict("Upload conflict")
    return True


def begin_profile_upload(
    actor,
    purpose,
    subject_uuid,
    operation_id,
    at,
    *,
    declared_size,
    declared_type,
    subject,
    record,
    lookup,
):
    validate_context(actor, at)
    operation(operation_id)
    validate_declaration(declared_size, declared_type)
    with transaction.atomic():
        user = locked_actor(actor, "asset.owner_write", at)
        target = subject(user, purpose, subject_uuid)
        old = lookup(operation_id)
        if old is not None:
            if old[0] != "asset.begun":
                raise UploadConflict("Upload conflict")
            row = owned_asset(user, old[1], subject)
            if (row.subject_kind, row.subject_uuid) != astuple(target) or (
                row.purpose,
                row.declared_size,
                row.declared_type,
            ) != (purpose, declared_size, declared_type):
                raise UploadConflict("Upload conflict")
            return dto(row)
        pending = Asset.objects.filter(
            owner=user,
            accepted_at__isnull=True,
            state__in=["pending_upload", "receiving", "quarantined"],
            upload_expires_at__gt=at,
        )
        day = at.replace(hour=0, minute=0, second=0, microsecond=0)
        used = (
            Asset.objects.filter(
                owner=user,
                accepted_at__gte=day,
                accepted_at__lt=day + timedelta(days=1),
            ).aggregate(total=Sum("actual_size"))["total"]
            or 0
        )
        reserved = pending.aggregate(total=Sum("declared_size"))["total"] or 0
        if (
            pending.count() >= settings.PROFILE_UPLOAD_MAX_PENDING
            or used + reserved + declared_size > settings.PROFILE_UPLOAD_DAILY_BYTES
        ):
            raise UploadQuota("Upload quota")
        row = Asset.objects.create(
            owner=user,
            subject_kind=target.kind,
            subject_uuid=target.id,
            purpose=purpose,
            source_key="quarantine/" + uuid4().hex,
            declared_size=declared_size,
            declared_type=declared_type,
            created_at=at,
            upload_expires_at=at
            + timedelta(seconds=settings.PROFILE_UPLOAD_EXPIRY_SECONDS),
        )
        record_change(record, row, "asset.begun", operation_id)
        return dto(row)


def receive_profile_upload(
    actor,
    asset_uuid,
    expected_version,
    stream,
    at,
    *,
    subject,
    record,
    store,
):
    validate_context(actor, at)
    version(expected_version)
    if transaction.get_connection().in_atomic_block:
        raise RuntimeError("Upload I/O requires its own commit boundary")
    with transaction.atomic():
        user = locked_actor(actor, "asset.owner_write", at)
        row = owned_asset(user, asset_uuid, subject)
        live(row, expected_version, at, "pending_upload")
        validate_declaration(row.declared_size, row.declared_type)
        if hasattr(stream, "content_type"):
            if stream.content_type != row.declared_type:
                raise ValueError("Upload declaration mismatch")
            validate_filename(stream.name, row.declared_type)
        intended = binding(row)
        row.state, row.version = "receiving", row.version + 1
        row.save(update_fields=["state", "version", "updated_at"])
    # Byte cap is based on actual reads, not Content-Length or declared size.
    provider = store()
    with limited_spool(stream, MAX_BYTES) as content:
        content.seek(0, 2)
        actual_size = content.tell()
        content.seek(0)
        detected = raster_signature(content.read(8), row.declared_type)
        if actual_size != row.declared_size:
            raise ValueError("Upload size mismatch")
        content.seek(0)
        checksum = sha256()
        while chunk := content.read(65536):
            checksum.update(chunk)
        content.seek(0)
        try:
            provider.put_stream(row.source_key, content, detected, MAX_BYTES)
        except ValueError:
            raise UploadConflict("Upload conflict") from None
    current_at = max(at, timezone.now())
    with transaction.atomic():
        user = locked_actor(actor, "asset.owner_write", current_at)
        current = owned_asset(user, asset_uuid, subject)
        live(current, expected_version + 1, current_at, "receiving")
        if binding(current) != intended:
            raise UploadConflict("Upload conflict")
        current.state, current.version = "quarantined", current.version + 1
        current.actual_size, current.detected_type = actual_size, detected
        current.sha256 = checksum.hexdigest()
        current.save(
            update_fields=[
                "state",
                "version",
                "actual_size",
                "detected_type",
                "sha256",
                "updated_at",
            ]
        )
        record_change(record, current, "asset.uploaded", source_receipt(current))
        return dto(current)


def finalize_profile_upload(
    actor,
    asset_uuid,
    expected_version,
    operation_id,
    at,
    *,
    subject,
    record,
    lookup,
    source_bound,
    store,
    emit,
):
    validate_context(actor, at)
    version(expected_version)
    operation(operation_id)
    if transaction.get_connection().in_atomic_block:
        raise RuntimeError("Upload I/O requires its own commit boundary")
    with transaction.atomic():
        user = locked_actor(actor, "asset.owner_write", at)
        row = owned_asset(user, asset_uuid, subject)
        if replay(row, expected_version, operation_id, "asset.finalized", lookup):
            return dto(row)
        live(row, expected_version, at, "quarantined")
        if not source_bound(row):
            raise UploadConflict("Upload conflict")
        intended = source_receipt(row)
    provider = store()
    try:
        metadata = provider.head(row.source_key)
        validate_declaration(metadata.size, metadata.content_type)
        if (
            metadata.size != row.actual_size
            or metadata.size != row.declared_size
            or metadata.content_type != row.declared_type
            or metadata.content_type != row.detected_type
        ):
            raise UploadConflict("Upload conflict")
        content = provider.read_limited(row.source_key, MAX_BYTES)
        if (
            len(content) != metadata.size
            or sha256(content).hexdigest() != row.sha256
            or raster_signature(content[:8], row.declared_type) != row.detected_type
        ):
            raise UploadConflict("Upload conflict")
    except (FileNotFoundError, ValueError):
        raise UploadConflict("Upload conflict") from None
    current_at = max(at, timezone.now())
    with transaction.atomic():
        user = locked_actor(actor, "asset.owner_write", current_at)
        current = owned_asset(user, asset_uuid, subject)
        if replay(current, expected_version, operation_id, "asset.finalized", lookup):
            return dto(current)
        live(current, expected_version, current_at, "quarantined")
        if source_receipt(current) != intended or not source_bound(current):
            raise UploadConflict("Upload conflict")
        current.accepted_at = current.finalized_at = current_at
        current.version += 1
        current.save(
            update_fields=[
                "accepted_at",
                "finalized_at",
                "version",
                "updated_at",
            ]
        )
        record_change(record, current, "asset.finalized", operation_id)
        emit(current)
        return dto(current)


def abandon_profile_upload(
    actor,
    asset_uuid,
    expected_version,
    operation_id,
    at,
    *,
    subject,
    record,
    lookup,
):
    validate_context(actor, at)
    version(expected_version)
    operation(operation_id)
    with transaction.atomic():
        user = locked_actor(actor, "asset.owner_write", at)
        row = owned_asset(user, asset_uuid, subject)
        if replay(row, expected_version, operation_id, "asset.revoked", lookup):
            return dto(row)
        if (
            row.version != expected_version
            or row.accepted_at is not None
            or row.state not in {"pending_upload", "receiving", "quarantined"}
        ):
            raise UploadConflict("Upload conflict")
        row.state, row.version, row.revoked_at = "abandoned", row.version + 1, at
        row.save(update_fields=["state", "version", "revoked_at", "updated_at"])
        record_change(record, row, "asset.revoked", operation_id)
        return dto(row)
