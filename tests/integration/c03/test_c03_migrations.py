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


@pytest.mark.parametrize(
    "field,value",
    [
        ("height_cm", 49),
        ("height_cm", 251),
        ("weight_kg", 19),
        ("weight_kg", 401),
        ("waist_cm", 19),
        ("waist_cm", 251),
        ("sleep_hours", 25),
        ("energy", 0),
        ("energy", 11),
        ("meals_per_day", 13),
        ("training_experience_months", 1201),
        ("experience", "medical"),
        ("lifestyle", "private-sentinel"),
        ("hydration_habit", "private-data"),
    ],
)
def test_baseline_sql_rejects_out_of_contract_values(schema_factory, field, value):
    s = schema_factory()
    athlete = require_model("AthleteProfile", "athletes").objects.create(user=s.owner)
    reject(
        require_model("BaselineAssessment", "athletes"),
        athlete=athlete,
        sequence=1,
        observed_at=s.at,
        **{field: value},
    )


@pytest.mark.parametrize(
    "field,value",
    [("experience_years", 81), ("accent_color", "red"), ("setup_step", "payments")],
)
def test_professional_sql_rejects_out_of_contract_values(schema_factory, field, value):
    s = schema_factory()
    with pytest.raises(IntegrityError), transaction.atomic():
        type(s.profile).objects.filter(pk=s.profile.pk).update(**{field: value})


@pytest.mark.parametrize(
    "field,value",
    [
        ("declared_size", 10_000_001),
        ("actual_size", 10_000_001),
        ("declared_type", "text/html"),
        ("detected_type", "image/svg+xml"),
        ("sha256", "private-value"),
        ("subject_kind", "public_athlete"),
    ],
)
def test_asset_sql_rejects_out_of_contract_values(schema_factory, field, value):
    s = schema_factory()
    asset = s.revisions["coach"].source_asset
    with pytest.raises(IntegrityError), transaction.atomic():
        type(asset).objects.filter(pk=asset.pk).update(**{field: value})


def test_assistant_metadata_cannot_reference_profile_owner(schema_factory):
    s = schema_factory()
    reject(require_model("AssistantMembership"), profile=s.profile, assistant=s.owner)


@pytest.mark.parametrize("label", ["athletes", "professionals"])
@pytest.mark.parametrize(
    "changes", [{"command": "private-data"}, {"request_hash": "private-data"}]
)
def test_receipt_cannot_store_unbounded_command_or_hash(schema_factory, label, changes):
    s = schema_factory()
    reject(
        require_model("ProfileCommandReceipt", label),
        **{
            "owner": s.owner,
            "operation_id": uuid4(),
            "command": "profile.create",
            "request_hash": "a" * 64,
            "object_uuid": s.profile.pk,
            "resulting_version": 1,
            **changes,
        },
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("goals", {"injuries": "private-data"}),
        ("goals", ["medical"]),
        ("goals", ["strength"] * 6),
        ("available_days", [0]),
        ("available_days", [8]),
        ("available_days", [1, 1]),
        ("available_days", ["1"]),
        ("equipment", ["medication"]),
        ("facilities", ["clinic"]),
        ("approximate_records", [{"injuries": "private-data"}]),
    ],
)
def test_baseline_json_cannot_bypass_typed_schema(schema_factory, field, value):
    s = schema_factory()
    athlete = require_model("AthleteProfile", "athletes").objects.create(user=s.owner)
    reject(
        require_model("BaselineAssessment", "athletes"),
        athlete=athlete,
        sequence=1,
        observed_at=s.at,
        **{field: value},
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("specialties", {"private": "data"}),
        ("specialties", ["x" * 65]),
        ("specialties", [str(i) for i in range(11)]),
        ("languages", ["bad tag"]),
        ("languages", ["fa"] * 6),
        ("service_modes", ["clinic"]),
    ],
)
def test_professional_json_cannot_bypass_typed_schema(schema_factory, field, value):
    s = schema_factory()
    with pytest.raises(IntegrityError), transaction.atomic():
        type(s.profile).objects.filter(pk=s.profile.pk).update(**{field: value})


@pytest.mark.parametrize(
    "defect", ["reason", "time", "history_reason", "history_version"]
)
def test_restriction_has_reasoned_forward_history(schema_factory, defect):
    s = schema_factory()
    Restriction = require_model("ProfessionalRoleRestriction")
    values = dict(
        role=s.coach,
        verification=s.case,
        applied_by=s.staff,
        reason_code="role_restricted",
        applied_at=s.at,
    )
    if defect == "reason":
        reject(Restriction, **{**values, "reason_code": "private-data"})
    elif defect == "time":
        reject(
            Restriction,
            **values,
            released_by=s.staff,
            released_at=s.at - timedelta(seconds=1),
        )
    else:
        row = Restriction.objects.create(**values)
        reject(
            require_model("RoleRestrictionHistory"),
            restriction=row,
            actor=s.staff,
            event="applied",
            at=s.at,
            prior_version=1,
            new_version=1 if defect == "history_version" else 2,
            reason_code="private-data"
            if defect == "history_reason"
            else "role_restricted",
        )
