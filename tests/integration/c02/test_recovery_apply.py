import threading
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from django.apps import apps
from django.db import DatabaseError, close_old_connections, connection, transaction
from django.utils import timezone
from test_otp_issue import record
from test_recovery_authorization import NEW, OLD, contract, owner, prepared
from test_sessions import request_with_session

from apps.accounts.contracts import SecurityOutcome

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def approved(settings, old=OLD, new=NEW):
    values = prepared(settings, old, new)
    recovery, commands, receipt, actor, staff, grant, step, case = values
    commands.resolve_recovery(
        actor, case.id, case.version, step, "identity_verified", timezone.now()
    )
    case.refresh_from_db()
    commands.add_recovery_evidence(
        actor,
        case.id,
        case.version,
        "identity_match",
        "verified",
        "a" * 64,
        uuid4(),
        step,
        "identity_verified",
        timezone.now(),
    )
    case.refresh_from_db()
    commands.decide_recovery(
        actor,
        case.id,
        case.version,
        "approved",
        "identity_verified",
        step,
        timezone.now(),
    )
    case.refresh_from_db()
    return values


def prove(commands, receipt, at=None):
    from apps.accounts.sms import MockSmsProvider

    provider = MockSmsProvider()
    at = at or timezone.now()
    result = commands.request_recovery_otp(
        receipt.request_uuid, receipt.raw_receipt, "127.0.0.1", at, provider=provider
    )
    code = provider.drain()[0].code
    proof = commands.verify_recovery_otp(
        receipt.request_uuid,
        receipt.raw_receipt,
        result.challenge_id,
        code,
        "127.0.0.1",
        at,
    )
    assert proof.valid
    return result.challenge_id


@pytest.mark.parametrize(
    "state,active", [("active", True), ("restricted", True), ("suspended", False)]
)
def test_recovery_updates_existing_identity_preserving_restrictions(
    limiter, settings, state, active
):
    from test_otp_issue import record

    from apps.accounts.sessions import issue_session, resolve_session

    target = owner(state=state, active=active)
    old_uuid, old_password = target.public_id, target.password
    request = request_with_session()
    if active:
        with transaction.atomic():
            issue_session(
                request,
                target,
                "normal" if state == "active" else "account_control",
                timezone.now(),
                record,
            )
    recovery, commands, receipt, actor, staff, grant, step, case = approved(settings)
    challenge = prove(commands, receipt)
    case.refresh_from_db()
    result = commands.apply_recovery(
        actor, case.id, case.version, step, "identity_verified", timezone.now()
    )
    target.refresh_from_db()
    assert target.public_id == old_uuid and target.password == old_password
    assert target.phone == NEW and target.state == state and target.is_active is active
    assert target.auth_version == 2 and target.birth_date is not None
    assert resolve_session(request, timezone.now()) is None
    assert (
        apps.get_model("accounts", "OTPChallenge")
        .objects.get(pk=challenge)
        .proof_applied_at
        is not None
    )
    history = apps.get_model("accounts", "PhoneChangeHistory").objects.get()
    assert (history.old_phone, history.new_phone, history.recovery_context) == (
        OLD,
        NEW,
        case.id,
    )
    replay = commands.apply_recovery(
        actor, case.id, case.version, step, "identity_verified", timezone.now()
    )
    assert (
        replay == result
        and apps.get_model("accounts", "PhoneChangeHistory").objects.count() == 1
    )
    assert (
        recovery.recovery_status(case.id, receipt.raw_receipt, timezone.now())
        == "closed"
    )


def test_unique_conflict_never_merges_and_rolls_back_proof(limiter, settings):
    target, destination = owner(), owner(NEW)
    recovery, commands, receipt, actor, staff, grant, step, case = approved(settings)
    challenge = prove(commands, receipt)
    case.refresh_from_db()
    with pytest.raises(recovery.RecoveryConflict):
        commands.apply_recovery(
            actor, case.id, case.version, step, "identity_verified", timezone.now()
        )
    target.refresh_from_db()
    assert target.phone == OLD and target.auth_version == 1
    assert (
        apps.get_model("accounts", "User").objects.get(pk=destination.pk).phone == NEW
    )
    assert (
        apps.get_model("accounts", "OTPChallenge")
        .objects.get(pk=challenge)
        .proof_applied_at
        is None
    )
    assert not apps.get_model("accounts", "PhoneChangeHistory").objects.exists()


