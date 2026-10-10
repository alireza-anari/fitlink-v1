"""Real current privacy capability/case authority, never a blanket owner hold."""

import os
from dataclasses import replace
from datetime import timedelta
from io import BytesIO
from uuid import uuid4

import pytest
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

from apps.assets.models import Asset, AssetDerivative
from apps.assets.storage import FakePrivateStore, S3PrivateStore
from apps.governance import retention
from apps.governance.privacy_models import PrivacyRequest, RecordHold, RetentionPolicy
from apps.governance.staff import MockStepUpProvider, issue_mock_step_up
from apps.governance.staff_models import StaffCapabilityGrant
from config.use_cases import c03_privacy as commands
from config.use_cases.privacy import request_privacy

from .profile_helpers import make_actor
from .test_credential_revisions import ready
from .test_professional_setup import owner

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def api(name, *args, **kwargs):
    assert callable(getattr(commands, name, None)), f"Task 9 command absent: {name}"
    return getattr(commands, name)(*args, **kwargs)


def private_store():
    # The complete hosted Foundation runs these same cases on real private MinIO.
    # The PostgreSQL-only job exercises metadata/races with a deterministic store.
    return (
        S3PrivateStore()
        if os.environ.get("STORAGE_BACKEND") == "s3"
        else FakePrivateStore()
    )


def media(s, purpose="avatar", store=None):
    store = store or private_store()
    asset = ready(s, purpose)
    derivative = asset.derivatives.get()
    for key in (asset.source_key, derivative.key):
        store.put_stream(key, BytesIO(b"synthetic retention bytes"), "image/png", 100)
    return asset, store


def revoke(asset, at=None):
    asset.state = "revoked"
    asset.revoked_at = at or timezone.now() - timedelta(minutes=5)
    asset.version += 1
    asset.save()
    return asset


def subject(asset):
    asset.refresh_from_db()
    return retention.ValidatedRecordSubject(
        "profile_asset", asset.id, asset.owner.public_id, asset.version
    )


def privacy_case(s):
    return request_privacy(s.actor, "export", uuid4(), timezone.now(), confirmed=True)


def authority(settings, case, staff=None):
    settings.ACCOUNT_SECURITY = replace(
        settings.ACCOUNT_SECURITY, step_up_provider="mock"
    )
    staff = staff or make_actor("+989123456786")
    from apps.accounts.models import User

    issuer = User.objects.filter(phone="+989123456787").first()
    if issuer is None:
        issuer = make_actor("+989123456787").user
    at = timezone.now()
    StaffCapabilityGrant.objects.get_or_create(
        user=staff.user,
        capability="privacy_operations",
        defaults=dict(
            granted_by=issuer,
            reason_code="policy_approved",
            valid_from=at - timedelta(seconds=1),
            valid_until=at + timedelta(hours=2),
        ),
    )
    provider = MockStepUpProvider()
    proof = provider.prepare(staff.user.public_id, "privacy_operations", case, at)
    with transaction.atomic():
        step = issue_mock_step_up(
            staff.user,
            "privacy_operations",
            case,
            proof.raw_assertion,
            issuer,
            at,
            provider,
        )
    return staff, step


def hold(settings, s, record, case=None, staff=None, seconds=120):
    case = case or privacy_case(s)
    staff, step = authority(settings, case, staff)
    at = timezone.now()
    result = api(
        "apply_c03_hold",
        staff.actor,
        record,
        case,
        "security",
        "hold_applied",
        at + timedelta(seconds=10),
        at + timedelta(seconds=seconds),
        step,
        at,
    )
    return result, staff, step, at


def policy(s, asset, duration=1):
    at = timezone.now() - timedelta(hours=1)
    return RetentionPolicy.objects.create(
        data_class="credential_source"
        if asset.purpose.endswith("evidence")
        else "profile_media",
        purpose=asset.purpose,
        status="effective",
        version=3,
        duration_seconds=duration,
        backup_reference="synthetic-backup-v1",
        approved_by=s.user,
        created_at=at,
        updated_at=at,
        approved_at=at,
        effective_at=at,
    )


def cleanup(asset, rule, store, at=None):
    asset.refresh_from_db()
    return api(
        "cleanup_asset",
        asset.id,
        asset.version,
        rule.id if rule else uuid4(),
        at or timezone.now(),
        store=store,
    )


def absent(store, key):
    with pytest.raises(FileNotFoundError):
        store.head(key)


