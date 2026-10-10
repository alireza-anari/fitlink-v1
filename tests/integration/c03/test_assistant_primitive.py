"""Inert internal metadata, real authorization, CAS, receipts and rollback."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from django.utils import timezone

from apps.governance.audit_models import AuditEvent
from apps.governance.outbox_models import OutboxEvent
from apps.professionals.contracts import ProfileConflict, ProfileNotFound
from apps.professionals.models import AssistantMembership, ProfileCommandReceipt
from config.use_cases import professional_profile as commands

from .profile_helpers import in_connection, make_actor, read
from .test_professional_setup import owner

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def command(name, *args, **kwargs):
    assert callable(getattr(commands, name, None)), f"Missing inert command: {name}"
    return getattr(commands, name)(*args, **kwargs)


def define(s, assistant, operation=None):
    return command(
        "define_assistant_role",
        s.actor,
        assistant.user.public_id,
        operation or uuid4(),
        timezone.now(),
    )


def revoke(s, membership, operation=None, version=None):
    return command(
        "revoke_assistant_role",
        s.actor,
        membership.id,
        version or membership.version,
        operation or uuid4(),
        timezone.now(),
    )


def test_assistant_fixed_role_never_grants_access():
    s, assistant = owner(), make_actor("+989123456789")
    dto = define(s, assistant)
    assert dto.role == "client_support" and dto.state == "defined"
    assert (
        dto.profile_uuid == s.profile.id
        and dto.assistant_uuid == assistant.user.public_id
    )
    for label in ("athletes", "professionals"):
        with pytest.raises(LookupError):
            read(label, assistant.actor, timezone.now())
    from apps.professionals.selectors import own_credential, own_verification

    for selector in (own_credential, own_verification):
        with pytest.raises(ProfileNotFound):
            selector(assistant.actor, uuid4(), timezone.now())
    from config.use_cases.profile_assets import begin_profile_upload

    with pytest.raises(LookupError):
        begin_profile_upload(
            assistant.actor,
            "avatar",
            s.profile.id,
            uuid4(),
            timezone.now(),
            declared_size=128,
            declared_type="image/png",
        )
    assert not assistant.user.is_staff


def test_definition_replay_duplicate_and_revocation_current_result():
    s, assistant, operation = owner(), make_actor("+989123456789"), uuid4()
    first = define(s, assistant, operation)
    counts = (AuditEvent.objects.count(), OutboxEvent.objects.count())
    assert define(s, assistant, operation) == first
    assert define(s, assistant) == first
    assert counts == (AuditEvent.objects.count(), OutboxEvent.objects.count())
    revoked = revoke(s, first)
    assert revoked.state == "revoked" and revoked.version == first.version + 1
    assert define(s, assistant, operation) == revoked
    assert AssistantMembership.objects.count() == 1
    replacement = define(s, assistant)
    assert replacement.id != revoked.id and replacement.state == "defined"


def test_revoke_replay_and_version_payload_conflict():
    s, assistant = owner(), make_actor("+989123456789")
    row, op = define(s, assistant), uuid4()
    dto = revoke(s, row, op)
    assert revoke(s, row, op) == dto
    with pytest.raises(ProfileConflict):
        revoke(s, row, version=row.version + 10)
    other = make_actor("+989123456788")
    with pytest.raises(ProfileConflict):
        define(s, other, op)


@pytest.mark.parametrize("fault", ["self", "missing", "restricted", "suspended"])
def test_definition_is_nonself_and_current(fault):
    s, assistant = owner(), make_actor("+989123456789")
    identifier = assistant.user.public_id
    if fault == "self":
        identifier = s.user.public_id
    elif fault == "missing":
        identifier = uuid4()
    else:
        assistant.user.state = fault
        assistant.user.is_active = fault != "suspended"
        assistant.user.save(update_fields=["state", "is_active"])
    with pytest.raises((ValueError, LookupError, PermissionError)):
        command("define_assistant_role", s.actor, identifier, uuid4(), timezone.now())
    assert AssistantMembership.objects.count() == 0


def test_definitions_have_no_activation_or_catalog_limit():
    s = owner()
    for phone in ("+989123456789", "+989123456788", "+989123456787"):
        assert define(s, make_actor(phone)).state == "defined"
    assert (
        AssistantMembership.objects.filter(profile=s.profile, state="defined").count()
        == 3
    )


@pytest.mark.parametrize(
    "fault", ["anonymous", "auth_version", "restricted", "archived"]
)
def test_definition_replay_revalidates_owner(fault):
    s, assistant, operation = owner(), make_actor("+989123456789"), uuid4()
    define(s, assistant, operation)
    if fault == "anonymous":
        s.actor = None
    elif fault == "auth_version":
        s.user.auth_version += 1
        s.user.save(update_fields=["auth_version"])
    elif fault == "restricted":
        s.user.state = "restricted"
        s.user.save(update_fields=["state"])
    else:
        s.profile.state = "archived"
        s.profile.save(update_fields=["state"])
    with pytest.raises((PermissionError, ProfileNotFound)):
        define(s, assistant, operation)


def test_foreign_uuid_and_stale_owner_deny_before_conflicts():
    s, assistant = owner(), make_actor("+989123456789")
    row = define(s, assistant)
    other = owner("+989123456788")
    for identifier in (row.id, uuid4()):
        with pytest.raises(ProfileNotFound):
            command(
                "revoke_assistant_role",
                other.actor,
                identifier,
                100,
                uuid4(),
                timezone.now(),
            )
    s.user.state = "pending_deletion"
    s.user.save(update_fields=["state"])
    with pytest.raises(PermissionError):
        revoke(s, row, version=100)


@pytest.mark.parametrize(
    "command_name", ["define_assistant_role", "revoke_assistant_role"]
)
@pytest.mark.parametrize("fault", ["audit", "outbox"])
def test_membership_mutation_is_transactional(monkeypatch, command_name, fault):
    s, assistant = owner(), make_actor("+989123456789")
    membership = define(s, assistant) if command_name.startswith("revoke") else None
    counts = (
        AssistantMembership.objects.count(),
        ProfileCommandReceipt.objects.count(),
        AuditEvent.objects.count(),
        OutboxEvent.objects.count(),
    )

    def unavailable(*args, **kwargs):
        raise RuntimeError("Synthetic unavailable")

    monkeypatch.setattr(
        commands, "append_event" if fault == "audit" else "append_outbox", unavailable
    )
    with pytest.raises(RuntimeError):
        revoke(s, membership) if membership else define(s, assistant)
    assert counts == (
        AssistantMembership.objects.count(),
        ProfileCommandReceipt.objects.count(),
        AuditEvent.objects.count(),
        OutboxEvent.objects.count(),
    )
    if membership:
        assert AssistantMembership.objects.get(pk=membership.id).state == "defined"


def test_define_define_independent_connections_one_inert_row():
    s, assistant, barrier = owner(), make_actor("+989123456789"), Barrier(2)

    def run():
        def action():
            barrier.wait(timeout=10)
            return define(s, assistant)

        return in_connection(action)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: run(), range(2)))
    assert results[0].id == results[1].id
    assert AssistantMembership.objects.count() == 1
    assert AuditEvent.objects.filter(action="assistant.defined").count() == 1


def test_revoke_revoke_independent_connections_one_effect():
    s, assistant, barrier = owner(), make_actor("+989123456789"), Barrier(2)
    row = define(s, assistant)

    def run():
        def action():
            barrier.wait(timeout=10)
            try:
                return revoke(s, row)
            except ProfileConflict:
                return None

        return in_connection(action)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: run(), range(2)))
    assert sum(result is not None for result in results) == 1
    assert AuditEvent.objects.filter(action="assistant.revoked").count() == 1


def test_metadata_contains_only_identifiers_and_fixed_fields():
    s, assistant = owner(), make_actor("+989123456789")
    row = define(s, assistant)
    revoke(s, row)
    events = AuditEvent.objects.filter(action__startswith="assistant.")
    assert list(events.values_list("action", flat=True)) == [
        "assistant.defined",
        "assistant.revoked",
    ]
    assert all(
        event.subject_uuid == row.id and event.subject_type == "assistant"
        for event in events
    )
    for event in OutboxEvent.objects.filter(event_type="professional.profile_changed"):
        assert set(event.payload) == {"profile_uuid", "user_uuid"}
    # No invitation, activation, client or entitlement parameters.
    with pytest.raises(TypeError):
        command(
            "define_assistant_role",
            s.actor,
            assistant.user.public_id,
            uuid4(),
            timezone.now(),
            client_uuid=uuid4(),
            role="coach",
            activate=True,
        )
