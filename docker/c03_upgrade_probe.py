"""Task 14 preservation boundary; actual compatibility proof remains pending."""

import json
import os
import re
import sys
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from uuid import uuid4


def private_log_metadata(path):
    """Bounded static diagnostics only; private error text never leaves the host."""
    with Path(path).open("rb") as stream:
        stream.seek(0, 2)
        stream.seek(max(0, stream.tell() - 65536))
        text = stream.read(65536).decode(errors="replace")
    exceptions = {
        name
        for name in (
            "AssertionError",
            "ValueError",
            "RuntimeError",
            "PermissionError",
            "IntegrityError",
            "OperationalError",
            "ImproperlyConfigured",
            "CalledProcessError",
            "ModuleNotFoundError",
            "ConnectionError",
        )
        if re.search(r"\b" + name + r"\b", text)
    }
    root = Path(__file__).resolve().parents[1]
    known_tests = {
        p.relative_to(root).as_posix() for p in (root / "tests").rglob("test_*.py")
    }
    tests = {
        path + "::" + name
        for path, name in re.findall(
            r"(tests/(?:[a-z0-9_]+/)*test_[a-z0-9_]+\.py)::([a-zA-Z_][a-zA-Z0-9_]*)",
            text,
        )
        if path in known_tests
    }
    sources = {p.name for p in (root / "apps").rglob("*.py")}
    sources |= {p.name for p in (root / "config").rglob("*.py")}
    sources |= {"probe.py", "manage.py", "subprocess.py"}
    locations = [
        {"file": Path(filename).name, "line": int(line)}
        for filename, line in re.findall(r'File "([^"\n]+\.py)", line ([0-9]+)', text)
        if Path(filename).name in sources
    ][-12:]
    counts = {
        name: [int(n) for n in re.findall(r"\b([0-9]+) " + name + r"\b", text)][-16:]
        for name in ("passed", "failed", "skipped")
    }
    infrastructure = [
        name
        for name, pattern in (
            ("build_failure", r"failed to (?:build|solve)"),
            ("registry_rate_limit", r"(?:toomanyrequests|pull rate limit)"),
            ("service_unhealthy", r"(?:unhealthy|failed to start)"),
            ("connection_refused", r"[Cc]onnection refused"),
            ("dependency_download", r"[Ff]ailed to (?:download|fetch)"),
        )
        if re.search(pattern, text)
    ]
    return {
        "exceptions": sorted(exceptions),
        "tests": sorted(tests)[-24:],
        "locations": locations,
        "counts": counts,
        "infrastructure": infrastructure,
    }


def snapshot(connection):
    """Private snapshot of every installed table and its physical identity."""
    tables = {}
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT relname, oid FROM pg_class "
            "WHERE relnamespace = 'public'::regnamespace AND relkind = 'r' "
            "ORDER BY relname"
        )
        identities = cursor.fetchall()
        for name, oid in identities:
            table = connection.ops.quote_name(name)
            cursor.execute(f"SELECT row_to_json(t)::text FROM {table} t")
            rows = sorted(row[0] for row in cursor.fetchall())
            tables[name] = {"oid": oid, "count": len(rows), "rows": rows}
        cursor.execute("SELECT oid FROM pg_database WHERE datname=current_database()")
        database_oid = cursor.fetchone()[0]
    return {"database_oid": database_oid, "tables": tables}


