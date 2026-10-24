"""Synthetic post commands always use actual account and profile authority."""

import importlib
import importlib.util
from uuid import uuid4

from django.utils import timezone


def command(name):
    module = "config.use_cases.public_content"
    assert importlib.util.find_spec(module), "Missing post/moderation composition"
    value = getattr(importlib.import_module(module), name, None)
    assert callable(value), "Missing post/moderation command: " + name
    return value


def draft(subject, text="آموزش حرکت"):
    from apps.professionals.post_contracts import PostInput

    return command("save_post")(
        subject.actor, None, PostInput(text), None, uuid4(), timezone.now()
    )


def image(subject, post):
    """Synthetic metadata fixture; real scan/quarantine is tested in media gate."""
    from datetime import timedelta
    from hashlib import sha256
    from io import BytesIO

    from PIL import Image

    from apps.assets.models import Asset, AssetDerivative, AssetProcessingAttempt
    from tests.integration.c04.copy_helpers import ObservedStore

    data = BytesIO()
    Image.new("RGB", (64, 48), (32, 96, 128)).save(data, format="PNG")
    body = data.getvalue()
    now = timezone.now()
    asset = Asset.objects.create(
        owner=subject.user,
        subject_kind="educational_post",
        subject_uuid=post.id,
        purpose="educational_image",
        state="ready",
        source_key=f"source/{uuid4()}",
        declared_size=len(body),
        declared_type="image/png",
        actual_size=len(body),
        detected_type="image/png",
        sha256=sha256(body).hexdigest(),
        accepted_at=now,
        finalized_at=now,
        upload_expires_at=now + timedelta(hours=1),
    )
    AssetProcessingAttempt.objects.create(
        asset=asset,
        processing_version=1,
        state="ready",
        algorithm_version="jpeg-png-pixels-v1",
        owner_auth_version=subject.user.auth_version,
        asset_version=1,
        authority_hash="b" * 64,
        scanner_engine="ClamAV 1.5.4",
        scanner_signature="28000",
    )
    derivative = AssetDerivative.objects.create(
        asset=asset,
        processing_version=1,
        purpose="post_preview",
        key=f"derivatives/{uuid4()}",
        sha256=sha256(body).hexdigest(),
        width=64,
        height=48,
        mime_type="image/png",
        state="ready",
    )
    store = ObservedStore()
    store.put(derivative.key, body, "image/png")
    return asset, derivative, store


def pending_post(subject, image_count=1):
    from apps.assets.models import PublicAssetCopy
    from apps.assets.public_copies import scan_due_public_copies
    from apps.professionals.post_contracts import PostImageInput, PostInput
    from config.use_cases.public_media import validate_release

    post = draft(subject)
    sources = [image(subject, post) for _ in range(image_count)]
    store = sources[0][2]
    for _, _, other in sources[1:]:
        store.objects.update(other.objects)
        store.content_types.update(other.content_types)
    post = command("save_post")(
        subject.actor,
        post.id,
        PostInput(
            "آموزش",
            tuple(PostImageInput(asset.id, "شرح تصویر") for asset, _, _ in sources),
        ),
        post.version,
        uuid4(),
        timezone.now(),
    )
    post = command("publish_post")(
        subject.actor, post.id, True, post.version, uuid4(), timezone.now()
    )
    assert command("public_post")(post.id, timezone.now()) is None
    queued = []
    assert (
        scan_due_public_copies(
            timezone.now(),
            100,
            authorize=validate_release,
            enqueue=lambda *args: queued.append(args),
        )
        == image_count
    )
    copies = list(PublicAssetCopy.objects.filter(publication_uuid=post.id))
    return (
        post,
        tuple(x[0] for x in sources),
        tuple(x[1] for x in sources),
        store,
        copies,
        queued,
    )


def published(subject):
    from tests.integration.c04.copy_helpers import process

    post, assets, derivatives, store, copies, jobs = pending_post(subject)
    for job in jobs:
        assert process(store, job).status == "ready"
    return post, assets[0], derivatives[0], store, copies[0]


def moderator(settings, case_uuid, *, person=None, phone="+989155557010", issuer=None):
    from dataclasses import replace
    from datetime import timedelta

    from django.db import transaction

    from apps.governance.staff import MockStepUpProvider, issue_mock_step_up
    from apps.governance.staff_models import StaffCapabilityGrant
    from tests.integration.c03.profile_helpers import make_actor

    settings.ACCOUNT_SECURITY = replace(
        settings.ACCOUNT_SECURITY, step_up_provider="mock"
    )
    staff = person or make_actor(phone)
    issuer = issuer or make_actor("+989155557011")
    staff.issuer = issuer
    staff.grant = StaffCapabilityGrant.objects.create(
        user=staff.user,
        capability="marketplace_moderation",
        granted_by=issuer.user,
        reason_code="staff_assigned",
        valid_from=staff.at - timedelta(seconds=1),
        valid_until=staff.at + timedelta(hours=1),
    )
    provider = MockStepUpProvider()
    proof = provider.prepare(
        staff.user.public_id, "marketplace_moderation", case_uuid, staff.at
    )
    with transaction.atomic():
        staff.step = issue_mock_step_up(
            staff.user,
            "marketplace_moderation",
            case_uuid,
            proof.raw_assertion,
            issuer.user,
            staff.at,
            provider,
        )
    return staff


def case_step(staff, identifier):
    from django.db import transaction

    from apps.governance.staff import MockStepUpProvider, issue_mock_step_up

    provider = MockStepUpProvider()
    now = timezone.now()
    proof = provider.prepare(
        staff.user.public_id, "marketplace_moderation", identifier, now
    )
    with transaction.atomic():
        return issue_mock_step_up(
            staff.user,
            "marketplace_moderation",
            identifier,
            proof.raw_assertion,
            staff.issuer.user,
            now,
            provider,
        )