def test_hold_specific_source_derivatives_not_other_media(settings):
    s = owner()
    held, store = media(s)
    other, _ = media(s, "cover", store)
    revoke(held)
    revoke(other)
    hold(settings, s, subject(held))
    assert cleanup(held, policy(s, held), store) == "held"
    assert cleanup(other, policy(s, other), store) == "deleted"
    assert store.head(held.source_key).size > 0
    assert store.head(held.derivatives.get().key).size > 0
    absent(store, other.source_key)
    absent(store, other.derivatives.get().key)


@pytest.mark.parametrize(
    "defect",
    [
        "owner",
        "version",
        "kind",
        "reference",
        "case",
        "self",
        "capability",
        "step",
        "future",
    ],
)
def test_forged_subject_or_case_or_version_denied(settings, defect):
    s = owner()
    asset, store = media(s)
    case = privacy_case(s)
    staff, step = authority(settings, case)
    record = subject(asset)
    if defect == "owner":
        record = replace(record, owner_uuid=uuid4())
    if defect == "version":
        record = replace(record, version=record.version + 1)
    if defect == "kind":
        record = replace(record, kind="health")
    if defect == "reference":
        record = replace(record, record_uuid=uuid4())
    if defect == "case":
        case = uuid4()
    if defect == "self":
        staff.actor = s.actor
    if defect == "step":
        step = uuid4()
    if defect == "capability":
        StaffCapabilityGrant.objects.filter(user=staff.user).update(
            revoked_at=timezone.now()
        )
    at = timezone.now() - timedelta(days=1) if defect == "future" else timezone.now()
    with pytest.raises((PermissionError, PermissionDenied, ValueError)):
        api(
            "apply_c03_hold",
            staff.actor,
            record,
            case,
            "security",
            "hold_applied",
            at + timedelta(seconds=10),
            at + timedelta(minutes=2),
            step,
            at,
        )
    assert not RecordHold.objects.exists()
    assert store.head(asset.source_key).size > 0


def test_overdue_review_not_silent_release(settings):
    s = owner()
    asset, store = media(s)
    revoke(asset)
    _, _, _, at = hold(settings, s, subject(asset))
    assert cleanup(asset, policy(s, asset), store, at + timedelta(seconds=11)) == "held"
    assert api("is_c03_record_held", subject(asset), at + timedelta(seconds=11))


@pytest.mark.parametrize("release", [True, False])
def test_released_expired_hold_allows_eligible_retry(settings, release):
    s = owner()
    asset, store = media(s)
    revoke(asset)
    ident, staff, step, at = hold(settings, s, subject(asset))
    rule = policy(s, asset)
    assert cleanup(asset, rule, store, at) == "held"
    if release:
        api(
            "release_c03_hold",
            staff.actor,
            ident,
            1,
            "hold_released",
            step,
            at + timedelta(seconds=1),
        )
    assert (
        cleanup(asset, rule, store, at + timedelta(seconds=1 if release else 121))
        == "deleted"
    )
    absent(store, asset.source_key)


def test_c02_default_validation_still_denies_c03_subject(settings):
    s = owner()
    asset, _ = media(s)
    with pytest.raises(PermissionError):
        retention.is_record_held(subject(asset), timezone.now())


def test_credential_hold_pins_case_sources_not_future_or_other_media(settings):
    from .verification_helpers import assign, reviewer, submitted

    s = submitted()
    staff = reviewer(settings, s.case.id)
    s.case = assign(s, staff)
    asset, credential = s.assets["coach"]
    row = s.profile.credentials.get(pk=credential.id)
    record = retention.ValidatedRecordSubject(
        "professional_credential", row.id, s.user.public_id, row.version
    )
    hold(settings, s, record, s.case.id, staff)
    store = private_store()
    for key in (asset.source_key, asset.derivatives.get().key):
        store.put_stream(key, BytesIO(b"evidence"), "image/png", 100)
    unrelated, _ = media(s, "logo", store)
    revoke(asset)
    revoke(unrelated)
    assert cleanup(asset, policy(s, asset), store) == "held"
    assert cleanup(unrelated, policy(s, unrelated), store) == "deleted"


