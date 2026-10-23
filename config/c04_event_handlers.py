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
        elif getattr(event, "event_type", None) == "feature_flag.changed":
            from apps.governance.flag_models import FeatureFlag
            from config.use_cases.marketplace import mark_publications_due

            if FeatureFlag.objects.filter(
                pk=event.aggregate_uuid, key="marketplace"
            ).exists():
                mark_publications_due(at)
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


def professional_post_metadata(event, at):
    from apps.professionals.post_models import EducationalPost

    return (
        "applied"
        if EducationalPost.objects.filter(
            pk=event.aggregate_uuid,
            version=event.aggregate_version,
            profile__user__public_id=event.payload["user_uuid"],
        ).exists()
        else "skipped"
    )


def public_moderation_metadata(event, at):
    from apps.governance.moderation_models import ModerationCase

    return (
        "applied"
        if ModerationCase.objects.filter(
            pk=event.aggregate_uuid,
            version=event.aggregate_version,
            owner__public_id=event.payload["user_uuid"],
        ).exists()
        else "skipped"
    )
