"""Post ingress cannot borrow evidence or another subject's asset authority."""

from uuid import uuid4

import pytest
from django.utils import timezone

from tests.integration.c04.post_helpers import command, draft

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_post_foreign_evidence_or_profile_assets_cannot_bind(corpus):
    save = command("save_post")
    subject, _ = corpus()
    post = draft(subject)
    from apps.assets.models import Asset
    from apps.professionals.post_contracts import PostImageInput, PostInput

    evidence = Asset.objects.filter(
        owner=subject.user, purpose="identity_evidence", state="ready"
    ).first()
    assert evidence is not None
    with pytest.raises((ValueError, LookupError, PermissionError)):
        save(
            subject.actor,
            post.id,
            PostInput("آموزش", (PostImageInput(evidence.id, "شرح"),)),
            post.version,
            uuid4(),
            timezone.now(),
        )


def test_post_upload_is_bound_to_exact_owned_draft(corpus):
    begin = command("begin_post_upload")
    subject, _ = corpus()
    post = draft(subject)
    with pytest.raises((ValueError, LookupError, PermissionError)):
        begin(
            subject.actor,
            uuid4(),
            uuid4(),
            timezone.now(),
            declared_size=100,
            declared_type="image/png",
        )
    upload = begin(
        subject.actor,
        post.id,
        uuid4(),
        timezone.now(),
        declared_size=100,
        declared_type="image/png",
    )
    from apps.assets.models import Asset

    row = Asset.objects.get(pk=upload.id)
    assert (row.subject_kind, row.subject_uuid, row.purpose, row.classification) == (
        "educational_post",
        post.id,
        "educational_image",
        "private_source",
    )
