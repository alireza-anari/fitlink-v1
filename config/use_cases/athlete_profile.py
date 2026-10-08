"""Synchronous audit wiring; owner is always derived from AccountActor."""

from datetime import datetime
from uuid import UUID

from apps.accounts.contracts import SecurityOutcome
from apps.accounts.sessions import AccountActor
from apps.athletes import baseline, services
from apps.athletes.contracts import AthleteProfileDTO, BaselineDTO, BaselineStepInput
from apps.governance.audit import append_event
from apps.governance.outbox import append_outbox
from config.use_cases.c03_privacy import (
    baseline_storage_current,
)
from config.use_cases.c03_privacy import (
    grant_baseline_storage as grant_baseline_storage,
)
from config.use_cases.c03_privacy import (
    revoke_baseline_storage as revoke_baseline_storage,
)


def create_athlete_profile(
    actor: AccountActor, operation_id: UUID, at: datetime
) -> AthleteProfileDTO:
    def record(outcome: SecurityOutcome) -> None:
        append_event(outcome, actor_uuid=actor.user_uuid, subject_type="athlete")

    return services.create_athlete_profile(
        actor,
        operation_id,
        at,
        record=record,
    )


def _callbacks(actor: AccountActor):
    def record(outcome: SecurityOutcome) -> None:
        append_event(outcome, actor_uuid=actor.user_uuid, subject_type="baseline")

    def emit(row) -> None:
        append_outbox(
            "athlete.baseline_changed",
            row.id,
            row.version,
            {"baseline_uuid": str(row.id), "user_uuid": str(actor.user_uuid)},
            f"athlete.baseline_changed:{row.id}:{row.version}",
        )

    return record, emit


def begin_baseline(
    actor: AccountActor, expected_profile_version: int, operation_id: UUID, at: datetime
) -> BaselineDTO:
    record, emit = _callbacks(actor)
    return baseline.begin_baseline(
        actor,
        expected_profile_version,
        operation_id,
        at,
        storage=baseline_storage_current,
        record=record,
        emit=emit,
    )


def save_baseline_step(
    actor: AccountActor,
    baseline_uuid: UUID,
    step: str,
    input: BaselineStepInput,
    expected_version: int,
    operation_id: UUID,
    at: datetime,
) -> BaselineDTO:
    record, emit = _callbacks(actor)
    return baseline.mutate_baseline(
        actor,
        baseline_uuid,
        expected_version,
        operation_id,
        at,
        "baseline.save_step",
        step=step,
        payload=input,
        storage=baseline_storage_current,
        record=record,
        emit=emit,
    )


def _mutate(
    actor: AccountActor,
    baseline_uuid: UUID,
    expected_version: int,
    operation_id: UUID,
    at: datetime,
    command: str,
) -> BaselineDTO:
    record, emit = _callbacks(actor)
    return baseline.mutate_baseline(
        actor,
        baseline_uuid,
        expected_version,
        operation_id,
        at,
        command,
        storage=baseline_storage_current,
        record=record,
        emit=emit,
    )


def submit_baseline(
    actor: AccountActor,
    baseline_uuid: UUID,
    expected_version: int,
    operation_id: UUID,
    at: datetime,
) -> BaselineDTO:
    return _mutate(
        actor, baseline_uuid, expected_version, operation_id, at, "baseline.submit"
    )


def correct_baseline(
    actor: AccountActor,
    baseline_uuid: UUID,
    expected_version: int,
    operation_id: UUID,
    at: datetime,
) -> BaselineDTO:
    return _mutate(
        actor, baseline_uuid, expected_version, operation_id, at, "baseline.correct"
    )


def clear_optional_baseline(
    actor: AccountActor,
    baseline_uuid: UUID,
    expected_version: int,
    operation_id: UUID,
    at: datetime,
) -> BaselineDTO:
    return _mutate(
        actor, baseline_uuid, expected_version, operation_id, at, "baseline.clear"
    )


def own_baseline(actor: AccountActor, baseline_uuid: UUID, at: datetime) -> BaselineDTO:
    from apps.athletes.selectors import own_baseline as select_baseline

    record, _ = _callbacks(actor)
    return select_baseline(
        actor, baseline_uuid, at, storage=baseline_storage_current, record=record
    )
