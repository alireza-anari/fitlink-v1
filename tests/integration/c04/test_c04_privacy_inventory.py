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


def test_owned_selection_inventory_contains_all_records_without_session_capability(
    corpus,
):
    from uuid import uuid4

    from apps.marketplace.selection_models import ComparisonCollection
    from config.use_cases.c04_privacy import enumerate_marketplace_inventory
    from tests.integration.c04.selection_helpers import athlete, change, require, scope

    owner = athlete()
    target, _ = corpus()
    require("set_favorite")(
        owner.actor, target.profile.id, True, uuid4(), timezone.now()
    )
    state = require("read_comparison")(scope(owner), timezone.now())
    change(owner, "add", target.profile.id, state.version)
    collection = ComparisonCollection.objects.get(owner=owner.user)
    rows = enumerate_marketplace_inventory(owner.user.public_id)
    selected = [row for row in rows if row.kind.startswith("marketplace_selection")]
    assert {row.kind for row in selected} == {
        "marketplace_selection_favorite",
        "marketplace_selection_favorite_receipt",
        "marketplace_selection_collection",
        "marketplace_selection_entry",
        "marketplace_selection_comparison_receipt",
    }, "Owned selection records are missing from the private inventory"
    assert all(row.owner_uuid == owner.user.public_id for row in selected)
    assert not any(
        hasattr(row, "session_digest") or hasattr(row, "snapshot") for row in selected
    )
    assert str(collection.id) in repr(selected)
