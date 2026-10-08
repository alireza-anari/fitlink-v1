"""Resume, optimistic receipts and immutable dated corrections on PostgreSQL."""

from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from django.db import IntegrityError, ProgrammingError, transaction

from apps.athletes.baseline_models import BaselineAssessment
from apps.athletes.models import AthleteProfile
from apps.athletes.receipt_models import ProfileCommandReceipt

from .baseline_helpers import command, grant, input_value, required, save, setup
from .profile_helpers import create, make_actor

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_resume_partial_steps():
    ctx, row = setup()
    row = save(ctx, row, "goals", {"goals": ["strength"]})
    profile = AthleteProfile.objects.get(user=ctx.user)
    resumed = command("begin_baseline", ctx.actor, profile.version, uuid4(), ctx.at)
    assert resumed.id == row.id and resumed.version == row.version
    assert resumed.answers["goals"] == ["strength"]
    assert BaselineAssessment.objects.filter(athlete=profile).count() == 1
    assert row.observed_at == ctx.at and row.age_at_assessment >= 18
    assert row.provenance == "self_reported"


def test_optional_decline_is_unknown_and_completes_setup():
    ctx, row = setup()
    row = required(ctx, row)
    submitted = command(
        "submit_baseline", ctx.actor, row.id, row.version, uuid4(), ctx.at
    )
    assert submitted.state == "submitted"
    assert submitted.answers["height_cm"] is None
    assert submitted.optional_access is False
    profile = AthleteProfile.objects.get(user=ctx.user)
    assert profile.status == "active" and profile.current_baseline_id == row.id


def test_submit_requires_only_non_sensitive_setup():
    ctx, row = setup()
    with pytest.raises(ValueError):
        command("submit_baseline", ctx.actor, row.id, row.version, uuid4(), ctx.at)
    assert BaselineAssessment.objects.get(pk=row.id).state == "draft"


def test_submit_freezes_answers_and_correction_new_snapshot():
    ctx, row = setup()
    grant(ctx, row)
    row = save(ctx, required(ctx, row), "basics", {"height_cm": "170.1"})
    old = command("submit_baseline", ctx.actor, row.id, row.version, uuid4(), ctx.at)
    with pytest.raises(ValueError):
        save(ctx, old, "goals", {"goals": ["endurance"]})
    with pytest.raises(ProgrammingError) as frozen, transaction.atomic():
        BaselineAssessment.objects.filter(pk=old.id).update(height_cm=Decimal("180"))
    assert frozen.value.__cause__.sqlstate == "42501"
    correction = command(
        "correct_baseline",
        ctx.actor,
        old.id,
        old.version,
        uuid4(),
        ctx.at + timedelta(seconds=1),
    )
    assert (
        correction.id != old.id
        and correction.parent == old.id
        and correction.sequence == 2
    )
    assert correction.answers["goals"] == ["strength"]
    assert correction.answers["height_cm"] is None
    assert not correction.optional_access
    corrected = command(
        "submit_baseline",
        ctx.actor,
        correction.id,
        correction.version,
        uuid4(),
        ctx.at + timedelta(seconds=2),
    )
    stored = BaselineAssessment.objects.get(pk=old.id)
    assert stored.state == "superseded" and stored.height_cm == Decimal("170.1")
    assert corrected.state == "submitted"


def test_save_retry_reconstructs_current_dto_and_conflicts_changed_input():
    ctx, row = setup()
    key = uuid4()
    first = save(ctx, row, "goals", {"goals": ["strength"]}, key)
    current = save(ctx, first, "experience", {"experience": "advanced"})
    retry = command(
        "save_baseline_step",
        ctx.actor,
        row.id,
        "goals",
        input_value({"goals": ["strength"]}),
        row.version,
        key,
        ctx.at,
    )
    assert (
        retry.version == current.version and retry.answers["experience"] == "advanced"
    )
    assert (
        ProfileCommandReceipt.objects.filter(owner=ctx.user, operation_id=key).count()
        == 1
    )
    with pytest.raises(ValueError):
        command(
            "save_baseline_step",
            ctx.actor,
            row.id,
            "goals",
            input_value({"goals": ["endurance"]}),
            row.version,
            key,
            ctx.at,
        )
    with pytest.raises(ValueError):
        command(
            "save_baseline_step",
            ctx.actor,
            row.id,
            "goals",
            input_value({"goals": ["endurance"]}),
            row.version,
            uuid4(),
            ctx.at,
        )


@pytest.mark.parametrize("name", ["save", "submit", "correct", "read", "clear"])
def test_foreign_and_missing_baseline_uniformly_unavailable(name):
    ctx, row = setup()
    other = make_actor("+989123456781")
    create("athletes", other.actor, uuid4(), other.at)
    for identifier in (row.id, uuid4()):
        with pytest.raises(LookupError, match="Baseline unavailable"):
            if name == "read":
                command("own_baseline", other.actor, identifier, other.at)
            elif name == "save":
                command(
                    "save_baseline_step",
                    other.actor,
                    identifier,
                    "goals",
                    input_value({"goals": ["strength"]}),
                    1,
                    uuid4(),
                    other.at,
                )
            else:
                command(
                    {
                        "submit": "submit_baseline",
                        "correct": "correct_baseline",
                        "clear": "clear_optional_baseline",
                    }[name],
                    other.actor,
                    identifier,
                    1,
                    uuid4(),
                    other.at,
                )


def test_invalid_onboarding_step_sql_rejected():
    ctx = make_actor()
    profile = create("athletes", ctx.actor, uuid4(), ctx.at)
    with pytest.raises(IntegrityError), transaction.atomic():
        AthleteProfile.objects.filter(pk=profile.id).update(
            onboarding_step="health_upload"
        )


def test_baseline_change_audit_failure_rolls_back(monkeypatch):
    ctx, row = setup()
    composition = __import__(
        "config.use_cases.athlete_profile", fromlist=["append_event"]
    )

    def fail(*_args, **_kwargs):
        raise RuntimeError("audit unavailable")

    monkeypatch.setattr(composition, "append_event", fail)
    with pytest.raises(RuntimeError, match="audit unavailable"):
        save(ctx, row, "goals", {"goals": ["strength"]})
    stored = BaselineAssessment.objects.get(pk=row.id)
    assert stored.version == row.version and stored.goals == []
