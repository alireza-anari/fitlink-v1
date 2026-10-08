"""Installed metadata receipts only; no publication or external side effects."""

from apps.professionals.models import ProfessionalProfile


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
