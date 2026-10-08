"""Private owner projections and bounded command conflicts."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


class ProfileNotFound(LookupError):
    pass


class ProfileConflict(ValueError):
    pass


@dataclass(frozen=True)
class AthleteProfileDTO:
    id: UUID
    version: int
    state: str
    timezone: str
    onboarding_step: str
    current_baseline: UUID | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class BaselineStepInput:
    values: dict[str, object]


@dataclass(frozen=True)
class BaselineDTO:
    id: UUID
    athlete_id: UUID
    version: int
    state: str
    schema_version: int
    sequence: int
    parent: UUID | None
    observed_at: datetime
    age_at_assessment: int | None
    provenance: str
    submitted_at: datetime | None
    saved_at: datetime
    answers: dict[str, object]
    optional_access: bool
    completed_steps: tuple[str, ...]
