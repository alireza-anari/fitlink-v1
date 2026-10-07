"""Mutable ORM access, bulk operations and direct SQL cannot rewrite evidence."""

import pytest
from django.db import DatabaseError, IntegrityError, connection, transaction

from .conftest import require_model

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def submit(s):
    for target in s.targets.values():
        target.state = "submitted"
        target.save(update_fields=["state"])
    s.case.state, s.case.submitted_at = "submitted", s.at
    s.case.snapshot_hash = "d" * 64
    s.case.save()


@pytest.mark.parametrize("domain", ["athletes", "professionals"])
def test_profile_owner_is_permanent_in_direct_sql(schema_factory, domain):
    s = schema_factory()
    profile = s.profile
    if domain == "athletes":
        profile = require_model("AthleteProfile", domain).objects.create(user=s.owner)
    with (
        pytest.raises(DatabaseError),
        transaction.atomic(),
        connection.cursor() as cursor,
    ):
        cursor.execute(
            f'UPDATE "{profile._meta.db_table}" SET user_id = %s WHERE id = %s',
            [s.staff.pk, profile.pk],
        )


def test_submitted_role_profile_cannot_be_reparented(schema_factory):
    s = schema_factory()
    submit(s)
    with pytest.raises(DatabaseError), transaction.atomic():
        type(s.coach).objects.filter(pk=s.coach.pk).update(profile=s.foreign)


def test_role_kind_is_permanent_without_unique_collision(schema_factory):
    s = schema_factory()
    role = type(s.coach).objects.create(profile=s.foreign, role="coach")
    with (
        pytest.raises(DatabaseError),
        transaction.atomic(),
        connection.cursor() as cursor,
    ):
        cursor.execute(
            "UPDATE professionals_professionalrole SET role = %s WHERE id = %s",
            ["nutritionist", role.pk],
        )


@pytest.mark.parametrize("operation", ["foreign_parent", "reparent_draft"])
def test_baseline_ownership_anchor(schema_factory, operation):
    s = schema_factory()
    Profile = require_model("AthleteProfile", "athletes")
    Baseline = require_model("BaselineAssessment", "athletes")
    own = Profile.objects.create(user=s.owner)
    other = Profile.objects.create(user=s.other)
    parent = Baseline.objects.create(
        athlete=other,
        sequence=1,
        state="submitted",
        observed_at=s.at,
        submitted_at=s.at,
    )
    if operation == "foreign_parent":
        with pytest.raises(DatabaseError), transaction.atomic():
            Baseline.objects.create(
                athlete=own,
                parent=parent,
                sequence=1,
                observed_at=s.at,
            )
    else:
        draft = Baseline.objects.create(athlete=own, sequence=2, observed_at=s.at)
        with (
            pytest.raises(DatabaseError),
            transaction.atomic(),
            connection.cursor() as cursor,
        ):
            cursor.execute(
                "UPDATE athletes_baselineassessment SET athlete_id = %s WHERE id = %s",
                [other.pk, draft.pk],
            )


def decision(s, kind="coach", **changes):
    return require_model("VerificationDecision")(
        **{
            **dict(
                target=s.targets[kind],
                profile=s.profile,
                target_kind=kind,
                actor=s.staff,
                decision="approve",
                reason_code="credentials_approved",
                target_snapshot_hash="c" * 64,
                bound_evidence_revision=1,
                decision_sequence=1,
                decided_at=s.at,
            ),
            **changes,
        }
    )


def test_one_terminal_outcome_per_target(schema_factory):
    s = schema_factory()
    submit(s)
    first = decision(s)
    first.save()
    for change in (
        {"decision": "reject", "decision_sequence": 2},
        {"target_kind": "nutritionist"},
        {"profile": s.foreign},
    ):
        with pytest.raises(IntegrityError), transaction.atomic():
            type(first).objects.bulk_create([decision(s, **change)])
    second = decision(
        s, "nutritionist", decision="reject", reason_code="credentials_invalid"
    )
    second.save()
    assert type(first).objects.filter(decision="approve").count() == 1
    assert type(first).objects.filter(decision="reject").count() == 1


