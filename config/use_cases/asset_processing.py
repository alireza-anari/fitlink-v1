"""Composition owns subject/governance fences; assets owns bounded private I/O."""

import hashlib
import json

from django.conf import settings
from django.db.models import Q

from apps.assets import processing
from apps.assets.contracts import AssetNotFound
from apps.governance.consent_models import ConsentScope
from apps.governance.privacy_models import RecordHold
from apps.professionals.models import Credential, ProfessionalProfile, ProfessionalRole


def authority(user, asset, at):
    profile = ProfessionalProfile.objects.select_for_update().filter(user=user).first()
    if profile is None or profile.state == "archived":
        raise AssetNotFound("Asset unavailable")
    facts = [
        str(profile.id),
        profile.version,
        profile.state,
        profile.identity_evidence_revision,
        profile.identity_decision_version,
    ]
    if asset.purpose in {"avatar", "cover", "logo"}:
        if (
            asset.subject_kind != "professional_profile"
            or asset.subject_uuid != profile.id
        ):
            raise AssetNotFound("Asset unavailable")
    else:
        # Lock parent roles before credentials, in deterministic order.
        roles = list(
            ProfessionalRole.objects.select_for_update()
            .filter(profile=profile)
            .order_by("id")
        )
        credential = (
            Credential.objects.select_for_update()
            .filter(
                pk=asset.subject_uuid,
                profile=profile,
                withdrawn_at__isnull=True,
                category="identity"
                if asset.purpose == "identity_evidence"
                else "qualification",
            )
            .first()
        )
        if asset.subject_kind != "professional_credential" or credential is None:
            raise AssetNotFound("Asset unavailable")
        if credential.expires_on and credential.expires_on < at.date():
            raise AssetNotFound("Asset unavailable")
        facts += [
            str(credential.id),
            credential.version,
            str(credential.current_revision_id),
            str(credential.expires_on),
            credential.category,
        ]
        if asset.purpose == "credential_evidence":
            role = next(
                (r for r in roles if r.id == credential.role_id and r.declared_active),
                None,
            )
            if role is None:
                raise AssetNotFound("Asset unavailable")
            facts += [
                str(role.id),
                role.version,
                role.declaration_version,
                role.evidence_revision,
                role.decision_version,
            ]
    # Holds retain records; they never grant access. All exact-record changes fence
    # release, and no processing path deletes a held source or derivative inventory.
    subjects = Q(subject_kind="profile_asset", subject_uuid=asset.id)
    if asset.subject_kind == "professional_credential":
        subjects |= Q(subject_kind=asset.subject_kind, subject_uuid=asset.subject_uuid)
    holds = list(
        RecordHold.objects.select_for_update()
        .filter(subjects, owner_uuid=user.public_id)
        .order_by("id")
    )
    facts += [
        [str(h.id), h.subject_version, h.version, str(h.released_at), str(h.expires_at)]
        for h in holds
    ]
    # No professional self-storage consent purpose is installed. Existing exact
    # account-metadata scopes are fences, never invented grants or sharing authority.
    scopes = list(
        ConsentScope.objects.filter(
            kind__in=["profile_asset", "professional_credential"],
            object_uuid__in=[asset.id, asset.subject_uuid],
            consent__subject=user,
        )
        .select_related("consent")
        .order_by("id")
    )
    facts += [
        [
            str(s.id),
            s.object_version,
            s.consent.version,
            str(s.consent.revoked_at),
            str(s.consent.expires_at),
        ]
        for s in scopes
    ]
    facts += [
        asset.subject_kind,
        str(asset.subject_uuid),
        asset.purpose,
        asset.source_key,
        asset.sha256,
        asset.actual_size,
        asset.detected_type,
        str(asset.finalized_at),
        str(asset.accepted_at),
    ]
    return hashlib.sha256(json.dumps(facts, separators=(",", ":")).encode()).hexdigest()


def request_processing(event, at):
    return processing.request_processing(event, at)


def scan_due_assets(at, batch_size=100, *, enqueue=None):
    if enqueue is None and not settings.ASSET_PROCESSING_ENABLED:
        return 0
    return processing.scan_due_assets(
        at, batch_size, enqueue=enqueue, authority=authority
    )


def process_asset(
    asset_uuid, processing_version, lease_uuid, at, *, store=None, scanner=None
):
    return processing.process_asset(
        asset_uuid,
        processing_version,
        lease_uuid,
        at,
        store=store,
        scanner=scanner,
        authority=authority,
    )
