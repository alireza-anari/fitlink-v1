"""PostgreSQL independent connections, bounded barriers and ordered commits."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event
from uuid import uuid4

import pytest
from django.core.exceptions import PermissionDenied
from django.db import connection

from apps.professionals.contracts import ProfileConflict
from apps.professionals.models import ProfessionalRoleRestriction, VerificationDecision

from .profile_helpers import in_connection
from .test_professional_setup import save
from .test_verification_decisions import (
    approved,
    decision,
    eligibility,
    facts,
    mutate_evidence,
    review,
)
from .test_verification_revocation import restrict, restriction_facts, revoke

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def race(first, second):
    assert connection.vendor == "postgresql"
    barrier = Barrier(2)

    def run(action):
        def call():
            barrier.wait(timeout=10)
            try:
                return action()
            except (ProfileConflict, PermissionDenied, PermissionError):
                return "conflict"

        return in_connection(call)

    with ThreadPoolExecutor(2) as pool:
        a = pool.submit(run, first)
        b = pool.submit(run, second)
        return a.result(timeout=30), b.result(timeout=30)


def test_one_concurrent_approve_reject_terminal_decision(settings):
    s = review(settings)
    captured = facts(s, "coach")
    results = race(
        lambda: decision(s, "coach", "approve", captured=captured),
        lambda: decision(s, "coach", "reject", captured=captured),
    )
    assert results.count("conflict") == 1
    assert VerificationDecision.objects.filter(target=captured[1]).count() == 1
    assert (
        s.profile.roles.get(role="coach").decision_version
        == captured[2].decision_version + 1
    )


@pytest.mark.parametrize("order", ["edit_first", "decide_first"])
@pytest.mark.parametrize("edit", ["evidence", "declaration"])
def test_edit_while_decide_two_orders(settings, order, edit):
    s = review(settings)
    captured = facts(s, "coach")
    committed = Event()

    def change():
        if edit == "evidence":
            return mutate_evidence(s, "coach")
        return save(s, "identity", {"roles": ["nutritionist"]})

    first, second = (
        (change, lambda: decision(s, "coach", captured=captured))
        if order == "edit_first"
        else (lambda: decision(s, "coach", captured=captured), change)
    )

    def leader():
        try:
            return in_connection(first)
        finally:
            committed.set()

    def follower():
        assert committed.wait(timeout=20)
        try:
            return in_connection(second)
        except ProfileConflict:
            return "conflict"

    with ThreadPoolExecutor(2) as pool:
        a, b = pool.submit(leader), pool.submit(follower)
        a.result(timeout=30)
        result = b.result(timeout=30)
    if order == "edit_first":
        assert result == "conflict"
        assert not VerificationDecision.objects.filter(
            target=captured[1], decision="approve"
        ).exists()
    else:
        assert (
            VerificationDecision.objects.filter(
                target=captured[1], decision="approve"
            ).count()
            == 1
        )
        assert "coach" not in eligibility(s).verified_roles
    decision(s, "nutritionist")
    assert "nutritionist" in eligibility(s).verified_roles


def test_duplicate_decision_replay_independent_connections(settings):
    s = review(settings)
    captured, operation = facts(s, "coach"), uuid4()
    results = race(
        lambda: decision(s, "coach", captured=captured, operation=operation),
        lambda: decision(s, "coach", captured=captured, operation=operation),
    )
    assert results[0] == results[1]
    assert VerificationDecision.objects.filter(target=captured[1]).count() == 1


@pytest.mark.parametrize(
    "pair",
    [
        "revoke_revoke",
        "revoke_edit",
        "restrict_restrict",
        "restrict_release",
        "query_revoke",
        "query_restrict",
    ],
)
def test_concurrent_restriction_revocation_decision_consistent(settings, pair):
    s = approved(settings)
    captured = facts(s, "coach")
    restriction = restriction_facts(s, "coach")
    if pair == "revoke_revoke":
        results = race(
            lambda: revoke(s, captured=captured), lambda: revoke(s, captured=captured)
        )
        assert results.count("conflict") == 1
    elif pair == "revoke_edit":
        race(lambda: revoke(s, captured=captured), lambda: mutate_evidence(s, "coach"))
    elif pair == "restrict_restrict":
        results = race(
            lambda: restrict(s, "coach", captured=restriction),
            lambda: restrict(s, "coach", captured=restriction),
        )
        assert results.count("conflict") == 1
        assert (
            ProfessionalRoleRestriction.objects.filter(
                role=restriction[1], released_at__isnull=True
            ).count()
            == 1
        )
    elif pair == "restrict_release":
        race(
            lambda: restrict(s, "coach", captured=restriction),
            lambda: restrict(s, "coach", release=True, captured=restriction),
        )
        assert (
            ProfessionalRoleRestriction.objects.filter(
                role=restriction[1], released_at__isnull=True
            ).count()
            == 1
        )
    else:
        mutation = (
            (lambda: revoke(s, captured=captured))
            if pair == "query_revoke"
            else (lambda: restrict(s, "coach", captured=restriction))
        )
        results = race(mutation, lambda: eligibility(s))
        assert results[1].verified_roles in {
            ("coach", "nutritionist"),
            ("nutritionist",),
        }
    assert eligibility(s).verified_roles == ("nutritionist",)


@pytest.mark.parametrize("first", ["restriction", "decision"])
def test_decision_restriction_both_commit_orders(settings, first):
    s = review(settings)
    captured = facts(s, "coach")
    if first == "restriction":
        in_connection(lambda: restrict(s, "coach"))
        with pytest.raises(ProfileConflict):
            in_connection(lambda: decision(s, "coach", captured=captured))
        in_connection(lambda: decision(s, "coach"))
    else:
        in_connection(lambda: decision(s, "coach", captured=captured))
        in_connection(lambda: restrict(s, "coach"))
    assert "coach" not in eligibility(s).verified_roles
    in_connection(lambda: restrict(s, "coach", release=True))
    assert eligibility(s).verified_roles == ("coach",)
