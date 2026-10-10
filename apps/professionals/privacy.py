"""Explicit inventory of installed private professional records only."""

from apps.assets.privacy import MAX_INVENTORY, InventoryRecord, bounded_rows

from .models import (
    AssistantMembership,
    Credential,
    CredentialRevision,
    ProfessionalLocation,
    ProfessionalProfile,
    ProfessionalRole,
    ProfessionalRoleRestriction,
    ProfileCommandReceipt,
    RoleRestrictionHistory,
    Verification,
    VerificationAssignment,
    VerificationDecision,
    VerificationEvidence,
    VerificationHistory,
    VerificationTarget,
)


def enumerate_professional_inventory(owner_uuid):
    records = []
    # This fixed installed set is internal lifetime metadata, not a subject registry.
    queries = (
        (
            ProfessionalProfile.objects.filter(user__public_id=owner_uuid),
            "professional_profile",
            "profile",
            None,
        ),
        (
            ProfessionalRole.objects.filter(profile__user__public_id=owner_uuid),
            "professional_role",
            "profile",
            "profile_id",
        ),
        (
            ProfessionalLocation.objects.filter(profile__user__public_id=owner_uuid),
            "professional_location",
            "profile",
            "profile_id",
        ),
        (
            Credential.objects.filter(profile__user__public_id=owner_uuid),
            "professional_credential",
            "credential_source",
            "profile_id",
        ),
        (
            CredentialRevision.objects.filter(
                credential__profile__user__public_id=owner_uuid
            ),
            "credential_revision",
            "credential_source",
            "credential_id",
        ),
        (
            Verification.objects.filter(profile__user__public_id=owner_uuid),
            "professional_verification",
            "verification",
            "profile_id",
        ),
        (
            VerificationTarget.objects.filter(
                verification__profile__user__public_id=owner_uuid
            ),
            "verification_target",
            "verification",
            "verification_id",
        ),
        (
            VerificationEvidence.objects.filter(
                target__verification__profile__user__public_id=owner_uuid
            ),
            "verification_evidence",
            "verification",
            "target_id",
        ),
        (
            VerificationAssignment.objects.filter(
                verification__profile__user__public_id=owner_uuid
            ),
            "verification_assignment",
            "verification",
            "verification_id",
        ),
        (
            VerificationDecision.objects.filter(profile__user__public_id=owner_uuid),
            "verification_decision",
            "verification",
            "target_id",
        ),
        (
            VerificationHistory.objects.filter(
                verification__profile__user__public_id=owner_uuid
            ),
            "verification_history",
            "verification",
            "verification_id",
        ),
        (
            ProfessionalRoleRestriction.objects.filter(
                role__profile__user__public_id=owner_uuid
            ),
            "professional_restriction",
            "verification",
            "role_id",
        ),
        (
            RoleRestrictionHistory.objects.filter(
                restriction__role__profile__user__public_id=owner_uuid
            ),
            "restriction_history",
            "verification",
            "restriction_id",
        ),
        (
            AssistantMembership.objects.filter(profile__user__public_id=owner_uuid),
            "assistant_membership",
            "profile",
            "profile_id",
        ),
        (
            ProfileCommandReceipt.objects.filter(owner__public_id=owner_uuid),
            "professional_receipt",
            "command_receipt",
            None,
        ),
    )
    for query, kind, data_class, parent in queries:
        for row in bounded_rows(query):
            assets = ()
            if isinstance(row, CredentialRevision):
                if row.source_asset.owner.public_id != owner_uuid:
                    raise PermissionError("Inventory subject denied")
                assets = (row.source_asset_id,)
            if isinstance(row, VerificationEvidence):
                revision = row.credential_revision
                if (
                    revision.credential.profile_id != row.target.verification.profile_id
                    or revision.source_asset.owner.public_id != owner_uuid
                ):
                    raise PermissionError("Inventory subject denied")
                assets = (revision.source_asset_id,)
            records.append(
                InventoryRecord(
                    kind,
                    row.pk,
                    owner_uuid,
                    getattr(row, "version", getattr(row, "resulting_version", 1)),
                    data_class,
                    getattr(row, "state", ""),
                    getattr(row, parent) if parent else None,
                    assets,
                )
            )
            if len(records) > MAX_INVENTORY:
                raise PermissionError("Inventory bound exceeded")
    return tuple(records)
