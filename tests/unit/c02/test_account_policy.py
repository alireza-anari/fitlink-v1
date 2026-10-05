from datetime import date
from types import SimpleNamespace

import pytest

from apps.accounts import policies
from apps.accounts.contracts import SessionScope


def gate():
    assert callable(getattr(policies, "require_account_action", None)), (
        "missing current account action policy"
    )
    return policies.require_account_action


@pytest.mark.parametrize(
    "state,scope,action,allowed",
    [
        ("active", SessionScope.NORMAL, "account.self", True),
        ("active", SessionScope.NORMAL, "referral.create", True),
        ("restricted", SessionScope.ACCOUNT_CONTROL, "account.self", True),
        ("restricted", SessionScope.ACCOUNT_CONTROL, "privacy.intake", True),
        ("restricted", SessionScope.ACCOUNT_CONTROL, "referral.create", False),
        ("restricted", SessionScope.NORMAL, "account.self", False),
        ("pending_deletion", SessionScope.ACCOUNT_CONTROL, "account.logout", True),
        ("pending_deletion", SessionScope.NORMAL, "consent.grant", False),
        ("suspended", SessionScope.ACCOUNT_CONTROL, "account.self", False),
        ("deleted", SessionScope.NORMAL, "account.self", False),
        ("active", SessionScope.NORMAL, "new.unknown_action", False),
    ],
)
def test_current_state_scope_and_unknown_deny(state, scope, action, allowed):
    user = SimpleNamespace(
        state=state,
        is_active=state not in {"suspended", "deleted"},
        birth_date=date(1990, 1, 1),
        adult_attested_at=True,
        adult_attestation_version="adult-v1",
    )
    if allowed:
        gate()(user, action, scope)
    else:
        with pytest.raises(PermissionError):
            gate()(user, action, scope)


def test_legacy_data_or_inactive_never_product_authority():
    for active, birth, attested in [
        (True, None, None),
        (False, date(1990, 1, 1), True),
    ]:
        user = SimpleNamespace(
            state="active",
            is_active=active,
            birth_date=birth,
            adult_attested_at=attested,
            adult_attestation_version="adult-v1" if attested else "",
        )
        with pytest.raises(PermissionError):
            gate()(user, "referral.create", SessionScope.NORMAL)
