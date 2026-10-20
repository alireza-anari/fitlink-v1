"""Role intersection and unchanged-version timestamp authority on every read."""

import pytest
from django.utils import timezone

from tests.integration.c03.test_verification_revocation import restrict, revoke
from tests.integration.c04.test_public_projection import api, published

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize("role", ["coach", "nutritionist"])
def test_current_two_role_projection_intersection(settings, role):
    subject, draft = published(settings, roles=("coach", "nutritionist"))
    api().refresh_public_projection(subject.profile.id, timezone.now())
    revoke(subject, role)
    dto = api().public_professional(subject.profile.id, timezone.now())
    assert dto.as_public_dict()["verified_roles"] == [
        r for r in ["coach", "nutritionist"] if r != role
    ]


def test_temporary_role_release_restores_only_selected_current_role(settings):
    subject, draft = published(settings, roles=("coach", "nutritionist"))
    restrict(subject, "nutritionist")
    assert api().public_professional(
        subject.profile.id, timezone.now()
    ).as_public_dict()["verified_roles"] == ["coach"]
    restrict(subject, "nutritionist", release=True)
    assert api().public_professional(
        subject.profile.id, timezone.now()
    ).as_public_dict()["verified_roles"] == ["coach", "nutritionist"]


def test_stale_copy_hides_whole_selected_release(settings):
    from tests.integration.c04.copy_helpers import pending, process

    subject, asset, draft, derivative, store, dto, job = pending(settings)
    assert process(store, job).status == "ready"
    assert api().public_professional(subject.profile.id, timezone.now()) is not None
    derivative.version += 1
    derivative.save(update_fields=["version"])
    assert api().public_professional(subject.profile.id, timezone.now()) is None


def test_buffered_payload_expiry_is_rechecked_after_render(settings, monkeypatch):
    from datetime import timedelta

    subject, draft = published(
        settings, valid_until=timezone.now() + timedelta(hours=1)
    )

    def rendered(dto):
        assert dto is not None
        body = dto.as_public_dict()
        # A synthetic trusted clock only; real PostgreSQL/source predicates run.
        monkeypatch.setattr(timezone, "now", lambda: draft.valid_until)
        return body

    assert (
        api().public_professional(subject.profile.id, timezone.now(), release=rendered)
        is None
    )