def verify_preservation(previous, current):
    """Exact old rows/OIDs; only enumerated Django installation metadata may grow."""
    from django.apps import apps
    from django.db import connection
    from django.db.migrations.loader import MigrationLoader

    def require(value, reason):
        if not value:
            raise AssertionError("preservation " + reason)

    require(previous["database_oid"] == current["database_oid"], "database identity")
    before, after = previous["tables"], current["tables"]
    require("accounts_user" in before, "original User table")
    require("auth_user" not in before and "auth_user" not in after, "auth_user absent")
    require(set(before) <= set(after), "original tables")
    catalogs = {"django_migrations", "django_content_type", "auth_permission"}
    additions = {}
    for name, original in before.items():
        actual = after[name]
        require(original["oid"] == actual["oid"], "original table OID")
        require(original["count"] == len(original["rows"]), "original count")
        require(actual["count"] == len(actual["rows"]), "current count")
        if name not in catalogs:
            require(original == actual, "original rows and values")
            continue
        old_rows, new_rows = set(original["rows"]), set(actual["rows"])
        require(len(old_rows) == original["count"], "original catalog identity")
        require(len(new_rows) == actual["count"], "current catalog identity")
        require(old_rows <= new_rows, "original catalog rows")
        additions[name] = [json.loads(row) for row in new_rows - old_rows]
    models = {
        (model._meta.app_label, model._meta.model_name): model
        for model in apps.get_models()
        if model._meta.app_label in {"assets", "athletes", "professionals"}
    }
    types = [json.loads(row) for row in before["django_content_type"]["rows"]]
    old_models = {(row["app_label"], row["model"]) for row in types}
    new_types = additions["django_content_type"]
    added_models = {(row["app_label"], row["model"]) for row in new_types}
    require(added_models == set(models) - old_models, "exact C03 content types")
    require(len(new_types) == len(added_models), "unique new content types")
    expected_permissions = set()
    for row in new_types:
        model = models[(row["app_label"], row["model"])]
        permissions = [
            (
                f"{verb}_{model._meta.model_name}",
                f"Can {verb} {model._meta.verbose_name_raw}",
            )
            for verb in model._meta.default_permissions
        ] + list(model._meta.permissions)
        expected_permissions.update(
            (row["id"], code, name) for code, name in permissions
        )
    permission_rows = additions["auth_permission"]
    require(
        {
            (row["content_type_id"], row["codename"], row["name"])
            for row in permission_rows
        }
        == expected_permissions,
        "exact C03 permission metadata",
    )
    require(len(permission_rows) == len(expected_permissions), "unique new permissions")
    old_migrations = {
        (row["app"], row["name"])
        for row in map(json.loads, before["django_migrations"]["rows"])
    }
    expected_migrations = (
        set(MigrationLoader(connection).disk_migrations) - old_migrations
    )
    new_migrations = additions["django_migrations"]
    require(
        {(row["app"], row["name"]) for row in new_migrations} == expected_migrations,
        "exact additive migration records",
    )
    require(len(new_migrations) == len(expected_migrations), "unique new migrations")
    require(
        all(
            table["count"] == 0
            for name, table in after.items()
            if name.startswith(("assets_", "athletes_", "professionals_"))
        ),
        "no automatic C03 business rows",
    )
    return True


CAPABILITY_CASES = (
    "coach_approve_nutritionist_reject",
    "nutritionist_expiry_preserves_coach",
    "coach_revocation_preserves_nutritionist",
    "temporary_role_restriction_is_local",
    "restriction_removal_reuses_valid_approval",
    "restriction_removal_cannot_undo_revocation",
    "add_declared_role_preserves_other_approval",
    "deactivate_role_preserves_other_approval",
    "inflight_requested_role_or_evidence_edit_is_stale",
    "c04_input_excludes_unverified_declarations",
    "concurrent_restriction_revocation_decision_consistent",
)
CONSTRAINT_CASES = (
    "identity_role_null_rule",
    "role_target_equality",
    "evidence_target_binding",
    "terminal_outcome_uniqueness",
    "explicit_revoke_linkage",
    "one_current_restriction",
    "immutable_decision",
    "immutable_snapshot",
    "immutable_history",
    "cross_role_rejection",
    "bulk_protection",
    "direct_sql_protection",
)


