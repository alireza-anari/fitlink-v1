import os
from dataclasses import replace
from datetime import date, timedelta
from types import SimpleNamespace

import pytest
import pytest_asyncio
from django.db import connection
from playwright.async_api import async_playwright


@pytest_asyncio.fixture
async def browser(auth_runtime, live_server):
    # Function-scoped async Playwright never installs a synchronous driver loop
    # around Django database setup/fixture teardown.
    async with async_playwright() as driver:
        browser = await driver.chromium.launch()
        yield browser
        await browser.close()


@pytest_asyncio.fixture
async def page(browser):
    context = await browser.new_context()
    page = await context.new_page()
    yield page
    await context.close()


@pytest.fixture
def auth_runtime(settings, monkeypatch, transactional_db, request):
    from apps.accounts import limiter
    from apps.accounts.sms import MockSmsProvider
    from config.use_cases import identity, recovery

    assert connection.vendor == "postgresql"
    assert not os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE")
    settings.ACCOUNT_SECURITY = replace(
        settings.ACCOUNT_SECURITY,
        entry_enabled=True,
        staff_recovery_enabled=True,
        step_up_provider="mock",
    )
    # Plaintext fixture codes stay in process memory and transient browser input.
    assert request.config.getoption("tracing") == "off"
    assert request.config.getoption("screenshot") == "off"
    assert request.config.getoption("video") == "off"
    redis = limiter.redis_client()
    assert redis.connection_pool.connection_kwargs["db"] == 4
    redis.flushdb()
    provider = MockSmsProvider()
    monkeypatch.setattr(identity, "configured_provider", lambda: provider)
    monkeypatch.setattr(recovery, "configured_provider", lambda: provider)
    yield provider
    provider.drain()
    redis.flushdb()


@pytest_asyncio.fixture
async def browser_errors(page):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on(
        "console",
        lambda message: (
            errors.append(message.text) if message.type == "error" else None
        ),
    )
    yield errors
    assert errors == []


def adult_user(phone, **kwargs):
    from django.utils import timezone

    from apps.accounts.models import User

    return User.objects.create_user(
        phone,
        birth_date=date(1990, 1, 1),
        adult_attested_at=timezone.now(),
        adult_attestation_version="adult-v1",
        **kwargs,
    )


@pytest.fixture
def staff_case(auth_runtime):
    from django.contrib.auth.models import AnonymousUser
    from django.contrib.sessions.backends.db import SessionStore
    from django.db import transaction
    from django.test import RequestFactory
    from django.utils import timezone

    from apps.accounts.recovery_models import RecoveryRequest
    from apps.accounts.sessions import issue_session, resolve_session
    from apps.governance.staff import MockStepUpProvider, issue_mock_step_up
    from apps.governance.staff_models import StaffCapabilityGrant
    from config.use_cases import identity, recovery

    target = adult_user("+989123456789")
    staff = adult_user("+989123456788")
    issuer = adult_user("+989123456787")
    now = timezone.now()
    receipt = recovery.open_recovery(target.phone, "+989123456780", "127.0.0.1", now)
    grant = StaffCapabilityGrant.objects.create(
        user=staff,
        capability="account_recovery",
        valid_from=now - timedelta(seconds=1),
        valid_until=now + timedelta(hours=1),
        granted_by=issuer,
        reason_code="staff_assigned",
    )
    request = RequestFactory().get("/accounts/me/")
    request.session, request.user = SessionStore(), AnonymousUser()
    provider = MockStepUpProvider()
    assertion = provider.prepare(
        staff.public_id, "account_recovery", receipt.request_uuid, now
    )
    with transaction.atomic():
        issue_session(request, staff, "normal", now, identity.record_security_outcome)
        step = issue_mock_step_up(
            staff,
            "account_recovery",
            receipt.request_uuid,
            assertion.raw_assertion,
            issuer,
            now,
            provider,
        )
    actor = resolve_session(request, now)
    case = RecoveryRequest.objects.get(pk=receipt.request_uuid)
    recovery.assign_recovery(
        actor, case.id, case.version, staff.public_id, step, "staff_assigned", now
    )
    case.refresh_from_db()
    # Assignment/resolution remain trusted existing domain operations, not a
    # newly invented staff directory or account lookup HTML surface.
    recovery.resolve_recovery(
        actor, case.id, case.version, step, "identity_verified", now
    )
    case.refresh_from_db()
    return SimpleNamespace(
        target=target,
        staff=staff,
        issuer=issuer,
        grant=grant,
        step=step,
        case=case,
        receipt=receipt,
    )
