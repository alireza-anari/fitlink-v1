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
