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
            "professional_profile",
            None,
        ),
        (
            ProfessionalRole.objects.filter(profile__user__public_id=owner_uuid),
            "professional_role",
            "professional_profile",
            "profile_id",
        ),
        (
            ProfessionalLocation.objects.filter(profile__user__public_id=owner_uuid),
            "professional_location",
            "professional_profile",
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
            "credential_revision",
            "credential_id",
        ),
        (
            Verification.objects.filter(profile__user__public_id=owner_uuid),
            "professional_verification",
            "verification_history",
            "profile_id",
        ),
        (
            VerificationTarget.objects.filter(
                verification__profile__user__public_id=owner_uuid
            ),
            "verification_target",
            "verification_history",
            "verification_id",
        ),
        (
            VerificationEvidence.objects.filter(
                target__verification__profile__user__public_id=owner_uuid
            ),
            "verification_evidence",
            "verification_evidence",
            "target_id",
        ),
        (
            VerificationAssignment.objects.filter(
                verification__profile__user__public_id=owner_uuid
            ),
            "verification_assignment",
            "verification_history",
            "verification_id",
        ),
        (
            VerificationDecision.objects.filter(profile__user__public_id=owner_uuid),
            "verification_decision",
            "verification_history",
            "target_id",
        ),
        (
            VerificationHistory.objects.filter(
                verification__profile__user__public_id=owner_uuid
            ),
            "verification_history",
            "verification_history",
            "verification_id",
        ),
        (
            ProfessionalRoleRestriction.objects.filter(
                role__profile__user__public_id=owner_uuid
            ),
            "professional_restriction",
            "verification_history",
            "role_id",
        ),
        (
            RoleRestrictionHistory.objects.filter(
                restriction__role__profile__user__public_id=owner_uuid
            ),
            "restriction_history",
            "verification_history",
            "restriction_id",
        ),
        (
            AssistantMembership.objects.filter(profile__user__public_id=owner_uuid),
            "assistant_membership",
            "professional_profile",
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
            if isinstance(row, Credential) and (
                row.role_id is not None
                and row.role.profile_id != row.profile_id
                or row.current_revision_id is not None
                and row.current_revision.credential_id != row.id
            ):
                raise PermissionError("Inventory subject denied")
            if isinstance(row, CredentialRevision):
                if not revision_asset_valid(row):
                    raise PermissionError("Inventory subject denied")
                assets = (row.source_asset_id,)
            if isinstance(row, VerificationEvidence):
                revision = row.credential_revision
                if (
                    revision.credential.profile_id != row.target.verification.profile_id
                    or not revision_asset_valid(revision)
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


def revision_asset_valid(revision):
    asset = revision.source_asset
    credential = revision.credential
    return (
        asset.owner_id == credential.profile.user_id
        and asset.classification == "private_source"
        and asset.purpose
        == (
            "identity_evidence"
            if revision.category == "identity"
            else "credential_evidence"
        )
        and (
            (
                asset.subject_kind == "professional_profile"
                and asset.subject_uuid == credential.profile_id
            )
            or (
                asset.subject_kind == "professional_credential"
                and asset.subject_uuid == credential.id
            )
        )
    )


def case_asset_inventory(case_uuid, owner_uuid, credential_uuid=None):
    """Immutable submitted evidence is the hold's exact source inventory."""
    evidence = VerificationEvidence.objects.filter(
        target__verification_id=case_uuid,
        target__verification__profile__user__public_id=owner_uuid,
    )
    assets = []
    for row in bounded_rows(
        evidence.select_related(
            "target__verification",
            "credential_revision__credential__profile",
            "credential_revision__source_asset",
        )
    ):
        revision = row.credential_revision
        credential = revision.credential
        if (
            credential.profile_id != row.target.verification.profile_id
            or row.category != revision.category
            or (row.target.target == "identity") != (revision.category == "identity")
            or credential.role_id != row.target.role_id
            or not revision_asset_valid(revision)
        ):
            raise PermissionError("Inventory subject denied")
        if credential_uuid is None or credential.id == credential_uuid:
            assets.append(revision.source_asset_id)
    return tuple(sorted(set(assets)))
