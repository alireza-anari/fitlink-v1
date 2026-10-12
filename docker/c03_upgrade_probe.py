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
    """Unimplemented comparator boundary for independently observed RED."""
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
    """Missing Task14 constraint execution boundary, specified before implementation."""
    return {}


def upgraded_capability_case(name, subject):
    """Missing Task14 replay boundary; never borrow an earlier CI result."""
    return False


def prepare(path):
    """Populate only through the exact C02 runtime and its trusted helpers."""
    from django.apps import apps
    from django.conf import settings
    from django.db import connection, transaction
    from django.utils import timezone

    from apps.accounts.models import User
    from apps.accounts.sessions import issue_session, resolve_session
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
    # C02 issue_session rotates/revokes the old key through its normal service.
    revoked_user = owner("+989123000005")
    old = session("revoked", revoked_user)
    with transaction.atomic():
        issue_session(old, revoked_user, "normal", now, append_event)
    revoked_control_user = owner("+989123000006", state="restricted")
    old = session("revoked_control", revoked_control_user, "account_control")
    with transaction.atomic():
        issue_session(old, revoked_control_user, "account_control", now, append_event)
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
        raise AssertionError("Task 14 populated preservation is not implemented")
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
