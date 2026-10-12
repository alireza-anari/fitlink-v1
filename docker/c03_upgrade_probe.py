"""Task 14 replay corrections layered over the preserved upgrade harness."""

import importlib
import signal
import sys
from copy import copy
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_impl = importlib.import_module("docker.c03_upgrade_probe_impl")

CAPABILITY_CASES = _impl.CAPABILITY_CASES
CONSTRAINT_CASES = _impl.CONSTRAINT_CASES
private_log_metadata = _impl.private_log_metadata
snapshot = _impl.snapshot
verify_preservation = _impl.verify_preservation
upgraded_constraints = _impl.upgraded_constraints

_original_upgraded_capability_case = _impl.upgraded_capability_case
_original_history_http_diagnostic = _impl.history_http_diagnostic


def _rereview_targets(subject, targets):
    """Open one fresh submitted review bundle for the exact requested targets."""
    from django.db import transaction
    from django.utils import timezone

    from apps.governance.staff import MockStepUpProvider, issue_mock_step_up
    from tests.integration.c03.verification_helpers import assign, command

    subject.profile.refresh_from_db()
    subject.case = command(
        "prepare_verification",
        subject.actor,
        tuple(targets),
        subject.profile.version,
        uuid4(),
        timezone.now(),
    )
    subject.case = command(
        "submit_verification",
        subject.actor,
        subject.case.id,
        subject.case.version,
        uuid4(),
        timezone.now(),
    )
    at = timezone.now()
    provider = MockStepUpProvider()
    assertion = provider.prepare(
        subject.staff.user.public_id,
        "professional_verification",
        subject.case.id,
        at,
    )
    with transaction.atomic():
        subject.staff.step = issue_mock_step_up(
            subject.staff.user,
            "professional_verification",
            subject.case.id,
            assertion.raw_assertion,
            subject.user,
            at,
            provider,
        )
    subject.case = assign(subject, subject.staff)
    subject.case = command(
        "start_verification_review",
        subject.staff.actor,
        subject.case.id,
        subject.case.version,
        subject.staff.step,
        "verification_review",
        timezone.now(),
    )
    return subject.case


