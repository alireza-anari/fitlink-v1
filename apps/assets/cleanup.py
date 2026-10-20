"""Versioned private-object erasure; no generic deletion or access authority."""

import logging
from datetime import datetime
from uuid import UUID, uuid4

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.accounts.contracts import SecurityOutcome
from apps.accounts.models import User
from apps.governance.audit import append_event
from apps.governance.privacy_models import RetentionPolicy

from .models import Asset, AssetDerivative, AssetProcessingAttempt
from .privacy import asset_data_class, bounded_rows
from .storage import get_private_store, validate_key

logger = logging.getLogger(__name__)


def _policy(asset, policy_uuid, at):
    return (
        RetentionPolicy.objects.select_for_update()
        .filter(
            pk=policy_uuid,
            data_class=asset_data_class(asset),
            purpose=asset.purpose,
            status="effective",
            approved_by__isnull=False,
            approved_at__lte=at,
            effective_at__lte=at,
            duration_seconds__gt=0,
        )
        .exclude(backup_reference="")
        .first()
    )


def _keys(asset):
    children = bounded_rows(
        AssetDerivative.objects.select_for_update().filter(asset=asset)
    )
    keys = tuple(
        dict.fromkeys(
            ([asset.source_key] if asset.source_key else [])
            + [row.key for row in children]
        )
    )
    for key in keys:
        validate_key(key)
    # Caller-supplied references or corrupt unpublished metadata cannot erase a
    # key that belongs to another installed source or derivative inventory.
    if (
        Asset.objects.exclude(pk=asset.id).filter(source_key__in=keys).exists()
        or AssetDerivative.objects.exclude(asset=asset).filter(key__in=keys).exists()
    ):
        raise PermissionError("Storage inventory denied")
    return keys


def _current(
    asset_uuid,
    expected_version,
    policy_uuid,
    at,
    subject_validator,
    hold_validator,
    in_use_validator,
):
    locator = Asset.objects.filter(pk=asset_uuid).values("owner_id").first()
    if locator is None:
        return "denied", None, None, ()
    owner = User.objects.select_for_update().get(pk=locator["owner_id"])
    candidate = Asset.objects.get(pk=asset_uuid)
    candidate.owner = owner
    # The server callback locks domain anchors before the private asset row.
    if subject_validator(candidate) is not True:
        return "denied", None, None, ()
    asset = Asset.objects.select_for_update().get(pk=asset_uuid)
    asset.owner = owner
    # The caller's tick can predate time spent waiting on a hold's owner lock.
    # Every destructive recheck must see holds committed during that wait.
    at = max(at, timezone.now())
    if asset.owner_id != owner.pk or asset.version != expected_version:
        return "conflict", None, None, ()
    if asset.state not in {"abandoned", "revoked", "deletion_pending", "deleted"}:
        return "denied", None, None, ()
    policy = _policy(asset, policy_uuid, at)
    if policy is None:
        logger.warning("private_asset_cleanup_policy_required")
        return "policy_required", None, None, ()
    if (
        asset.revoked_at is None
        or (at - asset.revoked_at).total_seconds() < policy.duration_seconds
    ):
        return "not_due", None, None, ()
    if hold_validator(asset, at) is not False:
        return "held", None, None, ()
    if in_use_validator(asset) is not False:
        return "in_use", None, None, ()
    return "eligible", asset, policy, _keys(asset)


