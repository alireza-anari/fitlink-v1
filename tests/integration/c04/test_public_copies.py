"""Actual confirmed C03 fixtures; publication copies have separate authority."""

import importlib
import importlib.util
from dataclasses import replace
from uuid import uuid4

import pytest
from django.db import connection
from django.utils import timezone

from apps.assets.contracts import AssetNotFound
from tests.integration.c03.test_credential_revisions import ready
from tests.integration.c03.test_professional_setup import save
from tests.integration.c03.test_verification_decisions import approved
from tests.integration.c04.publication_helpers import (
    configure,
    confirm,
    module,
    prepare,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def api():
    path = "config.use_cases.public_media"
    assert importlib.util.find_spec(path), "Missing confirmed public-copy authority"
    return importlib.import_module(path)


def selected(settings, *, confirmed=True):
    configure(settings)
    subject = approved(settings)
    asset = ready(subject, "avatar")
    save(subject, "branding", {"avatar": asset.id})
    choice = module(
        "apps.professionals.publication_contracts"
    ).PublicationMediaSelection
    draft = prepare(subject, media=(choice("avatar", asset.id),))
    if confirmed:
        confirm(subject, draft)
    return subject, asset, draft


@pytest.mark.parametrize("purpose", ["identity_evidence", "credential_evidence"])
def test_private_source_and_evidence_never_public_copy(settings, purpose):
    assert connection.vendor == "postgresql"
    subject, asset, draft = selected(settings)
    with pytest.raises((ValueError, AssetNotFound)):
        api().authorize_public_media(
            draft.publication_id, draft.revision_id, purpose, timezone.now()
        )
    asset.refresh_from_db()
    assert asset.classification == "private_source"


def test_wrong_owner_purpose_revision_or_stale_confirmation_denied_before_storage(
    settings,
):
    subject, asset, draft = selected(settings)
    service = api()
    release = service.authorize_public_media(
        draft.publication_id, draft.revision_id, "avatar", timezone.now()
    )
    boundary = module("apps.assets.public_copies")
    for changes in (
        {"owner_uuid": uuid4()},
        {"revision_uuid": uuid4()},
        {"source_asset_uuid": uuid4()},
        {"publication_version": release.publication_version + 1},
    ):
        with pytest.raises((ValueError, AssetNotFound, PermissionError)):
            boundary.prepare_public_copy(
                replace(release, **changes),
                timezone.now(),
                authorize=service.validate_release,
            )
    save(subject, "description", {"biography": "Changed synthetic source"})
    with pytest.raises((ValueError, AssetNotFound, PermissionError)):
        boundary.prepare_public_copy(
            release, timezone.now(), authorize=service.validate_release
        )


def test_unconfirmed_selection_cannot_request_a_copy(settings):
    subject, asset, draft = selected(settings, confirmed=False)
    with pytest.raises((ValueError, AssetNotFound, PermissionError)):
        api().authorize_public_media(
            draft.publication_id, draft.revision_id, "avatar", timezone.now()
        )


def test_duplicate_prepare_is_one_effect_and_never_changes_private_derivative(settings):
    from apps.assets.models import AssetDerivative

    subject, asset, draft = selected(settings)
    before = list(AssetDerivative.objects.filter(asset=asset).values())
    service = api()
    release = service.authorize_public_media(
        draft.publication_id, draft.revision_id, "avatar", timezone.now()
    )
    boundary = module("apps.assets.public_copies")
    first = boundary.prepare_public_copy(
        release, timezone.now(), authorize=service.validate_release
    )
    second = boundary.prepare_public_copy(
        release, timezone.now(), authorize=service.validate_release
    )
    assert first.id == second.id and first.state == "pending"
    assert list(AssetDerivative.objects.filter(asset=asset).values()) == before
    asset.refresh_from_db()
    assert asset.classification == "private_source"


@pytest.mark.parametrize("change", ["owner", "revision", "ready_without_output"])
def test_copy_sql_binding_cannot_be_forged(settings, change):
    from django.db import DatabaseError, transaction
    from django.db.models import F

    from tests.integration.c03.test_professional_setup import owner
    from tests.integration.c04.copy_helpers import copy_model, pending

    subject, asset, draft, derivative, store, dto, job = pending(settings, claim=False)
    values = {
        "owner": {"owner_id": owner("+989123456789").user.pk},
        "revision": {"release_revision_uuid": uuid4()},
        "ready_without_output": {"state": "ready"},
    }
    with pytest.raises(DatabaseError), transaction.atomic():
        copy_model().objects.filter(pk=dto.id).update(
            **values[change], version=F("version") + 1
        )


def test_publication_sql_cannot_promote_media_before_outputs_ready(settings):
    from django.db import DatabaseError, transaction
    from django.db.models import F

    from apps.professionals.publication_models import ProfessionalPublication

    person, asset, draft = selected(settings)
    with pytest.raises(DatabaseError), transaction.atomic():
        ProfessionalPublication.objects.filter(pk=draft.publication_id).update(
            state="published",
            current_revision_id=draft.revision_id,
            requested_revision_id=None,
            version=F("version") + 1,
        )
