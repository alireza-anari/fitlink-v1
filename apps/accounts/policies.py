"""Current identity eligibility; declared adulthood is never age verification."""

from datetime import date, datetime

from django.utils import timezone

from .dates import require_adult
from .models import User

ADULT_ATTESTATION_VERSION = "adult-v1"
ENTRY_STATES = frozenset(
    {"active", "restricted", "deletion_requested", "pending_deletion"}
)


def entry_allowed(user: User | None) -> bool:
    return user is None or (user.is_active and user.state in ENTRY_STATES)


def adult_entry_date(
    user: User | None, birth_date: date | None, attested: bool, at: datetime
) -> date:
    if user and user.adult_attested_at and user.adult_attestation_version:
        if user.birth_date is None:
            raise ValueError("adult declaration required")
        require_adult(user.birth_date, True, at)
        return user.birth_date
    if birth_date is None:
        raise ValueError("adult declaration required")
    require_adult(birth_date, attested, at)
    assert birth_date is not None
    return birth_date


CONTROL_ACTIONS = frozenset(
    {
        "account.self",
        "account.logout",
        "account.logout_all",
        "privacy.intake",
        "privacy.status",
    }
)
NORMAL_ACTIONS = CONTROL_ACTIONS | frozenset(
    {
        "phone_change.begin",
        "phone_change.apply",
        "consent.grant",
        "consent.revoke",
        "consent.status",
        "referral.create",
        "referral.attribute",
        "referral.status",
        "staff.command",
        "athlete.profile_read",
        "athlete.profile_write",
        "athlete.baseline_read",
        "athlete.baseline_write",
        "professional.profile_read",
        "professional.profile_write",
        "asset.owner_read",
        "asset.owner_write",
    }
)


def require_account_action(user: User, action: str, scope: str) -> None:
    if not entry_allowed(user):
        raise PermissionError("Account action denied")
    if (
        not user.birth_date
        or not user.adult_attested_at
        or not user.adult_attestation_version
    ):
        raise PermissionError("Account action denied")
    try:
        require_adult(user.birth_date, True, timezone.now())
    except ValueError:
        raise PermissionError("Account action denied") from None

    if scope == "account_control":
        if user.state == "active" or action not in CONTROL_ACTIONS:
            raise PermissionError("Account action denied")
        return
    if scope != "normal" or user.state != "active" or action not in NORMAL_ACTIONS:
        raise PermissionError("Account action denied")
