"""Bound-edit governance wiring only; Task 7 commands are not installed."""

from apps.accounts.contracts import SecurityOutcome
from apps.accounts.sessions import AccountActor
from apps.governance.audit import append_event
from apps.professionals.verification_models import Verification


def binding_hooks(actor: AccountActor):
    def record(outcome: SecurityOutcome) -> None:
        append_event(outcome, actor_uuid=actor.user_uuid, subject_type="verification")

    def emit(case: Verification) -> None:
        # Owner edits emit the installed professional.profile_changed effect.
        # A verification consumer is Task 7 scope. Audit/history are synchronous.
        return None

    return record, emit
