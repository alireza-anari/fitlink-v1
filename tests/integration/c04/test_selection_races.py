"""Actual PostgreSQL cap, immutable ownership and independent-session races."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from tests.integration.c03.profile_helpers import in_connection
from tests.integration.c04.selection_helpers import athlete, change, require, scope

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_concurrent_final_slot_has_one_success_and_no_fourth_entry(corpus):
    from apps.marketplace.selection_contracts import SelectionConflict

    person = athlete()
    targets = [corpus()[0] for _ in range(4)]
    state = require("read_comparison")(scope(person), timezone.now())
    for target in targets[:2]:
        state = change(person, "add", target.profile.id, state.version)
    barrier = Barrier(2)

    def add(target):
        barrier.wait(timeout=10)
        try:
            change(person, "add", target.profile.id, state.version)
            return True
        except SelectionConflict:
            return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        calls = [
            pool.submit(in_connection, lambda target=t: add(target))
            for t in targets[2:]
        ]
        assert sum(f.result(timeout=25) for f in calls) == 1
    assert len(require("read_comparison")(scope(person), timezone.now()).items) == 3


@pytest.mark.parametrize("owners", ["neither", "both"])
def test_sql_collection_requires_exactly_one_owner(owners):
    from apps.marketplace.selection_models import ComparisonCollection

    person = athlete()
    values = (
        {}
        if owners == "neither"
        else {"owner": person.user, "session_digest": "a" * 64}
    )
    with pytest.raises(IntegrityError), transaction.atomic():
        ComparisonCollection.objects.create(**values)


def test_sql_cap_and_immutable_owner_receipt_keys(corpus):
    from apps.marketplace.selection_models import (
        ComparisonCollection,
        ComparisonEntry,
        ComparisonReceipt,
    )

    person = athlete()
    target, _ = corpus()
    initial = require("read_comparison")(scope(person), timezone.now())
    change(person, "add", target.profile.id, initial.version)
    row = ComparisonCollection.objects.get(owner=person.user)
    with pytest.raises(IntegrityError), transaction.atomic():
        ComparisonEntry.objects.create(
            collection=row, professional_uuid=uuid4(), slot=4
        )
    with pytest.raises(IntegrityError), transaction.atomic():
        ComparisonEntry.objects.create(
            collection=row, professional_uuid=target.profile.id, slot=2
        )
    with pytest.raises(IntegrityError), transaction.atomic():
        ComparisonCollection.objects.filter(pk=row.pk).update(
            owner=None, session_digest="b" * 64
        )
    with pytest.raises(IntegrityError), transaction.atomic():
        ComparisonReceipt.objects.filter(collection=row).update(operation_uuid=uuid4())