def test_audit_failure_rolls_back_history_identity_proof(
    limiter, settings, monkeypatch
):
    target = owner()
    recovery, commands, receipt, actor, staff, grant, step, case = approved(settings)
    challenge = prove(commands, receipt)
    case.refresh_from_db()

    def failed(outcome, **kwargs):
        raise RuntimeError("audit unavailable")

    monkeypatch.setattr(commands, "record_security_outcome", failed)
    with pytest.raises(RuntimeError):
        commands.apply_recovery(
            actor, case.id, case.version, step, "identity_verified", timezone.now()
        )
    target.refresh_from_db()
    assert target.phone == OLD and target.auth_version == 1
    assert not apps.get_model("accounts", "PhoneChangeHistory").objects.exists()
    assert (
        apps.get_model("accounts", "OTPChallenge")
        .objects.get(pk=challenge)
        .proof_applied_at
        is None
    )


def test_history_model_queryset_and_direct_sql_are_immutable(limiter, settings):
    owner()
    recovery, commands, receipt, actor, staff, grant, step, case = approved(settings)
    prove(commands, receipt)
    case.refresh_from_db()
    commands.apply_recovery(
        actor, case.id, case.version, step, "identity_verified", timezone.now()
    )
    model = apps.get_model("accounts", "PhoneChangeHistory")
    history = model.objects.get()
    for operation in [
        lambda: model.objects.update(new_phone=OLD),
        history.delete,
        lambda: history.save(),
    ]:
        with pytest.raises(ValueError):
            operation()
    from django.db import connection

    for sql in [
        "UPDATE accounts_phonechangehistory SET new_phone=old_phone",
        "DELETE FROM accounts_phonechangehistory",
    ]:
        with (
            pytest.raises(DatabaseError),
            transaction.atomic(),
            connection.cursor() as cursor,
        ):
            cursor.execute(sql)


def test_unknown_and_known_cases_have_same_new_phone_transport(limiter, settings):
    recovery, commands = contract(settings)
    owner()
    for old, new in [(OLD, NEW), ("+989123456786", "+989123456781")]:
        receipt = recovery.open_recovery(old, new, "127.0.0.1", timezone.now(), record)
        prove(commands, receipt)
    assert apps.get_model("accounts", "User").objects.count() == 1
    assert not apps.get_model("accounts", "AccountSessionControl").objects.exists()


def test_receipt_and_evidence_selectors_never_cross_cases(limiter, settings):
    owner()
    recovery, commands, receipt, actor, staff, grant, step, case = approved(settings)
    foreign = recovery.open_recovery(
        "+989123456786",
        "+989123456781",
        "127.0.0.1",
        timezone.now(),
        record,
    )
    with pytest.raises(PermissionError):
        commands.recovery_detail(
            actor, foreign.request_uuid, step, "identity_verified", timezone.now()
        )
    evidence = apps.get_model("accounts", "RecoveryEvidenceMetadata").objects.get()
    assert (
        commands.evidence_detail(
            actor, case.id, evidence.id, step, "identity_verified", timezone.now()
        )
        is not None
    )
    assert (
        commands.evidence_detail(
            actor, case.id, uuid4(), step, "identity_verified", timezone.now()
        )
        is None
    )


def test_two_accounts_race_for_one_phone(limiter, settings):
    owner()
    owner("+989123456786")
    first = approved(settings)
    second = approved(settings, "+989123456786", NEW)
    for values in (first, second):
        # Independent valid proofs on one phone are serialized by its generation.
        # Retire/resend makes the first ineligible; it cannot acquire identity.
        values[7].refresh_from_db()
    prove(first[1], first[2])
    phone_state = apps.get_model("accounts", "OTPPhoneState")
    phone_state.objects.filter(phone=NEW).update(next_send_at=timezone.now())
    prove(second[1], second[2])
    barrier = threading.Barrier(2)

    def apply(values):
        close_old_connections()
        try:
            values[7].refresh_from_db()
            barrier.wait(timeout=10)
            try:
                values[1].apply_recovery(
                    values[3],
                    values[7].id,
                    values[7].version,
                    values[6],
                    "identity_verified",
                    timezone.now(),
                )
                return True
            except (PermissionError, values[0].RecoveryConflict):
                return False
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(apply, [first, second]))
    assert outcomes.count(True) == 1
    assert apps.get_model("accounts", "User").objects.filter(phone=NEW).count() == 1
    assert apps.get_model("accounts", "PhoneChangeHistory").objects.count() == 1


