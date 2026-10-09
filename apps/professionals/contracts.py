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


@dataclass(frozen=True)
class VerificationTargetDTO:
    id: UUID
    target: str
    state: str
    version: int


@dataclass(frozen=True)
class VerificationOwnerDTO:
    id: UUID
    sequence: int
    state: str
    version: int
    submitted_at: datetime | None
    targets: tuple[VerificationTargetDTO, ...]
    history: tuple[tuple[str, UUID | None, datetime], ...]


@dataclass(frozen=True)
class VerificationEvidenceDTO:
    revision_uuid: UUID
    asset_uuid: UUID
    category: str
    type_code: str
    issuer: str
    title: str
    issued_on: date | None
    expires_on: date | None


@dataclass(frozen=True)
class VerificationStaffDTO:
    id: UUID
    state: str
    version: int
    submitted_at: datetime | None
    targets: tuple[VerificationTargetDTO, ...]
    identity_name: str
    evidence: tuple[VerificationEvidenceDTO, ...]
    assignment_uuid: UUID | None


@dataclass(frozen=True)
class VerificationQueueItem:
    id: UUID
    state: str
    submitted_at: datetime
    requested_targets: tuple[str, ...]


@dataclass(frozen=True)
class VerificationQueueDTO:
    items: tuple[VerificationQueueItem, ...]
    next_cursor: tuple[datetime, UUID] | None
