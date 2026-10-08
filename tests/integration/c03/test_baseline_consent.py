"""Self storage is neither sharing authority nor permanent access."""

from dataclasses import replace
from datetime import timedelta
from uuid import uuid4

import pytest
from django.test import override_settings

from apps.athletes.baseline_models import BaselineAssessment
from apps.governance import consents
from apps.governance.consent_models import Consent

from .baseline_helpers import command, grant, read, required, save, setup
from .profile_helpers import make_actor, module

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_optional_write_needs_current_explicit_self_storage():
    ctx, row = setup()
    with pytest.raises(PermissionError):
        save(ctx, row, "basics", {"height_cm": "170.0"})
    with pytest.raises(PermissionError):
        command(
            "grant_baseline_storage",
            ctx.actor,
            row.id,
            row.version,
            False,
            uuid4(),
            ctx.at,
        )
    with (
        override_settings(BASELINE_STORAGE_CONSENT_SECONDS=None),
        pytest.raises(ValueError),
    ):
        command(
            "grant_baseline_storage",
            ctx.actor,
            row.id,
            row.version,
            True,
            uuid4(),
            ctx.at,
        )
    consent_id = grant(ctx, row)
    row = save(ctx, row, "basics", {"height_cm": "170.0"})
    assert row.optional_access and row.answers["height_cm"] is not None
    consent = Consent.objects.get(pk=consent_id)
    assert consent.subject_id == ctx.user.id == consent.grantee_id
    assert consent.purpose == "baseline_storage"
    scope = consent.scopes.get()
    assert (
        scope.kind == "athlete_baseline"
        and scope.object_uuid == row.id
        and scope.object_version == 1
    )


@pytest.mark.parametrize("change", ["grantee", "purpose", "owner", "schema", "kind"])
def test_storage_grant_cannot_share(change):
    ctx, row = setup()
    other = make_actor("+989123456781")
    callback = module("config.use_cases.c03_privacy").validate_baseline_scope
    scope = consents.ValidatedConsentScope(
        ctx.user.public_id,
        ctx.user.public_id,
        "baseline_storage",
        "athlete_baseline",
        row.id,
        1,
        ctx.at + timedelta(days=1),
    )
    changes = {
        "grantee": {"grantee_uuid": other.user.public_id},
        "purpose": {"purpose": "professional_share"},
        "owner": {"subject_uuid": other.user.public_id},
        "schema": {"object_version": 2},
        "kind": {"kind": "health_storage"},
    }[change]
    with pytest.raises(PermissionError):
        consents.grant_consent(
            ctx.actor,
            replace(scope, **changes),
            "baseline-v1",
            "a" * 64,
            ctx.at,
            lambda _: None,
            scope_validator=callback,
        )
    assert not Consent.objects.exists()


def test_revoke_and_expiry_immediately_filter_optional_values():
    ctx, row = setup()
    consent_id = grant(ctx, row)
    row = save(ctx, row, "basics", {"height_cm": "170.0"})
    consent = Consent.objects.get(pk=consent_id)
    expired = read(ctx, row, consent.expires_at)
    assert expired.answers["height_cm"] is None and not expired.optional_access
    command(
        "revoke_baseline_storage",
        ctx.actor,
        row.id,
        consent_id,
        consent.version,
        uuid4(),
        ctx.at + timedelta(seconds=1),
    )
    revoked = read(ctx, row, ctx.at + timedelta(seconds=1))
    assert revoked.answers["height_cm"] is None and not revoked.optional_access
    assert BaselineAssessment.objects.get(pk=row.id).height_cm is not None
    with pytest.raises(PermissionError):
        command(
            "save_baseline_step",
            ctx.actor,
            row.id,
            "basics",
            __import__(
                "apps.athletes.contracts", fromlist=["BaselineStepInput"]
            ).BaselineStepInput({"weight_kg": "70.0"}),
            row.version,
            uuid4(),
            ctx.at + timedelta(seconds=1),
        )


def test_grant_and_revoke_operation_replays_are_current_and_once():
    ctx, row = setup()
    key = uuid4()
    consent_id = grant(ctx, row, key)
    assert grant(ctx, row, key) == consent_id and Consent.objects.count() == 1
    revoke_key = uuid4()
    for _ in range(2):
        command(
            "revoke_baseline_storage",
            ctx.actor,
            row.id,
            consent_id,
            1,
            revoke_key,
            ctx.at,
        )
    assert Consent.objects.get(pk=consent_id).version == 2
    assert not read(ctx, row).optional_access


def test_current_auth_precedes_grant_retry():
    ctx, row = setup()
    key = uuid4()
    grant(ctx, row, key)
    ctx.user.auth_version += 1
    ctx.user.save(update_fields=["auth_version"])
    with pytest.raises(PermissionError):
        grant(ctx, row, key)


def test_clear_optional_draft_does_not_require_consent_and_preserves_required():
    ctx, row = setup()
    consent_id = grant(ctx, row)
    row = save(ctx, required(ctx, row), "basics", {"height_cm": "170.0"})
    command(
        "revoke_baseline_storage", ctx.actor, row.id, consent_id, 1, uuid4(), ctx.at
    )
    cleared = command(
        "clear_optional_baseline", ctx.actor, row.id, row.version, uuid4(), ctx.at
    )
    assert cleared.answers["height_cm"] is None and cleared.answers["goals"] == [
        "strength"
    ]
    assert BaselineAssessment.objects.get(pk=row.id).height_cm is None


def test_submitted_clear_uses_correction_not_snapshot_mutation():
    ctx, row = setup()
    grant(ctx, row)
    row = save(ctx, required(ctx, row), "basics", {"height_cm": "170.0"})
    row = command("submit_baseline", ctx.actor, row.id, row.version, uuid4(), ctx.at)
    with pytest.raises(ValueError):
        command(
            "clear_optional_baseline", ctx.actor, row.id, row.version, uuid4(), ctx.at
        )
    assert BaselineAssessment.objects.get(pk=row.id).height_cm is not None
