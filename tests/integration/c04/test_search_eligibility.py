"""No rank/filter/count/cursor grants authority to stale role or timestamp facts."""

from datetime import timedelta

import pytest
from django.utils import timezone

from tests.integration.c03.test_verification_revocation import restrict
from tests.integration.c04.search_helpers import names, search
from tests.integration.c04.test_public_projection import api

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_restricted_role_filters_use_current_intersection(corpus):
    subject, _ = corpus(roles=("coach", "nutritionist"))
    restrict(subject, "nutritionist")
    assert search(role="nutritionist").items == ()
    assert names(search(role="coach")) == ["کیان"]


def test_timestamp_expiry_without_projection_or_counter_change(corpus):
    from apps.marketplace.contracts import SearchCriteria

    until = timezone.now() + timedelta(hours=1)
    subject, _ = corpus(valid_until=until)
    assert search().items
    assert api().search_public_professionals(SearchCriteria(), None, until).items == ()


def test_unselected_private_identity_never_searchable(corpus):
    corpus(name="کیان")
    assert search(q="Private Fixture").items == ()
    assert search(q="Private").items == ()


def test_candidate_budget_fails_without_partial_output_and_recovers(corpus):
    from uuid import uuid4

    from apps.marketplace.models import (
        PublicationScanCursor,
        PublicProfessionalProjection,
    )
    from apps.marketplace.search import ProjectionRefreshRequired
    from apps.professionals.publication_models import ProfessionalPublication
    from config.use_cases.publication import unpublish_profile

    for _ in range(100):
        subject, draft = corpus()
        publication = ProfessionalPublication.objects.get(pk=draft.publication_id)
        unpublish_profile(
            subject.actor, publication.id, publication.version, uuid4(), timezone.now()
        )
    assert PublicProfessionalProjection.objects.filter(state="active").count() == 100
    with pytest.raises(
        ProjectionRefreshRequired, match="^projection_refresh_required$"
    ):
        search()
    assert PublicationScanCursor.objects.get(name="publications").after_uuid is None
    for _ in range(4):
        api().reconcile_publications(timezone.now(), 100)
    assert PublicProfessionalProjection.objects.filter(state="active").count() == 0
    assert search().items == ()


def test_flag_off_denies_search_without_claiming_empty_marketplace(corpus):
    from apps.governance.flag_models import FeatureFlag
    from apps.marketplace.contracts import MarketplaceClosed

    corpus()
    FeatureFlag.objects.filter(key="marketplace").update(enabled=False)
    with pytest.raises(MarketplaceClosed):
        search()
