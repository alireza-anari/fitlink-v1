"""Publication is deliberate and independent of actual C03 role approval."""

import importlib
import importlib.util
from uuid import uuid4

import pytest
from django.apps import apps
from django.db import connection
from django.utils import timezone

from tests.integration.c03.test_verification_decisions import approved

from .publication_helpers import configure

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def publication_model():
    model = next(
        (
            m
            for m in apps.get_models()
            if m._meta.label == "professionals.ProfessionalPublication"
        ),
        None,
    )
    assert model is not None, "Verification alone has no deliberate publication model"
    return model


def test_verification_never_publishes(settings):
    assert connection.vendor == "postgresql"
    subject = approved(settings)
    assert not publication_model().objects.filter(profile=subject.profile).exists()
    name = "apps.professionals.publication_selectors"
    assert importlib.util.find_spec(name) is not None, (
        "Missing current publication reader"
    )
    reader = importlib.import_module(name)
    assert reader.effective_publication(subject.profile.id, timezone.now()) is None


def test_confirm_requires_explicit_exact_revision_and_current_owner(settings):
    assert connection.vendor == "postgresql"
    configure(settings)
    subject = approved(settings)
    name = "config.use_cases.publication"
    assert importlib.util.find_spec(name) is not None, (
        "Missing deliberate publish command"
    )
    commands = importlib.import_module(name)
    contracts = importlib.import_module("apps.professionals.publication_contracts")
    subject.profile.refresh_from_db()
    draft = commands.prepare_publication(
        subject.actor,
        contracts.PublicationSelection(fields=("display_name",), roles=("coach",)),
        subject.profile.version,
        None,
        uuid4(),
        timezone.now(),
    )
    with pytest.raises(ValueError):
        commands.confirm_publication(
            subject.actor,
            draft.publication_id,
            draft.revision_id,
            False,
            draft.version,
            uuid4(),
            timezone.now(),
        )
    assert (
        publication_model().objects.get(pk=draft.publication_id).current_revision_id
        is None
    )


def test_changed_source_requires_reconfirmation(settings):
    from tests.integration.c03.test_professional_setup import save

    from .publication_helpers import confirm, effective, prepare

    configure(settings)
    subject = approved(settings)
    draft = prepare(subject)
    confirm(subject, draft)
    assert effective(subject) is not None
    save(subject, "description", {"biography": "Updated private draft"})
    assert effective(subject) is None
    fresh = prepare(subject)
    assert effective(subject) is None
    confirm(subject, fresh)
    assert effective(subject).snapshot["biography"] == "Updated private draft"


def test_coach_only_release_excludes_private_nutritionist(settings):
    from tests.integration.c03.test_verification_decisions import decision, review

    from .publication_helpers import confirm, effective, prepare

    configure(settings)
    subject = review(settings)
    decision(subject, "identity")
    decision(subject, "coach")
    decision(subject, "nutritionist", "reject")
    draft = prepare(
        subject, qualifications=(subject.assets["coach"][1].current_revision_id,)
    )
    confirm(subject, draft)
    current = effective(subject)
    assert tuple(current.snapshot["verified_roles"]) == ("coach",)
    assert {row["role"] for row in current.snapshot["qualification_summaries"]} == {
        "coach"
    }
    assert "identity_name" not in current.snapshot
    assert "user_uuid" not in current.snapshot


def test_identity_credentials_and_foreign_media_rejected(settings):
    from tests.integration.c03.test_credential_revisions import ready
    from tests.integration.c03.test_professional_setup import owner

    from .publication_helpers import module, prepare

    configure(settings)
    subject = approved(settings)
    with pytest.raises(ValueError):
        prepare(
            subject, qualifications=(subject.assets["identity"][1].current_revision_id,)
        )
    foreign = owner("+989123456789")
    media = ready(foreign, "avatar")
    selected = module(
        "apps.professionals.publication_contracts"
    ).PublicationMediaSelection
    with pytest.raises((ValueError, LookupError)):
        prepare(subject, media=(selected("avatar", media.id),))
    assert not publication_model().objects.filter(profile=subject.profile).exists()