def test_apply_races_suspension_without_reactivation(limiter, settings):
    target = owner()
    values = approved(settings)
    recovery, commands, receipt, actor, staff, grant, step, case = values
    prove(commands, receipt)
    case.refresh_from_db()
    barrier = threading.Barrier(2)

    def apply():
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            try:
                commands.apply_recovery(
                    actor,
                    case.id,
                    case.version,
                    step,
                    "identity_verified",
                    timezone.now(),
                )
                return True
            except (PermissionError, recovery.RecoveryConflict):
                return False
        finally:
            close_old_connections()

    def suspend():
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            # Version-independent internal restriction, serialized on identity.
            from apps.accounts.state import invalidate_auth_locked, locked_identity

            with locked_identity(target.public_id) as current:
                current.state, current.is_active = "suspended", False
                current.state_version += 1
                current.save(update_fields=["state", "is_active", "state_version"])
                invalidate_auth_locked(current, timezone.now())
                record(
                    SecurityOutcome(
                        "account.state_changed",
                        "succeeded",
                        current.public_id,
                        uuid4(),
                        ("state", "auth_version"),
                        "security_restriction",
                    )
                )
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as pool:
        a, b = pool.submit(apply), pool.submit(suspend)
        a.result(timeout=20)
        b.result(timeout=20)
    target.refresh_from_db()
    assert not target.is_active and target.state == "suspended"
    assert (
        not apps.get_model("accounts", "AccountSessionControl")
        .objects.filter(user=target, revoked_at__isnull=True)
        .exists()
    )


def test_unresolved_proof_cannot_apply_after_staff_resolution(limiter, settings):
    target = owner()
    values = prepared(settings)
    recovery, commands, receipt, actor, staff, grant, step, case = values
    prove(commands, receipt)
    case.refresh_from_db()
    commands.resolve_recovery(
        actor, case.id, case.version, step, "identity_verified", timezone.now()
    )
    case.refresh_from_db()
    commands.add_recovery_evidence(
        actor,
        case.id,
        case.version,
        "identity_match",
        "verified",
        "a" * 64,
        uuid4(),
        step,
        "identity_verified",
        timezone.now(),
    )
    case.refresh_from_db()
    commands.decide_recovery(
        actor,
        case.id,
        case.version,
        "approved",
        "identity_verified",
        step,
        timezone.now(),
    )
    case.refresh_from_db()
    with pytest.raises((PermissionError, recovery.RecoveryConflict)):
        commands.apply_recovery(
            actor, case.id, case.version, step, "identity_verified", timezone.now()
        )
    target.refresh_from_db()
    assert target.phone == OLD


def test_history_failure_rolls_back_every_identity_effect(
    limiter, settings, monkeypatch
):
    target = owner()
    recovery, commands, receipt, actor, staff, grant, step, case = approved(settings)
    challenge = prove(commands, receipt)
    case.refresh_from_db()
    model = apps.get_model("accounts", "PhoneChangeHistory")

    def failed(*args, **kwargs):
        raise RuntimeError("history unavailable")

    monkeypatch.setattr(model, "save", failed)
    with pytest.raises(RuntimeError):
        commands.apply_recovery(
            actor, case.id, case.version, step, "identity_verified", timezone.now()
        )
    target.refresh_from_db()
    case.refresh_from_db()
    assert target.phone == OLD and target.auth_version == 1 and case.state == "approved"
    assert (
        apps.get_model("accounts", "OTPChallenge")
        .objects.get(pk=challenge)
        .proof_applied_at
        is None
    )
    assert not apps.get_model("governance", "OutboxEvent").objects.exists()


def test_history_restricted_runtime_role_has_no_mutation_privilege(limiter, settings):
    owner()
    recovery, commands, receipt, actor, staff, grant, step, case = approved(settings)
    prove(commands, receipt)
    case.refresh_from_db()
    commands.apply_recovery(
        actor, case.id, case.version, step, "identity_verified", timezone.now()
    )
    role = "c02_history_" + uuid4().hex
    q = connection.ops.quote_name
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE ROLE {q(role)} NOLOGIN")
        cursor.execute(f"GRANT USAGE ON SCHEMA public TO {q(role)}")
        cursor.execute(
            f"GRANT SELECT, INSERT ON accounts_phonechangehistory TO {q(role)}"
        )
    try:
        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute(f"SET LOCAL ROLE {q(role)}")
            cursor.execute("SELECT count(*) FROM accounts_phonechangehistory")
            assert cursor.fetchone()[0] == 1
            cursor.execute(
                """INSERT INTO accounts_phonechangehistory
                (id,user_id,old_phone,new_phone,recovery_context,change_context,
                actor_uuid,at,old_auth_version,new_auth_version)
                SELECT %s,user_id,old_phone,new_phone,%s,NULL,actor_uuid,at,
                old_auth_version,new_auth_version FROM accounts_phonechangehistory
                LIMIT 1""",
                [uuid4(), uuid4()],
            )
            cursor.execute("SELECT count(*) FROM accounts_phonechangehistory")
            assert cursor.fetchone()[0] == 2
        for sql in [
            "UPDATE accounts_phonechangehistory SET old_phone=new_phone",
            "DELETE FROM accounts_phonechangehistory",
            "TRUNCATE accounts_phonechangehistory",
        ]:
            with (
                pytest.raises(DatabaseError),
                transaction.atomic(),
                connection.cursor() as cursor,
            ):
                cursor.execute(f"SET LOCAL ROLE {q(role)}")
                cursor.execute(sql)
    finally:
        with connection.cursor() as cursor:
            cursor.execute(f"DROP OWNED BY {q(role)}")
            cursor.execute(f"DROP ROLE {q(role)}")


