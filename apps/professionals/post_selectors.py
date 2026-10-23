"""Exact confirmed immutable post source; no projection or media grants."""

from django.utils import timezone

from .post_contracts import PostImageInput, PostInput
from .post_models import EducationalPost
from .posts import ready_images


def stored_post(revision):
    return PostInput(
        revision.text,
        tuple(
            PostImageInput(b.asset_id, b.alt)
            for b in revision.images.order_by("position")
        ),
    )


def confirmed_post(user, identifier, revision_uuid, at, *, parent_source):
    """Caller holds User anchor; parent authorization is injected composition."""
    row = (
        EducationalPost.objects.select_for_update()
        .filter(
            pk=identifier,
            profile__user=user,
            state__in=["draft", "published"],
            withdrawn_at__isnull=True,
            hidden_at__isnull=True,
            hidden_case_uuid__isnull=True,
        )
        .first()
    )
    if row is None or revision_uuid not in {
        row.current_revision_id,
        row.requested_revision_id,
    }:
        return None
    revision = row.revisions.filter(pk=revision_uuid).first()
    now = max(at, timezone.now())
    if (
        revision is None
        or revision.confirmed_by_id != user.pk
        or revision.confirmed_at is None
        or revision.confirmed_at > now
    ):
        return None
    parent = parent_source(row.profile_id, now)
    if parent is None or parent.revision_uuid != revision.parent_revision_id:
        return None
    try:
        payload = stored_post(revision)
        payload.validate_publication()
        assets = ready_images(user, row, payload)
        if any(
            assets[b.asset_id].version != b.asset_version
            or assets[b.asset_id].processing_version != b.processing_version
            for b in revision.images.all()
        ):
            return None
    except (ValueError, LookupError):
        return None
    return row, revision, payload
