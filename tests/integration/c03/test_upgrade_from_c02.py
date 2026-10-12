"""PostgreSQL preservation checker behaviors; not a substitute for exact upgrade."""

import copy

import pytest
from django.db import connection

from apps.accounts.models import User
from docker.c03_upgrade_probe import (
    CAPABILITY_CASES,
    CONSTRAINT_CASES,
    snapshot,
    upgraded_capability_case,
    upgraded_constraints,
    verify_preservation,
)

from .test_verification_decisions import approved, eligibility

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize(
    "defect", ["row", "table_oid", "missing_table", "extra_profile"]
)
def test_upgrade_probe_preserves_all_c02_rows_sessions_governance_oid_and_no_profiles(
    defect,
):
    assert connection.vendor == "postgresql"
    User.objects.create_user("+989123000001")
    previous = snapshot(connection)
    assert previous["tables"]["accounts_user"]["count"] == 1
    current = copy.deepcopy(previous)
    assert verify_preservation(previous, current)
    if defect == "row":
        User.objects.filter(phone="+989123000001").update(auth_version=2)
        current = snapshot(connection)
    elif defect == "table_oid":
        current["tables"]["accounts_user"]["oid"] += 1
    elif defect == "missing_table":
        del current["tables"]["django_session"]
    else:
        from apps.athletes.models import AthleteProfile

        AthleteProfile.objects.create(user=User.objects.get())
        current = snapshot(connection)
    with pytest.raises(AssertionError, match="preservation"):
        verify_preservation(previous, current)


def test_upgrade_new_target_and_restriction_constraints(settings):
    assert connection.vendor == "postgresql"
    subject = approved(settings)
    assert eligibility(subject).verified_roles == ("coach", "nutritionist")
    proof = upgraded_constraints(subject)
    assert set(proof) == set(CONSTRAINT_CASES), "Task14 constraint replay is missing"
    assert all(proof[name] is True for name in CONSTRAINT_CASES)


@pytest.mark.parametrize("case", CAPABILITY_CASES)
def test_upgrade_replays_all_eleven_capability_cases(settings, case):
    assert connection.vendor == "postgresql"
    subject = approved(settings)
    assert eligibility(subject).identity_verified
    assert eligibility(subject).verified_roles == ("coach", "nutritionist")
    assert upgraded_capability_case(case, subject) is True, (
        "Task14 capability replay is missing: " + case
    )
