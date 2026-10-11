"""Actual Persian staff navigation at both viewports with memory-only authority."""

from datetime import timedelta
from uuid import uuid4

import pytest
from django.utils import timezone
from playwright.async_api import expect

from tests.e2e.c02.helpers import VIEWPORTS, assets_and_layout, database, entry, verify
from tests.integration.c03.test_verification_decisions import review

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.asyncio,
    pytest.mark.django_db(transaction=True),
]


@pytest.fixture
def staff_review(settings, auth_runtime):
    return review(settings)


async def open_case(page, live_server, auth_runtime, s, viewport):
    await page.set_viewport_size(viewport)
    await verify(
        page, await entry(page, live_server.url, auth_runtime, phone="09123456781")
    )
    response = await page.goto(
        live_server.url + f"/staff/professional-verification/{s.case.id}/"
    )
    assert response.status == 200
    await page.get_by_label("شناسهٔ احراز تازه").fill(str(s.staff.step))
    await page.get_by_role("button", name="باز کردن پرونده", exact=True).click()
    await expect(
        page.get_by_role("heading", name="بررسی خصوصی پرونده", exact=True)
    ).to_be_visible()
    assert "?" not in page.url
    assert str(s.staff.step) not in page.url


def target(page, kind):
    return page.locator(f'[data-target="{kind}"]')


async def decide(page, kind, value="approve"):
    area = target(page, kind)
    await area.get_by_label("تصمیم").select_option(value)
    await area.get_by_label("توضیح خصوصی تصمیم").fill("بررسی آزمایشی مدارک")
    await area.get_by_role("button", name="ثبت تصمیم", exact=True).click()


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_assigned_staff_approve_reject_resubmit_revoke(
    page, live_server, auth_runtime, staff_review, browser_errors, viewport
):
    s = staff_review
    await open_case(page, live_server, auth_runtime, s, viewport)
    await decide(page, "identity")
    await decide(page, "coach")
    await decide(page, "nutritionist", "reject")
    await target(page, "coach").get_by_label("توضیح خصوصی ابطال").fill("ابطال آزمایشی")
    await (
        target(page, "coach")
        .get_by_role("button", name="ابطال تأیید مشخص", exact=True)
        .click()
    )
    from tests.integration.c03.test_verification_decisions import mutate_evidence
    from tests.integration.c03.verification_helpers import assign, command

    def resubmit():
        mutate_evidence(s, "nutritionist")
        s.profile.refresh_from_db()
        new = command(
            "prepare_verification",
            s.actor,
            ("nutritionist",),
            s.profile.version,
            uuid4(),
            timezone.now(),
        )
        s.case = command(
            "submit_verification", s.actor, new.id, new.version, uuid4(), timezone.now()
        )
        from django.db import transaction

        from apps.governance.staff import MockStepUpProvider, issue_mock_step_up

        provider = MockStepUpProvider()
        at = timezone.now()
        assertion = provider.prepare(
            s.staff.user.public_id, "professional_verification", s.case.id, at
        )
        with transaction.atomic():
            s.staff.step = issue_mock_step_up(
                s.staff.user,
                "professional_verification",
                s.case.id,
                assertion.raw_assertion,
                s.staff.grant.granted_by,
                at,
                provider,
            )
        s.case = assign(s, s.staff)
        return s.case.id, s.staff.step

    identifier, step = await database(resubmit)
    await page.goto(live_server.url + f"/staff/professional-verification/{identifier}/")
    await page.get_by_label("شناسهٔ احراز تازه").fill(str(step))
    await page.get_by_role("button", name="باز کردن پرونده", exact=True).click()
    await page.get_by_role("button", name="شروع بررسی", exact=True).click()
    await decide(page, "nutritionist")
    await expect(
        target(page, "nutritionist").get_by_text("تأیید شده", exact=True)
    ).to_be_visible()


