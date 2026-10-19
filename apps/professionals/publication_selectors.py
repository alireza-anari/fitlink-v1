"""Current source authority for an exact confirmed publication, never an index."""

from copy import deepcopy
from datetime import datetime
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from .contracts import ProfileNotFound
from .credential_models import CredentialRevision
from .models import ProfessionalProfile
from .policies import ready_asset
from .publication_contracts import (
    EffectivePublication,
    PublicationMediaSelection,
    PublicationSelection,
    PublicCredentialSummary,
    bounded_json,
    validate_public_snapshot,
)
from .publication_models import ProfessionalPublication
from .selectors import publication_eligibility


def stored_selection(value):
    if not isinstance(value, dict) or set(value) != {
        "fields",
        "roles",
        "qualification_revision_ids",
        "media",
        "slug",
        "valid_until",
    }:
        raise ValueError("Invalid stored publication selection")
    try:
        if any(
            not isinstance(value[k], list)
            for k in ("fields", "roles", "qualification_revision_ids", "media")
        ):
            raise ValueError
        media = []
        for row in value["media"]:
            if not isinstance(row, dict) or set(row) != {"purpose", "asset_uuid"}:
                raise ValueError
            media.append(
                PublicationMediaSelection(row["purpose"], UUID(row["asset_uuid"]))
            )
        expiry = value["valid_until"]
        selection = PublicationSelection(
            tuple(value["fields"]),
            tuple(value["roles"]),
            tuple(UUID(v) for v in value["qualification_revision_ids"]),
            tuple(media),
            value["slug"],
            datetime.fromisoformat(expiry) if expiry is not None else None,
        )
        if selection.as_selection_dict() != value:
            raise ValueError
        return selection
    except (ValueError, TypeError, KeyError, AttributeError):
        raise ValueError("Invalid stored publication selection") from None


def selected_sources(profile, selection):
    """Exact same-owner current qualification revisions and private branding only."""
    rows = {
        r.id: r
        for r in CredentialRevision.objects.filter(
            pk__in=selection.qualification_revision_ids
        ).select_related("credential__role")
    }
    qualifications = []
    for identifier in selection.qualification_revision_ids:
        row = rows.get(identifier)
        if row is None or (
            row.category != "qualification"
            or row.credential.profile_id != profile.id
            or row.credential.category != "qualification"
            or row.credential.withdrawn_at is not None
            or row.credential.current_revision_id != row.id
            or row.credential.role_id is None
            or row.credential.role.profile_id != profile.id
            or row.credential.role.role not in selection.roles
        ):
            raise ValueError("Selected qualification unavailable")
        qualifications.append(row)
    media = []
    for item in selection.media:
        if getattr(profile, item.purpose + "_id") != item.asset_uuid:
            raise ValueError("Selected branding is not current")
        try:
            asset = ready_asset(
                profile.user, profile, item.asset_uuid, item.purpose, None
            )
        except (ValueError, LookupError):
            raise ValueError("Selected branding unavailable") from None
        media.append((item.purpose, asset))
    return qualifications, media


def source_snapshot(profile, selection, qualifications):
    snapshot = {}
    for name in selection.fields:
        if name == "locations":
            snapshot[name] = [
                {
                    "country_code": r.country_code,
                    "region": r.region,
                    "city": r.city,
                    "modes": list(r.modes),
                }
                for r in profile.locations.filter(archived_at__isnull=True).order_by(
                    "country_code", "region", "city", "id"
                )
            ]
        else:
            snapshot[name] = deepcopy(getattr(profile, name))
    snapshot["verified_roles"] = sorted(selection.roles)
    snapshot["qualification_summaries"] = [
        PublicCredentialSummary(
            r.credential.role.role,
            r.title,
            r.issuer,
            r.type_code,
            r.issued_on,
            r.expires_on,
        ).as_public_dict()
        for r in qualifications
    ]
    snapshot["media_purposes"] = sorted(item.purpose for item in selection.media)
    validate_public_snapshot(snapshot)
    return snapshot