def test_hold_audit_failure_rolls_back_without_private_access(settings, monkeypatch):
    s = owner()
    asset, _ = media(s)
    case = privacy_case(s)
    staff, step = authority(settings, case)

    def fail(*args, **kwargs):
        raise RuntimeError("audit unavailable")

    monkeypatch.setattr(retention, "append_event", fail)
    at = timezone.now()
    with pytest.raises(RuntimeError):
        api(
            "apply_c03_hold",
            staff.actor,
            subject(asset),
            case,
            "security",
            "hold_applied",
            at + timedelta(seconds=10),
            at + timedelta(minutes=2),
            step,
            at,
        )
    assert not RecordHold.objects.exists()


def test_inventory_exact_owner_typed_no_storage_urls_or_bytes():
    s, other = owner(), owner("+989123456789")
    asset, _ = media(s)
    foreign, _ = media(other)
    result = api("inventory_c03_owner", s.user.public_id, timezone.now())
    assert result.owner_uuid == s.user.public_id
    assert all(row.owner_uuid == s.user.public_id for row in result.records)
    assert asset.id in {row.record_uuid for row in result.records}
    assert foreign.id not in {row.record_uuid for row in result.records}
    assert {row.kind for row in result.records} >= {
        "professional_profile",
        "profile_asset",
        "asset_derivative",
    }
    assert asset.source_key not in repr(result)
    assert "http" not in repr(result) and "synthetic retention bytes" not in repr(
        result
    )
    with pytest.raises(PermissionError):
        api("inventory_c03_owner", uuid4(), timezone.now())


def test_inventory_includes_baseline_history_and_installed_verification():
    from apps.athletes.baseline_models import BaselineAssessment
    from apps.athletes.models import AthleteProfile

    from .verification_helpers import submitted

    s = submitted()
    athlete = AthleteProfile.objects.create(user=s.user)
    baseline = BaselineAssessment.objects.create(
        athlete=athlete, sequence=1, observed_at=timezone.now()
    )
    inventory = api("inventory_c03_owner", s.user.public_id, timezone.now())
    refs = {(r.kind, r.record_uuid) for r in inventory.records}
    assert ("athlete_profile", athlete.id) in refs and (
        "athlete_baseline",
        baseline.id,
    ) in refs
    assert ("professional_verification", s.case.id) in refs
    for asset, credential in s.assets.values():
        assert ("professional_credential", credential.id) in refs
        assert ("profile_asset", asset.id) in refs
        assert ("credential_revision", credential.current_revision_id) in refs
    assert len(inventory.records) <= 1000


def test_inventory_forged_asset_binding_fails_closed():
    s, other = owner(), owner("+989123456789")
    asset, _ = media(s)
    # Unaccepted rows can be malformed by direct SQL; inventory must validate them.
    Asset.objects.create(
        owner=s.user,
        subject_kind="professional_profile",
        subject_uuid=other.profile.id,
        purpose="avatar",
        source_key="quarantine/" + uuid4().hex,
        upload_expires_at=timezone.now() + timedelta(hours=1),
    )
    with pytest.raises(PermissionError):
        api("inventory_c03_owner", s.user.public_id, timezone.now())
    assert AssetDerivative.objects.filter(asset=asset).count() == 1
    assert PrivacyRequest.objects.count() == 0


def test_verification_hold_pins_all_case_sources_not_owner_branding(settings):
    from .verification_helpers import assign, reviewer, submitted

    s = submitted()
    staff = reviewer(settings, s.case.id)
    s.case = assign(s, staff)
    case = s.profile.verifications.get(pk=s.case.id)
    record = retention.ValidatedRecordSubject(
        "professional_verification", case.id, s.user.public_id, case.version
    )
    hold(settings, s, record, case.id, staff)
    store = private_store()
    for asset, _ in s.assets.values():
        for key in (asset.source_key, asset.derivatives.get().key):
            store.put_stream(key, BytesIO(b"case evidence"), "image/png", 100)
        revoke(asset)
        assert cleanup(asset, policy(s, asset), store) == "held"
    branding, _ = media(s, "cover", store)
    revoke(branding)
    assert cleanup(branding, policy(s, branding), store) == "deleted"


def test_baseline_hold_is_one_record_and_not_owner_assets(settings):
    from apps.athletes.baseline_models import BaselineAssessment
    from apps.athletes.models import AthleteProfile

    s = owner()
    athlete = AthleteProfile.objects.create(user=s.user)
    row = BaselineAssessment.objects.create(
        athlete=athlete, sequence=1, observed_at=timezone.now()
    )
    record = retention.ValidatedRecordSubject(
        "athlete_baseline", row.id, s.user.public_id, row.version
    )
    hold(settings, s, record)
    assert retention.is_record_held(
        record, timezone.now(), subject_validator=commands.validate_c03_hold_subject
    )
    asset, store = media(s)
    revoke(asset)
    assert cleanup(asset, policy(s, asset), store) == "deleted"