def cleanup_asset(
    asset_uuid,
    expected_version,
    policy_uuid,
    at,
    *,
    subject_validator=None,
    hold_validator=None,
    in_use_validator=None,
    store=None,
):
    """Reserve at commit, then erase only a fixed revalidated private inventory.

    A new hold must reject deletion_pending/deleted inventory. A prior active
    hold wins the reservation. Keys survive deletion as recovery tombstones,
    including keys of writers whose old metadata lease can no longer commit.
    """
    if (
        not all(
            callable(c) for c in (subject_validator, hold_validator, in_use_validator)
        )
        or not isinstance(asset_uuid, UUID)
        or not isinstance(policy_uuid, UUID)
        or type(expected_version) is not int
        or expected_version < 1
        or not isinstance(at, datetime)
        or not timezone.is_aware(at)
        or transaction.get_connection().in_atomic_block
    ):
        return "denied"
    try:
        with transaction.atomic():
            status, asset, policy, keys = _current(
                asset_uuid,
                expected_version,
                policy_uuid,
                at,
                subject_validator,
                hold_validator,
                in_use_validator,
            )
            if status != "eligible":
                return status
            policy_version = policy.version
            if asset.state in {"abandoned", "revoked"}:
                asset.state, asset.version = "deletion_pending", asset.version + 1
                asset.save(update_fields=["state", "version", "updated_at"])
                AssetProcessingAttempt.objects.filter(
                    asset=asset, state__in=["pending", "running"]
                ).update(
                    state="failed",
                    lease_uuid=None,
                    lease_until=None,
                    failure_code="retention_due",
                    updated_at=at,
                )
                AssetDerivative.objects.filter(asset=asset).exclude(
                    state="deleted"
                ).update(state="revoked", version=F("version") + 1, updated_at=at)
            reserved_version = asset.version
        if store is None and settings.STORAGE_BACKEND == "fake":
            # A newly constructed memory adapter cannot erase an existing store.
            return "retry"
        store = store or get_private_store()
        for key in keys:
            with transaction.atomic():
                status, _, policy, current_keys = _current(
                    asset_uuid,
                    reserved_version,
                    policy_uuid,
                    at,
                    subject_validator,
                    hold_validator,
                    in_use_validator,
                )
                if status != "eligible":
                    return status
                if policy.version != policy_version or current_keys != keys:
                    return "conflict"
            try:
                store.delete(key)
            except FileNotFoundError:
                pass
            try:
                store.head(key)
            except FileNotFoundError:
                pass
            else:
                return "retry"
        with transaction.atomic():
            status, asset, policy, current_keys = _current(
                asset_uuid,
                reserved_version,
                policy_uuid,
                at,
                subject_validator,
                hold_validator,
                in_use_validator,
            )
            if status != "eligible":
                return status
            if policy.version != policy_version or current_keys != keys:
                return "conflict"
            if asset.state != "deleted":
                asset.state, asset.version = "deleted", asset.version + 1
                asset.save(update_fields=["state", "version", "updated_at"])
                AssetDerivative.objects.filter(asset=asset).exclude(
                    state="deleted"
                ).update(state="deleted", version=F("version") + 1, updated_at=at)
                append_event(
                    SecurityOutcome(
                        "asset.deleted",
                        "succeeded",
                        asset.id,
                        uuid4(),
                        ("state", "version"),
                        "retention_due",
                    ),
                    subject_type="asset",
                )
            return "deleted"
    except (PermissionError, ValueError):
        return "denied"
    except Exception:
        # The committed reservation is durable. Provider/audit failures leave a
        # bounded retry result; exception text, keys, URLs and bytes never escape.
        return "retry"


