"""Explicit bounded C02 effects only; no provider or privacy execution hooks."""

from types import MappingProxyType

from apps.accounts.models import User
from apps.accounts.security_models import AccountSessionControl
from apps.governance.consent_models import Consent
from apps.governance.flag_models import FeatureFlag
from apps.governance.privacy_models import PrivacyRequest
from config.c03_event_handlers import (
    athlete_baseline_metadata,
    professional_profile_metadata,
    request_processing,
    verification_metadata,
)


def account_security(event, at):
    user = User.objects.filter(public_id=event.aggregate_uuid).first()
    if not user or user.auth_version != event.aggregate_version:
        return "skipped"
    AccountSessionControl.objects.filter(
        user=user, auth_version__lt=user.auth_version, revoked_at__isnull=True
    ).update(revoked_at=at)
    return "applied"


def consent_metadata(event, at):
    row = Consent.objects.filter(
        pk=event.aggregate_uuid,
        version=event.aggregate_version,
        subject__public_id=event.payload["user_uuid"],
    ).first()
    if not row or (event.event_type == "consent.revoked") != (
        row.revoked_at is not None
    ):
        return "skipped"
    return "applied"


def privacy_metadata(event, at):
    row = PrivacyRequest.objects.filter(
        pk=event.aggregate_uuid,
        version=event.aggregate_version,
        user__public_id=event.payload["user_uuid"],
    ).first()
    return "applied" if row else "skipped"


def flag_metadata(event, at):
    return (
        "applied"
        if FeatureFlag.objects.filter(
            pk=event.aggregate_uuid, version=event.aggregate_version
        ).exists()
        else "skipped"
    )


HANDLERS = MappingProxyType(
    {
        "account.security_changed": account_security,
        "consent.granted": consent_metadata,
        "consent.revoked": consent_metadata,
        "privacy.intake_recorded": privacy_metadata,
        "feature_flag.changed": flag_metadata,
        "professional.profile_changed": professional_profile_metadata,
        "athlete.baseline_changed": athlete_baseline_metadata,
        "asset.processing_requested": request_processing,
        "verification.changed": verification_metadata,
    }
)