def test_qualification_summary_exact_revision_only(settings):
    from tests.integration.c03.test_verification_decisions import mutate_evidence

    from .publication_helpers import confirm, effective, prepare

    configure(settings)
    subject = approved(settings)
    selected = subject.assets["coach"][1].current_revision_id
    draft = prepare(subject, qualifications=(selected,))
    confirm(subject, draft)
    snapshot = effective(subject).snapshot
    assert set(snapshot["qualification_summaries"][0]) == {
        "role",
        "title",
        "issuer",
        "type_label",
        "issued_on",
        "expires_on",
    }
    mutate_evidence(subject, "coach")
    assert effective(subject) is None
    with pytest.raises((ValueError, LookupError, PermissionError)):
        prepare(subject, qualifications=(selected,))


def test_cross_account_confirmation_and_stale_session_denied(settings):
    from apps.accounts.sessions import revoke_sessions
    from apps.governance.audit import append_event
    from tests.integration.c03.profile_helpers import make_actor

    from .publication_helpers import confirm, prepare

    configure(settings)
    subject = approved(settings)
    draft = prepare(subject)
    foreign = make_actor("+989123456789")
    with pytest.raises((LookupError, PermissionError)):
        confirm(subject, draft, actor=foreign.actor)
    revoke_sessions(subject.user, "all", timezone.now(), append_event)
    with pytest.raises(PermissionError):
        confirm(subject, draft)
    assert (
        publication_model().objects.get(pk=draft.publication_id).current_revision_id
        is None
    )


def test_duplicate_confirm_single_effect_changed_payload_conflict(settings):
    from apps.governance.audit_models import AuditEvent
    from apps.governance.outbox_models import OutboxEvent

    from .publication_helpers import confirm, module, prepare

    configure(settings)
    subject = approved(settings)
    draft = prepare(subject)
    operation = uuid4()
    result = confirm(subject, draft, operation=operation)
    before = (AuditEvent.objects.count(), OutboxEvent.objects.count())
    assert confirm(subject, draft, operation=operation).version == result.version
    assert before == (AuditEvent.objects.count(), OutboxEvent.objects.count())
    with pytest.raises(ValueError):
        module("config.use_cases.publication").confirm_publication(
            subject.actor,
            draft.publication_id,
            uuid4(),
            True,
            draft.version,
            operation,
            timezone.now(),
        )


def test_expiry_withdrawal_and_flag_off_are_fail_closed(settings):
    from datetime import timedelta

    from apps.governance.flag_models import FeatureFlag

    from .publication_helpers import confirm, effective, module, prepare

    configure(settings)
    subject = approved(settings)
    expiry = timezone.now() + timedelta(minutes=10)
    draft = prepare(subject, valid_until=expiry)
    published = confirm(subject, draft)
    assert effective(subject, at=expiry) is None
    FeatureFlag.objects.filter(key="marketplace").update(enabled=False)
    module("config.use_cases.publication").unpublish_profile(
        subject.actor, draft.publication_id, published.version, uuid4(), timezone.now()
    )
    assert effective(subject) is None
    with pytest.raises((ValueError, RuntimeError, PermissionError)):
        prepare(subject)


def test_selected_private_media_waits_for_separate_public_copy(settings):
    from apps.assets.models import AssetDerivative
    from tests.integration.c03.test_credential_revisions import ready
    from tests.integration.c03.test_professional_setup import save

    from .publication_helpers import confirm, effective, module, prepare

    configure(settings)
    subject = approved(settings)
    media = ready(subject, "avatar")
    save(subject, "branding", {"avatar": media.id})
    before = AssetDerivative.objects.count()
    selected = module(
        "apps.professionals.publication_contracts"
    ).PublicationMediaSelection
    draft = prepare(subject, media=(selected("avatar", media.id),))
    confirm(subject, draft)
    assert effective(subject) is None
    media.refresh_from_db()
    assert media.classification == "private_source"
    assert AssetDerivative.objects.count() == before
