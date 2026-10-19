"""Ordered commits on independent PostgreSQL connections, not mocked races."""

import pytest

from tests.integration.c03.test_verification_decision_races import ordered_connections
from tests.integration.c03.test_verification_decisions import approved
from tests.integration.c03.test_verification_revocation import revoke
from tests.integration.c04.publication_helpers import (
    configure,
    confirm,
    effective,
    prepare,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize("order", ["publish_first", "revoke_first"])
def test_publish_vs_revoke_two_orders(settings, order):
    configure(settings)
    subject = approved(settings)
    draft = prepare(subject)
    first, second = (
        (lambda: confirm(subject, draft), lambda: revoke(subject, "coach"))
        if order == "publish_first"
        else (lambda: revoke(subject, "coach"), lambda: confirm(subject, draft))
    )
    a, b = ordered_connections(first, second)
    if order == "revoke_first":
        assert b == "conflict"
    else:
        assert a != "conflict"
    assert effective(subject) is None
