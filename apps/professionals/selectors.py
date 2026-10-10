"""Coherent current-session own projection; no publication authority."""

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from uuid import UUID

from django.db import transaction

from apps.accounts.sessions import AccountActor, locked_actor

from .contracts import (
    CredentialDTO,
    ProfessionalLocationDTO,
    ProfessionalProfileDTO,
    ProfessionalRoleDTO,
    ProfileNotFound,
)
from .models import Credential, ProfessionalProfile
from .policies import owned_profile, validate_context
from .restrictions import RestrictionToken
from .validation import PROFILE_FIELDS


def project_credential(row: Credential) -> CredentialDTO:
    return CredentialDTO(
        row.id,
        row.version,
        row.category,
        row.role.role if row.role is not None else None,
        row.type_code,
        row.issuer,
        row.title,
        row.issued_on,
        row.expires_on,
        row.current_revision_id,
        row.withdrawn_at,
    )


def own_credential(
    actor: AccountActor, credential_uuid: UUID, at: datetime
) -> CredentialDTO:
    validate_context(actor, at)
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_read", at)
        profile = (
            ProfessionalProfile.objects.select_for_update()
            .filter(user=user)
            .exclude(state="archived")
            .first()
        )
        if profile is None or not isinstance(credential_uuid, UUID):
            raise ProfileNotFound("Credential unavailable")
        row = (
            Credential.objects.filter(pk=credential_uuid, profile=profile)
            .select_related("role")
            .first()
        )
        if row is None:
            raise ProfileNotFound("Credential unavailable")
        return project_credential(row)


def own_professional_profile(
    actor: AccountActor, at: datetime
) -> ProfessionalProfileDTO:
    validate_context(actor, at)
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_read", at)
        identifier = (
            ProfessionalProfile.objects.filter(user=user)
            .values_list("id", flat=True)
            .first()
        )
        if identifier is None:
            raise ProfileNotFound("Profile unavailable")
        row = owned_profile(user, identifier, lock=True)
        return ProfessionalProfileDTO(
            row.id,
            row.version,
            row.state,
            row.setup_step,
            row.created_at,
            row.updated_at,
            deepcopy(
                {
                    name: getattr(
                        row,
                        name + "_id" if name in {"avatar", "cover", "logo"} else name,
                    )
                    for name in PROFILE_FIELDS
                }
            ),
            tuple(
                ProfessionalRoleDTO(
                    role.id,
                    role.role,
                    role.declared_active,
                    role.version,
                    role.declaration_version,
                    role.evidence_revision,
                    role.decision_version,
                )
                for role in row.roles.order_by("role")
            ),
            tuple(
                ProfessionalLocationDTO(
                    location.id,
                    location.country_code,
                    location.region,
                    location.city,
                    tuple(location.modes),
                    location.version,
                )
                for location in row.locations.filter(archived_at__isnull=True).order_by(
                    "country_code", "region", "city", "id"
                )
            ),
        )


def owner_preview(actor: AccountActor, at: datetime):
    from .preview import owner_preview as preview

    return preview(actor, at)


def own_verification(actor: AccountActor, verification_uuid: UUID, at: datetime):
    """Coarse immutable target/history view with no staff-private explanation."""
    from uuid import uuid4

    from apps.accounts.contracts import SecurityOutcome
    from apps.governance import audit

    from .setup import locked_profile
    from .verification import _case, _owner_dto

    validate_context(actor, at)
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_read", at)
        profile = locked_profile(user)
        case = _case(profile, verification_uuid)
        audit.append_event(
            SecurityOutcome(
                "verification.read", "succeeded", case.id, uuid4(), (), "user_requested"
            ),
            actor_uuid=actor.user_uuid,
            subject_type="verification",
        )
        return _owner_dto(case)


@dataclass(frozen=True)
class BlockedRole:
    role: str
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class TargetEvidenceBinding:
    kind: str
    declaration_version: int | None
    evidence_revision: int
    decision_version: int
    effective_decision_uuid: UUID | None
    snapshot_hash: str | None = field(repr=False)
    evidence_revision_ids: tuple[UUID, ...]
    restriction_token: RestrictionToken | None
    next_expiry_boundary: datetime | None


@dataclass(frozen=True)
class SelectedMediaBinding:
    purpose: str
    asset_uuid: UUID
    asset_version: int | None
    processing_version: int | None
    ready: bool


@dataclass(frozen=True)
class EligibilityEvidenceBinding:
    user_auth_version: int
    user_state_version: int
    profile_version: int
    profile_state: str
    identity: TargetEvidenceBinding
    roles: tuple[TargetEvidenceBinding, ...]
    selected_media: tuple[SelectedMediaBinding, ...]


@dataclass(frozen=True)
class PublicationEligibility:
    identity_verified: bool
    verified_roles: tuple[str, ...]
    eligible: bool
    reason_codes: tuple[str, ...]
    blocked_roles: tuple[BlockedRole, ...]
    evaluated_at: datetime
    evidence_binding: EligibilityEvidenceBinding = field(repr=False)


