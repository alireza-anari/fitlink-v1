import importlib
import importlib.util
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, replace
from datetime import timedelta
from threading import Barrier
from uuid import NAMESPACE_URL, uuid4, uuid5

import pytest
from django.db import close_old_connections, transaction
from django.utils import timezone
from test_phone_change import actor_for
from test_recovery_authorization import owner

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture(autouse=True)
def restore_seeded_switches():
    # Django's transaction test flush removes migration seeds between cases.
    from apps.governance.flag_models import FEATURE_KEYS, FeatureFlag

    for key in FEATURE_KEYS:
        FeatureFlag.objects.get_or_create(
            key=key,
            defaults={"id": uuid5(NAMESPACE_URL, "fitlink:c02:flag:" + key)},
        )


def flags():
    assert importlib.util.find_spec("apps.governance.flags"), (
        "missing versioned feature flags"
    )
    return importlib.import_module("apps.governance.flags")


def referrals():
    assert importlib.util.find_spec("config.use_cases.referral"), (
        "missing referral composition"
    )
    return importlib.import_module("config.use_cases.referral")


def staff_for_flag(settings, flag):
    from apps.governance.staff import MockStepUpProvider, issue_mock_step_up
    from apps.governance.staff_models import StaffCapabilityGrant

    settings.ACCOUNT_SECURITY = replace(
        settings.ACCOUNT_SECURITY, step_up_provider="mock"
    )
    staff = owner("+989123456780")
    issuer = owner("+989123456781")
    now = timezone.now()
    StaffCapabilityGrant.objects.create(
        user=staff,
        capability="feature_flags",
        valid_from=now,
        valid_until=now + timedelta(hours=1),
        granted_by=issuer,
        reason_code="policy_approved",
    )
    provider = MockStepUpProvider()
    assertion = provider.prepare(staff.public_id, "feature_flags", flag.id, now)
    with transaction.atomic():
        step = issue_mock_step_up(
            staff,
            "feature_flags",
            flag.id,
            assertion.raw_assertion,
            issuer,
            now,
            provider,
        )
    actor, _ = actor_for(staff)
    return actor, step, timezone.now()


@pytest.mark.parametrize(
    "key", ["marketplace", "professional_registration", "ai_insights", "ai_mirror"]
)
def test_switches_are_disabled_and_change_independently(settings, key):
    from apps.governance.audit_models import AuditEvent
    from apps.governance.outbox_models import OutboxEvent

    module = flags()
    assert module.FeatureFlag.objects.count() == 4
    assert all(not module.feature_enabled(name) for name in module.FEATURE_KEYS)
    row = module.FeatureFlag.objects.get(key=key)
    actor, step, now = staff_for_flag(settings, row)
    module.set_feature(actor, key, True, 1, "policy_approved", step, now)
    assert {name for name in module.FEATURE_KEYS if module.feature_enabled(name)} == {
        key
    }
    assert (
        AuditEvent.objects.filter(
            action="feature_flag.changed", subject_uuid=row.id
        ).count()
        == 1
    )
    assert (
        OutboxEvent.objects.filter(
            event_type="feature_flag.changed", aggregate_uuid=row.id
        ).count()
        == 1
    )
    from apps.accounts.models import User

    assert User.objects.get(public_id=actor.user_uuid).state == "active"
    assert module.feature_enabled("unknown") is False


@pytest.mark.parametrize("superuser", [False, True])
def test_bare_staff_or_superuser_cannot_write(superuser):
    from django.core.exceptions import PermissionDenied

    module = flags()
    user = owner()
    user.is_staff = True
    user.is_superuser = superuser
    user.save(update_fields=["is_staff", "is_superuser"])
    actor, _ = actor_for(user)
    with pytest.raises(PermissionDenied):
        module.set_feature(
            actor, "marketplace", True, 1, "policy_approved", uuid4(), timezone.now()
        )
    assert not module.feature_enabled("marketplace")


