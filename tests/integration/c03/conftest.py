"""Synthetic metadata only; no source bytes or operational authority."""

from datetime import timedelta
from types import SimpleNamespace

import pytest
from django.apps import apps
from django.utils import timezone


def require_model(name, label="professionals"):
    installed = {m.__name__: m for m in apps.get_models() if m._meta.app_label == label}
    assert name in installed, f"C03 schema missing: {label}.{name}"
    return installed[name]


@pytest.fixture
def schema_factory():
    def build():
        Profile = require_model("ProfessionalProfile")
        User = apps.get_model("accounts", "User")
        at = timezone.now()
        owner = User.objects.create_user("+989123456780")
        staff = User.objects.create_user("+989123456781")
        other = User.objects.create_user("+989123456782")
        profile = Profile.objects.create(user=owner, identity_name="Synthetic")
        foreign = Profile.objects.create(user=other)
        Role = require_model("ProfessionalRole")
        coach = Role.objects.create(profile=profile, role="coach")
        nutritionist = Role.objects.create(profile=profile, role="nutritionist")
        case = require_model("Verification").objects.create(profile=profile, sequence=1)
        targets, revisions = {}, {}
        for kind, role in (
            ("identity", None),
            ("coach", coach),
            ("nutritionist", nutritionist),
        ):
            purpose = "identity_evidence" if role is None else "credential_evidence"
            asset = require_model("Asset", "assets").objects.create(
                owner=owner,
                subject_kind="professional_profile",
                subject_uuid=profile.pk,
                purpose=purpose,
                state="ready",
                declared_size=100,
                declared_type="image/png",
                actual_size=100,
                detected_type="image/png",
                sha256="a" * 64,
                accepted_at=at,
                finalized_at=at,
                upload_expires_at=at + timedelta(hours=1),
            )
            category = "identity" if role is None else "qualification"
            credential = require_model("Credential").objects.create(
                profile=profile,
                role=role,
                category=category,
                type_code="synthetic",
                title="Synthetic",
                issuer="Fixture",
            )
            revision = require_model("CredentialRevision").objects.create(
                credential=credential,
                sequence=1,
                category=category,
                type_code="synthetic",
                title="Synthetic",
                issuer="Fixture",
                source_asset=asset,
                source_sha256="a" * 64,
                revision_hash="b" * 64,
            )
            credential.current_revision = revision
            credential.save(update_fields=["current_revision"])
            target = require_model("VerificationTarget").objects.create(
                verification=case,
                target=kind,
                role=role,
                bound_evidence_revision=1,
                bound_decision_version=1,
                bound_declaration_version=1 if role else None,
                target_snapshot_hash="c" * 64,
                identity_name="Synthetic" if role is None else "",
            )
            require_model("VerificationEvidence").objects.create(
                target=target,
                credential_revision=revision,
                category=category,
            )
            targets[kind], revisions[kind] = target, revision
        return SimpleNamespace(**locals())

    return build
