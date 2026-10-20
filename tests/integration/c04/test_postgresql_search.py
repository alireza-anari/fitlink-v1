"""Real PostgreSQL extension, current authority and Persian indexed discovery."""

import pytest
from django.db import connection
from django.utils import timezone

from tests.integration.c04.test_public_projection import api, published

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def search(**values):
    from apps.marketplace import contracts

    assert hasattr(contracts, "SearchCriteria"), "Missing bounded search criteria"
    assert callable(getattr(api(), "search_public_professionals", None)), (
        "Missing fresh PostgreSQL search"
    )
    return api().search_public_professionals(
        contracts.SearchCriteria(**values), None, timezone.now()
    )


def test_real_pg_trgm_and_both_gin_search_indexes_installed():
    assert connection.vendor == "postgresql"
    with connection.cursor() as cursor:
        cursor.execute("SELECT extname FROM pg_extension WHERE extname='pg_trgm'")
        assert cursor.fetchone() is not None, "Missing required real pg_trgm extension"
        cursor.execute(
            "SELECT indexdef FROM pg_indexes WHERE tablename='marketplace_publicprofessionalprojection'"
        )
        definitions = [row[0] for row in cursor.fetchall()]
    assert sum("USING gin" in value for value in definitions) >= 2, (
        "Missing FTS/trigram GIN indexes"
    )


def test_empty_browse_returns_only_current_public_dto(settings):
    subject, draft = published(settings)
    api().refresh_public_projection(subject.profile.id, timezone.now())
    page = search()
    assert [item.profile_uuid for item in page.items] == [subject.profile.id]
    assert page.next_cursor is None
    assert not hasattr(page, "total")


def test_stale_index_cannot_expose_withdrawn_candidate(settings):
    from uuid import uuid4
    from config.use_cases.publication import unpublish_profile

    subject, draft = published(settings)
    api().refresh_public_projection(subject.profile.id, timezone.now())
    unpublish_profile(
        subject.actor, draft.publication_id, draft.version, uuid4(), timezone.now()
    )
    page = search()
    assert page.items == () and page.next_cursor is None
