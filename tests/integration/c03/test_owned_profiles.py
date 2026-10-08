"""Optional owner profiles must survive retries without gaining wider authority."""

from dataclasses import asdict, replace
from datetime import date, timedelta
from uuid import uuid4

import pytest
from django.db import DatabaseError, transaction

from apps.accounts.contracts import SessionScope
from apps.accounts.security_models import AccountSessionControl
from apps.governance.audit_models import AuditEvent
from apps.governance.outbox_models import OutboxEvent

from .profile_helpers import create, make_actor, module, profile_model, read

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]
LABELS = ("athletes", "professionals")


def test_dual_profiles_one_user():
    s = make_actor()
    athlete = create("athletes", s.actor, uuid4(), s.at)
    professional = create("professionals", s.actor, uuid4(), s.at)
    assert athlete.id != professional.id
    assert athlete.state == "onboarding" and professional.state == "setup"
    assert athlete.version == professional.version == 1
    assert athlete.timezone == "Europe/London"
    assert profile_model("athletes").objects.get().user_id == s.user.pk
    assert profile_model("professionals").objects.get().user_id == s.user.pk
    assert read("athletes", s.actor, s.at).id == athlete.id
    assert read("professionals", s.actor, s.at).id == professional.id
    from apps.professionals.models import ProfessionalRole, VerificationDecision

    assert ProfessionalRole.objects.count() == VerificationDecision.objects.count() == 0


@pytest.mark.parametrize("label", LABELS)
def test_create_and_receipt_replay_have_one_audited_effect(label):
    s = make_actor()
    operation = uuid4()
    first = create(label, s.actor, operation, s.at)
    assert create(label, s.actor, operation, s.at) == first
    assert create(label, s.actor, uuid4(), s.at) == first
    assert profile_model(label).objects.count() == 1
    Receipt = module(f"apps.{label}.receipt_models").ProfileCommandReceipt
    assert Receipt.objects.filter(owner=s.user).count() == 2
    assert (
        AuditEvent.objects.filter(action=f"{label[:-1]}.profile_created").count() == 1
    )
    if label == "professionals":
        event = OutboxEvent.objects.get(event_type="professional.profile_changed")
        assert event.aggregate_uuid == first.id and event.aggregate_version == 1
        assert event.payload == {
            "profile_uuid": str(first.id),
            "user_uuid": str(s.user.public_id),
        }


@pytest.mark.parametrize("label", LABELS)
def test_receipt_reconstructs_current_owned_dto_and_hides_private_fields(label):
    s = make_actor()
    operation = uuid4()
    first = create(label, s.actor, operation, s.at)
    profile_model(label).objects.filter(pk=first.id).update(version=2)
    current = create(label, s.actor, operation, s.at)
    assert current.version == 2
    assert current == read(label, s.actor, s.at)
    assert not (
        set(asdict(current))
        & {
            "user",
            "user_id",
            "owner",
            "phone",
            "identity_name",
            "request_hash",
            "source_key",
            "approved_roles",
            "credentials",
            "signed_url",
        }
    )


@pytest.mark.parametrize("label", LABELS)
def test_cross_owner_profile_read_write_count_and_uuid(label):
    s = make_actor()
    other = make_actor("+989123456781")
    foreign = profile_model(label).objects.create(user=other.user)
    policies = module(f"apps.{label}.policies")
    missing = []
    for identifier in (foreign.pk, uuid4()):
        for lock in (False, True):
            with transaction.atomic(), pytest.raises(LookupError) as denied:
                policies.owned_profile(s.user, identifier, lock=lock)
            missing.append((type(denied.value), str(denied.value)))
    assert len(set(missing)) == 1
    with pytest.raises(LookupError):
        read(label, s.actor, s.at)
    own = create(label, s.actor, uuid4(), s.at)
    assert own.id != foreign.pk
    assert read(label, s.actor, s.at).id == own.id
    assert policies.owned_profile(s.user, own.id).user_id == s.user.pk


@pytest.mark.parametrize("label", LABELS)
def test_receipt_payload_conflict_returns_only_after_current_authorization(label):
    s = make_actor()
    operation = uuid4()
    create(label, s.actor, operation, s.at)
    Receipt = module(f"apps.{label}.receipt_models").ProfileCommandReceipt
    Receipt.objects.filter(owner=s.user, operation_id=operation).update(
        request_hash="f" * 64
    )
    with pytest.raises(module(f"apps.{label}.contracts").ProfileConflict):
        create(label, s.actor, operation, s.at)
    AccountSessionControl.objects.filter(pk=s.actor.control_id).update(revoked_at=s.at)
    with pytest.raises(PermissionError):
        create(label, s.actor, operation, s.at)


@pytest.mark.parametrize("label", LABELS)
@pytest.mark.parametrize(
    "defect",
    [
        "version",
        "revoked",
        "expired",
        "control",
        "legacy",
        "underage",
        "suspended",
        "restricted",
        "deleted",
        "pending_deletion",
    ],
)
def test_old_control_underage_or_ineligible_actor_has_no_profile_access(label, defect):
    s = make_actor()
    actor = s.actor
    if defect == "version":
        s.user.auth_version += 1
    elif defect in {"revoked", "expired"}:
        change = {"revoked_at": s.at} if defect == "revoked" else {"expires_at": s.at}
        AccountSessionControl.objects.filter(pk=actor.control_id).update(**change)
    elif defect == "control":
        actor = replace(actor, scope=SessionScope.ACCOUNT_CONTROL)
    elif defect == "legacy":
        s.user.birth_date = s.user.adult_attested_at = None
        s.user.adult_attestation_version = ""
    elif defect == "underage":
        s.user.birth_date = date.today() - timedelta(days=365 * 10)
    else:
        s.user.state = defect
        if defect in {"suspended", "deleted"}:
            s.user.is_active = False
    s.user.save()
    with pytest.raises(PermissionError):
        create(label, actor, uuid4(), s.at)
    with pytest.raises(PermissionError):
        read(label, actor, s.at)
    assert profile_model(label).objects.count() == 0