def test_role_specific_revoke_same_approval_and_unique_sequence(schema_factory):
    s = schema_factory()
    submit(s)
    approval = decision(s)
    approval.save()
    for row in (
        decision(
            s,
            "nutritionist",
            decision="revoke",
            revoked_approval=approval,
            decision_sequence=2,
        ),
        decision(s, decision="revoke", revoked_approval=None, decision_sequence=2),
        decision(s, decision="revoke", revoked_approval=approval, decision_sequence=1),
    ):
        with pytest.raises(IntegrityError), transaction.atomic():
            type(row).objects.bulk_create([row])
    revocation = decision(
        s,
        decision="revoke",
        revoked_approval=approval,
        supersedes_decision=approval,
        decision_sequence=2,
        reason_code="evidence_revoked",
    )
    revocation.save()
    with pytest.raises(IntegrityError), transaction.atomic():
        type(revocation).objects.bulk_create(
            [
                decision(
                    s, decision="revoke", revoked_approval=approval, decision_sequence=3
                )
            ]
        )


@pytest.mark.parametrize("operation", ["orm", "bulk", "sql_update", "sql_delete"])
def test_c03_evidence_append_only(schema_factory, operation):
    s = schema_factory()
    submit(s)
    row = decision(s)
    row.save()
    with pytest.raises((ValueError, DatabaseError)), transaction.atomic():
        if operation == "orm":
            row.explanation = "rewritten"
            row.save()
        elif operation == "bulk":
            type(row).objects.filter(pk=row.pk).update(explanation="rewritten")
        else:
            with connection.cursor() as cursor:
                if operation == "sql_update":
                    cursor.execute(
                        "UPDATE professionals_verificationdecision "
                        "SET explanation = %s WHERE id = %s",
                        ["rewritten", row.pk],
                    )
                else:
                    cursor.execute(
                        "DELETE FROM professionals_verificationdecision WHERE id = %s",
                        [row.pk],
                    )
    row.refresh_from_db()
    assert row.explanation == ""


@pytest.mark.parametrize(
    "table,field,value,lookup",
    [
        (
            "professionals_verificationtarget",
            "target_snapshot_hash",
            "e" * 64,
            "target",
        ),
        ("professionals_credentialrevision", "title", "rewritten", "revision"),
        ("professionals_verification", "snapshot_hash", "e" * 64, "case"),
    ],
)
def test_submitted_binding_and_source_snapshot_direct_sql_immutable(
    schema_factory, table, field, value, lookup
):
    s = schema_factory()
    submit(s)
    pk = {
        "target": s.targets["coach"].pk,
        "revision": s.revisions["coach"].pk,
        "case": s.case.pk,
    }[lookup]
    with (
        pytest.raises(DatabaseError),
        transaction.atomic(),
        connection.cursor() as cursor,
    ):
        cursor.execute(
            f'UPDATE "{table}" SET "{field}" = %s WHERE id = %s', [value, pk]
        )


def test_runtime_principal_cannot_update_delete_or_truncate_evidence(schema_factory):
    s = schema_factory()
    submit(s)
    row = decision(s)
    row.save()
    # An ordinary SQL principal has no DDL, trigger-disable or truncate authority.
    with connection.cursor() as cursor:
        cursor.execute("CREATE ROLE c03_evidence_probe NOLOGIN")
        cursor.execute("GRANT USAGE ON SCHEMA public TO c03_evidence_probe")
        cursor.execute(
            "GRANT SELECT, INSERT, UPDATE, DELETE "
            "ON professionals_verificationdecision TO c03_evidence_probe"
        )
    try:
        for command in (
            "UPDATE professionals_verificationdecision SET explanation = 'changed'",
            "DELETE FROM professionals_verificationdecision",
            "TRUNCATE professionals_verificationdecision CASCADE",
        ):
            with (
                pytest.raises(DatabaseError),
                transaction.atomic(),
                connection.cursor() as cursor,
            ):
                cursor.execute("SET LOCAL ROLE c03_evidence_probe")
                cursor.execute(command)
    finally:
        with connection.cursor() as cursor:
            cursor.execute("DROP OWNED BY c03_evidence_probe")
            cursor.execute("DROP ROLE c03_evidence_probe")


