"""Explicit profile/post callbacks; governance cannot import feature domains."""

from django.db import transaction

from apps.accounts.models import User
from apps.governance.moderation_models import ModerationCase
from apps.professionals.models import ProfessionalProfile, ProfessionalPublication
from apps.professionals.post_models import EducationalPost


def lock_target(actor, target):
    owners = (
        ProfessionalProfile.objects.filter(pk=target.object_uuid).values_list(
            "user_id", flat=True
        )
        if target.kind == "profile"
        else EducationalPost.objects.filter(pk=target.object_uuid).values_list(
            "profile__user_id", flat=True
        )
    )
    ids = list(owners) + list(
        User.objects.filter(public_id=actor.user_uuid).values_list("pk", flat=True)
    )
    list(User.objects.select_for_update().filter(pk__in=ids).order_by("pk"))


def lock_case(actor, identifier):
    owner = (
        ModerationCase.objects.filter(pk=identifier)
        .values_list("owner_id", flat=True)
        .first()
    )
    ids = list(
        User.objects.filter(public_id=actor.user_uuid).values_list("pk", flat=True)
    )
    if owner is not None:
        ids.append(owner)
    list(User.objects.select_for_update().filter(pk__in=ids).order_by("pk"))


def target_source(target, at):
    if target.kind == "profile":
        from config.use_cases.marketplace import current_source

        value = current_source(target.object_uuid, at)
        owner = (
            ProfessionalProfile.objects.filter(pk=target.object_uuid)
            .values_list("user_id", flat=True)
            .first()
        )
    else:
        from config.use_cases.public_content import public_post

        value = public_post(target.object_uuid, at)
        owner = (
            EducationalPost.objects.filter(pk=target.object_uuid)
            .values_list("profile__user_id", flat=True)
            .first()
        )
    return (
        (owner, value.revision_uuid)
        if value is not None and owner is not None
        else None
    )


def apply_decision(case, action, at):
    if not transaction.get_connection().in_atomic_block:
        raise PermissionError("Moderation transaction required")
    if action == "dismiss":
        return
    query = (
        ProfessionalPublication.objects
        if case.target_kind == "profile"
        else EducationalPost.objects
    )
    where = (
        {"profile_id": case.target_uuid}
        if case.target_kind == "profile"
        else {"pk": case.target_uuid}
    )
    row = query.select_for_update().filter(**where).first()
    if row is None:
        raise LookupError("Content unavailable")
    if action == "hide":
        if row.current_revision_id != case.revision_uuid or row.hidden_at is not None:
            raise ValueError("Content version changed")
        row.hidden_at, row.hidden_case_uuid = at, case.id
        if case.target_kind == "post":
            row.state = "hidden"
    else:
        if row.hidden_case_uuid != case.id:
            raise ValueError("Moderation latch changed")
        row.hidden_at = row.hidden_case_uuid = None
        if case.target_kind == "post":
            row.state = (
                "published"
                if row.current_revision_id and row.withdrawn_at is None
                else "draft"
            )
    row.version += 1
    row.updated_at = at
    row.save()