def upgraded_constraints(subject):
    """Exercise native guards on this connection, never a historical model graph."""
    from django.db import DatabaseError, connection, transaction
    from django.db.models import Max
    from django.utils import timezone

    from apps.professionals.models import (
        CredentialRevision,
        ProfessionalRoleRestriction,
        RoleRestrictionHistory,
        Verification,
        VerificationDecision,
        VerificationEvidence,
        VerificationHistory,
        VerificationTarget,
    )

    assert connection.vendor == "postgresql"
    result = {}

    def denied(name, operation):
        try:
            with transaction.atomic():
                operation()
                transaction.set_rollback(True)
        except DatabaseError as error:
            assert getattr(error.__cause__, "sqlstate", None) in {
                "23503",
                "23505",
                "23514",
                "42501",
            }, "Unexpected infrastructure/SQL error, not a constraint proof"
            result[name] = True
            return
        raise AssertionError("Upgraded PostgreSQL accepted forbidden " + name)

    def sql(statement, parameters):
        with connection.cursor() as cursor:
            cursor.execute(statement, parameters)

    sequence = (
        Verification.objects.filter(profile=subject.profile).aggregate(
            value=Max("sequence")
        )["value"]
        + 1
    )
    draft = Verification.objects.create(profile=subject.profile, sequence=sequence)
    roles = {row.role: row for row in subject.profile.roles.all()}
    base = {"verification": draft, "target_snapshot_hash": "c" * 64}
    denied(
        "identity_role_null_rule",
        lambda: VerificationTarget.objects.create(
            **base,
            target="identity",
            role=roles["coach"],
            bound_declaration_version=1,
        ),
    )
    denied(
        "role_target_equality",
        lambda: VerificationTarget.objects.create(
            **base,
            target="coach",
            role=roles["nutritionist"],
            bound_declaration_version=1,
        ),
    )
    coach = VerificationTarget.objects.create(
        **base,
        target="coach",
        role=roles["coach"],
        bound_declaration_version=1,
    )
    nutrition = (
        CredentialRevision.objects.filter(
            credential__profile=subject.profile, credential__role=roles["nutritionist"]
        )
        .order_by("sequence")
        .last()
    )
    assert nutrition is not None
    denied(
        "evidence_target_binding",
        lambda: VerificationEvidence.objects.bulk_create(
            [
                VerificationEvidence(
                    target=coach,
                    credential_revision=nutrition,
                    category="qualification",
                )
            ]
        ),
    )
    approval = VerificationDecision.objects.get(
        profile=subject.profile, target_kind="coach", decision="approve"
    )

    def clone(**changes):
        values = {
            field.attname: getattr(approval, field.attname)
            for field in approval._meta.concrete_fields
            if not field.primary_key
        }
        values.update(id=uuid4(), decision_sequence=approval.decision_sequence + 1)
        values.update(changes)
        return VerificationDecision(**values)

    denied(
        "terminal_outcome_uniqueness",
        lambda: VerificationDecision.objects.bulk_create(
            [clone(decision="reject", reason_code="credentials_invalid")]
        ),
    )
    denied(
        "explicit_revoke_linkage",
        lambda: VerificationDecision.objects.bulk_create(
            [
                clone(
                    decision="revoke",
                    reason_code="evidence_revoked",
                    revoked_approval_id=None,
                )
            ]
        ),
    )
    other = VerificationTarget.objects.get(
        verification_id=subject.case.id, target="nutritionist"
    )
    denied(
        "cross_role_rejection",
        lambda: VerificationDecision.objects.bulk_create(
            [
                clone(
                    target_id=other.id,
                    target_kind="nutritionist",
                    decision="revoke",
                    reason_code="evidence_revoked",
                    revoked_approval_id=approval.id,
                    target_snapshot_hash=other.target_snapshot_hash,
                    bound_evidence_revision=other.bound_evidence_revision,
                )
            ]
        ),
    )
    restricted = dict(
        role=roles["nutritionist"],
        verification_id=subject.case.id,
        applied_by=subject.staff.user,
        reason_code="role_restricted",
        applied_at=timezone.now(),
    )
    episode = ProfessionalRoleRestriction.objects.create(**restricted)
    denied(
        "one_current_restriction",
        lambda: ProfessionalRoleRestriction.objects.bulk_create(
            [ProfessionalRoleRestriction(**restricted)]
        ),
    )
    denied(
        "immutable_decision",
        lambda: sql(
            "UPDATE professionals_verificationdecision "
            "SET explanation='changed' WHERE id=%s",
            [approval.id],
        ),
    )
    frozen = VerificationTarget.objects.get(
        verification_id=subject.case.id, target="coach"
    )
    denied(
        "immutable_snapshot",
        lambda: sql(
            "UPDATE professionals_verificationtarget "
            "SET target_snapshot_hash=%s WHERE id=%s",
            ["f" * 64, frozen.id],
        ),
    )
    history = VerificationHistory.objects.filter(
        verification_id=subject.case.id
    ).first()
    assert history is not None
    denied(
        "immutable_history",
        lambda: sql(
            "DELETE FROM professionals_verificationhistory WHERE id=%s",
            [history.id],
        ),
    )
    restriction_history = RoleRestrictionHistory.objects.create(
        restriction=episode,
        actor=subject.staff.user,
        event="applied",
        reason_code="role_restricted",
        prior_version=0,
        new_version=1,
        at=episode.applied_at,
    )
    denied(
        "bulk_protection",
        lambda: sql(
            "UPDATE professionals_rolerestrictionhistory "
            "SET reason_code='restriction_removed' "
            "WHERE id=%s",
            [restriction_history.id],
        ),
    )
    role_name = "c03_task14_" + uuid4().hex
    role_sql = connection.ops.quote_name(role_name)
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE ROLE {role_sql} NOLOGIN NOSUPERUSER")
        cursor.execute(f"GRANT USAGE ON SCHEMA public TO {role_sql}")
        cursor.execute(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON "
            f"professionals_verificationdecision TO {role_sql}"
        )
    try:

        def runtime(statement):
            with connection.cursor() as cursor:
                cursor.execute(f"SET LOCAL ROLE {role_sql}")
                cursor.execute(statement)

        for statement in (
            "UPDATE professionals_verificationdecision SET explanation='changed'",
            "DELETE FROM professionals_verificationdecision",
            "TRUNCATE professionals_verificationdecision CASCADE",
        ):
            denied("direct_sql_protection", lambda value=statement: runtime(value))
    finally:
        with connection.cursor() as cursor:
            cursor.execute(f"DROP OWNED BY {role_sql}")
            cursor.execute(f"DROP ROLE {role_sql}")
    assert set(result) == set(CONSTRAINT_CASES)
    return result