@pytest.mark.parametrize("name", ["VerificationHistory", "RoleRestrictionHistory"])
def test_reasoned_history_immutable_through_bulk_and_direct_sql(schema_factory, name):
    s = schema_factory()
    submit(s)
    Model = require_model(name)
    if name == "VerificationHistory":
        row = Model.objects.create(
            verification=s.case,
            target=s.targets["coach"],
            actor=s.staff,
            event="submit",
            reason_code="verification_submitted",
            prior_version=1,
            new_version=2,
            at=s.at,
        )
    else:
        restriction = require_model("ProfessionalRoleRestriction").objects.create(
            role=s.coach,
            verification=s.case,
            applied_by=s.staff,
            reason_code="role_restricted",
            applied_at=s.at,
        )
        row = Model.objects.create(
            restriction=restriction,
            actor=s.staff,
            event="applied",
            reason_code="role_restricted",
            prior_version=1,
            new_version=2,
            at=s.at,
        )
    with pytest.raises((ValueError, DatabaseError)), transaction.atomic():
        Model.objects.filter(pk=row.pk).update(reason_code="user_requested")
    with (
        pytest.raises(DatabaseError),
        transaction.atomic(),
        connection.cursor() as cursor,
    ):
        cursor.execute(f'DELETE FROM "{Model._meta.db_table}" WHERE id = %s', [row.pk])


def test_submitted_baseline_answers_are_immutable_and_current_pointer_is_owned(
    schema_factory,
):
    s = schema_factory()
    Athlete = require_model("AthleteProfile", "athletes")
    Baseline = require_model("BaselineAssessment", "athletes")
    athlete = Athlete.objects.create(user=s.owner)
    other = Athlete.objects.create(user=s.other)
    baseline = Baseline.objects.create(
        athlete=athlete,
        sequence=1,
        observed_at=s.at,
        goals=["strength"],
        experience="beginner",
        available_days=[1, 3],
        facilities=["home"],
        state="submitted",
        submitted_at=s.at,
    )
    with (
        pytest.raises(DatabaseError),
        transaction.atomic(),
        connection.cursor() as cursor,
    ):
        cursor.execute(
            "UPDATE athletes_baselineassessment SET weight_kg=80 WHERE id=%s",
            [baseline.pk],
        )
    with pytest.raises(IntegrityError), transaction.atomic():
        Athlete.objects.filter(pk=other.pk).update(current_baseline=baseline)
    # Superseding may change lifecycle only; historical answers remain identical.
    Baseline.objects.filter(pk=baseline.pk).update(state="superseded", version=2)
    baseline.refresh_from_db()
    assert baseline.goals == ["strength"] and baseline.weight_kg is None


@pytest.mark.parametrize("kind", ["bundle", "target", "baseline"])
def test_submitted_snapshot_cannot_reopen_as_editable_draft(schema_factory, kind):
    s = schema_factory()
    submit(s)
    if kind == "bundle":
        row = s.case
        changes = {"state": "draft", "submitted_at": None}
    elif kind == "target":
        row = s.targets["coach"]
        changes = {"state": "draft"}
    else:
        athlete = require_model("AthleteProfile", "athletes").objects.create(
            user=s.owner
        )
        row = require_model("BaselineAssessment", "athletes").objects.create(
            athlete=athlete,
            sequence=1,
            observed_at=s.at,
            state="submitted",
            submitted_at=s.at,
        )
        changes = {"state": "draft", "submitted_at": None}
    # Reopening must fail itself, before a second SQL statement rewrites answers.
    with pytest.raises(DatabaseError), transaction.atomic():
        type(row).objects.filter(pk=row.pk).update(**changes)


def test_submitted_bundle_cannot_gain_a_new_target(schema_factory):
    s = schema_factory()
    target = s.targets.pop("nutritionist")
    Evidence = require_model("VerificationEvidence")
    Evidence.objects.filter(target=target).delete()
    target.delete()
    submit(s)
    with pytest.raises(DatabaseError), transaction.atomic():
        type(target).objects.create(
            verification=s.case,
            target="nutritionist",
            role=s.nutritionist,
            bound_evidence_revision=1,
            bound_decision_version=1,
            bound_declaration_version=1,
            target_snapshot_hash="c" * 64,
        )


def test_submitted_target_cannot_gain_new_evidence(schema_factory):
    s = schema_factory()
    Evidence = require_model("VerificationEvidence")
    row = Evidence.objects.get(target=s.targets["coach"])
    values = {
        "target": row.target,
        "credential_revision": row.credential_revision,
        "category": row.category,
    }
    row.delete()
    submit(s)
    with pytest.raises(DatabaseError), transaction.atomic():
        Evidence.objects.create(**values)


