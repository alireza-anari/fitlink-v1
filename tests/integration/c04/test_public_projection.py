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
        "pending_deletion",
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
    elif failure in {"account_inactive", "pending_deletion"}:
        from apps.accounts.state import transition_account_state
        from apps.governance.audit import append_event

        transition_account_state(
            subject.user.public_id,
            subject.user.auth_version,
            "suspended" if failure == "account_inactive" else "pending_deletion",
            at,
            append_event,
        )
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
    from types import SimpleNamespace

    from django.db import transaction

    from config.event_handlers import HANDLERS

    old = SimpleNamespace(
        aggregate_uuid=row.id,
        aggregate_version=draft.version,
        payload={
            "publication_uuid": str(row.id),
            "user_uuid": str(subject.user.public_id),
        },
    )
    with transaction.atomic():
        assert (
            HANDLERS["professional.publication_changed"](old, timezone.now())
            == "skipped"
        )
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


@pytest.mark.parametrize(
    "defect", ["private_field", "foreign_release", "old_generation"]
)
def test_direct_sql_cannot_cross_bind_or_pollute_projection(settings, defect):
    from django.db import DatabaseError, transaction

    from apps.marketplace.models import PublicProfessionalProjection

    subject, draft = published(settings)
    api().refresh_public_projection(subject.profile.id, timezone.now())
    api().refresh_public_projection(subject.profile.id, timezone.now())
    row = PublicProfessionalProjection.objects.get(pk=subject.profile.id)
    values = {
        "private_field": {
            "snapshot": {**row.snapshot, "identity_name": "PRIVATE_SENTINEL"}
        },
        "foreign_release": {"publication_uuid": uuid4()},
        "old_generation": {"generation": row.generation - 1},
    }[defect]
    with pytest.raises(DatabaseError), transaction.atomic():
        PublicProfessionalProjection.objects.filter(pk=row.pk).update(**values)


def test_rebuilt_disposable_index_preserves_durable_generation(settings):
    from apps.marketplace.models import PublicProfessionalProjection

    subject, draft = published(settings)
    first = api().refresh_public_projection(subject.profile.id, timezone.now())
    previous = api().refresh_public_projection(subject.profile.id, timezone.now())
    assert previous.generation > first.generation
    PublicProfessionalProjection.objects.filter(pk=subject.profile.id).delete()
    rebuilt = api().refresh_public_projection(subject.profile.id, timezone.now())
    assert rebuilt.generation > previous.generation


@pytest.mark.parametrize("defect", ["state_zero", "cursor_zero", "state_rebind"])
def test_durable_projection_metadata_rejects_invalid_identity_or_version(
    settings, defect
):
    from django.db import DatabaseError, transaction

    from apps.marketplace.models import ProjectionRefreshState, PublicationScanCursor

    subject, draft = published(settings)
    api().reconcile_publications(timezone.now(), 100)
    if defect == "cursor_zero":
        query = PublicationScanCursor.objects.all()
        values = {"version": 0}
    else:
        query = ProjectionRefreshState.objects.filter(pk=subject.profile.id)
        values = (
            {"generation": 0} if defect == "state_zero" else {"profile_uuid": uuid4()}
        )
    with pytest.raises(DatabaseError), transaction.atomic():
        assert query.update(**values) == 1


def test_projection_metrics_count_missing_due_and_exhausted_work_without_content(
    settings,
):
    import json

    from apps.governance.outbox_models import OutboxEvent
    from apps.marketplace.models import ProjectionRefreshState

    subject, draft = published(settings)
    initial = api().projection_metrics(timezone.now()).as_dict()
    assert initial["backlog"] == 1 and initial["exhausted"] == 0
    api().refresh_public_projection(subject.profile.id, timezone.now())
    now = timezone.now()
    assert api().projection_metrics(now).backlog == 0
    ProjectionRefreshState.objects.filter(pk=subject.profile.id).update(
        due_at=now - timedelta(seconds=60)
    )
    # A constraint-valid exhausted metadata fixture, never a delivery PASS.
    events = OutboxEvent.objects.filter(
        event_type="professional.publication_changed",
        aggregate_uuid=draft.publication_id,
    )
    count = events.count()
    assert count > 0
    events.update(
        state="exhausted",
        attempts=8,
        exhausted_at=now,
        lease_uuid=None,
        lease_until=None,
        last_error_code="attempts_exhausted",
    )
    metrics = api().projection_metrics(now, purges=2).as_dict()
    assert metrics["backlog"] == 1 and metrics["oldest_age_seconds"] >= 60
    assert (
        metrics["exhausted"] == count
        and metrics["failures"] == count
        and metrics["purges"] == 2
    )
    assert all(type(value) is int for value in metrics.values())
    assert "Private" not in json.dumps(metrics) and str(
        subject.profile.id
    ) not in json.dumps(metrics)


def test_flag_event_requests_bounded_global_rescan_without_replacing_its_effect(
    settings,
):
    from types import SimpleNamespace

    from django.db import transaction

    from apps.governance.flag_models import FeatureFlag
    from apps.marketplace.models import PublicationScanCursor
    from config.event_handlers import HANDLERS

    subject, draft = published(settings)
    api().reconcile_publications(timezone.now(), 100)
    cursor = PublicationScanCursor.objects.get(name="publications")
    assert cursor.after_uuid == subject.profile.id
    previous = cursor.version
    flag = FeatureFlag.objects.get(key="marketplace")
    event = SimpleNamespace(
        event_type="feature_flag.changed",
        aggregate_uuid=flag.id,
        aggregate_version=flag.version,
        payload={"flag_uuid": str(flag.id)},
    )
    with transaction.atomic():
        assert HANDLERS["feature_flag.changed"](event, timezone.now()) == "applied"
    cursor.refresh_from_db()
    assert cursor.after_uuid is None and cursor.version > previous
