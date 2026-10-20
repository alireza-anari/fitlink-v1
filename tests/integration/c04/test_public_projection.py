"""Current source authority wins over every damaged or delayed projection."""

from datetime import timedelta
from uuid import uuid4

import pytest
from django.db import connection
from django.utils import timezone

from tests.integration.c03.test_verification_decisions import approved
from tests.integration.c04.publication_helpers import (
    configure,
    confirm,
    module,
    prepare,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def published(settings, **selection):
    configure(settings)
    subject = approved(settings)
    draft = prepare(subject, **selection)
    confirm(subject, draft)
    return subject, draft


def api():
    return module("config.use_cases.marketplace")


def test_index_eligible_bit_never_authorizes(settings):
    assert connection.vendor == "postgresql"
    subject, draft = published(settings)
    current = api().public_professional(subject.profile.id, timezone.now())
    assert current is not None
    assert set(current.as_public_dict()) == {
        "profile_uuid",
        "slug",
        "display_name",
        "biography",
        "verified_roles",
        "qualification_summaries",
        "media",
    }
    assert (
        api().refresh_public_projection(subject.profile.id, timezone.now()).state
        == "active"
    )
    from apps.marketplace.models import PublicProfessionalProjection

    row = PublicProfessionalProjection.objects.get(pk=subject.profile.id)
    row.snapshot = {**row.snapshot, "display_name": "DAMAGED INDEX VALUE"}
    row.save()
    assert (
        api()
        .public_professional(subject.profile.id, timezone.now())
        .as_public_dict()["display_name"]
        != "DAMAGED INDEX VALUE"
    )
    from apps.professionals.publication_models import ProfessionalPublication
    from config.use_cases.publication import unpublish_profile

    p = ProfessionalPublication.objects.get(pk=draft.publication_id)
    unpublish_profile(subject.actor, p.id, p.version, uuid4(), timezone.now())
    assert api().public_professional(subject.profile.id, timezone.now()) is None


def test_initial_scan_finds_already_receipted_profiles(settings):
    subject, draft = published(settings)
    from apps.marketplace.models import PublicProfessionalProjection

    assert not PublicProfessionalProjection.objects.filter(
        pk=subject.profile.id
    ).exists()
    assert api().reconcile_publications(timezone.now(), 1).processed == 1
    assert (
        PublicProfessionalProjection.objects.get(pk=subject.profile.id).state
        == "active"
    )


@pytest.mark.parametrize(
    "failure",
    [
        "flag_off",
        "flag_missing",
        "source_edit",
        "account_inactive",
        "expiry",
        "identity_revoked",
    ],
)
def test_broker_and_beat_down_reads_still_deny(settings, failure):
    from apps.governance.flag_models import FeatureFlag
    from tests.integration.c03.test_professional_setup import save

    subject, draft = published(
        settings, valid_until=timezone.now() + timedelta(hours=1)
    )
    api().refresh_public_projection(subject.profile.id, timezone.now())
    at = timezone.now()
    if failure == "flag_off":
        FeatureFlag.objects.filter(key="marketplace").update(enabled=False)
    elif failure == "flag_missing":
        FeatureFlag.objects.filter(key="marketplace").delete()
    elif failure == "source_edit":
        save(subject, "description", {"biography": "Unconfirmed private edit"})
    elif failure == "account_inactive":
        subject.user.is_active = False
        subject.user.save(update_fields=["is_active"])
    elif failure == "expiry":
        at = draft.valid_until
    else:
        from tests.integration.c03.test_verification_revocation import revoke

        revoke(subject, "identity")
    assert api().public_professional(subject.profile.id, at) is None
    assert api().refresh_public_projection(subject.profile.id, at).state == "tombstone"


def test_old_event_cannot_restore_withdrawn_or_staff_hidden_release(settings):
    from apps.professionals.publication_models import ProfessionalPublication

    subject, draft = published(settings)
    api().refresh_public_projection(subject.profile.id, timezone.now())
    row = ProfessionalPublication.objects.get(pk=draft.publication_id)
    row.hidden_at = timezone.now()
    row.hidden_case_uuid = uuid4()
    row.version += 1
    row.save()
    assert (
        api().refresh_public_projection(subject.profile.id, timezone.now()).state
        == "tombstone"
    )
    assert api().public_professional(subject.profile.id, timezone.now()) is None


def test_flag_repository_outage_returns_unavailable_without_content(
    settings, monkeypatch
):
    from django.db import OperationalError

    subject, draft = published(settings)

    def unavailable(*args, **kwargs):
        raise OperationalError("PRIVATE_PROVIDER_DETAIL")

    monkeypatch.setattr("config.use_cases.marketplace.feature_enabled", unavailable)
    from apps.marketplace.contracts import MarketplaceUnavailable

    with pytest.raises(MarketplaceUnavailable) as error:
        api().public_professional(subject.profile.id, timezone.now())
    assert "PRIVATE_PROVIDER_DETAIL" not in str(error.value)
