from datetime import datetime
from uuid import UUID

from django.core import signing

from apps.accounts import referrals
from apps.accounts.contracts import SecurityOutcome
from apps.accounts.models import User
from apps.accounts.sessions import AccountActor
from apps.governance.audit import append_event

resolve_referral = referrals.resolve_referral
revoke_referral = referrals.revoke_referral


def _record(actor_uuid: UUID, outcome: SecurityOutcome) -> None:
    append_event(outcome, actor_uuid=actor_uuid, subject_type="referral")


def issue_referral(actor: AccountActor, at: datetime) -> str:
    return referrals.issue_referral(
        actor, at, lambda outcome: _record(actor.user_uuid, outcome)
    )


def bind_attribution(user: User, token: str, at: datetime) -> UUID:
    return referrals.bind_attribution(
        user, token, at, lambda outcome: _record(user.public_id, outcome)
    )


def bind_cookie(user: User, cookie: str, at: datetime) -> UUID | None:
    try:
        payload = signing.loads(
            cookie, salt="fitlink.referral", max_age=referrals.REFERRAL_SECONDS
        )
        if not isinstance(payload, dict) or set(payload) != {"link"}:
            return None
        descriptor = referrals.ReferralDescriptor(UUID(payload["link"]))
    except (signing.BadSignature, ValueError, TypeError):
        return None
    try:
        return referrals.bind_descriptor(
            user, descriptor, at, lambda outcome: _record(user.public_id, outcome)
        )
    except PermissionError:
        return None
