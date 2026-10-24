"""Post commands and finite public content; source policy remains domain owned."""

from django.db import DatabaseError, transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.governance.audit import append_event
from apps.governance.flags import feature_enabled
from apps.governance.outbox import append_outbox
from apps.marketplace.contracts import MarketplaceUnavailable, context
from apps.professionals import posts
from apps.professionals.post_contracts import PublicPostDTO, PublicPostImage
from apps.professionals.post_models import EducationalPost
from apps.professionals.post_selectors import confirmed_post
from config.use_cases import post_media, profile_assets
from config.use_cases.publication import _disclosure


def _hooks(actor):
    def record(outcome):
        append_event(outcome, actor_uuid=actor.user_uuid, subject_type="professional")

    def emit(row):
        post_media.prepare(row, timezone.now())
        append_outbox(
            "professional.post_changed",
            row.id,
            row.version,
            {"post_uuid": str(row.id), "user_uuid": str(actor.user_uuid)},
            f"professional.post_changed:{row.id}:{row.version}",
        )

    return {"record": record, "emit": emit}


def save_post(actor, post_uuid, payload, expected_version, operation_id, at):
    return posts.save_post(
        actor,
        post_uuid,
        payload,
        expected_version,
        operation_id,
        at,
        **_hooks(actor),
        disclose=_disclosure,
    )


def publish_post(actor, post_uuid, confirmed, expected_version, operation_id, at):
    return posts.publish_post(
        actor,
        post_uuid,
        confirmed,
        expected_version,
        operation_id,
        at,
        **_hooks(actor),
        disclose=_disclosure,
        enabled=lambda: feature_enabled("marketplace"),
        parent_source=post_media.parent_source,
    )


def withdraw_post(actor, post_uuid, expected_version, operation_id, at):
    return posts.withdraw_post(
        actor, post_uuid, expected_version, operation_id, at, **_hooks(actor)
    )


def begin_post_upload(
    actor, post_uuid, operation_id, at, *, declared_size, declared_type
):
    return profile_assets.begin_profile_upload(
        actor,
        "educational_image",
        post_uuid,
        operation_id,
        at,
        declared_size=declared_size,
        declared_type=declared_type,
    )


def receive_post_upload(actor, asset_uuid, expected_version, stream, at):
    return profile_assets.receive_profile_upload(
        actor, asset_uuid, expected_version, stream, at
    )


def finalize_post_upload(actor, asset_uuid, expected_version, operation_id, at):
    return profile_assets.finalize_profile_upload(
        actor, asset_uuid, expected_version, operation_id, at
    )


def authorized_post_download(actor, asset_uuid, purpose, at):
    from hashlib import sha256
    from uuid import uuid4

    from apps.accounts.contracts import SecurityOutcome
    from apps.accounts.sessions import locked_actor
    from apps.assets.contracts import (
        AssetNotFound,
        AuthorizedAssetRead,
        UploadUnavailable,
    )
    from apps.assets.models import AssetDerivative
    from apps.assets.policies import owned_asset, validate_context
    from apps.assets.validation import raster_signature
    from apps.professionals.policies import owned_asset_subject
    from config.use_cases.asset_processing import authority

    if purpose != "post_preview":
        raise AssetNotFound("Asset unavailable")
    validate_context(actor, at)
    record, _ = profile_assets.hooks(actor)

    def capture():
        user = locked_actor(actor, "asset.owner_read", max(at, timezone.now()))
        asset = owned_asset(user, asset_uuid, owned_asset_subject)
        if (
            asset.purpose != "educational_image"
            or asset.state != "ready"
            or asset.revoked_at
        ):
            raise AssetNotFound("Asset unavailable")
        row = (
            AssetDerivative.objects.select_for_update()
            .filter(
                asset=asset,
                purpose="post_preview",
                processing_version=asset.processing_version,
                state="ready",
            )
            .first()
        )
        attempt = (
            asset.processing_attempts.filter(
                processing_version=asset.processing_version
            )
            .order_by("-attempt")
            .first()
        )
        if (
            row is None
            or attempt is None
            or attempt.state != "ready"
            or attempt.algorithm_version != "jpeg-png-pixels-v1"
            or attempt.scanner_engine != "ClamAV 1.5.4"
            or not attempt.scanner_signature.isdecimal()
        ):
            raise AssetNotFound("Asset unavailable")
        return (
            asset.version,
            row.id,
            row.version,
            row.key,
            row.sha256,
            row.mime_type,
            authority(user, asset, max(at, timezone.now())),
        )

    with transaction.atomic():
        expected = capture()
    try:
        body = profile_assets.get_private_store().read_limited(expected[3], 10_000_000)
        if not isinstance(body, bytes) or sha256(body).hexdigest() != expected[4]:
            raise ValueError
        raster_signature(body[:8], expected[5])
    except Exception:
        raise UploadUnavailable("Asset unavailable") from None
    with transaction.atomic():
        if capture() != expected:
            raise AssetNotFound("Asset unavailable")
        record(
            SecurityOutcome(
                "asset.read", "succeeded", asset_uuid, uuid4(), (), "user_requested"
            )
        )
        return AuthorizedAssetRead(asset_uuid, expected[1], expected[5], body)


