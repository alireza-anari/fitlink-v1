from datetime import date, timedelta
from uuid import uuid4

import pytest
from django.db import DatabaseError, transaction
from django.utils import timezone

from apps.assets.models import Asset, AssetDerivative, AssetProcessingAttempt
from apps.professionals import contracts
from apps.professionals.models import (
    Credential,
    CredentialRevision,
    Verification,
    VerificationDecision,
    VerificationEvidence,
    VerificationTarget,
)

from .test_professional_setup import owner, save

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def command(name, *args):
    from config.use_cases import professional_profile as api

    assert hasattr(api, name), f"Private credential command absent: {name}"
    return getattr(api, name)(*args)


def payload(**changes):
    assert hasattr(contracts, "CredentialInput"), "Credential input absent"
    return contracts.CredentialInput(
        {
            "category": "identity",
            "role": None,
            "type_code": "synthetic",
            "title": "گواهی",
            "issuer": "Fixture",
            "issued_on": date(2020, 1, 1),
            "expires_on": date(2030, 1, 1),
            **changes,
        }
    )


def ready(s, category="identity", subject=None):
    at = timezone.now()
    asset = Asset.objects.create(
        owner=s.user,
        subject_kind="professional_credential" if subject else "professional_profile",
        subject_uuid=subject or s.profile.id,
        purpose="identity_evidence"
        if category == "identity"
        else "credential_evidence",
        state="ready",
        source_key=f"source/{uuid4()}",
        declared_size=100,
        declared_type="image/png",
        actual_size=100,
        detected_type="image/png",
        sha256="a" * 64,
        accepted_at=at,
        finalized_at=at,
        upload_expires_at=at + timedelta(hours=1),
    )
    AssetProcessingAttempt.objects.create(
        asset=asset,
        processing_version=1,
        state="ready",
        algorithm_version="jpeg-png-pixels-v1",
        owner_auth_version=s.user.auth_version,
        asset_version=asset.version,
        authority_hash="b" * 64,
        scanner_engine="ClamAV 1.5.4",
        scanner_signature="28000",
    )
    AssetDerivative.objects.create(
        asset=asset,
        processing_version=1,
        purpose="evidence_preview",
        key=f"derivative/{uuid4()}",
        sha256="b" * 64,
        width=64,
        height=48,
        mime_type="image/png",
        state="ready",
    )
    return asset


def create(s, **values):
    s.profile.refresh_from_db()
    return command(
        "create_credential",
        s.actor,
        payload(**values),
        s.profile.version,
        uuid4(),
        timezone.now(),
    )


def revise(s, dto, **values):
    return command(
        "revise_credential",
        s.actor,
        dto.id,
        payload(**values),
        dto.version,
        uuid4(),
        timezone.now(),
    )


def targets(s, approved=False):
    case = Verification.objects.create(profile=s.profile, sequence=1)
    result = {}
    for kind in ("identity", "coach", "nutritionist"):
        role = s.profile.roles.filter(role=kind).first()
        target = VerificationTarget.objects.create(
            verification=case,
            target=kind,
            role=role,
            bound_evidence_revision=role.evidence_revision
            if role
            else s.profile.identity_evidence_revision,
            bound_decision_version=role.decision_version
            if role
            else s.profile.identity_decision_version,
            bound_declaration_version=role.declaration_version if role else None,
            target_snapshot_hash="c" * 64,
            identity_name=s.profile.identity_name if role is None else "",
        )
        if approved:
            VerificationDecision.objects.create(
                target=target,
                profile=s.profile,
                target_kind=kind,
                actor=s.user,
                decision="approve",
                reason_code="credentials_approved",
                target_snapshot_hash=target.target_snapshot_hash,
                bound_evidence_revision=target.bound_evidence_revision,
                decision_sequence=1,
                decided_at=timezone.now(),
            )
        target.state = "approved" if approved else "submitted"
        target.save()
        result[kind] = target
    case.state = "decided" if approved else "submitted"
    case.submitted_at = timezone.now()
    case.snapshot_hash = "d" * 64
    case.decided_at = timezone.now() if approved else None
    case.save()
    return result


@pytest.mark.parametrize("kind", ["identity", "coach", "nutritionist"])
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("type_code", "other"),
        ("issuer", "دیگر"),
        ("title", "جدید"),
        ("issued_on", date(2021, 1, 1)),
        ("expires_on", date(2031, 1, 1)),
        ("source_asset", None),
    ],
)
def test_each_bound_field_increments_only_target_evidence_revision(kind, field, value):
    s = owner()
    save(s, "identity", {"identity_name": "علی", "roles": ["coach", "nutritionist"]})
    role = None if kind == "identity" else kind
    category = "identity" if role is None else "qualification"
    asset = ready(s, category)
    dto = create(s, category=category, role=role, source_asset=asset.id)
    prior = counters(s)
    if field == "source_asset":
        value = ready(s, category).id
    revise(
        s,
        dto,
        category=category,
        role=role,
        source_asset=asset.id,
        **({field: value} if field != "source_asset" else {}),
    ) if field != "source_asset" else revise(
        s, dto, category=category, role=role, source_asset=value
    )
    current = counters(s)
    for target in current:
        assert current[target] == prior[target] + (target == kind)
    assert CredentialRevision.objects.filter(credential_id=dto.id).count() == 2