def upgraded_capability_case(name, subject):
    """Run fresh commands/assertions on the caller's actual upgraded connection."""
    from copy import copy

    from django.db import connection
    from django.utils import timezone

    from apps.professionals.contracts import ProfileConflict
    from apps.professionals.models import VerificationDecision, VerificationTarget
    from tests.integration.c03.profile_helpers import in_connection
    from tests.integration.c03.test_professional_setup import save
    from tests.integration.c03.test_verification_decision_races import race
    from tests.integration.c03.test_verification_decisions import (
        decision,
        eligibility,
        facts,
        mutate_evidence,
    )
    from tests.integration.c03.test_verification_revocation import (
        rereview,
        restrict,
        revoke,
    )

    assert connection.vendor == "postgresql" and name in CAPABILITY_CASES
    s = subject

    def roles(expected):
        current = eligibility(s)
        assert current.identity_verified and current.eligible
        assert current.verified_roles == expected

    def counters(kind):
        row = s.profile.roles.get(role=kind)
        return row.declaration_version, row.evidence_revision, row.decision_version

    if name == "coach_approve_nutritionist_reject":
        before = counters("coach")
        mutate_evidence(s, "nutritionist")
        rereview(s, "nutritionist")
        decision(s, "nutritionist", "reject")
        roles(("coach",))
        assert counters("coach") == before
    elif name == "nutritionist_expiry_preserves_coach":
        before = counters("coach")
        current = eligibility(s, timezone.now() + timedelta(days=2))
        assert current.identity_verified and current.verified_roles == ("coach",)
        assert counters("coach") == before
    elif name == "coach_revocation_preserves_nutritionist":
        before = counters("nutritionist")
        revoke(s, "coach")
        roles(("nutritionist",))
        assert counters("nutritionist") == before
        row = VerificationDecision.objects.get(profile=s.profile, decision="revoke")
        assert row.revoked_approval.target_id == row.target_id
    elif name in {
        "temporary_role_restriction_is_local",
        "restriction_removal_reuses_valid_approval",
    }:
        before = counters("nutritionist"), counters("coach")
        count = VerificationDecision.objects.filter(profile=s.profile).count()
        restrict(s)
        roles(("coach",))
        if name == "restriction_removal_reuses_valid_approval":
            restrict(s, release=True)
            roles(("coach", "nutritionist"))
        assert (counters("nutritionist"), counters("coach")) == before
        assert VerificationDecision.objects.filter(profile=s.profile).count() == count
    elif name == "restriction_removal_cannot_undo_revocation":
        restrict(s)
        revoke(s, "nutritionist")
        restrict(s, release=True)
        roles(("coach",))
        assert (
            VerificationDecision.objects.filter(
                profile=s.profile, decision="revoke"
            ).count()
            == 1
        )
    elif name == "add_declared_role_preserves_other_approval":
        revoke(s, "nutritionist")
        save(s, "identity", {"roles": ["coach"]})
        before = counters("coach")
        save(s, "identity", {"roles": ["coach", "nutritionist"]})
        roles(("coach",))
        assert counters("coach") == before
    elif name == "deactivate_role_preserves_other_approval":
        before = counters("nutritionist")
        approvals = list(
            VerificationDecision.objects.filter(profile=s.profile).values_list(
                "id", flat=True
            )
        )
        save(s, "identity", {"roles": ["nutritionist"]})
        roles(("nutritionist",))
        assert counters("nutritionist") == before
        assert set(approvals) == set(
            VerificationDecision.objects.filter(profile=s.profile).values_list(
                "id", flat=True
            )
        )
    elif name == "inflight_requested_role_or_evidence_edit_is_stale":
        for change in ("evidence", "declaration"):
            mutate_evidence(s, "coach")
            rereview(s, "coach")
            captured = facts(s, "coach")
            before = counters("nutritionist")
            if change == "evidence":
                mutate_evidence(s, "coach")
            else:
                save(s, "identity", {"roles": ["nutritionist"]})
            try:
                decision(s, "coach", captured=captured)
            except ProfileConflict:
                pass
            else:
                raise AssertionError("Stale upgraded decision accepted")
            row = VerificationTarget.objects.get(pk=captured[1].id)
            assert (
                row.state == "stale"
                and row.target_snapshot_hash == captured[1].target_snapshot_hash
            )
            assert counters("nutritionist") == before
            roles(("nutritionist",))
    elif name == "c04_input_excludes_unverified_declarations":
        revoke(s, "nutritionist")
        assert set(
            s.profile.roles.filter(declared_active=True).values_list("role", flat=True)
        ) == {"coach", "nutritionist"}
        roles(("coach",))
    else:
        original = copy(s)
        original.staff = copy(s.staff)
        original_facts = facts(original, "coach")
        rereview(s, "coach")
        pending = facts(s, "coach")
        results = race(
            lambda: revoke(original, captured=original_facts),
            lambda: revoke(original, captured=original_facts),
        )
        assert results.count("conflict") == 1
        try:
            in_connection(lambda: decision(s, "coach", captured=pending))
        except ProfileConflict:
            pass
        else:
            raise AssertionError("Older pending decision overwrote revoke")
        assert VerificationTarget.objects.get(pk=pending[1].id).state == "stale"
        # Real separate connections also race a restriction and query; release
        # cannot undo the already committed approval-linked revocation.
        race(lambda: restrict(original, "coach"), lambda: eligibility(s))
        in_connection(lambda: restrict(original, "coach", release=True))
        roles(("nutritionist",))
        assert (
            VerificationDecision.objects.filter(
                profile=s.profile, target_kind="coach", decision="revoke"
            ).count()
            == 1
        )
    return True


