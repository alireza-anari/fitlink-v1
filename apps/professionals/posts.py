"""Current owned post commands; publication never follows from verification."""

from uuid import UUID

from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from apps.accounts.contracts import SecurityOutcome
from apps.accounts.sessions import locked_actor
from apps.assets.models import Asset

from .contracts import ProfileConflict, ProfileNotFound
from .policies import validate_context
from .post_contracts import PostDTO, PostInput
from .post_models import EducationalPost, PostHistory, PostImageBinding, PostRevision
from .publication import _callbacks, _disclosure, _enabled
from .publication_models import ProfessionalPublication
from .setup import locked_profile, receipt, remember, request_hash


def project_post(row, revision=None, version=None):
    return PostDTO(
        row.id,
        revision or row.requested_revision_id or row.current_revision_id,
        version or row.version,
        row.state,
    )


def _context(actor, post_uuid, version, operation_id, at):
    validate_context(actor, at)
    if (
        not isinstance(operation_id, UUID)
        or (post_uuid is not None and not isinstance(post_uuid, UUID))
        or (post_uuid is None and version is not None)
        or (post_uuid is not None and (type(version) is not int or version < 1))
    ):
        raise ValueError("Invalid post command")


def _owned(profile, identifier):
    row = (
        EducationalPost.objects.select_for_update()
        .filter(pk=identifier, profile=profile)
        .exclude(state__in=["archived", "deleted"])
        .first()
    )
    if row is None:
        raise ProfileNotFound("Post unavailable")
    return row


def ready_images(user, post, payload):
    """Exact source and successful isolated scan/decoder attestation are required."""
    selected = {}
    for image in sorted(payload.images, key=lambda i: i.asset_uuid):
        row = (
            Asset.objects.select_for_update()
            .filter(
                pk=image.asset_uuid,
                owner=user,
                subject_kind="educational_post",
                subject_uuid=post.id,
                purpose="educational_image",
                classification="private_source",
                state="ready",
                revoked_at__isnull=True,
            )
            .first()
        )
        if row is None:
            raise ProfileNotFound("Post image unavailable")
        attempt = (
            row.processing_attempts.filter(processing_version=row.processing_version)
            .order_by("-attempt")
            .first()
        )
        if (
            attempt is None
            or attempt.state != "ready"
            or attempt.algorithm_version != "jpeg-png-pixels-v1"
            or attempt.scanner_engine != "ClamAV 1.5.4"
            or not attempt.scanner_signature.isdecimal()
            or not row.derivatives.filter(
                processing_version=row.processing_version,
                purpose="post_preview",
                state="ready",
            ).exists()
        ):
            raise ProfileNotFound("Post image unavailable")
        selected[row.id] = row
    return selected


def _history(
    actor, user, row, revision, operation_id, action, digest, at, record, emit
):
    PostHistory.objects.create(
        post=row,
        revision=revision,
        actor=user,
        operation_id=operation_id,
        action=action,
        resulting_version=row.version,
        created_at=at,
        updated_at=at,
    )
    command = {
        "saved": "post.save",
        "confirmed": "post.publish",
        "withdrawn": "post.withdraw",
    }[action]
    remember(
        user,
        operation_id,
        command,
        digest,
        row.profile_id,
        revision.id if revision else None,
        row.version,
        at,
    )
    record(
        SecurityOutcome(
            "post." + action,
            "succeeded",
            row.id,
            operation_id,
            ("version", "state", "current_revision"),
            "user_requested",
        )
    )
    emit(row)


def save_post(
    actor,
    post_uuid,
    payload,
    expected_version,
    operation_id,
    at,
    *,
    record,
    emit,
    disclose,
):
    _context(actor, post_uuid, expected_version, operation_id, at)
    _callbacks(record, emit)
    if not isinstance(payload, PostInput):
        raise ValueError("Invalid post input")
    payload = PostInput.from_dict(payload.as_dict())
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_write", at)
        profile = locked_profile(user)
        disclosure = _disclosure(disclose)
        digest = request_hash(
            "post.save",
            {
                "post": post_uuid,
                "payload": payload.as_dict(),
                "version": expected_version,
            },
        )
        old = receipt(user, operation_id, "post.save", digest, profile.id)
        if old:
            revision = PostRevision.objects.select_related("post").get(
                pk=old.result_uuid, post__profile=profile
            )
            return project_post(revision.post, revision.id, old.resulting_version)
        if post_uuid is None:
            # Images can only be uploaded after the owned post identity exists.
            if payload.images:
                raise ValueError("Create a private draft before selecting images")
            row = EducationalPost.objects.create(
                profile=profile, created_at=at, updated_at=at
            )
        else:
            row = _owned(profile, post_uuid)
            if row.version != expected_version:
                raise ProfileConflict("Post version changed")
        assets = ready_images(user, row, payload)
        parent = (
            ProfessionalPublication.objects.select_for_update()
            .filter(profile=profile)
            .first()
        )
        sequence = (row.revisions.aggregate(value=Max("sequence"))["value"] or 0) + 1
        revision = PostRevision.objects.create(
            post=row,
            sequence=sequence,
            author=user,
            parent_revision_id=parent.current_revision_id if parent else None,
            text=payload.text,
            disclosure_version=disclosure.version,
            disclosure_hash=disclosure.digest,
            created_at=at,
            updated_at=at,
        )
        PostImageBinding.objects.bulk_create(
            [
                PostImageBinding(
                    revision=revision,
                    asset=assets[image.asset_uuid],
                    position=index,
                    alt=image.alt,
                    asset_version=assets[image.asset_uuid].version,
                    processing_version=assets[image.asset_uuid].processing_version,
                    created_at=at,
                    updated_at=at,
                )
                for index, image in enumerate(payload.images, 1)
            ]
        )
        row.current_revision = None
        row.requested_revision = revision
        row.state = "hidden" if row.hidden_at else "draft"
        row.withdrawn_at = None
        if post_uuid is not None:
            row.version += 1
        row.updated_at = at
        row.save(
            update_fields=[
                "current_revision",
                "requested_revision",
                "state",
                "withdrawn_at",
                "version",
                "updated_at",
            ]
        )
        _history(
            actor, user, row, revision, operation_id, "saved", digest, at, record, emit
        )
        return project_post(row)


