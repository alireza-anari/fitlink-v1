"""C03 metadata cannot introduce publication or authoritative role JSON."""

from uuid import uuid4

import pytest
from django.apps import apps
from django.db import models

from apps.governance.audit_models import ACTIONS, CHANGED_FIELDS, REASONS, SUBJECT_TYPES
from apps.governance.consent_models import PURPOSES
from apps.governance.outbox import validate_dispatch
from apps.governance.privacy_models import RecordHold

pytestmark = pytest.mark.unit
EXPECTED = {
    "athletes": {"AthleteProfile", "BaselineAssessment", "ProfileCommandReceipt"},
    "professionals": {
        "ProfessionalProfile",
        "ProfessionalRole",
        "ProfessionalLocation",
        "Credential",
        "CredentialRevision",
        "Verification",
        "VerificationTarget",
        "VerificationEvidence",
        "VerificationAssignment",
        "VerificationDecision",
        "VerificationHistory",
        "ProfessionalRoleRestriction",
        "RoleRestrictionHistory",
        "AssistantMembership",
        "ProfileCommandReceipt",
    },
    "assets": {"Asset", "AssetDerivative", "AssetProcessingAttempt"},
}


def test_private_relational_schema_registered_without_future_models():
    for label, names in EXPECTED.items():
        installed = {
            m.__name__ for m in apps.get_models() if m._meta.app_label == label
        }
        assert installed == names, f"Missing bounded {label} metadata"
        for name in names:
            model = apps.get_model(label, name)
            assert isinstance(model._meta.pk, models.UUIDField)
            for field in model._meta.local_fields:
                assert field.name not in {
                    "slug",
                    "is_public",
                    "is_verified",
                    "approved_roles",
                    "requested_roles",
                    "identity_approved",
                    "latitude",
                    "longitude",
                    "injuries",
                    "medications",
                }
                if isinstance(field, models.ForeignKey):
                    assert field.remote_field.on_delete is models.PROTECT


def test_c03_governance_allowlists_are_bounded_and_installed():
    assert {
        "athlete.profile_created",
        "baseline.saved",
        "baseline.submitted",
        "baseline.corrected",
        "baseline.cleared",
        "professional.profile_created",
        "professional.profile_saved",
        "professional.roles_changed",
        "credential.created",
        "credential.revised",
        "credential.withdrawn",
        "asset.begun",
        "asset.uploaded",
        "asset.finalized",
        "asset.read",
        "asset.rejected",
        "asset.revoked",
        "asset.deleted",
        "verification.submitted",
        "verification.assigned",
        "verification.review_started",
        "verification.read",
        "verification.approved",
        "verification.rejected",
        "verification.stale",
        "verification.withdrawn",
        "verification.revoked",
        "professional.role_restricted",
        "professional.role_released",
        "assistant.defined",
        "assistant.revoked",
    } <= set(ACTIONS)
    assert {
        "verification_submitted",
        "verification_review",
        "credentials_approved",
        "evidence_incomplete",
        "credentials_invalid",
        "evidence_expired",
        "evidence_revoked",
        "role_restricted",
        "restriction_removed",
        "material_changed",
        "owner_withdrawn",
        "upload_invalid",
        "scan_failed",
        "retention_due",
    } <= set(REASONS)
    assert {
        "athlete",
        "baseline",
        "professional",
        "credential",
        "asset",
        "verification",
        "assistant",
    } <= set(SUBJECT_TYPES)
    assert {
        "onboarding_step",
        "current_baseline",
        "setup_step",
        "declared_active",
        "declaration_version",
        "evidence_revision",
        "decision_version",
        "current_revision",
        "processing_version",
        "withdrawn_at",
        "released_at",
    } <= CHANGED_FIELDS
    assert "baseline_storage" in PURPOSES
    constraint = next(
        item
        for item in RecordHold._meta.constraints
        if item.name == "hold_subject_kind"
    )
    assert constraint.condition == models.Q(
        subject_kind__in=[
            "privacy_request",
            "athlete_baseline",
            "professional_credential",
            "professional_verification",
            "profile_asset",
        ]
    )


@pytest.mark.parametrize(
    "kind,key",
    [
        ("athlete.baseline_changed", "baseline_uuid"),
        ("professional.profile_changed", "profile_uuid"),
        ("verification.changed", "verification_uuid"),
        ("asset.processing_requested", "asset_uuid"),
        ("asset.cleanup_requested", "asset_uuid"),
        ("assistant.membership_changed", "membership_uuid"),
    ],
)
def test_c03_events_accept_exact_uuid_envelopes_and_deny_private_values(kind, key):
    aggregate, owner = uuid4(), uuid4()
    payload = {key: str(aggregate), "user_uuid": str(owner)}
    validate_dispatch(kind, 1, aggregate, 1, payload)
    for bad in (
        {**payload, "document": "PRIVATE"},
        {**payload, key: "https://private"},
        {key: str(aggregate)},
        {**payload, key: str(uuid4())},
    ):
        with pytest.raises(ValueError):
            validate_dispatch(kind, 1, aggregate, 1, bad)