def test_flag_version_race_has_one_winner(settings):
    from django.core.exceptions import PermissionDenied

    module = flags()
    row = module.FeatureFlag.objects.get(key="marketplace")
    actor, step, now = staff_for_flag(settings, row)
    barrier = Barrier(2)

    def edit():
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            module.set_feature(
                actor, "marketplace", True, 1, "policy_approved", step, now
            )
            return True
        except PermissionDenied:
            return False
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(lambda _: edit(), range(2))) == [False, True]
    row.refresh_from_db()
    assert row.version == 2


def test_db_failure_never_reuses_enabled_state(settings, monkeypatch):
    from django.db import DatabaseError

    module = flags()
    row = module.FeatureFlag.objects.get(key="ai_insights")
    actor, step, now = staff_for_flag(settings, row)
    module.set_feature(actor, row.key, True, 1, "policy_approved", step, now)
    assert module.feature_enabled(row.key)

    def fail(**kw):
        raise DatabaseError("unavailable")

    monkeypatch.setattr(module.FeatureFlag.objects, "get", fail)
    assert not module.feature_enabled(row.key)


def test_referral_entropy_digest_anonymous_descriptor_expiry_and_revocation():
    from apps.accounts.referral_models import InviteReferralLink
    from apps.governance.audit_models import AuditEvent

    module = referrals()
    user = owner()
    actor, _ = actor_for(user)
    now = timezone.now()
    tokens = [module.issue_referral(actor, now) for _ in range(2)]
    assert len(set(tokens)) == 2
    assert all(re.fullmatch(r"[A-Za-z0-9_-]{43}", token) for token in tokens)
    descriptor = module.resolve_referral(tokens[0], now)
    assert set(asdict(descriptor)) == {"link_uuid"}
    row = InviteReferralLink.objects.get(pk=descriptor.link_uuid)
    assert row.token_digest != tokens[0]
    assert len(row.token_digest) == 64
    assert module.resolve_referral(tokens[0], row.expires_at) is None
    module.revoke_referral(actor, row.id, now + timedelta(seconds=1))
    assert module.resolve_referral(tokens[0], now + timedelta(seconds=2)) is None
    assert all(token not in repr(list(AuditEvent.objects.values())) for token in tokens)


def test_landing_cleans_url_and_cookie_contains_only_signed_descriptor(client):
    from django.core import signing

    module = referrals()
    actor, _ = actor_for(owner())
    token = module.issue_referral(actor, timezone.now())
    response = client.get(f"/i/{token}/")
    assert response.status_code == 302
    assert response["Location"] == "/"
    assert response["Referrer-Policy"] == "no-referrer"
    assert response["Cache-Control"] == "no-store"
    cookie = response.cookies["fitlink_referral"]
    assert cookie["secure"] and cookie["httponly"] and cookie["samesite"] == "Strict"
    assert token not in cookie.value
    assert set(
        signing.loads(cookie.value, salt="fitlink.referral", max_age=2592000)
    ) == {"link"}
    invalid = client.get("/i/invalid/")
    assert invalid.status_code == 302 and invalid["Location"] == "/"


def test_first_attribution_is_idempotent_and_cannot_be_overwritten():
    from apps.accounts.referral_models import ReferralAttribution

    module = referrals()
    issuer = owner()
    other = owner("+989123456782")
    recipient = owner("+989123456783")
    actor, _ = actor_for(issuer)
    actor2, _ = actor_for(other)
    now = timezone.now()
    first = module.issue_referral(actor, now)
    second = module.issue_referral(actor2, now)
    assert module.bind_attribution(recipient, first, now) == module.bind_attribution(
        recipient, first, now
    )
    assert module.bind_attribution(recipient, second, now) == module.bind_attribution(
        recipient, first, now
    )
    assert (
        ReferralAttribution.objects.get(recipient=recipient).link.issuer_id == issuer.pk
    )


def test_first_attribution_race_preserves_exactly_one(settings):
    from apps.accounts.referral_models import ReferralAttribution

    module = referrals()
    issuers = [owner("+989123456780"), owner("+989123456781")]
    recipient = owner("+989123456782")
    now = timezone.now()
    tokens = [module.issue_referral(actor_for(user)[0], now) for user in issuers]
    barrier = Barrier(2)

    def bind(token):
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            return module.bind_attribution(recipient, token, now)
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(bind, tokens))
    assert results[0] == results[1]
    assert ReferralAttribution.objects.filter(recipient=recipient).count() == 1


