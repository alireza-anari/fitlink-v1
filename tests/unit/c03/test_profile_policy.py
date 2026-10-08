"""Profile actions extend the finite account gate without granting ownership."""

from datetime import date

import pytest
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.policies import require_account_action

pytestmark = pytest.mark.unit
ACTIONS = (
    "athlete.profile_read",
    "athlete.profile_write",
    "professional.profile_read",
    "professional.profile_write",
)


def eligible_user(**changes):
    return User(
        birth_date=date(1990, 1, 1),
        adult_attested_at=timezone.now(),
        adult_attestation_version="adult-v1",
        **changes,
    )


@pytest.mark.parametrize("action", ACTIONS)
def test_active_declared_adult_can_reach_profile_ownership_gate(action):
    # Removing a finite profile action denies legitimate owner setup.
    require_account_action(eligible_user(), action, "normal")


@pytest.mark.parametrize("action", ACTIONS)
@pytest.mark.parametrize("state", ["restricted", "suspended", "pending_deletion"])
def test_profile_action_is_not_account_control(action, state):
    for scope in ("normal", "account_control"):
        with pytest.raises(PermissionError):
            require_account_action(eligible_user(state=state), action, scope)


def test_unknown_profile_action_stays_denied_even_for_superuser():
    with pytest.raises(PermissionError):
        require_account_action(
            eligible_user(is_superuser=True), "professional.profile_directory", "normal"
        )
