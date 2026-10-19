"""Installed publication metadata receipt; no projection/publication side effect."""

from apps.professionals.publication_models import ProfessionalPublication


def professional_publication_metadata(event, at):
    return (
        "applied"
        if ProfessionalPublication.objects.filter(
            pk=event.aggregate_uuid,
            version=event.aggregate_version,
            profile__user__public_id=event.payload["user_uuid"],
        ).exists()
        else "skipped"
    )
