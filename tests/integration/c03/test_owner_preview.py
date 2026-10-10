"""Real current owner sessions and separate private verification facts."""

import importlib
import importlib.util
from dataclasses import asdict, replace
from datetime import timedelta
from uuid import uuid4

import pytest
from django.utils import timezone

from apps.accounts.security_models import AccountSessionControl
from apps.professionals.contracts import ProfileNotFound
from apps.professionals.models import AssistantMembership, ProfessionalProfile

from .profile_helpers import make_actor
from .test_professional_setup import owner, save
from .test_verification_decisions import approved, decision, review
from .test_verification_revocation import restrict, revoke
from .verification_helpers import submitted

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def preview(actor, at=None):
    from apps.professionals import selectors

    assert callable(getattr(selectors, "owner_preview", None)), "Missing owner preview"
    return selectors.owner_preview(actor, at or timezone.now())


@pytest.mark.parametrize(
    "state", ["unverified", "submitted", "under_review", "partial", "verified"]
)
def test_unverified_verified_preview_owner_only_and_noindex(settings, state):
    if state == "unverified":
        s = owner()
    elif state == "submitted":
        s = submitted()
    elif state == "verified":
        s = approved(settings)
    else:
        s = review(settings)
        if state == "partial":
            decision(s, "identity")
            decision(s, "coach")
    dto = preview(s.actor)
    assert dto.id == s.profile.id
    assert dto.cache_control == "private, no-store"
    assert dto.robots == "noindex, nofollow"
    assert dto.identity_verified == (state in {"partial", "verified"})
    assert dto.verified_roles == (
        ()
        if state not in {"partial", "verified"}
        else ("coach",)
        if state == "partial"
        else ("coach", "nutritionist")
    )
    if state in {"submitted", "under_review"}:
        assert dto.identity_status == state
    foreign = make_actor("+989123456789")
    with pytest.raises(ProfileNotFound):
        preview(foreign.actor)
    ProfessionalProfile.objects.create(user=foreign.user, display_name="Foreign")
    assert preview(foreign.actor).id != dto.id


def test_preview_dto_no_evidence_keys_or_staff_notes(settings):
    s = approved(settings)
    dto = asdict(preview(s.actor))
    serialized = str(dto)
    for secret in (
        s.profile.identity_name,
        "Private synthetic explanation",
        "source_key",
        "sha256",
        "snapshot_hash",
        "evidence_binding",
        "current_revision",
        "signed",
        "http",
        "credentials",
    ):
        assert secret not in serialized
    assert not any(str(asset.id) in serialized for asset, _ in s.assets.values())
    assert dto["display_name"] == s.profile.display_name


@pytest.mark.parametrize(
    "fault",
    [
        "anonymous",
        "membership_actor",
        "auth_version",
        "session_revoked",
        "session_expired",
        "restricted",
        "suspended",
        "pending_deletion",
        "archived",
        "guessed_owner",
    ],
)
def test_preview_requires_current_exact_account_authority(fault):
    s = owner()
    actor, at = s.actor, timezone.now()
    if fault == "anonymous":
        actor = None
    elif fault == "membership_actor":
        other = make_actor("+989123456789")
        actor = AssistantMembership.objects.create(
            profile=s.profile, assistant=other.user
        )
    elif fault == "auth_version":
        s.user.auth_version += 1
        s.user.save(update_fields=["auth_version"])
    elif fault == "session_revoked":
        AccountSessionControl.objects.filter(pk=actor.control_id).update(revoked_at=at)
    elif fault == "session_expired":
        at = AccountSessionControl.objects.get(pk=actor.control_id).expires_at
    elif fault in {"restricted", "suspended", "pending_deletion"}:
        s.user.state = fault
        s.user.is_active = fault != "suspended"
        s.user.save(update_fields=["state", "is_active"])
    elif fault == "archived":
        s.profile.state = "archived"
        s.profile.save(update_fields=["state"])
    else:
        other = make_actor("+989123456789")
        actor = replace(other.actor, user_uuid=s.user.public_id)
    with pytest.raises((PermissionError, ProfileNotFound)):
        preview(actor, at)


