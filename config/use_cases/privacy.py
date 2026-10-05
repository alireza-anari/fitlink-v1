from datetime import datetime
from uuid import UUID

from apps.accounts.contracts import SecurityOutcome
from apps.accounts.sessions import AccountActor
from apps.accounts.state import transition_account_state
from apps.governance import privacy
from apps.governance.audit import append_event
from apps.governance.outbox import append_outbox
from apps.governance.privacy import privacy_status as privacy_status
from apps.governance.privacy import visible_requests as visible_requests


def _record(actor: AccountActor, outcome: SecurityOutcome) -> None:
    assert outcome.subject_uuid is not None
    append_event(
        outcome,
        actor_uuid=actor.user_uuid,
        subject_type="privacy"
        if outcome.action == "privacy.intake"
        else "consent"
        if outcome.action == "consent.revoked"
        else "account",
    )
    if outcome.action == "privacy.intake":
        append_outbox(
            "privacy.intake_recorded",
            outcome.subject_uuid,
            1,
            {
                "privacy_uuid": str(outcome.subject_uuid),
                "user_uuid": str(actor.user_uuid),
            },
            f"privacy.intake:{outcome.subject_uuid}",
        )
    elif outcome.action == "consent.revoked":
        row = privacy.Consent.objects.get(pk=outcome.subject_uuid)
        append_outbox(
            "consent.revoked",
            row.id,
            row.version,
            {"consent_uuid": str(row.id), "user_uuid": str(actor.user_uuid)},
            f"consent.revoked:{row.id}:{row.version}",
        )
    elif outcome.action == "account.state_changed":
        from apps.accounts.models import User

        user = User.objects.get(public_id=actor.user_uuid)
        append_outbox(
            "account.security_changed",
            user.public_id,
            user.auth_version,
            {"user_uuid": str(user.public_id)},
            f"account.security_changed:{user.public_id}:{user.auth_version}",
        )


def request_privacy(
    actor: AccountActor,
    kind: str,
    request_id: UUID,
    at: datetime,
    *,
    confirmed: bool = False,
) -> UUID:
    def restrict(user, when):
        transition_account_state(
            user.public_id,
            user.auth_version,
            "pending_deletion",
            when,
            lambda outcome: _record(actor, outcome),
        )

    return privacy.request_privacy(
        actor,
        kind,
        request_id,
        at,
        lambda outcome: _record(actor, outcome),
        confirmed=confirmed,
        restrict=restrict,
    )
