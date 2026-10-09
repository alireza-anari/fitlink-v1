import pytest
from django.apps import apps
from django.conf import settings
from django.urls import get_resolver

pytestmark = pytest.mark.unit


def test_only_foundation_routes_and_identity_model():
    assert {str(route.pattern) for route in get_resolver().url_patterns} == {
        "",
        "i/<str:token>/",
        "health/live/",
        "health/ready/",
        "api/v1/status/",
        # Exactly the Task14 approved adapters; no generic CRUD/future routes.
        "accounts/entry/",
        "accounts/verify/",
        "accounts/me/",
        "accounts/phone-change/",
        "accounts/recovery/",
        "privacy/requests/",
        "staff/recovery/<uuid:request_uuid>/",
        "api/v1/auth/otp/request/",
        "api/v1/auth/otp/verify/",
        "api/v1/auth/logout/",
        "api/v1/auth/logout-all/",
        "api/v1/account/me/",
        "api/v1/account/phone-change/",
        "api/v1/account/phone-change/proof/request/",
        "api/v1/account/phone-change/proof/verify/",
        "api/v1/account/phone-change/apply/",
        "api/v1/recovery/requests/",
        "api/v1/recovery/requests/<uuid:request_uuid>/status/",
        "api/v1/recovery/requests/<uuid:request_uuid>/new-phone/request/",
        "api/v1/recovery/requests/<uuid:request_uuid>/new-phone/verify/",
        "api/v1/staff/recovery/<uuid:request_uuid>/",
        "api/v1/staff/recovery/<uuid:request_uuid>/evidence/",
        "api/v1/staff/recovery/<uuid:request_uuid>/decision/",
        "api/v1/staff/recovery/<uuid:request_uuid>/apply/",
        "api/v1/privacy/requests/",
        "api/v1/privacy/requests/<uuid:request_uuid>/",
        # Exactly the Task 4 private POST adapters; no content/download route.
        "api/v1/profile-assets/begin/",
        "api/v1/profile-assets/<uuid:asset_uuid>/body/",
        "api/v1/profile-assets/<uuid:asset_uuid>/finalize/",
        "api/v1/profile-assets/<uuid:asset_uuid>/abandon/",
    }
    assert settings.AUTH_USER_MODEL == "accounts.User"
    assert "django.contrib.admin" not in settings.INSTALLED_APPS
    own_models = {
        model.__name__
        for model in apps.get_models()
        if model.__module__.startswith("apps.")
    }
    c02_models = {
        "User",
        "OTPPhoneState",
        "SecurityRateAnchor",
        "SecurityRateEvent",
        "OTPChallenge",
        "AccountSessionControl",
        "AuditEvent",
        "OutboxEvent",
        "OutboxDeliveryReceipt",
        "StaffCapabilityGrant",
        "StaffStepUpGrant",
        "RecoveryRequest",
        "RecoveryEvidenceMetadata",
        "PhoneChangeHistory",
        "PhoneChangeIntent",
        "Consent",
        "ConsentScope",
        "FeatureFlag",
        "InviteReferralLink",
        "ReferralAttribution",
        "PrivacyRequest",
        "RetentionPolicy",
        "RecordHold",
    }
    c03_models = {
        "AthleteProfile",
        "BaselineAssessment",
        "ProfileCommandReceipt",
        "Asset",
        "AssetDerivative",
        "AssetProcessingAttempt",
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
    }
    # C03 may add only its approved profile/asset/verification models.
    assert own_models == c02_models | c03_models
    user = apps.get_model("accounts", "User")
    assert {field.name for field in user._meta.get_fields()} == {
        "id",
        "password",
        "last_login",
        "is_superuser",
        "groups",
        "user_permissions",
        "public_id",
        "phone",
        "is_active",
        "is_staff",
        "date_joined",
        "birth_date",
        "adult_attested_at",
        "adult_attestation_version",
        "locale",
        "timezone",
        "state",
        "state_version",
        "auth_version",
        "otpchallenge",
        "accountsessioncontrol",
        "staff_capabilities",
        "issued_staff_capabilities",
        "staff_step_ups",
        "issued_staff_step_ups",
        "recovery_targets",
        "assigned_recoveries",
        "recovery_decisions",
        "recovery_evidence_reviews",
        "phone_history",
        "phone_change_intents",
        # Exact reverse relations introduced by the approved C03 schema.
        "athlete_profile",
        "athlete_profile_receipts",
        "private_assets",
        "professional_profile",
        "professional_verification_assignments",
        "issued_professional_verification_assignments",
        "professional_verification_decisions",
        "professional_verification_history",
        "applied_role_restrictions",
        "released_role_restrictions",
        "role_restriction_history",
        "assistant_definitions",
        "professional_profile_receipts",
    }
