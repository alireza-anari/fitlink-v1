"""Current identity eligibility; declared adulthood is never age verification."""

from datetime import date, datetime

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
