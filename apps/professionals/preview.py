"""Authenticated private presentation; verification never publishes a profile."""

from datetime import datetime

from django.db import transaction

from apps.accounts.sessions import AccountActor, locked_actor

from .contracts import OwnerPreviewDTO, PreviewMediaDTO, PreviewRoleDTO
from .models import VerificationTarget
from .policies import ready_asset, validate_context
from .selectors import (
    TargetEvidenceBinding,
    own_professional_profile,
    publication_eligibility,
)
from .setup import locked_profile


def _status(profile, binding: TargetEvidenceBinding, verified: bool, reasons) -> str:
    if verified:
        return "approved"
    # Current denials remain separate from the private declaration and history.
    for reason, status in (
        ("approval_revoke", "revoked"),
        ("role_restricted", "restricted"),
        ("declaration_inactive", "inactive"),
        ("evidence_changed", "stale"),
        ("evidence_unavailable", "unavailable"),
    ):
        if reason in reasons:
            return status
    pending = (
        VerificationTarget.objects.filter(
            verification__profile=profile,
            target=binding.kind,
            bound_evidence_revision=binding.evidence_revision,
            bound_decision_version=binding.decision_version,
            bound_declaration_version=binding.declaration_version,
            state__in=["draft", "submitted", "under_review", "stale", "withdrawn"],
        )
        .order_by("-verification__sequence")
        .first()
    )
    if pending is not None:
        return pending.state
    return "rejected" if "approval_reject" in reasons else "unverified"


def owner_preview(actor: AccountActor, at: datetime) -> OwnerPreviewDTO:
    validate_context(actor, at)
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_read", at)
        profile = locked_profile(user)
        facts = publication_eligibility(profile.id, at)
        own = own_professional_profile(actor, at)
        blocked = {entry.role: entry.reason_codes for entry in facts.blocked_roles}
        bindings = {entry.kind: entry for entry in facts.evidence_binding.roles}
        roles = tuple(
            PreviewRoleDTO(
                role.role,
                role.declared_active,
                role.role in facts.verified_roles,
                _status(
                    profile,
                    bindings[role.role],
                    role.role in facts.verified_roles,
                    blocked.get(role.role, ()),
                ),
            )
            for role in own.roles
        )
        media = []
        for purpose in ("avatar", "cover", "logo"):
            identifier = getattr(profile, purpose + "_id")
            if identifier is None:
                continue
            try:
                asset = ready_asset(user, profile, identifier, purpose, None)
            except (ValueError, LookupError):
                continue
            derivative = (
                asset.derivatives.select_for_update()
                .filter(
                    processing_version=asset.processing_version,
                    purpose="owner_preview",
                    state="ready",
                    mime_type__in=["image/jpeg", "image/png"],
                )
                .first()
            )
            if derivative is not None:
                media.append(
                    PreviewMediaDTO(
                        asset.id, derivative.id, purpose, derivative.mime_type
                    )
                )
        return OwnerPreviewDTO(
            id=profile.id,
            version=profile.version,
            state=profile.state,
            display_name=profile.display_name,
            biography=profile.biography,
            specialties=tuple(profile.specialties),
            experience_years=profile.experience_years,
            service_modes=tuple(profile.service_modes),
            languages=tuple(profile.languages),
            locations=own.locations,
            accent_color=profile.accent_color,
            welcome_message=profile.welcome_message,
            identity_verified=facts.identity_verified,
            identity_status=_status(
                profile,
                facts.evidence_binding.identity,
                facts.identity_verified,
                facts.reason_codes,
            ),
            roles=roles,
            verified_roles=facts.verified_roles,
            media=tuple(media),
        )
