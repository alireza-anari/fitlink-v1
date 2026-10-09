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
