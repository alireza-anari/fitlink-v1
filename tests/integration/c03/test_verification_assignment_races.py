from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from django.utils import timezone

from apps.professionals.contracts import ProfileConflict
from apps.professionals.models import Verification, VerificationAssignment

from .profile_helpers import in_connection
from .verification_helpers import assign, command, prepared, reviewer

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_postgresql_duplicate_submit_has_one_effect():
    s = prepared()
    operation, barrier = uuid4(), Barrier(2)

    def action(_):
        def run():
            barrier.wait(timeout=10)
            return command(
                "submit_verification",
                s.actor,
                s.case.id,
                s.case.version,
                operation,
                timezone.now(),
            )

        return in_connection(run)

    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(action, range(2)))
    assert results[0] == results[1]
    assert (
        Verification.objects.get(pk=s.case.id).history.filter(event="submit").count()
        == 1
    )


def test_postgresql_assignment_expected_version_has_one_winner(settings):
    s = prepared()
    s.case = command(
        "submit_verification",
        s.actor,
        s.case.id,
        s.case.version,
        uuid4(),
        timezone.now(),
    )
    staff = reviewer(settings, s.case.id)
    barrier = Barrier(2)

    def action(_):
        def run():
            barrier.wait(timeout=10)
            try:
                return assign(s, staff)
            except ProfileConflict:
                return "conflict"

        return in_connection(run)

    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(action, range(2)))
    assert results.count("conflict") == 1
    assert (
        VerificationAssignment.objects.filter(
            verification_id=s.case.id, ended_at__isnull=True
        ).count()
        == 1
    )


def test_postgresql_prepare_different_payloads_one_winner():
    s = prepared()
    s.profile.refresh_from_db()
    version, barrier = s.profile.version, Barrier(2)

    def action(targets):
        def run():
            barrier.wait(timeout=10)
            try:
                return command(
                    "prepare_verification",
                    s.actor,
                    targets,
                    version,
                    uuid4(),
                    timezone.now(),
                )
            except ProfileConflict:
                return "conflict"

        return in_connection(run)

    with ThreadPoolExecutor(2) as pool:
        results = list(
            pool.map(action, [("identity", "coach"), ("identity", "nutritionist")])
        )
    assert results.count("conflict") == 1


def test_postgresql_submit_and_bound_edit_serialize():
    from apps.professionals.models import VerificationTarget
    from config.use_cases.professional_profile import revise_credential

    from .test_credential_revisions import payload

    s = prepared()
    barrier = Barrier(2)
    asset, credential = s.assets["coach"]

    def submit():
        barrier.wait(timeout=10)
        return command(
            "submit_verification",
            s.actor,
            s.case.id,
            s.case.version,
            uuid4(),
            timezone.now(),
        )

    def edit():
        barrier.wait(timeout=10)
        return revise_credential(
            s.actor,
            credential.id,
            payload(
                category="qualification",
                role="coach",
                source_asset=asset.id,
                title="Changed Fixture",
            ),
            credential.version,
            uuid4(),
            timezone.now(),
        )

    with ThreadPoolExecutor(2) as pool:
        first = pool.submit(in_connection, submit)
        second = pool.submit(in_connection, edit)
        first.result(timeout=30)
        second.result(timeout=30)
    target = VerificationTarget.objects.get(verification_id=s.case.id, target="coach")
    role = s.profile.roles.get(role="coach")
    assert target.state in {"submitted", "stale"}
    if target.state == "submitted":
        assert target.bound_evidence_revision == role.evidence_revision
        assert (
            target.evidence.get().credential_revision_id
            == role.credentials.get().current_revision_id
        )
    else:
        assert target.bound_evidence_revision < role.evidence_revision
    assert (
        VerificationTarget.objects.get(
            verification_id=s.case.id, target="nutritionist"
        ).state
        == "submitted"
    )


def test_postgresql_reassignment_and_old_reviewer_read_serialize(settings):
    from datetime import timedelta

    from django.core.exceptions import PermissionDenied

    from apps.governance.staff_models import StaffCapabilityGrant

    from .profile_helpers import make_actor
    from .verification_helpers import selectors, submitted

    s = submitted()
    staff = reviewer(settings, s.case.id)
    dto = assign(s, staff)
    other = make_actor("+989123456783")
    StaffCapabilityGrant.objects.create(
        user=other.user,
        capability="professional_verification",
        granted_by=staff.user,
        reason_code="staff_assigned",
        valid_from=other.at,
        valid_until=other.at + timedelta(hours=1),
    )
    barrier = Barrier(2)

    def reassign():
        barrier.wait(timeout=10)
        return command(
            "assign_verification",
            staff.actor,
            s.case.id,
            other.user.public_id,
            dto.version,
            staff.step,
            "case_conflict",
            timezone.now(),
        )

    def read():
        barrier.wait(timeout=10)
        try:
            return selectors().assigned_verification_detail(
                staff.actor,
                s.case.id,
                staff.step,
                "verification_review",
                timezone.now(),
            )
        except PermissionDenied:
            return "denied"

    with ThreadPoolExecutor(2) as pool:
        changed = pool.submit(in_connection, reassign)
        observed = pool.submit(in_connection, read)
        changed.result(timeout=30)
        result = observed.result(timeout=30)
    assert result == "denied" or result.assignment_uuid == dto.assignment_uuid
    with pytest.raises(PermissionDenied):
        selectors().assigned_verification_detail(
            staff.actor, s.case.id, staff.step, "verification_review", timezone.now()
        )
