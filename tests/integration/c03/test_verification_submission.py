from uuid import uuid4

import pytest
from django.db import DatabaseError, transaction
from django.utils import timezone

from apps.professionals.contracts import ProfileConflict
from apps.professionals.models import (
    Verification,
    VerificationEvidence,
    VerificationTarget,
)

from .test_professional_setup import save
from .verification_helpers import command, prepared, submitted

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_submit_freezes_relational_identity_and_each_role_snapshot():
    s = submitted()
    assert s.case.state == "submitted"
    targets = list(VerificationTarget.objects.filter(verification_id=s.case.id))
    assert {t.target for t in targets} == {"identity", "coach", "nutritionist"}
    assert (
        VerificationEvidence.objects.filter(target__verification_id=s.case.id).count()
        == 3
    )
    for target in targets:
        assert target.state == "submitted" and len(target.target_snapshot_hash) == 64
        with pytest.raises(DatabaseError), transaction.atomic():
            VerificationTarget.objects.filter(pk=target.id).update(
                target_snapshot_hash="f" * 64
            )
        with pytest.raises(DatabaseError), transaction.atomic():
            VerificationEvidence.objects.filter(target=target).update(
                category="qualification" if target.target == "identity" else "identity"
            )
    assert not any(
        asset.classification != "private_source" for asset, _ in s.assets.values()
    )


def test_inflight_requested_role_or_evidence_edit_is_stale():
    s = submitted()
    old = VerificationTarget.objects.get(
        verification_id=s.case.id, target="nutritionist"
    )
    digest = old.target_snapshot_hash
    save(s, "identity", {"roles": ["coach"]})
    old.refresh_from_db()
    assert old.state == "stale" and old.target_snapshot_hash == digest
    assert (
        VerificationTarget.objects.get(verification_id=s.case.id, target="coach").state
        == "submitted"
    )


def test_unrelated_role_edit_preserves_pending_target():
    s = submitted(("identity", "coach"))
    save(s, "identity", {"roles": ["coach"]})
    assert set(
        VerificationTarget.objects.filter(verification_id=s.case.id).values_list(
            "state", flat=True
        )
    ) == {"submitted"}


def test_duplicate_submission_and_new_resubmission_bundle():
    s = prepared()
    op, version = uuid4(), s.case.version
    first = command(
        "submit_verification", s.actor, s.case.id, version, op, timezone.now()
    )
    again = command(
        "submit_verification", s.actor, s.case.id, version, op, timezone.now()
    )
    assert first == again
    with pytest.raises(ProfileConflict):
        command(
            "prepare_verification",
            s.actor,
            ("identity", "coach"),
            s.profile.version,
            uuid4(),
            timezone.now(),
        )
    for t in VerificationTarget.objects.filter(verification_id=first.id).order_by("id"):
        row = Verification.objects.get(pk=first.id)
        command(
            "withdraw_verification_target",
            s.actor,
            first.id,
            t.id,
            row.version,
            uuid4(),
            timezone.now(),
        )
    row.refresh_from_db()
    assert Verification.objects.get(pk=first.id).state == "withdrawn"
    next_case = command(
        "prepare_verification",
        s.actor,
        ("identity", "coach"),
        s.profile.version,
        uuid4(),
        timezone.now(),
    )
    assert next_case.id != first.id and next_case.sequence == 2


@pytest.mark.parametrize("fault", ["expired", "withdrawn", "revoked", "unready"])
def test_submission_denies_current_invalid_evidence(fault):
    s = prepared()
    asset, dto = s.assets["coach"]
    from apps.professionals.models import Credential

    if fault == "expired":
        # Source metadata is immutable; expire by evaluating after its date.
        at = timezone.now().replace(year=2031)
    else:
        at = timezone.now()
        if fault == "withdrawn":
            Credential.objects.filter(pk=dto.id).update(withdrawn_at=at)
        else:
            asset.state = "revoked" if fault == "revoked" else "quarantined"
            asset.save(update_fields=["state"])
    with pytest.raises((ValueError, LookupError, PermissionError)):
        command("submit_verification", s.actor, s.case.id, s.case.version, uuid4(), at)
    assert Verification.objects.get(pk=s.case.id).state == "draft"