@pytest.mark.parametrize("viewport", VIEWPORTS)
@pytest.mark.parametrize(
    "fault",
    ["capability", "assignment", "expired_stepup", "crosscase", "self", "superuser"],
)
async def test_deny_capability_assignment_expired_stepup_crosscase_self_superuser(
    page, live_server, auth_runtime, staff_review, viewport, fault
):
    from apps.governance.staff_models import StaffStepUpGrant
    from apps.professionals.models import VerificationAssignment

    s = staff_review
    await page.set_viewport_size(viewport)
    phone = "09123456780" if fault == "self" else "09123456781"
    await verify(page, await entry(page, live_server.url, auth_runtime, phone=phone))

    def invalidate():
        if fault in {"capability", "superuser"}:
            s.staff.grant.revoked_at = timezone.now()
            s.staff.grant.save(update_fields=["revoked_at"])
            if fault == "superuser":
                s.staff.user.is_superuser = True
                s.staff.user.is_staff = True
                s.staff.user.save(update_fields=["is_superuser", "is_staff"])
        elif fault == "assignment":
            VerificationAssignment.objects.filter(verification_id=s.case.id).update(
                ended_at=timezone.now()
            )
        elif fault == "crosscase":
            StaffStepUpGrant.objects.filter(pk=s.staff.step).update(case_uuid=uuid4())
        elif fault == "expired_stepup":
            StaffStepUpGrant.objects.filter(pk=s.staff.step).update(
                verified_at=timezone.now() - timedelta(minutes=10),
                expires_at=timezone.now() - timedelta(seconds=1),
            )

    await database(invalidate)
    await page.goto(live_server.url + f"/staff/professional-verification/{s.case.id}/")
    await page.get_by_label("شناسهٔ احراز تازه").fill(str(s.staff.step))
    async with page.expect_response(lambda r: r.request.method == "POST") as response:
        await page.get_by_role("button", name="باز کردن پرونده", exact=True).click()
    assert (await response.value).status == 403
    assert s.user.phone not in await page.content()


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_decision_reload_single_effect(
    page, live_server, auth_runtime, staff_review, browser_errors, viewport
):
    from apps.professionals.models import VerificationDecision

    await open_case(page, live_server, auth_runtime, staff_review, viewport)
    await decide(page, "coach")
    await page.reload()
    await page.reload()
    assert (
        await database(
            lambda: VerificationDecision.objects.filter(
                profile=staff_review.profile, target_kind="coach"
            ).count()
        )
        == 1
    )
    await assets_and_layout(page, live_server.url)


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_mixed_role_outcomes_no_whole_profile_rejection(
    page, live_server, auth_runtime, staff_review, browser_errors, viewport
):
    await open_case(page, live_server, auth_runtime, staff_review, viewport)
    await decide(page, "coach")
    await decide(page, "nutritionist", "reject")
    await expect(
        target(page, "coach").get_by_text("تأیید شده", exact=True)
    ).to_be_visible()
    await expect(
        target(page, "nutritionist").get_by_text("تأیید نشده", exact=True)
    ).to_be_visible()
    assert await page.evaluate("localStorage.length + sessionStorage.length") == 0
    assert await page.evaluate("caches.keys().then(v=>v.length)") == 0
    assert await page.evaluate("indexedDB.databases().then(v=>v.length)") == 0


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_restrict_release_reuses_approval_and_cannot_undo_revoke(
    page, live_server, auth_runtime, staff_review, browser_errors, viewport
):
    from apps.professionals.models import VerificationDecision

    await open_case(page, live_server, auth_runtime, staff_review, viewport)
    await decide(page, "coach")
    for label in ("محدود کردن موقت نقش", "رفع محدودیت مشخص"):
        await (
            target(page, "coach").get_by_role("button", name=label, exact=True).click()
        )
        await expect(
            target(page, "coach").get_by_text(
                "محدودیت موقت فعال است."
                if label == "محدود کردن موقت نقش"
                else "محدودیت موقت فعال نیست.",
                exact=True,
            )
        ).to_be_visible()
    assert (
        await database(
            lambda: VerificationDecision.objects.filter(
                target_kind="coach", decision="approve"
            ).count()
        )
        == 1
    )
    await (
        target(page, "coach")
        .get_by_role("button", name="محدود کردن موقت نقش", exact=True)
        .click()
    )
    await target(page, "coach").get_by_label("توضیح خصوصی ابطال").fill("ابطال آزمایشی")
    await (
        target(page, "coach")
        .get_by_role("button", name="ابطال تأیید مشخص", exact=True)
        .click()
    )
    await (
        target(page, "coach")
        .get_by_role("button", name="رفع محدودیت مشخص", exact=True)
        .click()
    )
    assert (
        await target(page, "coach")
        .get_by_role("button", name="ابطال تأیید مشخص", exact=True)
        .count()
        == 0
    )


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_stale_target_or_restriction_binding_denied(
    page, live_server, auth_runtime, staff_review, viewport
):
    from tests.integration.c03.test_verification_revocation import restrict

    await open_case(page, live_server, auth_runtime, staff_review, viewport)
    await database(lambda: restrict(staff_review, "coach"))
    area = target(page, "coach")
    await area.get_by_label("توضیح خصوصی تصمیم").fill("درخواست کهنه")
    async with page.expect_response(lambda r: r.request.method == "POST") as response:
        await area.get_by_role("button", name="ثبت تصمیم", exact=True).click()
    assert (await response.value).status == 409


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_evidence_read_audited_and_no_source_url(
    page, live_server, auth_runtime, staff_review, browser_errors, viewport
):
    from hashlib import sha256
    from io import BytesIO

    from PIL import Image

    from apps.assets.storage import get_private_store
    from apps.governance.audit_models import AuditEvent

    s = staff_review

    def seed():
        output = BytesIO()
        Image.new("RGB", (12, 12), "white").save(output, format="PNG")
        content = output.getvalue()
        asset = s.assets["coach"][0]
        derivative = asset.derivatives.get()
        derivative.sha256 = sha256(content).hexdigest()
        derivative.save(update_fields=["sha256"])
        get_private_store().put(derivative.key, content, "image/png")
        return asset.id

    identifier = await database(seed)
    await open_case(page, live_server, auth_runtime, s, viewport)
    count = await database(
        lambda: AuditEvent.objects.filter(
            action="asset.read", subject_uuid=identifier
        ).count()
    )
    response = await page.request.get(
        live_server.url
        + f"/api/v1/staff/professional-verification/{s.case.id}/evidence/{identifier}/"
    )
    assert response.status == 200 and "no-store" in response.headers["cache-control"]
    assert response.headers["x-content-type-options"] == "nosniff"
    assert (
        await database(
            lambda: AuditEvent.objects.filter(
                action="asset.read", subject_uuid=identifier
            ).count()
        )
        == count + 1
    )
    body = await page.content()
    assert (
        "source/" not in body and "derivative/" not in body and "signed_url" not in body
    )


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_public_search_and_profile_paths_absent(
    page, live_server, auth_runtime, staff_review, viewport
):
    await open_case(page, live_server, auth_runtime, staff_review, viewport)
    await decide(page, "identity")
    await decide(page, "coach")
    for path in (
        "/marketplace/",
        "/search/",
        "/professionals/example/",
        "/api/v1/professionals/",
        "/sitemap.xml",
    ):
        assert (await page.request.get(live_server.url + path)).status == 404


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_case_revoked_between_post_and_get_denied(
    page, live_server, auth_runtime, staff_review, viewport
):
    from apps.professionals.models import VerificationAssignment

    s = staff_review
    await open_case(page, live_server, auth_runtime, s, viewport)

    async def invalidate_redirect(route):
        await database(
            lambda: VerificationAssignment.objects.filter(
                verification_id=s.case.id, ended_at__isnull=True
            ).update(ended_at=timezone.now())
        )
        await route.continue_()

    await page.route(
        "**/staff/professional-verification/*/",
        lambda route: (
            invalidate_redirect(route)
            if route.request.method == "GET"
            else route.continue_()
        ),
    )
    await decide(page, "coach")
    await expect(page.get_by_text("دسترسی مجاز نیست.", exact=True)).to_be_visible()