def upgraded_capability_case(name, subject):
    """Replay Task 14 gaps with real commands and ordered independent connections."""
    if name not in {
        "coach_approve_nutritionist_reject",
        "concurrent_restriction_revocation_decision_consistent",
    }:
        return _original_upgraded_capability_case(name, subject)

    from apps.professionals.models import (
        ProfessionalRoleRestriction,
        VerificationDecision,
        VerificationTarget,
    )
    from tests.integration.c03.profile_helpers import in_connection
    from tests.integration.c03.test_verification_decision_races import (
        ordered_connections,
    )
    from tests.integration.c03.test_verification_decisions import (
        decision,
        eligibility,
        facts,
        mutate_evidence,
    )
    from tests.integration.c03.test_verification_revocation import restrict, revoke

    subject_state = subject

    def roles(expected):
        current = eligibility(subject_state)
        assert current.identity_verified and current.eligible
        assert current.verified_roles == expected

    if name == "coach_approve_nutritionist_reject":
        asset, _ = subject_state.assets["nutritionist"]
        subject_state.assets["nutritionist"] = (
            asset,
            mutate_evidence(subject_state, "nutritionist"),
        )
        _rereview_targets(
            subject_state,
            ("identity", "coach", "nutritionist"),
        )
        decision(subject_state, "identity")
        decision(subject_state, "coach")
        decision(subject_state, "nutritionist", "reject")
        roles(("coach",))
        assert set(
            VerificationDecision.objects.filter(
                target__verification_id=subject_state.case.id
            ).values_list("target_kind", "decision", "reason_code")
        ) == {
            ("identity", "approve", "credentials_approved"),
            ("coach", "approve", "credentials_approved"),
            ("nutritionist", "reject", "credentials_invalid"),
        }
        return True

    cases = []

    def reapprove_coach():
        _rereview_targets(subject_state, ("coach",))
        result = in_connection(lambda: decision(subject_state, "coach"))
        assert result != "conflict"
        roles(("coach", "nutritionist"))

    # Restriction commits first: the captured pending decision must become stale.
    _rereview_targets(subject_state, ("coach",))
    pending = facts(subject_state, "coach")
    first, second = ordered_connections(
        lambda: restrict(subject_state, "coach"),
        lambda: decision(subject_state, "coach", captured=pending),
    )
    assert first != "conflict" and second == "conflict"
    in_connection(lambda: decision(subject_state, "coach"))
    roles(("nutritionist",))
    in_connection(lambda: restrict(subject_state, "coach", release=True))
    roles(("coach", "nutritionist"))
    cases.append("restrict_then_decide")

    # Decision commits first: a later restriction independently hides that approval.
    _rereview_targets(subject_state, ("coach",))
    pending = facts(subject_state, "coach")
    first, second = ordered_connections(
        lambda: decision(subject_state, "coach", captured=pending),
        lambda: restrict(subject_state, "coach"),
    )
    assert first != "conflict" and second != "conflict"
    roles(("nutritionist",))
    in_connection(lambda: restrict(subject_state, "coach", release=True))
    roles(("coach", "nutritionist"))
    cases.append("decide_then_restrict")

    # Revoke the current approval before an already-open newer decision can commit.
    original = copy(subject_state)
    original.staff = copy(subject_state.staff)
    approval_facts = facts(original, "coach")
    _rereview_targets(subject_state, ("coach",))
    pending = facts(subject_state, "coach")
    first, second = ordered_connections(
        lambda: revoke(original, captured=approval_facts),
        lambda: decision(subject_state, "coach", captured=pending),
    )
    assert first != "conflict" and second == "conflict"
    assert VerificationTarget.objects.get(pk=pending[1].id).state == "stale"
    roles(("nutritionist",))
    reapprove_coach()
    cases.append("revoke_then_decide")

    # A newly committed approval can subsequently be revoked on another connection.
    _rereview_targets(subject_state, ("coach",))
    pending = facts(subject_state, "coach")
    first, second = ordered_connections(
        lambda: decision(subject_state, "coach", captured=pending),
        lambda: revoke(subject_state, "coach"),
    )
    assert first != "conflict" and second != "conflict"
    roles(("nutritionist",))
    reapprove_coach()
    cases.append("decide_then_revoke")

    # Releasing a restriction after revocation cannot restore the revoked role.
    in_connection(lambda: restrict(subject_state, "coach"))
    first, second = ordered_connections(
        lambda: revoke(subject_state, "coach"),
        lambda: restrict(subject_state, "coach", release=True),
    )
    assert first != "conflict" and second != "conflict"
    assert not ProfessionalRoleRestriction.objects.filter(
        role=subject_state.profile.roles.get(role="coach"),
        released_at__isnull=True,
    ).exists()
    roles(("nutritionist",))
    reapprove_coach()
    cases.append("revoke_then_release")

    # Releasing first removes only the restriction; the following revoke still wins.
    in_connection(lambda: restrict(subject_state, "coach"))
    first, second = ordered_connections(
        lambda: restrict(subject_state, "coach", release=True),
        lambda: revoke(subject_state, "coach"),
    )
    assert first != "conflict" and second != "conflict"
    assert not ProfessionalRoleRestriction.objects.filter(
        role=subject_state.profile.roles.get(role="coach"),
        released_at__isnull=True,
    ).exists()
    roles(("nutritionist",))
    cases.append("release_then_revoke")

    subject_state.upgrade_race_cases = tuple(cases)
    assert set(subject_state.upgrade_race_cases) == {
        "restrict_then_decide",
        "decide_then_restrict",
        "revoke_then_decide",
        "decide_then_revoke",
        "revoke_then_release",
        "release_then_revoke",
    }
    return True


def history_http_diagnostic():
    """Keep the redundant historical HTTP observation finite inside its hard bound."""
    if not hasattr(signal, "setitimer"):
        return _original_history_http_diagnostic()

    def deadline(signum, frame):
        raise TimeoutError

    previous = signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, 90)
    try:
        try:
            return _original_history_http_diagnostic()
        except TimeoutError:
            print("C03_TASK14 history_http_observation_deadline", flush=True)
            return None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


_impl.upgraded_capability_case = upgraded_capability_case
_impl.history_http_diagnostic = history_http_diagnostic


def __getattr__(name):
    return getattr(_impl, name)


if __name__ == "__main__":
    try:
        _impl.main()
    except Exception as error:
        import traceback

        frames = traceback.extract_tb(error.__traceback__)
        own = [
            frame
            for frame in frames
            if Path(frame.filename).name
            in {
                "probe.py",
                Path(__file__).name,
                Path(_impl.__file__).name,
            }
        ]
        line = own[-1].lineno if own else 0
        print(
            "C03_TASK14 probe_failed " + type(error).__name__ + f" line={line}",
            flush=True,
        )
        raise SystemExit(1) from None
