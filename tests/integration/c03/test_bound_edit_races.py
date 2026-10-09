from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from django.utils import timezone

from apps.professionals import contracts

from .profile_helpers import in_connection
from .test_credential_revisions import command, create, owner, payload, ready, targets
from .test_professional_setup import save

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_postgresql_concurrent_revision_has_one_winner():
    s = owner()
    asset = ready(s)
    dto = create(s, source_asset=asset.id)
    barrier = Barrier(2)

    def run(title):
        def action():
            barrier.wait(timeout=10)
            try:
                return command(
                    "revise_credential",
                    s.actor,
                    dto.id,
                    payload(title=title, source_asset=asset.id),
                    dto.version,
                    uuid4(),
                    timezone.now(),
                )
            except contracts.ProfileConflict:
                return "conflict"

        return in_connection(action)

    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(run, ["الف", "ب"]))
    assert results.count("conflict") == 1
    from apps.professionals.models import CredentialRevision

    assert CredentialRevision.objects.filter(credential_id=dto.id).count() == 2


def test_postgresql_duplicate_operation_is_one_effect():
    s = owner()
    asset = ready(s)
    operation, barrier = uuid4(), Barrier(2)

    def run(_):
        def action():
            barrier.wait(timeout=10)
            return command(
                "create_credential",
                s.actor,
                payload(source_asset=asset.id),
                1,
                operation,
                timezone.now(),
            )

        return in_connection(action)

    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(run, range(2)))
    assert results[0].id == results[1].id
    from apps.professionals.models import CredentialRevision

    assert CredentialRevision.objects.count() == 1


def test_identity_edit_and_role_deactivation_serialize_without_cross_invalidation():
    s = owner()
    save(s, "identity", {"identity_name": "الف", "roles": ["coach", "nutritionist"]})
    pending = targets(s)
    s.profile.refresh_from_db()
    version, barrier = s.profile.version, Barrier(2)

    def run(values):
        def action():
            barrier.wait(timeout=10)
            try:
                return save(s, "identity", values, version=version)
            except contracts.ProfileConflict:
                return "conflict"

        return in_connection(action)

    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(run, [{"identity_name": "ب"}, {"roles": ["coach"]}]))
    assert results.count("conflict") == 1
    pending["coach"].refresh_from_db()
    assert pending["coach"].state == "submitted"
