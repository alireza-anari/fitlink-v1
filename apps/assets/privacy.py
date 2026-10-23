"""Bounded C03 metadata inventory. No object keys or read authority are exported."""

from dataclasses import dataclass
from uuid import UUID

from .models import (
    Asset,
    AssetDerivative,
    AssetProcessingAttempt,
    PublicAssetCopy,
    PublicCopyAttempt,
)

MAX_INVENTORY = 1000


@dataclass(frozen=True)
class InventoryRecord:
    kind: str
    record_uuid: UUID
    owner_uuid: UUID
    version: int
    data_class: str
    state: str = ""
    parent_uuid: UUID | None = None
    asset_uuids: tuple[UUID, ...] = ()
    classification: str = "private_record"
    policy_uuid: UUID | None = None
    deletion_behavior: str = "retain_only"


@dataclass(frozen=True)
class OwnerInventory:
    owner_uuid: UUID
    records: tuple[InventoryRecord, ...]


def bounded_rows(query):
    rows = list(query.order_by("pk")[: MAX_INVENTORY + 1])
    if len(rows) > MAX_INVENTORY:
        raise PermissionError("Inventory bound exceeded")
    return rows


def asset_data_class(asset):
    if asset.accepted_at is None:
        return "asset_quarantine"
    return (
        "credential_source"
        if asset.purpose in {"identity_evidence", "credential_evidence"}
        else "profile_media"
    )


def enumerate_asset_inventory(owner_uuid, at):
    from apps.governance.privacy_models import RetentionPolicy

    policies = {
        (p.data_class, p.purpose): p.id
        for p in bounded_rows(
            RetentionPolicy.objects.filter(
                status="effective",
                effective_at__lte=at,
                approved_at__lte=at,
                approved_by__isnull=False,
                duration_seconds__gt=0,
            )
            .exclude(backup_reference="")
            .filter(
                data_class__in=[
                    "asset_quarantine",
                    "profile_media",
                    "credential_source",
                ],
                purpose__in=[
                    "avatar",
                    "cover",
                    "logo",
                    "educational_image",
                    "identity_evidence",
                    "credential_evidence",
                ],
            )
        )
    }
    records = []
    for asset in bounded_rows(Asset.objects.filter(owner__public_id=owner_uuid)):
        records.append(
            InventoryRecord(
                "profile_asset",
                asset.id,
                owner_uuid,
                asset.version,
                asset_data_class(asset),
                asset.state,
                asset.subject_uuid,
                classification=asset.classification,
                policy_uuid=policies.get((asset_data_class(asset), asset.purpose)),
                deletion_behavior="policy_cleanup",
            )
        )
    for row in bounded_rows(
        AssetDerivative.objects.filter(asset__owner__public_id=owner_uuid)
    ):
        records.append(
            InventoryRecord(
                "asset_derivative",
                row.id,
                owner_uuid,
                row.version,
                asset_data_class(row.asset),
                row.state,
                row.asset_id,
                classification="private_derivative",
                policy_uuid=policies.get(
                    (asset_data_class(row.asset), row.asset.purpose)
                ),
                deletion_behavior="source_cleanup",
            )
        )
    for row in bounded_rows(
        AssetProcessingAttempt.objects.filter(asset__owner__public_id=owner_uuid)
    ):
        records.append(
            InventoryRecord(
                "asset_processing",
                row.id,
                owner_uuid,
                1,
                "asset_quarantine",
                row.state,
                row.asset_id,
            )
        )
    for copy in bounded_rows(
        PublicAssetCopy.objects.filter(owner__public_id=owner_uuid)
    ):
        records.append(
            InventoryRecord(
                "public_asset_copy",
                copy.id,
                owner_uuid,
                copy.version,
                "profile_media",
                copy.state,
                copy.source_asset_id,
                classification="private_publication_copy",
                policy_uuid=policies.get(("profile_media", copy.purpose)),
                deletion_behavior="policy_cleanup",
            )
        )
    for attempt in bounded_rows(
        PublicCopyAttempt.objects.filter(copy__owner__public_id=owner_uuid)
    ):
        records.append(
            InventoryRecord(
                "public_copy_attempt",
                attempt.id,
                owner_uuid,
                attempt.generation,
                "profile_media",
                attempt.state,
                attempt.copy_id,
                classification="private_publication_copy",
                policy_uuid=policies.get(("profile_media", attempt.copy.purpose)),
                deletion_behavior="source_cleanup",
            )
        )
    if len(records) > MAX_INVENTORY:
        raise PermissionError("Inventory bound exceeded")
    return tuple(records)
