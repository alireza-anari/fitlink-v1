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


def test_concurrent_same_version_post_edit_has_one_winner(corpus):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from apps.professionals.post_contracts import PostInput
    from apps.professionals.post_models import PostRevision
    from tests.integration.c03.profile_helpers import in_connection

    subject, _ = corpus()
    post = draft(subject)
    barrier = Barrier(2)

    def edit(text):
        barrier.wait(timeout=10)
        try:
            command("save_post")(
                subject.actor,
                post.id,
                PostInput(text),
                post.version,
                uuid4(),
                timezone.now(),
            )
            return True
        except (LookupError, ValueError):
            return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [
            pool.submit(in_connection, lambda value=x: edit(value))
            for x in ["نخست", "دوم"]
        ]
        assert sum(job.result(timeout=25) for job in jobs) == 1
    assert PostRevision.objects.filter(post_id=post.id).count() == 2
