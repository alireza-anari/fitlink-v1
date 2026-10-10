"""Explicit private owner projection, never a model serializer."""

from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID


class ProfileNotFound(LookupError):
    pass


class ProfileConflict(ValueError):
    pass


@dataclass(frozen=True)
class PreviewRoleDTO:
    role: str
    declared_active: bool
    verified: bool
    status: str


@dataclass(frozen=True)
class PreviewMediaDTO:
    asset_uuid: UUID
    derivative_uuid: UUID
    purpose: str
    content_type: str


@dataclass(frozen=True)
class OwnerPreviewDTO:
    id: UUID
    version: int
    state: str
    display_name: str
    biography: str
    specialties: tuple[str, ...]
    experience_years: int | None
    service_modes: tuple[str, ...]
    languages: tuple[str, ...]
    locations: tuple["ProfessionalLocationDTO", ...]
    accent_color: str
    welcome_message: str
    identity_verified: bool
    identity_status: str
    roles: tuple[PreviewRoleDTO, ...]
    verified_roles: tuple[str, ...]
    media: tuple[PreviewMediaDTO, ...]
    cache_control: str = "private, no-store"
    robots: str = "noindex, nofollow"


@dataclass(frozen=True)
class AssistantMembershipDTO:
    id: UUID
    profile_uuid: UUID
    assistant_uuid: UUID
    role: str
    state: str
    version: int
    defined_at: datetime
    revoked_at: datetime | None


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
