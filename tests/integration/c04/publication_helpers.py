"""Synthetic explicit disclosure and real C03 authority; no account bypass."""

import importlib
import importlib.util
from uuid import uuid4

from django.apps import apps
from django.utils import timezone

from apps.governance.flag_models import FeatureFlag


def configure(settings):
    FeatureFlag.objects.update_or_create(key="marketplace", defaults={"enabled": True})
    settings.C04_PUBLICATION_DISCLOSURE = {
        "version": "c04-synthetic-disclosure-v1",
        "text": (
            "SYNTHETIC TEST WORDING ONLY: selected facts are public; "
            "downloaded copies cannot be recalled."
        ),
    }


def module(path):
    assert importlib.util.find_spec(path) is not None, (
        "Missing C04 publication behavior"
    )
    return importlib.import_module(path)


def model(name="ProfessionalPublication"):
    found = next(
        (m for m in apps.get_models() if m._meta.label == "professionals." + name),
        None,
    )
    assert found is not None, "Missing deliberate professional publication schema"
    return found


def prepare(
    subject,
    *,
    fields=("display_name", "biography"),
    roles=("coach",),
    qualifications=(),
    media=(),
    slug=None,
    valid_until=None,
    operation=None,
):
    contracts = module("apps.professionals.publication_contracts")
    subject.profile.refresh_from_db()
    old = model().objects.filter(profile=subject.profile).first()
    return module("config.use_cases.publication").prepare_publication(
        subject.actor,
        contracts.PublicationSelection(
            fields=fields,
            roles=roles,
            qualification_revision_ids=qualifications,
            media=media,
            slug=slug,
            valid_until=valid_until,
        ),
        subject.profile.version,
        old.version if old else None,
        operation or uuid4(),
        timezone.now(),
    )


def confirm(subject, draft, *, operation=None, actor=None):
    return module("config.use_cases.publication").confirm_publication(
        actor or subject.actor,
        draft.publication_id,
        draft.revision_id,
        True,
        draft.version,
        operation or uuid4(),
        timezone.now(),
    )


def effective(subject, at=None):
    return module("apps.professionals.publication_selectors").effective_publication(
        subject.profile.id, at or timezone.now()
    )
