"""Explicit private owner projection, never a model serializer."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


class ProfileNotFound(LookupError):
    pass


class ProfileConflict(ValueError):
    pass


@dataclass(frozen=True)
class ProfessionalProfileDTO:
    id: UUID
    version: int
    state: str
    setup_step: str
    created_at: datetime
    updated_at: datetime
