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
            "SELECT indexdef FROM pg_indexes "
            "WHERE tablename='marketplace_publicprofessionalprojection'"
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

    from apps.professionals.publication_models import ProfessionalPublication
    from config.use_cases.publication import unpublish_profile

    subject, draft = published(settings)
    api().refresh_public_projection(subject.profile.id, timezone.now())
    unpublish_profile(
        subject.actor,
        draft.publication_id,
        ProfessionalPublication.objects.get(pk=draft.publication_id).version,
        uuid4(),
        timezone.now(),
    )
    page = search()
    assert page.items == () and page.next_cursor is None


def test_full_text_precedes_trigram_only_and_variants_agree(corpus):
    from tests.integration.c04.search_helpers import names

    corpus(name="کیان", specialties=())
    corpus(name="کیانا", specialties=())
    first = search(q="كيان")
    assert names(first) == ["کیان", "کیانا"]
    assert names(search(q="کِیـان")) == names(first)


def test_same_tokens_have_name_weight_a_before_biography_weight_c(corpus):
    from tests.integration.c04.search_helpers import names

    corpus(name="کیان", biography="شرح مربی", specialties=())
    corpus(name="سارا", biography="کیان", specialties=())
    assert names(search(q="کیان")) == ["کیان", "سارا"]


@pytest.mark.parametrize(
    "defect", ["private_filter", "mistyped_filter", "experience", "version"]
)
def test_actual_search_projection_sql_contracts(corpus, defect):
    from django.db import IntegrityError, transaction

    from apps.marketplace.models import PublicProfessionalProjection

    subject, _ = corpus()
    changes = {
        "private_filter": {"normalized_filters": {"identity_name": "PRIVATE"}},
        "mistyped_filter": {"normalized_filters": {"specialties": {}, "languages": []}},
        "experience": {"experience_years": 81},
        "version": {"normalization_version": "unsupported"},
    }
    with pytest.raises(IntegrityError), transaction.atomic():
        PublicProfessionalProjection.objects.filter(pk=subject.profile.id).update(
            **changes[defect]
        )


def test_populated_task4_to_task5_backfill_retains_release_identity_and_generation(
    corpus,
):
    from django.db.migrations.executor import MigrationExecutor

    from apps.marketplace.models import PublicProfessionalProjection

    subject, _ = corpus(name="كيان")
    row = PublicProfessionalProjection.objects.get(pk=subject.profile.id)
    original = (
        row.profile_uuid,
        row.publication_uuid,
        row.revision_uuid,
        row.snapshot,
        row.generation,
    )
    executor = MigrationExecutor(connection)
    latest = executor.loader.graph.leaf_nodes()
    try:
        # Disposable test database only; no repository or live data rollback.
        executor.migrate([("marketplace", "0001_public_projection")])
    finally:
        MigrationExecutor(connection).migrate(latest)
    row = PublicProfessionalProjection.objects.get(pk=subject.profile.id)
    assert (
        row.profile_uuid,
        row.publication_uuid,
        row.revision_uuid,
        row.snapshot,
        row.generation,
    ) == original
    assert row.normalization_version == "fa-search-v1" and row.normalized_name == "کیان"
    assert search(q="کیان").items[0].profile_uuid == subject.profile.id