def prepare(path):
    """Populate only through the exact C02 runtime and its trusted helpers."""
    from django.apps import apps
    from django.conf import settings
    from django.db import connection, transaction
    from django.utils import timezone

    from apps.accounts.models import User
    from apps.accounts.sessions import issue_session, resolve_session, revoke_sessions
    from apps.governance.audit import append_event
    from apps.governance.consents import validate_scope
    from apps.governance.flag_models import FeatureFlag
    from apps.governance.outbox_models import OutboxDeliveryReceipt
    from apps.governance.retention import (
        ValidatedRecordSubject,
        activate_policy,
        apply_hold,
        approve_policy,
        create_policy,
    )
    from config.use_cases.consent import grant_consent, revoke_consent
    from config.use_cases.privacy import request_privacy
    from config.use_cases.recovery import open_recovery
    from config.use_cases.referral import bind_attribution, issue_referral

    assert connection.vendor == "postgresql"
    assert not apps.is_installed("apps.athletes")
    assert not User.objects.exists()
    assert not path.exists()
    settings.ACCOUNT_SECURITY = replace(
        settings.ACCOUNT_SECURITY,
        entry_enabled=True,
        staff_recovery_enabled=True,
        step_up_provider="mock",
    )
    import test_flag_referral_state as flag_helpers
    import test_hold_metadata as hold_helpers
    from test_phone_change import fully_proved, started
    from test_recovery_authorization import owner
    from test_sessions import request_with_session

    now = timezone.now()
    candidate = owner("+989123000001")
    legacy = User.objects.create_user("+989123000002")
    restricted = owner("+989123000003", state="restricted")
    suspended = owner("+989123000004")
    sessions = {}

    def session(name, user, scope="normal", at=now):
        request = request_with_session()
        with transaction.atomic():
            issue_session(request, user, scope, at, append_event)
        sessions[name] = request.session.session_key
        return request

    request = session("normal", candidate)
    actor = resolve_session(request, now)
    assert actor is not None
    session("control", restricted, "account_control")
    session("expired", candidate, at=now - timedelta(days=30))
    session("expired_control", restricted, "account_control", now - timedelta(hours=1))
    # Native C02 logout retains session bytes while revoking control authority.
    revoked_user = owner("+989123000005")
    old = session("revoked", revoked_user)
    old_actor = resolve_session(old, now)
    assert old_actor is not None
    revoke_sessions(
        revoked_user, "current", now, append_event, control_id=old_actor.control_id
    )
    revoked_control_user = owner("+989123000006", state="restricted")
    old = session("revoked_control", revoked_control_user, "account_control")
    old_actor = resolve_session(old, now)
    assert old_actor is not None
    revoke_sessions(
        revoked_control_user,
        "current",
        now,
        append_event,
        control_id=old_actor.control_id,
    )
    # Real dual OTP/phone-change command creates proof/history and revokes actor.
    values = fully_proved(started())
    _, identity, phone_user, phone_actor, phone_request, intent = values
    sessions["stale_auth"] = phone_request.session.session_key
    identity.apply_phone_change(phone_actor, intent.id, timezone.now())
    open_recovery(phone_user.phone, "+989123000099", "127.0.0.1", timezone.now())
    from django.test import Client

    client = Client()
    client.force_login(legacy)
    sessions["legacy"] = client.session.session_key
    session("suspended", suspended)
    from apps.accounts.state import transition_account_state

    transition_account_state(
        suspended.public_id, suspended.auth_version, "suspended", now, append_event
    )
    recipient = owner("+989123000007")
    scope = validate_scope(
        actor,
        recipient.public_id,
        "account_metadata",
        "account_metadata",
        candidate.public_id,
        1,
        now + timedelta(hours=2),
        now,
    )
    consent = grant_consent(actor, scope, "synthetic-v1", "a" * 64, now)
    revoke_consent(actor, consent, 1, now + timedelta(seconds=1))
    grant_consent(actor, scope, "synthetic-v1", "a" * 64, now)
    token = issue_referral(actor, now)
    bind_attribution(recipient, token, now)
    privacy = request_privacy(actor, "export", uuid4(), now, confirmed=True)
    # Reuse the exact C02 trusted grant/step-up helpers, allocating disjoint
    # synthetic phone ranges per helper call. No grants are production authority.
    from pytest import MonkeyPatch

    counter = [100]

    def unique_owner(*args, **kwargs):
        counter[0] += 1
        return owner(f"+989123{counter[0]:06d}", **kwargs)

    with MonkeyPatch.context() as patch:
        patch.setattr(flag_helpers, "owner", unique_owner)
        patch.setattr(hold_helpers, "owner", unique_owner)
        flag = FeatureFlag.objects.get(key="professional_registration")
        flag_actor, step, at = flag_helpers.staff_for_flag(settings, flag)
        from apps.governance.flags import set_feature

        set_feature(
            flag_actor, flag.key, True, flag.version, "policy_approved", step, at
        )
        hold_actor, step, at = hold_helpers.authority(settings, privacy)
        apply_hold(
            hold_actor,
            ValidatedRecordSubject("privacy_request", privacy, candidate.public_id, 1),
            privacy,
            "security",
            "hold_applied",
            at + timedelta(minutes=30),
            at + timedelta(hours=2),
            step,
            at,
        )
        for index, state in enumerate(("draft", "effective")):
            policy = uuid4()
            policy_actor, step, at = hold_helpers.authority(settings, policy)
            create_policy(
                policy_actor,
                policy,
                f"synthetic_{index}",
                "rehearsal",
                "policy_approved",
                step,
                at,
            )
            if state == "effective":
                approve_policy(
                    policy_actor,
                    policy,
                    1,
                    3600,
                    "synthetic-backup",
                    "policy_approved",
                    step,
                    at,
                )
                activate_policy(policy_actor, policy, 2, "policy_approved", step, at)
    from apps.governance.outbox import dispatch_event, scan_outbox
    from apps.governance.outbox_models import OutboxEvent

    assert scan_outbox(timezone.now(), 100) > 0
    for event in OutboxEvent.objects.filter(state="leased"):
        assert dispatch_event(event.id, timezone.now(), lease_uuid=event.lease_uuid)
    assert OutboxDeliveryReceipt.objects.exists()
    from django.contrib.sessions.models import Session

    assert all(Session.objects.filter(pk=key).exists() for key in sessions.values())
    print("C03_TASK14 c02_population_complete", flush=True)
    data = {
        "source_commit": "0905be6c6ca608d469fe33e87f514b22591132d1",
        "source_tree": "ed788191bb6f5011e6b35a63823ae8183af7b53d",
        "snapshot": snapshot(connection),
        "sessions": sessions,
        "owner_uuid": str(candidate.public_id),
    }
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as stream:
        json.dump(data, stream)
    assert path.stat().st_mode & 0o777 == 0o600