def test_outbox_failure_rolls_back_identity_and_audit(limiter, settings, monkeypatch):
    target = owner()
    recovery, commands, receipt, actor, staff, grant, step, case = approved(settings)
    challenge = prove(commands, receipt)
    case.refresh_from_db()
    audit = apps.get_model("governance", "AuditEvent")
    count = audit.objects.count()

    def failed(*args, **kwargs):
        raise RuntimeError("outbox unavailable")

    monkeypatch.setattr(commands, "append_outbox", failed)
    with pytest.raises(RuntimeError):
        commands.apply_recovery(
            actor, case.id, case.version, step, "identity_verified", timezone.now()
        )
    target.refresh_from_db()
    case.refresh_from_db()
    assert target.phone == OLD and target.auth_version == 1 and case.state == "approved"
    assert audit.objects.count() == count
    assert not apps.get_model("accounts", "PhoneChangeHistory").objects.exists()
    assert (
        apps.get_model("accounts", "OTPChallenge")
        .objects.get(pk=challenge)
        .proof_applied_at
        is None
    )


@pytest.mark.parametrize("defect", ["expired", "generation", "purpose", "version"])
def test_apply_rechecks_durable_proof_binding_and_age(limiter, settings, defect):
    target = owner()
    recovery, commands, receipt, actor, staff, grant, step, case = approved(settings)
    challenge = prove(commands, receipt)
    case.refresh_from_db()
    proof = apps.get_model("accounts", "OTPChallenge").objects.get(pk=challenge)
    at = timezone.now()
    if defect == "expired":
        at = proof.expires_at
    elif defect == "generation":
        apps.get_model("accounts", "OTPPhoneState").objects.filter(
            pk=proof.phone_state_id
        ).update(generation=proof.generation + 1)
    elif defect == "purpose":
        type(proof).objects.filter(pk=proof.pk).update(purpose="phone_change_new")
    else:
        type(proof).objects.filter(pk=proof.pk).update(
            target_auth_version=target.auth_version + 1
        )
    with pytest.raises(recovery.RecoveryConflict):
        commands.apply_recovery(
            actor, case.id, case.version, step, "identity_verified", at
        )
    target.refresh_from_db()
    assert target.phone == OLD and target.auth_version == 1
    assert not apps.get_model("accounts", "PhoneChangeHistory").objects.exists()


def test_staff_evidence_reads_are_audited_and_audit_outage_denies(
    limiter, settings, monkeypatch
):
    owner()
    recovery, commands, receipt, actor, staff, grant, step, case = approved(settings)
    audit = apps.get_model("governance", "AuditEvent")
    evidence = apps.get_model("accounts", "RecoveryEvidenceMetadata").objects.get()
    before = audit.objects.filter(
        action="recovery.evidence", correlation_id=case.id
    ).count()
    commands.recovery_detail(actor, case.id, step, "identity_verified", timezone.now())
    commands.evidence_detail(
        actor, case.id, evidence.id, step, "identity_verified", timezone.now()
    )
    assert (
        audit.objects.filter(action="recovery.evidence", correlation_id=case.id).count()
        == before + 2
    )

    def failed(*args, **kwargs):
        raise RuntimeError("audit unavailable")

    monkeypatch.setattr(commands, "record_security_outcome", failed)
    with pytest.raises(RuntimeError):
        commands.evidence_detail(
            actor, case.id, evidence.id, step, "identity_verified", timezone.now()
        )


def test_resolved_proof_issued_before_approval_cannot_restore_identity(
    limiter, settings
):
    target = owner()
    recovery, commands, receipt, actor, staff, grant, step, case = prepared(settings)
    commands.resolve_recovery(
        actor, case.id, case.version, step, "identity_verified", timezone.now()
    )
    prove(commands, receipt)
    case.refresh_from_db()
    commands.add_recovery_evidence(
        actor,
        case.id,
        case.version,
        "identity_match",
        "verified",
        "a" * 64,
        uuid4(),
        step,
        "identity_verified",
        timezone.now(),
    )
    case.refresh_from_db()
    commands.decide_recovery(
        actor,
        case.id,
        case.version,
        "approved",
        "identity_verified",
        step,
        timezone.now(),
    )
    case.refresh_from_db()
    with pytest.raises(recovery.RecoveryConflict):
        commands.apply_recovery(
            actor, case.id, case.version, step, "identity_verified", timezone.now()
        )
    target.refresh_from_db()
    assert target.phone == OLD and target.auth_version == 1
