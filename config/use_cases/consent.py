from datetime import datetime
from uuid import UUID

from apps.accounts.contracts import SecurityOutcome
from apps.accounts.sessions import AccountActor
from apps.governance import consents
from apps.governance.audit import append_event
from apps.governance.outbox import append_outbox


def _record(actor: AccountActor, outcome: SecurityOutcome) -> None:
    append_event(outcome, actor_uuid=actor.user_uuid, subject_type="consent")
    if outcome.action in {"consent.revoked", "consent.granted"}:
        assert outcome.subject_uuid is not None
        row = consents.Consent.objects.get(pk=outcome.subject_uuid)
        append_outbox(
            outcome.action,
            row.id,
            row.version,
            {"consent_uuid": str(row.id), "user_uuid": str(actor.user_uuid)},
            f"{outcome.action}:{row.id}:{row.version}",
        )


def grant_consent(
    actor: AccountActor,
    scope: consents.ValidatedConsentScope,
    text_version: str,
    content_hash: str,
    at: datetime,
) -> UUID:
    return consents.grant_consent(
        actor,
        scope,
        text_version,
        content_hash,
        at,
        lambda outcome: _record(actor, outcome),
    )


def revoke_consent(
    actor: AccountActor, consent_uuid: UUID, expected_version: int, at: datetime
) -> None:
    consents.revoke_consent(
        actor,
        consent_uuid,
        expected_version,
        at,
        lambda outcome: _record(actor, outcome),
    )