def test_staff_and_assistant_do_not_substitute_for_owner(settings):
    s = approved(settings)
    assistant = make_actor("+989123456789")
    AssistantMembership.objects.create(profile=s.profile, assistant=assistant.user)
    s.staff.user.is_staff = s.staff.user.is_superuser = True
    s.staff.user.save(update_fields=["is_staff", "is_superuser"])
    for actor in (s.staff.actor, assistant.actor):
        with pytest.raises(ProfileNotFound):
            preview(actor)


def test_c04_input_excludes_unverified_declarations(settings):
    from apps.professionals.selectors import publication_eligibility

    s = review(settings)
    decision(s, "identity")
    decision(s, "coach")
    decision(s, "nutritionist", "reject")
    dto = preview(s.actor)
    assert dto.identity_verified and dto.verified_roles == ("coach",)
    assert {r.role for r in dto.roles if r.declared_active} == {"coach", "nutritionist"}
    assert {r.role: r.status for r in dto.roles} == {
        "coach": "approved",
        "nutritionist": "rejected",
    }
    internal = publication_eligibility(s.profile.id, timezone.now())
    assert internal.eligible and internal.verified_roles == dto.verified_roles
    assert not hasattr(dto, "evidence_binding")
    assert internal.evidence_binding.profile_version == dto.version


def test_preview_rechecks_restriction_release_revocation(settings):
    from apps.professionals.selectors import publication_eligibility

    s = approved(settings)
    before = publication_eligibility(s.profile.id, timezone.now())
    restrict(s)
    assert preview(s.actor).verified_roles == ("coach",)
    restrict(s, release=True)
    assert preview(s.actor).verified_roles == ("coach", "nutritionist")
    revoke(s, "nutritionist")
    assert preview(s.actor).verified_roles == ("coach",)
    assert (
        publication_eligibility(s.profile.id, timezone.now()).evidence_binding
        != before.evidence_binding
    )


def test_preview_expiry_revalidates_without_counter_change(settings):
    s = approved(settings)
    future = timezone.now() + timedelta(days=2)
    # Renew owner authority so the evidence expiry predicate is decisive.
    from django.db import transaction

    from apps.accounts.sessions import issue_session, resolve_session
    from apps.governance.audit import append_event

    with transaction.atomic():
        issue_session(s.request, s.user, "normal", future, append_event)
    actor = resolve_session(s.request, future)
    assert preview(actor, future).verified_roles == ("coach",)


def test_preview_cosmetic_fields_and_private_media_allowlist():
    s = owner()
    save(
        s,
        "identity",
        {
            "display_name": "نام",
            "identity_name": "Private Identity",
            "roles": ["coach"],
        },
    )
    save(
        s,
        "description",
        {"biography": "شرح", "specialties": ["قدرت"], "experience_years": 2},
    )
    dto = preview(s.actor)
    assert dto.display_name == "نام" and dto.biography == "شرح"
    assert dto.specialties == ("قدرت",) and dto.media == ()


@pytest.mark.parametrize("purpose", ["avatar", "cover", "logo"])
def test_preview_references_only_current_private_sanitized_media(purpose):
    from .test_credential_revisions import ready

    s = owner()
    asset = ready(s, purpose)
    save(s, "branding", {purpose: asset.id})
    dto = preview(s.actor)
    derivative = asset.derivatives.get(purpose="owner_preview")
    assert len(dto.media) == 1
    media = dto.media[0]
    assert media.asset_uuid == asset.id and media.derivative_uuid == derivative.id
    assert media.purpose == purpose and media.content_type == "image/png"
    assert set(asdict(media)) == {
        "asset_uuid",
        "derivative_uuid",
        "purpose",
        "content_type",
    }
    assert asset.source_key not in str(asdict(dto)) and derivative.key not in str(
        asdict(dto)
    )
    asset.state = "revoked"
    asset.revoked_at = timezone.now()
    asset.save(update_fields=["state", "revoked_at"])
    assert preview(s.actor).media == ()


def test_domain_preview_and_selector_are_the_same_private_contract():
    assert importlib.util.find_spec("apps.professionals.preview"), (
        "Missing preview boundary"
    )
    domain = importlib.import_module("apps.professionals.preview")
    s = owner()
    assert domain.owner_preview(s.actor, s.at) == preview(s.actor, s.at)


def test_preview_has_no_guessed_profile_argument():
    s = owner()
    from apps.professionals import selectors

    assert callable(getattr(selectors, "owner_preview", None))
    with pytest.raises(TypeError):
        selectors.owner_preview(s.actor, s.at, profile_uuid=uuid4())