def cleanup_public_copy(
    identifier,
    generation,
    policy_uuid,
    at,
    *,
    subject_validator=None,
    hold_validator=None,
    publication_store=None,
):
    """Erase one inventoried generation after a committed owner-serialized reservation.

    Old generation keys remain tombstones. Repeating cleanup re-reserves before
    removing a late writer, allowing a hold committed after earlier erasure to win.
    """
    from .models import PublicAssetCopy, PublicCopyAttempt
    from .public_storage import get_publication_store, publication_key

    if (
        not isinstance(identifier, UUID)
        or not isinstance(policy_uuid, UUID)
        or type(generation) is not int
        or not 1 <= generation <= 8
        or not isinstance(at, datetime)
        or not timezone.is_aware(at)
        or not callable(subject_validator)
        or not callable(hold_validator)
        or transaction.get_connection().in_atomic_block
    ):
        return "denied"

    def current():
        now = max(at, timezone.now())
        hint = PublicAssetCopy.objects.filter(pk=identifier).first()
        if hint is None:
            return "denied", None
        owner = User.objects.select_for_update().get(pk=hint.owner_id)
        source = Asset.objects.select_related("owner").get(pk=hint.source_asset_id)
        source.owner = owner
        if subject_validator(source) is not True:
            return "denied", None
        source = Asset.objects.select_for_update().get(pk=source.id)
        source.owner = owner
        row = PublicAssetCopy.objects.select_for_update().get(pk=identifier)
        attempt = (
            PublicCopyAttempt.objects.select_for_update()
            .filter(
                copy=row,
                generation=generation,
            )
            .first()
        )
        if (
            source.owner_id != owner.pk
            or row.owner_id != owner.pk
            or attempt is None
            or generation > row.generation
            or attempt.key != publication_key(row.id, generation)
        ):
            return "denied", None
        inactive = row.state in {"failed", "revoked", "deletion_pending", "deleted"}
        if not inactive and generation == row.generation:
            return "in_use", None
        if attempt.state in {"running", "pending"}:
            return "in_use", None
        rule = _policy(source, policy_uuid, now)
        if rule is None:
            return "policy_required", None
        stopped = row.revoked_at if inactive else attempt.retired_at
        if stopped is None or (now - stopped).total_seconds() < rule.duration_seconds:
            return "not_due", None
        if hold_validator(source, now) is not False:
            return "held", None
        return "eligible", (row, attempt, rule, now)

    try:
        with transaction.atomic():
            status, values = current()
            if status != "eligible":
                return status
            row, attempt, rule, now = values
            if row.state in {"failed", "revoked", "deleted"}:
                row.state = "deletion_pending"
                row.version += 1
                row.updated_at = now
                row.save()
            attempt.state = "deletion_pending"
            attempt.lease_uuid = attempt.lease_until = None
            attempt.updated_at = now
            attempt.save()
            expected = (
                row.version,
                row.generation,
                attempt.id,
                attempt.key,
                rule.version,
            )
        with transaction.atomic():
            status, values = current()
            if status != "eligible":
                return status
            row, attempt, rule, now = values
            if (
                row.version,
                row.generation,
                attempt.id,
                attempt.key,
                rule.version,
            ) != expected:
                return "conflict"
            if attempt.state != "deletion_pending":
                return "conflict"
        if publication_store is None and settings.STORAGE_BACKEND == "fake":
            return "retry"
        store = publication_store or get_publication_store()
        try:
            store.delete(expected[3])
        except FileNotFoundError:
            pass
        try:
            store.head(expected[3])
        except FileNotFoundError:
            pass
        else:
            return "retry"
        with transaction.atomic():
            status, values = current()
            if status != "eligible":
                return status
            row, attempt, rule, now = values
            if (
                row.version,
                row.generation,
                attempt.id,
                attempt.key,
                rule.version,
            ) != expected:
                return "conflict"
            if attempt.state != "deletion_pending":
                return "conflict"
            first_erasure = attempt.deleted_at is None
            attempt.state = "deleted"
            attempt.deleted_at = attempt.deleted_at or now
            attempt.updated_at = now
            attempt.save()
            if (
                row.state == "deletion_pending"
                and not PublicCopyAttempt.objects.filter(copy=row)
                .exclude(state="deleted")
                .exists()
            ):
                row.state = "deleted"
                row.version += 1
                row.updated_at = now
                row.save()
            # Retained tombstones still erase late writes, while preserving
            # the first completed erasure and its single audit effect.
            if first_erasure:
                append_event(
                    SecurityOutcome(
                        "asset.deleted",
                        "succeeded",
                        attempt.id,
                        uuid4(),
                        ("state",),
                        "retention_due",
                    ),
                    subject_type="asset",
                )
        return "deleted"
    except (PermissionError, ValueError, LookupError):
        return "denied"
    except Exception:
        return "retry"