@pytest.mark.parametrize("label", LABELS)
def test_profile_flag_is_not_authority(label):
    s = make_actor()
    s.user.is_superuser = s.user.is_staff = True
    s.user.save()
    other = make_actor("+989123456781")
    foreign = profile_model(label).objects.create(user=other.user)
    with pytest.raises(LookupError):
        module(f"apps.{label}.policies").owned_profile(s.user, foreign.pk)
    assert create(label, s.actor, uuid4(), s.at).id != foreign.pk


def test_registration_switch_blocks_only_new_professional_profile():
    from apps.governance.flag_models import FeatureFlag

    s = make_actor(enable_registration=False)
    with pytest.raises(PermissionError):
        create("professionals", s.actor, uuid4(), s.at)
    athlete = create("athletes", s.actor, uuid4(), s.at)
    FeatureFlag.objects.filter(key="professional_registration").update(enabled=True)
    operation = uuid4()
    pro = create("professionals", s.actor, operation, s.at)
    FeatureFlag.objects.filter(key="professional_registration").update(enabled=False)
    assert create("professionals", s.actor, operation, s.at) == pro
    assert create("professionals", s.actor, uuid4(), s.at) == pro
    assert read("professionals", s.actor, s.at) == pro
    assert read("athletes", s.actor, s.at) == athlete


def test_registration_outage_denies_new_but_preserves_owned_setup(
    monkeypatch,
):
    from apps.governance.flag_models import FeatureFlag

    s = make_actor()
    pro = create("professionals", s.actor, uuid4(), s.at)
    other = make_actor("+989123456781")

    def unavailable(*args, **kwargs):
        raise DatabaseError("private sentinel")

    monkeypatch.setattr(FeatureFlag.objects, "get", unavailable)
    with pytest.raises(PermissionError) as error:
        create("professionals", other.actor, uuid4(), other.at)
    assert "private sentinel" not in str(error.value)
    assert read("professionals", s.actor, s.at) == pro
    assert create("professionals", s.actor, uuid4(), s.at) == pro


@pytest.mark.parametrize(
    "label,sink",
    [("athletes", "audit"), ("professionals", "audit"), ("professionals", "outbox")],
)
def test_evidence_failure_rolls_back_profile_and_receipt(label, sink, monkeypatch):
    s = make_actor()
    wiring = module(f"config.use_cases.{label[:-1]}_profile")

    def unavailable(*args, **kwargs):
        raise RuntimeError("evidence unavailable")

    monkeypatch.setattr(
        wiring, "append_event" if sink == "audit" else "append_outbox", unavailable
    )
    with pytest.raises(RuntimeError):
        create(label, s.actor, uuid4(), s.at)
    assert profile_model(label).objects.count() == 0
    assert (
        module(f"apps.{label}.receipt_models").ProfileCommandReceipt.objects.count()
        == 0
    )
    assert (
        OutboxEvent.objects.filter(event_type="professional.profile_changed").count()
        == 0
    )


@pytest.mark.parametrize("label", LABELS)
def test_archived_profile_cannot_be_resurrected_by_receipt(label):
    s = make_actor()
    operation = uuid4()
    dto = create(label, s.actor, operation, s.at)
    field = "status" if label == "athletes" else "state"
    profile_model(label).objects.filter(pk=dto.id).update(**{field: "archived"})
    with pytest.raises(LookupError):
        create(label, s.actor, operation, s.at)
    with pytest.raises(LookupError):
        read(label, s.actor, s.at)


@pytest.mark.parametrize("label", LABELS)
def test_create_validates_uuid_and_aware_time_without_effect(label):
    s = make_actor()
    for operation, at in (
        ("owner-selected", s.at),
        (uuid4(), s.at.replace(tzinfo=None)),
    ):
        with pytest.raises(ValueError):
            create(label, s.actor, operation, at)
    assert profile_model(label).objects.count() == 0


def test_profile_metadata_handler_is_bounded_and_dispatch_is_durable():
    from apps.governance.outbox import dispatch_event
    from apps.governance.outbox_models import OutboxDeliveryReceipt
    from config.event_handlers import HANDLERS

    s = make_actor()
    create("professionals", s.actor, uuid4(), s.at)
    event = OutboxEvent.objects.get(event_type="professional.profile_changed")
    lease = uuid4()
    OutboxEvent.objects.filter(pk=event.pk).update(
        state="leased", lease_uuid=lease, lease_until=s.at + timedelta(minutes=1)
    )
    assert dispatch_event(event.pk, s.at, lease_uuid=lease)
    assert dispatch_event(event.pk, s.at, lease_uuid=lease)
    assert (
        OutboxDeliveryReceipt.objects.filter(event=event, result="applied").count() == 1
    )
    event.payload = {**event.payload, "user_uuid": str(uuid4())}
    assert HANDLERS["professional.profile_changed"](event, s.at) == "skipped"
    event.payload["user_uuid"] = str(s.user.public_id)
    event.aggregate_version += 1
    assert HANDLERS["professional.profile_changed"](event, s.at) == "skipped"