def _public_post(user, identifier, at):
    if feature_enabled("marketplace", raise_unavailable=True) is not True:
        return None
    row = EducationalPost.objects.filter(
        pk=identifier,
        profile__user=user,
        state="published",
        current_revision__isnull=False,
    ).first()
    if row is None:
        return None
    facts = confirmed_post(
        user,
        row.id,
        row.current_revision_id,
        at,
        parent_source=post_media.parent_source,
    )
    if facts is None:
        return None
    row, revision, payload = facts
    try:
        copies = post_media.current_copies(user, row, revision)
    except (ValueError, LookupError, PermissionError):
        return None
    images = [
        PublicPostImage(copies[b.asset_id].id, b.alt)
        for b in revision.images.order_by("position")
    ]
    return PublicPostDTO(
        row.id, row.profile_id, revision.id, payload.text, tuple(images)
    )


def public_post(identifier, at, *, release=None):
    context(identifier, at)
    try:
        with transaction.atomic():
            hint = (
                EducationalPost.objects.filter(pk=identifier)
                .values_list("profile__user_id", flat=True)
                .first()
            )
            if hint is None:
                return None
            user = User.objects.select_for_update().get(pk=hint)
            dto = _public_post(user, identifier, max(at, timezone.now()))
            if dto is None:
                return None
            result = release(dto) if release else dto
            return (
                result
                if _public_post(user, identifier, max(at, timezone.now())) == dto
                else None
            )
    except DatabaseError:
        raise MarketplaceUnavailable("Marketplace temporarily unavailable") from None


def report_public_content(actor, target, reason, operation_id, at):
    from apps.governance.moderation import report_public_content as report
    from config.use_cases.public_moderation import lock_target, target_source

    return report(
        actor,
        target,
        reason,
        operation_id,
        at,
        target_source=target_source,
        lock_target=lock_target,
    )


def claim_public_moderation(
    actor, case_uuid, expected_version, step_up_id, reason_code, operation_id, at
):
    from apps.governance.moderation import claim_public_moderation as claim
    from config.use_cases.public_moderation import lock_case

    return claim(
        actor,
        case_uuid,
        expected_version,
        step_up_id,
        reason_code,
        operation_id,
        at,
        lock_case=lock_case,
    )


def decide_public_moderation(
    actor,
    case_uuid,
    expected_version,
    action,
    step_up_id,
    reason_code,
    operation_id,
    at,
):
    from apps.governance.moderation import decide_public_moderation as decide
    from config.use_cases.public_moderation import apply_decision, lock_case

    return decide(
        actor,
        case_uuid,
        expected_version,
        action,
        step_up_id,
        reason_code,
        operation_id,
        at,
        lock_case=lock_case,
        apply_decision=apply_decision,
    )


def moderation_queue(actor, step_up_id, reason_code, at, *, limit=25, cursor=None):
    from apps.governance.moderation import moderation_queue as queue

    return queue(actor, step_up_id, reason_code, at, limit=limit, cursor=cursor)


def read_public_moderation(actor, case_uuid, step_up_id, reason_code, at):
    from apps.governance.moderation import read_public_moderation as read
    from config.use_cases.public_moderation import lock_case, review_content

    return read(
        actor,
        case_uuid,
        step_up_id,
        reason_code,
        at,
        lock_case=lock_case,
        read_target=review_content,
    )


def read_public_moderation_media(
    actor, case_uuid, copy_uuid, step_up_id, reason_code, at, *, publication_store=None
):
    from config.use_cases.public_moderation import read_moderation_media

    return read_moderation_media(
        actor,
        case_uuid,
        copy_uuid,
        step_up_id,
        reason_code,
        at,
        publication_store=publication_store,
    )
