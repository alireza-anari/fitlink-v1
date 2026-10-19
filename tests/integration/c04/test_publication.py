"""Publication is deliberate and independent of actual C03 role approval."""

import importlib
import importlib.util
from uuid import uuid4

import pytest
from django.apps import apps
from django.db import connection
from django.utils import timezone

from tests.integration.c03.test_verification_decisions import approved

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
