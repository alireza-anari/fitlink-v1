"""Owned finite inventory for derived C04 records; no new hold authority."""

from apps.assets.privacy import MAX_INVENTORY, InventoryRecord, bounded_rows
from apps.marketplace.models import (
    ProjectionRefreshState,
    PublicLocation,
    PublicProfessionalProjection,
)
from apps.professionals.models import ProfessionalProfile


def enumerate_marketplace_inventory(owner_uuid):
    identifiers = ProfessionalProfile.objects.filter(user__public_id=owner_uuid).values(
        "id"
    )
    result = []
    from apps.governance.moderation_models import (
        ModerationCase,
        ModerationHistory,
        PublicContentOperation,
        PublicContentReport,
    )

    for model, kind, owned in [
        (ModerationCase, "public_moderation_case", {"owner__public_id": owner_uuid}),
        (
            ModerationHistory,
            "public_moderation_history",
            {"actor__public_id": owner_uuid},
        ),
        (
            PublicContentReport,
            "public_content_report",
            {"reporter__public_id": owner_uuid},
        ),
        (
            PublicContentOperation,
            "public_content_operation",
            {"actor__public_id": owner_uuid},
        ),
    ]:
        for row in bounded_rows(model.objects.filter(**owned)):
            result.append(
                InventoryRecord(
                    kind,
                    row.id,
                    owner_uuid,
                    getattr(row, "version", getattr(row, "resulting_version", 1)),
                    "public_content_metadata",
                    classification="private_record",
                    deletion_behavior="retain_only",
                )
            )
    for model, kind in [
        (PublicProfessionalProjection, "public_projection"),
        (ProjectionRefreshState, "public_projection_refresh"),
    ]:
        for row in bounded_rows(model.objects.filter(profile_uuid__in=identifiers)):
            result.append(
                InventoryRecord(
                    kind,
                    row.profile_uuid,
                    owner_uuid,
                    row.generation,
                    "professional_profile",
                    getattr(row, "state", ""),
                    row.profile_uuid,
                    classification="derived_public_projection",
                    deletion_behavior="suppress_projection",
                )
            )
    for row in bounded_rows(
        PublicLocation.objects.filter(projection_id__in=identifiers)
    ):
        result.append(
            InventoryRecord(
                "public_projection_location",
                row.id,
                owner_uuid,
                1,
                "professional_profile",
                parent_uuid=row.projection_id,
                classification="derived_public_projection",
                deletion_behavior="suppress_projection",
            )
        )
    from apps.marketplace.selection_models import (
        ComparisonCollection,
        ComparisonEntry,
        ComparisonReceipt,
        Favorite,
        FavoriteReceipt,
    )

    # Account-owned private choices are separate from professional projections.
    # Visitor capabilities and target snapshots never enter an owner's inventory.
    for model, kind, owner_filter in [
        (Favorite, "favorite", {"owner__public_id": owner_uuid}),
        (FavoriteReceipt, "favorite_receipt", {"owner__public_id": owner_uuid}),
        (ComparisonCollection, "collection", {"owner__public_id": owner_uuid}),
        (ComparisonEntry, "entry", {"collection__owner__public_id": owner_uuid}),
        (
            ComparisonReceipt,
            "comparison_receipt",
            {"collection__owner__public_id": owner_uuid},
        ),
    ]:
        for row in bounded_rows(model.objects.filter(**owner_filter)):
            result.append(
                InventoryRecord(
                    "marketplace_selection_" + kind,
                    row.id,
                    owner_uuid,
                    getattr(row, "version", 1),
                    "account_selection",
                    parent_uuid=getattr(row, "collection_id", None),
                    classification="private_selection",
                    deletion_behavior="retain_only",
                )
            )
    if len(result) > MAX_INVENTORY:
        raise PermissionError("Inventory bound exceeded")
    return tuple(result)
