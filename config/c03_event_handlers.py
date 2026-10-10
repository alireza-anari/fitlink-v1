"""Installed metadata receipts only; no publication or external side effects."""

from apps.professionals.models import ProfessionalProfile
from config.use_cases.asset_processing import request_processing as request_processing


def professional_profile_metadata(event, at):
    return (
        "applied"
        if ProfessionalProfile.objects.filter(
            pk=event.aggregate_uuid,
            version=event.aggregate_version,
            user__public_id=event.payload["user_uuid"],
        ).exists()
        else "skipped"
    )


def athlete_baseline_metadata(event, at):
    from apps.athletes.baseline_models import BaselineAssessment

    return (
        "applied"
        if BaselineAssessment.objects.filter(
            pk=event.aggregate_uuid,
            version=event.aggregate_version,
            athlete__user__public_id=event.payload["user_uuid"],
        ).exists()
        else "skipped"
    )


def verification_metadata(event, at):
    from apps.professionals.models import Verification

    return (
        "applied"
        if Verification.objects.filter(
            pk=event.aggregate_uuid,
            version=event.aggregate_version,
            profile__user__public_id=event.payload["user_uuid"],
        ).exists()
        else "skipped"
    )


def cleanup_metadata(event, at):
    from apps.assets.models import Asset

    return (
        "applied"
        if Asset.objects.filter(
            pk=event.aggregate_uuid,
            version=event.aggregate_version,
            owner__public_id=event.payload["user_uuid"],
            state__in=["abandoned", "revoked", "deletion_pending", "deleted"],
        ).exists()
        else "skipped"
    )