def main():
    sys.path.insert(0, os.getcwd())
    sys.path.insert(0, str(Path.cwd() / "tests/integration/c02"))
    import django

    django.setup()
    from django.conf import settings
    from django.db import connection

    assert settings.SETTINGS_ENV == "development"
    assert connection.settings_dict["NAME"] == "fitlink"
    assert connection.settings_dict["HOST"] == "db"
    phase, filename = sys.argv[1:]
    path = Path(filename)
    if phase == "prepare":
        prepare(path)
        print("C03_TASK14 exact_c02_populated_snapshot_0600", flush=True)
    elif phase == "verify":
        # Harness first: prove the real preserved source/database are present.
        data = json.loads(path.read_text())
        assert path.stat().st_mode & 0o777 == 0o600
        assert data["source_commit"] == "0905be6c6ca608d469fe33e87f514b22591132d1"
        assert data["source_tree"] == "ed788191bb6f5011e6b35a63823ae8183af7b53d"
        current = snapshot(connection)
        assert current["database_oid"] == data["snapshot"]["database_oid"]
        assert current["tables"]["accounts_user"]["count"] > 0
        assert "professionals_verificationtarget" in current["tables"]
        verify_preservation(data["snapshot"], current)
        from django.utils import timezone
        from test_sessions import request_with_session

        from apps.accounts.sessions import actor_user, resolve_session

        at = timezone.now()
        sessions = data["sessions"]
        owner = resolve_session(request_with_session(sessions["normal"]), at)
        assert owner is not None and str(owner.user_uuid) == data["owner_uuid"]
        assert owner.scope == "normal"
        control = resolve_session(request_with_session(sessions["control"]), at)
        assert control is not None and control.scope == "account_control"
        for name in (
            "revoked",
            "revoked_control",
            "expired",
            "expired_control",
            "stale_auth",
            "legacy",
            "suspended",
        ):
            assert resolve_session(request_with_session(sessions[name]), at) is None
        assert resolve_session(request_with_session("unsupported-cookie"), at) is None
        for action in (
            "athlete.profile_write",
            "professional.profile_write",
            "professional.verify_submit",
            "asset.owner_write",
        ):
            try:
                actor_user(control, action, at)
            except PermissionError:
                pass
            else:
                raise AssertionError("Preserved control acquired C03 authority")
        # Session resolution is read-only; no regeneration or delayed mutation.
        verify_preservation(data["snapshot"], snapshot(connection))
        print("C03_TASK14 exact_preservation_and_sessions_passed", flush=True)
    else:
        raise ValueError("Unknown Task 14 phase")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        import traceback

        frames = traceback.extract_tb(error.__traceback__)
        # Static location only; never exception messages, source lines or locals.
        own = [frame for frame in frames if Path(frame.filename).name == "probe.py"]
        line = own[-1].lineno if own else 0
        print(
            "C03_TASK14 probe_failed " + type(error).__name__ + f" line={line}",
            flush=True,
        )
        raise SystemExit(1) from None
