"""Favorites require current own athlete authority and current public targets."""

from uuid import uuid4

import pytest
from django.utils import timezone

from tests.integration.c03.profile_helpers import make_actor
from tests.integration.c04.selection_helpers import athlete, require

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_favorites_require_current_owned_athlete_context(corpus):
    target, _ = corpus()
    person = make_actor("+989155550002")
    command = require("set_favorite")
    with pytest.raises((PermissionError, LookupError)):
        command(person.actor, target.profile.id, True, uuid4(), timezone.now())
    person = athlete()
    assert (
        command(person.actor, target.profile.id, True, uuid4(), timezone.now()).selected
        is True
    )
    assert [
        x.profile_uuid for x in require("list_favorites")(person.actor, timezone.now())
    ] == [target.profile.id]


def test_favorite_duplicate_receipt_and_off_flag_private_removal(corpus):
    from apps.governance.flag_models import FeatureFlag

    person = athlete()
    target, _ = corpus()
    command = require("set_favorite")
    operation = uuid4()
    for _ in range(2):
        assert command(
            person.actor, target.profile.id, True, operation, timezone.now()
        ).selected
    assert len(require("list_favorites")(person.actor, timezone.now())) == 1
    FeatureFlag.objects.filter(key="marketplace").update(enabled=False)
    assert require("list_favorites")(person.actor, timezone.now()) == ()
    assert (
        command(
            person.actor, target.profile.id, False, uuid4(), timezone.now()
        ).selected
        is False
    )
    with pytest.raises(LookupError):
        command(person.actor, target.profile.id, True, uuid4(), timezone.now())


def test_unrelated_user_staff_assistant_cannot_read_write_counts(corpus):
    person = athlete()
    other = athlete("+989155550003")
    other.user.is_staff = True
    other.user.save(update_fields=["is_staff"])
    target, _ = corpus()
    require("set_favorite")(
        person.actor, target.profile.id, True, uuid4(), timezone.now()
    )
    assert require("list_favorites")(other.actor, timezone.now()) == ()
    other.user.auth_version += 1
    other.user.save(update_fields=["auth_version"])
    with pytest.raises(PermissionError):
        require("list_favorites")(other.actor, timezone.now())


def test_withdrawn_favorites_emit_no_name_media_or_hidden_count(corpus):
    from apps.professionals.publication_models import ProfessionalPublication
    from config.use_cases.publication import unpublish_profile

    person = athlete()
    target, draft = corpus()
    require("set_favorite")(
        person.actor, target.profile.id, True, uuid4(), timezone.now()
    )
    row = ProfessionalPublication.objects.get(pk=draft.publication_id)
    unpublish_profile(target.actor, row.id, row.version, uuid4(), timezone.now())
    assert require("list_favorites")(person.actor, timezone.now()) == ()


def test_forged_actor_denied_before_hidden_favorite_count_is_observed():
    from dataclasses import replace

    from apps.marketplace.selection_models import Favorite

    victim = athlete()
    unrelated = athlete("+989155550008")
    Favorite.objects.bulk_create(
        [Favorite(owner=victim.user, professional_uuid=uuid4()) for _ in range(101)]
    )
    forged = replace(unrelated.actor, user_uuid=victim.user.public_id)
    with pytest.raises(PermissionError):
        require("list_favorites")(forged, timezone.now())


def test_changed_favorite_payload_cannot_reuse_operation_receipt(corpus):
    from apps.marketplace.selection_contracts import SelectionConflict

    person = athlete()
    target, _ = corpus()
    operation = uuid4()
    require("set_favorite")(
        person.actor, target.profile.id, True, operation, timezone.now()
    )
    with pytest.raises(SelectionConflict):
        require("set_favorite")(
            person.actor, target.profile.id, False, operation, timezone.now()
        )
    assert len(require("list_favorites")(person.actor, timezone.now())) == 1