@pytest.mark.parametrize("restricted", ["issuer", "recipient", "self", "adult"])
def test_restricted_or_self_attribution_denied(restricted):
    from apps.accounts.models import User
    from apps.accounts.referral_models import ReferralAttribution

    module = referrals()
    issuer = owner()
    recipient = owner("+989123456782")
    now = timezone.now()
    token = module.issue_referral(actor_for(issuer)[0], now)
    if restricted == "self":
        recipient = issuer
    elif restricted == "adult":
        User.objects.filter(pk=recipient.pk).update(
            birth_date=None, adult_attested_at=None, adult_attestation_version=""
        )
    else:
        User.objects.filter(
            pk=(issuer if restricted == "issuer" else recipient).pk
        ).update(state="suspended", is_active=False)
    with pytest.raises(PermissionError):
        module.bind_attribution(recipient, token, now)
    assert ReferralAttribution.objects.count() == 0


def test_restricted_issuer_cannot_issue():
    from apps.accounts.models import User

    module = referrals()
    user = owner()
    actor, _ = actor_for(user)
    User.objects.filter(pk=user.pk).update(state="suspended", is_active=False)
    with pytest.raises(PermissionError):
        module.issue_referral(actor, timezone.now())


def test_seed_migration_installs_exact_safe_defaults():
    import importlib

    from django.apps import apps
    from django.db import connection

    module = flags()
    module.FeatureFlag.objects.all().delete()
    migration = importlib.import_module(
        "apps.governance.migrations.0008_seed_feature_flags"
    )
    with connection.schema_editor() as editor:
        migration.seed_flags(apps, editor)
    assert set(module.FeatureFlag.objects.values_list("key", "enabled", "version")) == {
        (key, False, 1) for key in module.FEATURE_KEYS
    }


def test_wrong_flag_step_up_and_stale_actor_cannot_write(settings):
    from django.core.exceptions import PermissionDenied

    from apps.accounts.models import User

    module = flags()
    row = module.FeatureFlag.objects.get(key="marketplace")
    actor, step, now = staff_for_flag(settings, row)
    with pytest.raises(PermissionDenied):
        module.set_feature(actor, "ai_mirror", True, 1, "policy_approved", step, now)
    User.objects.filter(public_id=actor.user_uuid).update(auth_version=2)
    with pytest.raises(PermissionError):
        module.set_feature(actor, row.key, True, 1, "policy_approved", step, now)
    assert not module.feature_enabled(row.key)


def test_referral_audit_failure_rolls_back_creation_and_attribution(monkeypatch):
    from apps.accounts.referral_models import InviteReferralLink, ReferralAttribution

    module = referrals()
    issuer = owner()
    recipient = owner("+989123456782")
    actor, _ = actor_for(issuer)
    now = timezone.now()
    token = module.issue_referral(actor, now)

    def fail(*args, **kwargs):
        raise RuntimeError("audit unavailable")

    monkeypatch.setattr(module, "append_event", fail)
    with pytest.raises(RuntimeError):
        module.issue_referral(actor, now)
    assert InviteReferralLink.objects.count() == 1
    with pytest.raises(RuntimeError):
        module.bind_attribution(recipient, token, now)
    assert ReferralAttribution.objects.count() == 0


def test_cookie_binding_rechecks_revocation_and_denies_forgery(client):
    module = referrals()
    issuer = owner()
    recipient = owner("+989123456782")
    actor, _ = actor_for(issuer)
    now = timezone.now()
    token = module.issue_referral(actor, now)
    response = client.get(f"/i/{token}/")
    cookie = response.cookies["fitlink_referral"].value
    module.revoke_referral(actor, module.resolve_referral(token, now).link_uuid, now)
    assert module.bind_cookie(recipient, cookie, now) is None
    assert module.bind_cookie(recipient, cookie + "forged", now) is None