def review_content(case, at):
    """Exact still-current approved fields, ignoring only the moderation latch.

    Withdrawn, edited, expired or ineligible sources yield metadata-only views.
    Private drafts, verification evidence and unrelated history are never read.
    """
    from types import SimpleNamespace

    from apps.assets.models import PublicAssetCopy
    from apps.professionals.post_selectors import confirmed_post
    from apps.professionals.publication_contracts import (
        bounded_json,
        validate_public_snapshot,
    )
    from apps.professionals.publication_selectors import retained_publication

    def parent(identifier, now):
        facts = retained_publication(identifier, now)
        return SimpleNamespace(revision_uuid=facts.revision_id) if facts else None

    owner = User.objects.select_for_update().get(pk=case.owner_id)
    if case.target_kind == "profile":
        facts = retained_publication(case.target_uuid, at)
        if facts is None or facts.revision_id != case.revision_uuid:
            return None
        validate_public_snapshot(facts.snapshot)
        media = []
        for purpose in facts.snapshot.get("media_purposes", []):
            copy = PublicAssetCopy.objects.filter(
                owner=owner,
                publication_uuid=facts.publication_id,
                release_revision_uuid=facts.revision_id,
                purpose=purpose,
                state="ready",
                revoked_at__isnull=True,
            ).first()
            if copy is None:
                return None
            media.append({"purpose": purpose, "copy_uuid": str(copy.id)})
        value = {"fields": facts.snapshot, "media": media}
    else:
        facts = confirmed_post(
            owner,
            case.target_uuid,
            case.revision_uuid,
            at,
            parent_source=parent,
            retain_hidden=True,
        )
        if facts is None:
            return None
        post, revision, payload = facts
        images = []
        for link in revision.images.order_by("position"):
            copy = PublicAssetCopy.objects.filter(
                owner=owner,
                publication_uuid=post.id,
                release_revision_uuid=revision.id,
                purpose="educational_image",
                source_asset_id=link.asset_id,
                source_version=link.asset_version,
                processing_version=link.processing_version,
                state="ready",
                revoked_at__isnull=True,
            ).first()
            if copy is None:
                return None
            images.append({"copy_uuid": str(copy.id), "alt": link.alt})
        value = {"text": payload.text, "images": images}
    return bounded_json(value, limit=20 * 1024).decode()


def read_moderation_media(
    actor, case_uuid, copy_uuid, step_up_id, reason_code, at, *, publication_store=None
):
    import json
    from hashlib import sha256
    from uuid import UUID, uuid4

    from django.utils import timezone

    from apps.assets.contracts import (
        AssetNotFound,
        AuthorizedAssetRead,
        UploadUnavailable,
    )
    from apps.assets.models import PublicAssetCopy, PublicCopyAttempt
    from apps.assets.public_storage import get_publication_store
    from apps.governance.moderation import assigned_moderation, audit, context

    if not all(isinstance(v, UUID) for v in (case_uuid, copy_uuid, step_up_id)):
        raise ValueError("Invalid moderation media binding")
    context(actor, at)

    def capture():
        user, case = assigned_moderation(
            actor,
            case_uuid,
            step_up_id,
            reason_code,
            max(at, timezone.now()),
            lock_case=lock_case,
        )
        snapshot = review_content(case, max(at, timezone.now()))
        if snapshot is None:
            raise AssetNotFound("Moderation media unavailable")
        value = json.loads(snapshot)
        selected = value["images"] if case.target_kind == "post" else value["media"]
        if str(copy_uuid) not in {item["copy_uuid"] for item in selected}:
            raise AssetNotFound("Moderation media unavailable")
        copy = (
            PublicAssetCopy.objects.select_for_update()
            .filter(
                pk=copy_uuid,
                owner_id=case.owner_id,
                release_revision_uuid=case.revision_uuid,
                state="ready",
                revoked_at__isnull=True,
            )
            .first()
        )
        if copy is None:
            raise AssetNotFound("Moderation media unavailable")
        attempt = (
            PublicCopyAttempt.objects.select_for_update()
            .filter(copy=copy, generation=copy.generation, state="ready")
            .first()
        )
        if attempt is None:
            raise AssetNotFound("Moderation media unavailable")
        return (
            user,
            case,
            (
                case.version,
                copy.version,
                copy.generation,
                attempt.id,
                attempt.key,
                attempt.sha256,
                attempt.size,
                attempt.mime_type,
            ),
        )

    with transaction.atomic():
        _, _, expected = capture()
    try:
        body = (publication_store or get_publication_store()).read_limited(
            expected[4], 10_000_000
        )
        if len(body) != expected[6] or sha256(body).hexdigest() != expected[5]:
            raise ValueError
    except Exception:
        raise UploadUnavailable("Moderation media unavailable") from None
    with transaction.atomic():
        user, case, current = capture()
        if current != expected:
            raise AssetNotFound("Moderation media unavailable")
        audit(user, "read", case.id, uuid4(), max(at, timezone.now()), reason_code)
        return AuthorizedAssetRead(copy_uuid, expected[3], expected[7], body)
