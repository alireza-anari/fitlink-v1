"""Database guards protect immutable publication and cross-owner bindings."""

import pytest
from django.db import DatabaseError, connection, transaction

from tests.integration.c03.test_professional_setup import owner
from tests.integration.c03.test_verification_decisions import approved
from tests.integration.c04.publication_helpers import configure, confirm, model, prepare

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize("change", ["snapshot", "source_profile_version", "delete"])
def test_confirmed_revision_is_sql_immutable(settings, change):
    assert connection.vendor == "postgresql"
    configure(settings)
    subject = approved(settings)
    draft = prepare(subject)
    published = confirm(subject, draft)
    revision = model("PublicationRevision").objects.get(pk=draft.revision_id)
    if change == "delete":
        from uuid import uuid4

        from django.utils import timezone

        from config.use_cases.publication import unpublish_profile

        unpublish_profile(
            subject.actor,
            draft.publication_id,
            published.version,
            uuid4(),
            timezone.now(),
        )
        publication = model().objects.get(pk=draft.publication_id)
        assert publication.current_revision_id is None
        assert publication.requested_revision_id is None
    with pytest.raises(DatabaseError), transaction.atomic():
        with connection.cursor() as cursor:
            table = connection.ops.quote_name(revision._meta.db_table)
            if change == "delete":
                cursor.execute(f"DELETE FROM {table} WHERE id = %s", [revision.id])
            elif change == "snapshot":
                cursor.execute(
                    f"UPDATE {table} SET snapshot = "
                    "jsonb_set(snapshot, '{identity_name}', 'true') WHERE id = %s",
                    [revision.id],
                )
            else:
                cursor.execute(
                    f"UPDATE {table} SET source_profile_version = "
                    "source_profile_version + 1 WHERE id = %s",
                    [revision.id],
                )


def test_publication_pointer_cannot_cross_owner_or_revision(settings):
    configure(settings)
    subject = approved(settings)
    draft = prepare(subject)
    confirm(subject, draft)
    foreign = owner("+989123456789")
    publication = model().objects.create(
        profile=foreign.profile, slug="foreign-synthetic"
    )
    with pytest.raises(DatabaseError), transaction.atomic():
        model().objects.filter(pk=publication.pk).update(
            current_revision_id=draft.revision_id,
            state="published",
            version=2,
        )


def test_private_identity_revision_cannot_bind_as_public_summary(settings):
    configure(settings)
    subject = approved(settings)
    draft = prepare(subject)
    identity = subject.assets["identity"][1].current_revision_id
    with pytest.raises(DatabaseError), transaction.atomic():
        model("PublicationQualification").objects.create(
            revision_id=draft.revision_id,
            credential_revision_id=identity,
            position=0,
            role="coach",
        )
