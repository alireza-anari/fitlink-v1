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
