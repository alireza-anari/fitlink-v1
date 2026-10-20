"""Derived records join the owner's existing finite private inventory."""

import pytest
from django.utils import timezone

from tests.integration.c04.test_public_projection import api, published

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_projection_inventory_is_owned_and_contains_no_private_bindings(settings):
    from uuid import uuid4

    from config.use_cases.c03_privacy import inventory_c03_owner
    from config.use_cases.c04_privacy import enumerate_marketplace_inventory

    subject, draft = published(settings)
    api().refresh_public_projection(subject.profile.id, timezone.now())
    rows = inventory_c03_owner(subject.user.public_id, timezone.now()).records
    derived = [r for r in rows if r.kind.startswith("public_projection")]
    assert {r.kind for r in derived} >= {
        "public_projection",
        "public_projection_refresh",
    }
    assert all(r.owner_uuid == subject.user.public_id for r in derived)
    assert all(
        not hasattr(r, "authority_hash") and not hasattr(r, "snapshot") for r in derived
    )
    assert enumerate_marketplace_inventory(uuid4()) == ()