def publish_post(
    actor,
    post_uuid,
    confirmed,
    expected_version,
    operation_id,
    at,
    *,
    record,
    emit,
    enabled,
    disclose,
    parent_source,
):
    _context(actor, post_uuid, expected_version, operation_id, at)
    _callbacks(record, emit)
    if confirmed is not True or not callable(parent_source):
        raise ValueError("Exact post confirmation required")
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_write", at)
        profile = locked_profile(user)
        row = _owned(profile, post_uuid)
        _enabled(enabled)
        disclosure = _disclosure(disclose)
        digest = request_hash(
            "post.publish",
            {"post": post_uuid, "version": expected_version, "confirmed": True},
        )
        old = receipt(user, operation_id, "post.publish", digest, profile.id)
        if old:
            return project_post(row, old.result_uuid, old.resulting_version)
        if (
            row.version != expected_version
            or row.requested_revision_id is None
            or row.withdrawn_at is not None
            or row.hidden_at is not None
        ):
            raise ProfileConflict("Post publication changed")
        revision = PostRevision.objects.select_for_update().get(
            pk=row.requested_revision_id, post=row
        )
        if revision.confirmed_at is not None or (
            revision.disclosure_version,
            revision.disclosure_hash,
        ) != (disclosure.version, disclosure.digest):
            raise ProfileConflict("Post confirmation changed")
        source = parent_source(profile.id, max(at, timezone.now()))
        if source is None or source.revision_uuid != revision.parent_revision_id:
            raise ProfileConflict("Parent publication unavailable")
        from .post_selectors import stored_post

        payload = stored_post(revision)
        payload.validate_publication()
        selected = ready_images(user, row, payload)
        if any(
            selected[b.asset_id].version != b.asset_version
            or selected[b.asset_id].processing_version != b.processing_version
            for b in revision.images.all()
        ):
            raise ProfileConflict("Post image version changed")
        revision.confirmed_at = max(at, timezone.now())
        revision.confirmed_by = user
        revision.save(update_fields=["confirmed_at", "confirmed_by"])
        row.version += 1
        row.updated_at = max(at, timezone.now())
        row.save(update_fields=["version", "updated_at"])
        _history(
            actor,
            user,
            row,
            revision,
            operation_id,
            "confirmed",
            digest,
            row.updated_at,
            record,
            emit,
        )
        return project_post(row)


def withdraw_post(
    actor, post_uuid, expected_version, operation_id, at, *, record, emit
):
    _context(actor, post_uuid, expected_version, operation_id, at)
    _callbacks(record, emit)
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_write", at)
        profile = locked_profile(user)
        row = _owned(profile, post_uuid)
        digest = request_hash(
            "post.withdraw", {"post": post_uuid, "version": expected_version}
        )
        old = receipt(user, operation_id, "post.withdraw", digest, profile.id)
        if old:
            return project_post(row, old.result_uuid, old.resulting_version)
        if row.version != expected_version:
            raise ProfileConflict("Post version changed")
        revision = row.requested_revision or row.current_revision
        row.current_revision = row.requested_revision = None
        row.state = "hidden" if row.hidden_at else "draft"
        row.withdrawn_at = at
        row.version += 1
        row.updated_at = at
        row.save(
            update_fields=[
                "current_revision",
                "requested_revision",
                "state",
                "withdrawn_at",
                "version",
                "updated_at",
            ]
        )
        _history(
            actor,
            user,
            row,
            revision,
            operation_id,
            "withdrawn",
            digest,
            at,
            record,
            emit,
        )
        return project_post(row)