def test_submitted_baseline_cannot_be_deleted_with_direct_sql(schema_factory):
    s = schema_factory()
    athlete = require_model("AthleteProfile", "athletes").objects.create(user=s.owner)
    baseline = require_model("BaselineAssessment", "athletes").objects.create(
        athlete=athlete,
        sequence=1,
        observed_at=s.at,
        state="submitted",
        submitted_at=s.at,
    )
    with pytest.raises(DatabaseError), transaction.atomic(), connection.cursor() as cur:
        cur.execute(
            "DELETE FROM athletes_baselineassessment WHERE id=%s", [baseline.pk]
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"reason_code": "private-value"},
        {"target_snapshot_hash": "private-value"},
        {"target_snapshot_hash": "f" * 64},
        {"bound_evidence_revision": 2},
    ],
)
def test_decision_metadata_matches_exact_target_snapshot(schema_factory, changes):
    s = schema_factory()
    submit(s)
    row = decision(s, **changes)
    with pytest.raises(IntegrityError), transaction.atomic():
        type(row).objects.bulk_create([row])


@pytest.mark.parametrize("field", ["source_sha256", "revision_hash"])
def test_credential_revision_hash_cannot_store_private_text(schema_factory, field):
    s = schema_factory()
    revision = s.revisions["coach"]
    revision.pk = None
    revision.sequence = 2
    setattr(revision, field, "private-value")
    with pytest.raises(IntegrityError), transaction.atomic():
        type(revision).objects.bulk_create([revision])


@pytest.mark.parametrize(
    "changes",
    [{"target": None}, {"reason_code": "private-value"}, {"new_version": 1}],
)
def test_target_history_requires_target_reason_and_advancing_version(
    schema_factory, changes
):
    s = schema_factory()
    values = dict(
        verification=s.case,
        target=s.targets["coach"],
        actor=s.staff,
        event="decision",
        reason_code="credentials_approved",
        prior_version=1,
        new_version=2,
        at=s.at,
    )
    values.update(changes)
    with pytest.raises(IntegrityError), transaction.atomic():
        require_model("VerificationHistory").objects.create(**values)


@pytest.mark.parametrize(
    "field,value",
    [
        ("sha256", "f" * 64),
        ("source_key", "replacement"),
        ("actual_size", 101),
        ("subject_uuid", None),
    ],
)
def test_accepted_evidence_source_binding_is_immutable(schema_factory, field, value):
    s = schema_factory()
    submit(s)
    asset = s.revisions["coach"].source_asset
    if field == "subject_uuid":
        value = s.foreign.pk
    with pytest.raises(DatabaseError), transaction.atomic():
        type(asset).objects.filter(pk=asset.pk).update(**{field: value})


@pytest.mark.parametrize("field", ["profile", "role", "category"])
def test_credential_identity_cannot_be_reclassified(schema_factory, field):
    s = schema_factory()
    submit(s)
    credential = s.revisions["coach"].credential
    changes = {
        "profile": {"profile": s.foreign, "role": None, "category": "identity"},
        "role": {"role": s.nutritionist},
        "category": {"category": "identity", "role": None},
    }[field]
    with pytest.raises(DatabaseError), transaction.atomic():
        type(credential).objects.filter(pk=credential.pk).update(**changes)


@pytest.mark.parametrize("defect", ["owner", "checksum", "purpose"])
def test_revision_source_matches_credential_owner_purpose_checksum(
    schema_factory, defect
):
    s = schema_factory()
    Asset = require_model("Asset", "assets")
    source = Asset.objects.create(
        owner=s.other if defect == "owner" else s.owner,
        subject_kind="professional_profile",
        subject_uuid=s.foreign.pk if defect == "owner" else s.profile.pk,
        purpose="avatar" if defect == "purpose" else "credential_evidence",
        upload_expires_at=s.at,
        sha256="f" * 64 if defect == "checksum" else "a" * 64,
    )
    revision = s.revisions["coach"]
    revision.pk = None
    revision.sequence = 2
    revision.source_asset = source
    with pytest.raises(IntegrityError), transaction.atomic():
        type(revision).objects.bulk_create([revision])


def test_target_history_cannot_bind_another_case(schema_factory):
    s = schema_factory()
    case = require_model("Verification").objects.create(profile=s.foreign, sequence=1)
    with pytest.raises(IntegrityError), transaction.atomic():
        require_model("VerificationHistory").objects.create(
            verification=case,
            target=s.targets["coach"],
            actor=s.staff,
            event="decision",
            reason_code="credentials_approved",
            prior_version=1,
            new_version=2,
            at=s.at,
        )
