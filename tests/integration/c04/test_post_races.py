"""Stale post owners cannot replace a newer source revision."""

from uuid import uuid4

import pytest
from django.utils import timezone

from tests.integration.c04.post_helpers import command, draft

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_stale_post_edit_cannot_replace_current_revision(corpus):
    save = command("save_post")
    subject, _ = corpus()
    post = draft(subject)
    from apps.professionals.post_contracts import PostInput

    new = save(
        subject.actor, post.id, PostInput("نخست"), post.version, uuid4(), timezone.now()
    )
    with pytest.raises((LookupError, ValueError)):
        save(
            subject.actor,
            post.id,
            PostInput("دیررس"),
            post.version,
            uuid4(),
            timezone.now(),
        )
    from apps.professionals.post_models import EducationalPost

    assert (
        EducationalPost.objects.get(pk=post.id).requested_revision_id == new.revision_id
    )
