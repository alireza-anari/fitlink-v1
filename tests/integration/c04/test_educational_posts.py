"""Drafts/history remain owned; publication cannot substitute for consent."""

from uuid import uuid4

import pytest
from django.utils import timezone

from tests.integration.c03.profile_helpers import make_actor
from tests.integration.c04.post_helpers import command, draft

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_owner_private_draft_remains_private(corpus):
    save = command("save_post")
    read = command("public_post")
    subject, _ = corpus()
    post = draft(subject)
    assert post.state == "draft"
    assert post.version == 1
    assert read(post.id, timezone.now()) is None
    from apps.professionals.post_contracts import PostInput

    other = make_actor("+989155557001")
    with pytest.raises((PermissionError, LookupError)):
        save(other.actor, post.id, PostInput("تغییر"), 1, uuid4(), timezone.now())


def test_post_publish_requires_explicit_confirmation_and_images(corpus):
    publish = command("publish_post")
    subject, _ = corpus()
    post = draft(subject)
    for confirmed in (False, True, 1):
        with pytest.raises((ValueError, PermissionError, LookupError)):
            publish(
                subject.actor, post.id, confirmed, post.version, uuid4(), timezone.now()
            )
    assert command("public_post")(post.id, timezone.now()) is None


def test_post_revision_is_immutable_and_edits_withdraw_old_release(corpus):
    save = command("save_post")
    subject, _ = corpus()
    post = draft(subject)
    from django.db import DatabaseError, transaction

    from apps.professionals.post_contracts import PostInput
    from apps.professionals.post_models import PostRevision

    revision = PostRevision.objects.get(pk=post.revision_id)
    with pytest.raises(DatabaseError), transaction.atomic():
        PostRevision.objects.filter(pk=revision.id).update(text="forged")
    changed = save(
        subject.actor,
        post.id,
        PostInput("آموزش تازه"),
        post.version,
        uuid4(),
        timezone.now(),
    )
    assert changed.revision_id != post.revision_id
    assert PostRevision.objects.filter(post_id=post.id).count() == 2
    assert command("public_post")(post.id, timezone.now()) is None


def test_post_receipt_payload_and_expected_version_are_fenced(corpus):
    save = command("save_post")
    subject, _ = corpus()
    from apps.professionals.post_contracts import PostInput

    operation = uuid4()
    args = (subject.actor, None, PostInput("آموزش"), None, operation, timezone.now())
    first = save(*args)
    assert save(*args) == first
    with pytest.raises((ValueError, LookupError)):
        save(subject.actor, None, PostInput("متفاوت"), None, operation, timezone.now())
    with pytest.raises((ValueError, LookupError)):
        save(
            subject.actor,
            first.id,
            PostInput("تازه"),
            first.version + 1,
            uuid4(),
            timezone.now(),
        )


def test_confirmed_post_activates_only_complete_copies_and_edit_withdraws(corpus):
    from apps.professionals.post_contracts import PostInput
    from apps.professionals.post_models import EducationalPost
    from tests.integration.c04.post_helpers import published

    subject, _ = corpus()
    post, asset, derivative, store, copy = published(subject)
    dto = command("public_post")(post.id, timezone.now())
    assert dto is not None and dto.text == "آموزش"
    assert dto.images[0].copy_uuid == copy.id
    assert set(dto.__dataclass_fields__) == {
        "id",
        "profile_uuid",
        "revision_uuid",
        "text",
        "images",
    }
    row = EducationalPost.objects.get(pk=post.id)
    command("save_post")(
        subject.actor, post.id, PostInput("تازه"), row.version, uuid4(), timezone.now()
    )
    assert command("public_post")(post.id, timezone.now()) is None


@pytest.mark.parametrize(
    "defect", ["marketplace_off", "suspended", "parent_withdrawn", "stale_profile"]
)
def test_post_current_parent_and_account_authority(corpus, settings, defect):
    from tests.integration.c03.test_professional_setup import save
    from tests.integration.c04.post_helpers import published

    subject, parent = corpus()
    post, *_ = published(subject)
    assert command("public_post")(post.id, timezone.now()) is not None
    if defect == "marketplace_off":
        from apps.governance.flag_models import FeatureFlag

        FeatureFlag.objects.filter(key="marketplace").update(enabled=False)
    elif defect == "suspended":
        subject.user.state = "suspended"
        subject.user.is_active = False
        subject.user.save()
    elif defect == "parent_withdrawn":
        from apps.professionals.models import ProfessionalPublication
        from config.use_cases.publication import unpublish_profile

        row = ProfessionalPublication.objects.get(profile=subject.profile)
        unpublish_profile(subject.actor, row.id, row.version, uuid4(), timezone.now())
    else:
        save(subject, "description", {"biography": "تغییر"})
    assert command("public_post")(post.id, timezone.now()) is None