def source_is_current(profile, revision):
    if revision.source_profile_version != profile.version:
        return False
    selection = stored_selection(revision.selection)
    if selection.valid_until != revision.valid_until:
        return False
    qualifications, media = selected_sources(profile, selection)
    links = list(revision.selected_qualifications.order_by("position"))
    if len(links) != len(qualifications) or any(
        link.credential_revision_id != row.id
        or link.position != index
        or link.role != row.credential.role.role
        for index, (link, row) in enumerate(zip(links, qualifications, strict=True))
    ):
        return False
    bindings = {r.purpose: r for r in revision.selected_media.all()}
    if len(bindings) != len(media) or any(
        purpose not in bindings
        or bindings[purpose].asset_id != asset.id
        or bindings[purpose].asset_version != asset.version
        or bindings[purpose].processing_version != asset.processing_version
        for purpose, asset in media
    ):
        return False
    return source_snapshot(profile, selection, qualifications) == revision.snapshot


def _confirmed_publication(profile_uuid: UUID, at: datetime, media_revision=None):
    if (
        not isinstance(profile_uuid, UUID)
        or not isinstance(at, datetime)
        or not timezone.is_aware(at)
    ):
        raise ValueError("Invalid publication read context")
    with transaction.atomic():
        try:
            # Reuse C03's User-first locks and current account, identity, role,
            # restrictions, revocation, source/processing and expiry authority.
            facts = publication_eligibility(profile_uuid, at)
            if not facts.eligible or not facts.identity_verified:
                return None
            profile = ProfessionalProfile.objects.select_related("user").get(
                pk=profile_uuid
            )
            publication = (
                ProfessionalPublication.objects.select_for_update(of=("self",))
                .filter(
                    profile=profile,
                    state__in=(
                        ["published"]
                        if media_revision is None
                        else ["published", "publication_requested"]
                    ),
                    withdrawn_at__isnull=True,
                    hidden_at__isnull=True,
                    hidden_case_uuid__isnull=True,
                )
                .select_related("current_revision", "requested_revision")
                .first()
            )
            if publication is None:
                return None
            revision = (
                publication.current_revision
                if publication.state == "published"
                else publication.requested_revision
            )
            if revision is None or (
                media_revision is not None and revision.id != media_revision
            ):
                return None
            if (
                revision.publication_id != publication.id
                or revision.confirmed_by_id != profile.user_id
                or revision.confirmed_at is None
                or revision.confirmed_at > at
                or revision.valid_until is not None
                and revision.valid_until <= at
                or not source_is_current(profile, revision)
            ):
                return None
            roles = set(revision.snapshot["verified_roles"]) & set(facts.verified_roles)
            if not roles:
                return None
            approved = {
                binding.kind: set(binding.evidence_revision_ids)
                for binding in facts.evidence_binding.roles
                if binding.kind in roles
            }
            if any(
                link.role in roles
                and link.credential_revision_id not in approved.get(link.role, set())
                for link in revision.selected_qualifications.all()
            ):
                return None
            snapshot = deepcopy(revision.snapshot)
            snapshot["verified_roles"] = sorted(roles)
            snapshot["qualification_summaries"] = [
                r for r in snapshot["qualification_summaries"] if r["role"] in roles
            ]
            validate_public_snapshot(snapshot)
            return EffectivePublication(
                publication.id,
                revision.id,
                profile.id,
                publication.slug,
                publication.version,
                revision.source_profile_version,
                revision.valid_until,
                bounded_json(snapshot).decode(),
            )
        except (ProfileNotFound, ValueError, LookupError):
            return None


def effective_publication(profile_uuid: UUID, at: datetime):
    """Only an activated current revision can reach later public readers."""
    return _confirmed_publication(profile_uuid, at)


def confirmed_media_publication(profile_uuid: UUID, revision_uuid: UUID, at: datetime):
    """Same authority for preparing exact confirmed media, including pending copies."""
    if not isinstance(revision_uuid, UUID):
        raise ValueError("Invalid media release revision")
    return _confirmed_publication(profile_uuid, at, revision_uuid)
