"""Real PostgreSQL constraints, zero automatic profiles and additive upgrade."""

from datetime import timedelta
from uuid import uuid4

import pytest
from django.apps import apps
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.utils import timezone

from .conftest import require_model

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def reject(model, **values):
    with pytest.raises(IntegrityError), transaction.atomic():
        model.objects.bulk_create([model(**values)])


def test_optional_profiles_not_created():
    Athlete = require_model("AthleteProfile", "athletes")
    Professional = require_model("ProfessionalProfile")
    assert connection.vendor == "postgresql"
    user = apps.get_model("accounts", "User").objects.create_user("+989123456780")
    before = (user.pk, user.public_id, user.phone, user.password, user.auth_version)
    executor = MigrationExecutor(connection)
    # Latest migrations are idempotent and must never backfill optional profiles.
    executor.migrate(executor.loader.graph.leaf_nodes())
    user.refresh_from_db()
    assert before == (
        user.pk,
        user.public_id,
        user.phone,
        user.password,
        user.auth_version,
    )
    assert Athlete.objects.count() == Professional.objects.count() == 0
    assert "auth_user" not in connection.introspection.table_names()


def test_c03_unique_profiles_roles_live_drafts_verification_assignment(schema_factory):
    s = schema_factory()
    reject(type(s.profile), user=s.owner)
    reject(type(s.coach), profile=s.profile, role="coach")
    reject(type(s.coach), profile=s.profile, role="both")
    reject(type(s.coach), profile=s.profile, role="coach", evidence_revision=0)
    reject(type(s.case), profile=s.profile, sequence=2)
    Athlete = require_model("AthleteProfile", "athletes")
    athlete = Athlete.objects.create(user=s.owner)
    reject(Athlete, user=s.owner)
    Baseline = require_model("BaselineAssessment", "athletes")
    Baseline.objects.create(athlete=athlete, sequence=1, observed_at=s.at)
    reject(Baseline, athlete=athlete, sequence=2, observed_at=s.at)
    reject(
        Baseline,
        athlete=athlete,
        sequence=3,
        observed_at=s.at,
        state="submitted",
        submitted_at=None,
    )
    Assignment = require_model("VerificationAssignment")
    Assignment.objects.create(
        verification=s.case, assignee=s.staff, assigned_by=s.other
    )
    reject(Assignment, verification=s.case, assignee=s.other, assigned_by=s.staff)
    reject(Assignment, verification=s.case, assignee=s.owner, assigned_by=s.staff)


def test_target_identity_role_null_and_evidence_match(schema_factory):
    s = schema_factory()
    Target = require_model("VerificationTarget")
    for values in (
        dict(target="identity", role=s.coach, bound_declaration_version=1),
        dict(target="coach", role=None, bound_declaration_version=None),
        dict(target="coach", role=s.nutritionist, bound_declaration_version=1),
        dict(
            target="nutritionist", role=s.nutritionist, bound_declaration_version=None
        ),
    ):
        reject(Target, verification=s.case, target_snapshot_hash="c" * 64, **values)
    Evidence = require_model("VerificationEvidence")
    reject(
        Evidence,
        target=s.targets["coach"],
        credential_revision=s.revisions["nutritionist"],
        category="qualification",
    )
    Credential = require_model("Credential")
    for category, role in (("identity", s.coach), ("qualification", None)):
        reject(Credential, profile=s.profile, category=category, role=role)
    foreign_role = require_model("ProfessionalRole").objects.create(
        profile=s.foreign, role="coach"
    )
    reject(Credential, profile=s.profile, category="qualification", role=foreign_role)


def test_one_current_restriction_and_immutable_history(schema_factory):
    s = schema_factory()
    Restriction = require_model("ProfessionalRoleRestriction")
    values = dict(
        role=s.coach,
        verification=s.case,
        applied_by=s.staff,
        reason_code="role_restricted",
        applied_at=s.at,
    )
    restriction = Restriction.objects.create(**values)
    reject(Restriction, **values)
    # A release needs both actor and time; NULL must not evade the CHECK.
    with pytest.raises(IntegrityError), transaction.atomic():
        Restriction.objects.filter(pk=restriction.pk).update(
            released_at=s.at, released_by=None
        )
    restriction.released_by, restriction.released_at = s.staff, s.at
    restriction.version = 2
    restriction.save()
    Restriction.objects.create(**values)
    assert (
        Restriction.objects.filter(role=s.coach, released_at__isnull=True).count() == 1
    )
    assert s.coach.evidence_revision == s.coach.decision_version == 1


def test_c03_metadata_payload_denies_private_values():
    from apps.governance.outbox_models import OutboxEvent
    from apps.governance.staff_models import StaffCapabilityGrant

    require_model("ProfessionalProfile")
    owner = apps.get_model("accounts", "User").objects.create_user("+989123456780")
    issuer = apps.get_model("accounts", "User").objects.create_user("+989123456781")
    at = timezone.now()
    StaffCapabilityGrant.objects.create(
        user=owner,
        granted_by=issuer,
        capability="professional_verification",
        reason_code="staff_assigned",
        valid_until=at + timedelta(hours=1),
    )
    aggregate = uuid4()
    valid = dict(
        event_type="asset.processing_requested",
        aggregate_uuid=aggregate,
        aggregate_version=1,
        payload={"asset_uuid": str(aggregate), "user_uuid": str(owner.public_id)},
        dedup_key=str(uuid4()),
    )
    OutboxEvent.objects.bulk_create([OutboxEvent(**valid)])
    for value in (
        "https://private.invalid/signed",
        "PRIVATE-DOCUMENT",
        {"name": "PRIVATE"},
        None,
    ):
        reject(
            OutboxEvent,
            **{**valid, "dedup_key": str(uuid4()), "payload": {"asset_uuid": value}},
        )
    reject(
        OutboxEvent,
        **{**valid, "dedup_key": str(uuid4()), "payload": {"document": str(uuid4())}},
    )
