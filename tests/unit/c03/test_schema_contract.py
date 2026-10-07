"""C03 metadata cannot introduce publication or authoritative role JSON."""

from uuid import uuid4

import pytest
from django.apps import apps
from django.db import models

from apps.governance.outbox import validate_dispatch

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
