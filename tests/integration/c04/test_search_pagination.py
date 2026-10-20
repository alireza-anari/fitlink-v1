"""Stable order, visible-only cursor and strict finite candidate budget."""

from uuid import uuid4

import pytest
from django.utils import timezone

from tests.integration.c04.search_helpers import search  # noqa: F401
from tests.integration.c04.test_public_projection import api

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_equal_rank_pages_follow_uuid_and_never_repeat(corpus):
    from apps.marketplace.contracts import SearchCriteria

    subjects = [corpus("کیان")[0] for _ in range(3)]
    expected = sorted([s.profile.id for s in subjects])
    criteria = SearchCriteria(q="کیان", page_size=1)
    pages, token = [], None
    for _ in range(3):
        page = api().search_public_professionals(criteria, token, timezone.now())
        assert len(page.items) == 1
        pages.append(page.items[0].profile_uuid)
        token = page.next_cursor
    assert pages == expected and token is None


def test_withdrawn_intermediate_candidates_never_enter_cursor(corpus):
    from apps.marketplace.contracts import SearchCriteria
    from apps.professionals.publication_models import ProfessionalPublication
    from config.use_cases.publication import unpublish_profile

    first, draft = corpus("کیان")
    second, _ = corpus("کیان")
    unpublish_profile(
        first.actor,
        draft.publication_id,
        ProfessionalPublication.objects.get(pk=draft.publication_id).version,
        uuid4(),
        timezone.now(),
    )
    page = api().search_public_professionals(
        SearchCriteria(page_size=1), None, timezone.now()
    )
    assert [r.profile_uuid for r in page.items] == [second.profile.id]
    assert page.next_cursor is None