def _approval_facts(owner, profile, credentials, kind, role, at):
    from datetime import time, timedelta

    from django.core.exceptions import ObjectDoesNotExist

    from .policies import ready_asset
    from .restrictions import restriction_token
    from .verification import (
        _current_revisions,
        _validate_revisions,
        effective_decision,
    )

    latest = effective_decision(profile, kind)
    reasons = []
    try:
        revisions = _current_revisions(credentials, kind)
    except (ValueError, LookupError, ObjectDoesNotExist):
        revisions = []
        reasons.append("evidence_unavailable")
    token = restriction_token(role)
    expiries: list[date] = [r.expires_on for r in revisions if r.expires_on is not None]
    binding = TargetEvidenceBinding(
        kind,
        role.declaration_version if role else None,
        role.evidence_revision if role else profile.identity_evidence_revision,
        role.decision_version if role else profile.identity_decision_version,
        latest.id if latest else None,
        latest.target_snapshot_hash if latest else None,
        tuple(r.id for r in revisions),
        token,
        datetime.combine(min(expiries) + timedelta(days=1), time.min, UTC)
        if expiries and min(expiries) < date.max
        else None,
    )
    if latest is None or latest.decision != "approve":
        reasons.append(
            "approval_missing" if latest is None else "approval_" + latest.decision
        )
    else:
        target = latest.target
        if (
            latest.bound_evidence_revision != binding.evidence_revision
            or target.target_snapshot_hash != latest.target_snapshot_hash
            or target.state != "approved"
            or (role is None and target.identity_name != profile.identity_name)
            or set(target.evidence.values_list("credential_revision_id", flat=True))
            != {r.id for r in revisions}
            or latest.revocations.exists()
        ):
            reasons.append("evidence_changed")
        else:
            try:
                _validate_revisions(owner, profile, revisions, at, ready_asset)
            except (ValueError, LookupError):
                reasons.append("evidence_unavailable")
    if role is not None:
        if not role.declared_active:
            reasons.append("declaration_inactive")
        if token and any(not released for _, _, released in token.episodes):
            reasons.append("role_restricted")
    return not reasons, tuple(reasons), binding


def publication_eligibility(profile_uuid: UUID, at: datetime) -> PublicationEligibility:
    """Internal coherent evidence facts; callers must recheck at consumption."""
    from django.db.models import Q
    from django.utils import timezone

    from apps.accounts.dates import require_adult
    from apps.accounts.models import User
    from apps.assets.models import Asset

    from .models import (
        CredentialRevision,
        Verification,
        VerificationEvidence,
        VerificationTarget,
    )
    from .policies import ready_asset
    from .restrictions import ProfessionalRoleRestriction
    from .setup import locked_roles

    if (
        not isinstance(profile_uuid, UUID)
        or not isinstance(at, datetime)
        or not timezone.is_aware(at)
    ):
        raise ValueError("Invalid eligibility context")
    with transaction.atomic():
        owner_id = (
            ProfessionalProfile.objects.filter(pk=profile_uuid)
            .values_list("user_id", flat=True)
            .first()
        )
        if owner_id is None:
            raise ProfileNotFound("Profile unavailable")
        owner = User.objects.select_for_update().get(pk=owner_id)
        profile = ProfessionalProfile.objects.select_for_update().get(
            pk=profile_uuid, user=owner
        )
        roles = locked_roles(profile)
        credentials = list(
            Credential.objects.select_for_update()
            .filter(profile=profile)
            .order_by("id")
        )
        cases = list(
            Verification.objects.select_for_update()
            .filter(profile=profile)
            .order_by("id")
        )
        targets = list(
            VerificationTarget.objects.select_for_update()
            .filter(verification__in=cases)
            .order_by("id")
        )
        list(
            ProfessionalRoleRestriction.objects.select_for_update()
            .filter(role__in=roles)
            .order_by("id")
        )
        list(
            VerificationEvidence.objects.select_for_update()
            .filter(target__in=targets)
            .order_by("id")
        )
        list(
            Asset.objects.select_for_update()
            .filter(
                Q(
                    pk__in=CredentialRevision.objects.filter(
                        credential__in=credentials
                    ).values("source_asset_id")
                )
                | Q(pk__in=[profile.avatar_id, profile.cover_id, profile.logo_id])
            )
            .order_by("id")
        )
        media_bindings = []
        for purpose in ("avatar", "cover", "logo"):
            identifier = getattr(profile, purpose + "_id")
            if identifier is None:
                continue
            asset = Asset.objects.filter(pk=identifier).first()
            try:
                ready_asset(owner, profile, identifier, purpose, None)
                media_ready = True
            except (ValueError, LookupError):
                media_ready = False
            media_bindings.append(
                SelectedMediaBinding(
                    purpose,
                    identifier,
                    asset.version if asset else None,
                    asset.processing_version if asset else None,
                    media_ready,
                )
            )
        media_ok = all(binding.ready for binding in media_bindings)
        identity, identity_reasons, identity_binding = _approval_facts(
            owner, profile, credentials, "identity", None, at
        )
        verified, blocked, bindings = [], [], []
        for role in sorted(roles, key=lambda r: r.role):
            ok, reasons, binding = _approval_facts(
                owner, profile, credentials, role.role, role, at
            )
            bindings.append(binding)
            if ok:
                verified.append(role.role)
            else:
                blocked.append(BlockedRole(role.role, reasons))
        reasons = list(identity_reasons)
        account_ok = (
            owner.is_active
            and owner.state == "active"
            and bool(owner.adult_attested_at and owner.adult_attestation_version)
        )
        try:
            if owner.birth_date is None:
                raise ValueError("Adult declaration required")
            require_adult(owner.birth_date, True, at)
        except ValueError:
            account_ok = False
        if not account_ok:
            reasons.append("account_unavailable")
        if profile.state != "private_ready":
            reasons.append("profile_incomplete")
        if not verified:
            reasons.append("verified_role_required")
        if not media_ok:
            reasons.append("media_unavailable")
        return PublicationEligibility(
            identity,
            tuple(verified),
            identity
            and account_ok
            and profile.state == "private_ready"
            and media_ok
            and bool(verified),
            tuple(reasons),
            tuple(blocked),
            at,
            EligibilityEvidenceBinding(
                owner.auth_version,
                owner.state_version,
                profile.version,
                profile.state,
                identity_binding,
                tuple(bindings),
                tuple(media_bindings),
            ),
        )
