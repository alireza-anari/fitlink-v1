"""Explicit private owner projection, never a model serializer."""

from dataclasses import dataclass, field
from datetime import date, datetime
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
    fields: dict[str, object] = field(default_factory=dict)
    roles: tuple["ProfessionalRoleDTO", ...] = ()
    locations: tuple["ProfessionalLocationDTO", ...] = ()


@dataclass(frozen=True)
class ProfessionalStepInput:
    values: dict[str, object]


@dataclass(frozen=True)
class CredentialInput:
    values: dict[str, object]


@dataclass(frozen=True)
class ProfessionalRoleDTO:
    id: UUID
    role: str
    declared_active: bool
    version: int
    declaration_version: int
    evidence_revision: int
    decision_version: int


@dataclass(frozen=True)
class ProfessionalLocationDTO:
    id: UUID
    country_code: str
    region: str
    city: str
    modes: tuple[str, ...]
    version: int


@dataclass(frozen=True)
class CredentialDTO:
    id: UUID
    version: int
    category: str
    role: str | None
    type_code: str
    issuer: str
    title: str
    issued_on: date | None
    expires_on: date | None
    current_revision_id: UUID | None
    withdrawn_at: datetime | None
