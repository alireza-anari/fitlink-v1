"""Installed publication metadata receipt; no projection/publication side effect."""

from apps.professionals.publication_models import ProfessionalPublication


def with_projection_due(handler):
    """Preserve inherited effects/results; persist only ID-based due metadata."""

    def composed(event, at):
        result = handler(event, at)
        from apps.professionals.models import ProfessionalProfile
        from config.use_cases.marketplace import mark_profile_due

        owner_uuid = event.payload.get("user_uuid")
        if owner_uuid is not None:
            identifier = (
                ProfessionalProfile.objects.filter(user__public_id=owner_uuid)
                .values_list("id", flat=True)
                .first()
            )
            if identifier is not None:
                mark_profile_due(identifier, at)
        # Flag events have no owner: the independent durable source scan keeps
        # purging with the flag off, without an unbounded outbox transaction.
        return result

    return composed


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