def counters(s):
    s.profile.refresh_from_db()
    return {
        "identity": s.profile.identity_evidence_revision,
        **dict(s.profile.roles.values_list("role", "evidence_revision")),
    }


@pytest.mark.parametrize(
    "state", ["quarantined", "processing", "rejected", "revoked", "pending_upload"]
)
def test_foreign_or_unready_asset_cannot_attach(state):
    s = owner()
    asset = ready(s)
    asset.state = state
    asset.revoked_at = timezone.now() if state == "revoked" else None
    asset.save()
    with pytest.raises(contracts.ProfileNotFound):
        create(s, source_asset=asset.id)
    other = owner("+989123456781")
    foreign = ready(other)
    with pytest.raises(contracts.ProfileNotFound):
        create(s, source_asset=foreign.id)
    assert not Credential.objects.filter(profile=s.profile).exists()


def test_ready_flag_without_task5_processing_denied():
    s = owner()
    asset = ready(s)
    asset.processing_attempts.all().delete()
    with pytest.raises(contracts.ProfileNotFound):
        create(s, source_asset=asset.id)


def test_metadata_draft_upload_anchor_and_immutable_revision():
    s = owner()
    dto = create(s)
    assert dto.current_revision_id is None
    asset = ready(s, subject=dto.id)
    dto = revise(s, dto, source_asset=asset.id)
    old = CredentialRevision.objects.get(pk=dto.current_revision_id)
    result = revise(s, dto, title="جدید", source_asset=asset.id)
    assert result.current_revision_id != old.id
    old.refresh_from_db()
    assert old.title == "گواهی"
    for mutation in (
        lambda: CredentialRevision.objects.filter(pk=old.id).update(title="bad"),
        lambda: CredentialRevision.objects.filter(pk=old.id).delete(),
    ):
        with pytest.raises(DatabaseError), transaction.atomic():
            mutation()


def test_submitted_source_immutable():
    s = owner()
    save(s, "identity", {"identity_name": "علی", "roles": ["coach", "nutritionist"]})
    dto = create(s, source_asset=ready(s).id)
    case = Verification.objects.create(profile=s.profile, sequence=1)
    target = VerificationTarget.objects.create(
        verification=case,
        target="identity",
        target_snapshot_hash="c" * 64,
        identity_name="علی",
        bound_evidence_revision=s.profile.identity_evidence_revision,
    )
    link = VerificationEvidence.objects.create(
        target=target,
        credential_revision_id=dto.current_revision_id,
        category="identity",
    )
    target.state = "submitted"
    target.save()
    case.state, case.submitted_at, case.snapshot_hash = (
        "submitted",
        timezone.now(),
        "d" * 64,
    )
    case.save()
    revise(s, dto, source_asset=ready(s).id)
    link.refresh_from_db()
    target.refresh_from_db()
    assert link.credential_revision_id == dto.current_revision_id
    assert target.state == "stale"
    assert target.target_snapshot_hash == "c" * 64
    assert target.bound_evidence_revision != counters(s)["identity"]


def test_requested_role_edit_stales_only_matching_pending_target():
    s = owner()
    save(s, "identity", {"identity_name": "علی", "roles": ["coach", "nutritionist"]})
    pending = targets(s)
    dto = create(
        s,
        category="qualification",
        role="coach",
        source_asset=ready(s, "qualification").id,
    )
    for kind, target in pending.items():
        target.refresh_from_db()
        assert target.state == ("stale" if kind == "coach" else "submitted")
    command(
        "withdraw_credential", s.actor, dto.id, dto.version, uuid4(), timezone.now()
    )
    assert counters(s)["coach"] == 3
    assert pending["coach"].history.count() == 1


@pytest.mark.parametrize("roles", [["coach"], ["coach", "nutritionist"]])
def test_add_deactivate_role_preserves_other_approval(roles):
    s = owner()
    save(s, "identity", {"identity_name": "علی", "roles": ["coach", "nutritionist"]})
    approved = targets(s, approved=True)
    before = list(VerificationDecision.objects.values())
    binding = counters(s)
    save(s, "identity", {"roles": ["coach"]})
    save(s, "identity", {"roles": roles})
    assert counters(s) == binding
    assert list(VerificationDecision.objects.values()) == before
    for target in approved.values():
        target.refresh_from_db()
        assert target.state == "approved"


def test_credential_receipt_version_and_reclassification_denied():
    s = owner()
    asset = ready(s)
    operation = uuid4()
    dto = command(
        "create_credential",
        s.actor,
        payload(source_asset=asset.id),
        1,
        operation,
        timezone.now(),
    )
    replay = command(
        "create_credential",
        s.actor,
        payload(source_asset=asset.id),
        1,
        operation,
        timezone.now(),
    )
    assert replay == dto
    with pytest.raises(contracts.ProfileConflict):
        command(
            "create_credential",
            s.actor,
            payload(title="different", source_asset=asset.id),
            1,
            operation,
            timezone.now(),
        )
    with pytest.raises(ValueError):
        revise(s, dto, category="qualification", role="coach", source_asset=asset.id)
    newer = revise(s, dto, title="جدید", source_asset=asset.id)
    with pytest.raises(contracts.ProfileConflict):
        revise(s, dto, source_asset=asset.id)
    assert newer.version == dto.version + 1
