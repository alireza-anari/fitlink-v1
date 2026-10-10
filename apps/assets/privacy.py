"""Bounded C03 metadata inventory. No object keys or read authority are exported."""

from dataclasses import dataclass
from uuid import UUID

from .models import Asset, AssetDerivative, AssetProcessingAttempt

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


def enumerate_asset_inventory(owner_uuid):
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
                "private_derivative",
                row.state,
                row.asset_id,
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
                "asset_processing",
                row.state,
                row.asset_id,
            )
        )
    if len(records) > MAX_INVENTORY:
        raise PermissionError("Inventory bound exceeded")
    return tuple(records)