def test_inventory_overflow_fails_closed_without_partial_owner_result():
    s = owner()
    Asset.objects.bulk_create(
        [
            Asset(
                owner=s.user,
                subject_kind="professional_profile",
                subject_uuid=s.profile.id,
                purpose="avatar",
                upload_expires_at=timezone.now() + timedelta(hours=1),
            )
            for _ in range(1001)
        ]
    )
    with pytest.raises(PermissionError):
        api("inventory_c03_owner", s.user.public_id, timezone.now())


def test_record_specific_holds_and_release_survive_large_owner_history(settings):
    s = owner()
    asset, _ = media(s)
    Asset.objects.bulk_create(
        [
            Asset(
                owner=s.user,
                subject_kind="professional_profile",
                subject_uuid=s.profile.id,
                purpose="avatar",
                state="deleted",
                revoked_at=timezone.now(),
                upload_expires_at=timezone.now(),
            )
            for _ in range(1001)
        ]
    )
    identifier, staff, step, _ = hold(settings, s, subject(asset))
    api(
        "release_c03_hold",
        staff.actor,
        identifier,
        1,
        "hold_released",
        step,
        timezone.now(),
    )
    assert RecordHold.objects.get(pk=identifier).released_at is not None


def test_inventory_exact_retained_classes_and_asset_policy_reference():
    from .verification_helpers import submitted

    s = submitted()
    asset, _ = s.assets["coach"]
    rule = policy(s, asset)
    inventory = api("inventory_c03_owner", s.user.public_id, timezone.now())
    records = {r.kind: r for r in inventory.records}
    assert records["credential_revision"].data_class == "credential_revision"
    assert records["verification_evidence"].data_class == "verification_evidence"
    assert records["verification_history"].data_class == "verification_history"
    assert records["professional_profile"].data_class == "professional_profile"
    source = next(r for r in inventory.records if r.record_uuid == asset.id)
    assert source.policy_uuid == rule.id and source.classification == "private_source"
    assert source.deletion_behavior == "policy_cleanup"
    assert records["verification_evidence"].deletion_behavior == "retain_only"


def test_assigned_case_hold_requires_current_verifier_capability(settings):
    from .verification_helpers import assign, reviewer, submitted

    s = submitted()
    staff = reviewer(settings, s.case.id)
    s.case = assign(s, staff)
    case = s.profile.verifications.get(pk=s.case.id)
    staff.grant.revoked_at = timezone.now()
    staff.grant.save()
    record = retention.ValidatedRecordSubject(
        "professional_verification", case.id, s.user.public_id, case.version
    )
    with pytest.raises((PermissionError, PermissionDenied)):
        hold(settings, s, record, case.id, staff)
    assert not RecordHold.objects.exists()


def test_c03_callbacks_cannot_bypass_composition_lock_reservation(settings):
    s = owner()
    asset, _ = media(s)
    case = privacy_case(s)
    staff, step = authority(settings, case)
    at = timezone.now()
    with pytest.raises((PermissionError, PermissionDenied)):
        retention.apply_hold(
            staff.actor,
            subject(asset),
            case,
            "security",
            "hold_applied",
            at + timedelta(seconds=10),
            at + timedelta(minutes=2),
            step,
            at,
            subject_validator=commands.validate_c03_hold_subject,
            case_validator=commands.validate_c03_hold_case,
        )
    assert not RecordHold.objects.exists()


def test_c02_intake_hold_does_not_become_blanket_c03_owner_hold(settings):
    s = owner()
    asset, store = media(s)
    revoke(asset)
    case = privacy_case(s)
    staff, step = authority(settings, case)
    row = PrivacyRequest.objects.get(pk=case)
    record = retention.ValidatedRecordSubject(
        "privacy_request", row.id, s.user.public_id, row.version
    )
    at = timezone.now()
    retention.apply_hold(
        staff.actor,
        record,
        case,
        "security",
        "hold_applied",
        at + timedelta(seconds=10),
        at + timedelta(minutes=2),
        step,
        at,
    )
    assert retention.is_record_held(record, at)
    assert cleanup(asset, policy(s, asset), store) == "deleted"
