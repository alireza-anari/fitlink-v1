import pytest
from playwright.async_api import expect

from tests.e2e.c03.helpers import VIEWPORTS, baseline_core, database, login, quality

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.asyncio,
    pytest.mark.django_db(transaction=True),
]


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_owner_dual_context_resume_optional_consent(
    page, live_server, auth_runtime, browser_errors, viewport
):
    await page.set_viewport_size(viewport)
    base = live_server.url
    await login(page, base, auth_runtime)
    await baseline_core(page, base)
    from apps.athletes.baseline_models import BaselineAssessment

    baseline = await database(lambda: BaselineAssessment.objects.get())
    assert baseline.height_cm is None and baseline.weight_kg is None
    await page.get_by_role("button", name="ایجاد اصلاحیهٔ ارزیابی", exact=True).click()
    correction_url = page.url.split("?")[0]
    await page.get_by_label(
        "با نگهداری خصوصی داده‌های اختیاری این ارزیابی برای خودم موافقم."
    ).check()
    await page.get_by_role("button", name="تأیید نگهداری خصوصی", exact=True).click()
    await page.goto(correction_url + "?step=basics")
    await page.get_by_label("قد (سانتی‌متر)", exact=True).fill("۱۷۰.۰")
    await page.get_by_role("button", name="ذخیرهٔ مرحله", exact=True).click()
    correction = await database(
        lambda: BaselineAssessment.objects.exclude(pk=baseline.id).get()
    )
    assert str(correction.height_cm) == "170.0" and correction.parent_id == baseline.id
    await page.get_by_role("button", name="پس‌گرفتن اجازهٔ نگهداری", exact=True).click()
    await expect(page.get_by_label("قد (سانتی‌متر)", exact=True)).to_have_value("")
    from apps.governance.flag_models import FeatureFlag

    await database(
        lambda: FeatureFlag.objects.update_or_create(
            key="professional_registration", defaults={"enabled": True}
        )
    )
    await page.goto(base + "/professional/setup/")
    await page.get_by_role("button", name="ایجاد نمایهٔ حرفه‌ای", exact=True).click()
    await page.get_by_label("نام نمایشی").fill("نام حرفه‌ای")
    await page.get_by_label("نام هویتی خصوصی").fill("نام خصوصی")
    await page.get_by_label("نقش‌های اعلام‌شده").select_option("coach")
    await page.get_by_role("button", name="ذخیرهٔ مرحله", exact=True).click()
    response = await page.reload()
    await quality(page, response)
    await expect(page.get_by_label("نام نمایشی")).to_have_value("نام حرفه‌ای")
    response = await page.goto(base + "/professional/preview/")
    await quality(page, response)
    assert response.headers["x-robots-tag"] == "noindex, nofollow"
    await expect(
        page.get_by_role("heading", name="پیش‌نمایش خصوصی", exact=True)
    ).to_be_visible()
    assert await page.get_by_text("نام خصوصی", exact=True).count() == 0
    response = await page.goto(base + f"/athlete/baseline/{baseline.id}/")
    await quality(page, response)
    assert await page.get_by_text("نام حرفه‌ای", exact=True).count() == 0


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_js_disabled_setup(browser, live_server, auth_runtime, viewport):
    context = await browser.new_context(java_script_enabled=False, viewport=viewport)
    page = await context.new_page()
    page.set_default_timeout(5000)
    page.set_default_navigation_timeout(15000)
    errors = []
    page.on("pageerror", lambda error: errors.append(type(error).__name__))
    page.on(
        "console",
        lambda message: (
            errors.append(message.type) if message.type == "error" else None
        ),
    )
    try:
        await login(page, live_server.url, auth_runtime)
        await baseline_core(page, live_server.url)
        await quality(page, await page.reload())
        assert errors == []
    finally:
        await context.close()


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_logout_or_switch_account_denied(
    page, live_server, auth_runtime, browser_errors, viewport
):
    await page.set_viewport_size(viewport)
    base = live_server.url
    await login(page, base, auth_runtime)
    await baseline_core(page, base)
    private_url = page.url
    await page.goto(base + "/accounts/me/")
    await page.get_by_role(
        "button", name="خروج من این نشست", exact=True
    ).count()  # no mutation from stale UI
    await page.get_by_role("button", name="خروج از این نشست", exact=True).click()
    assert (
        await page.request.get(base + "/api/v1/professional/preview/")
    ).status == 403
    response = await page.goto(private_url)
    assert response.url.endswith("/accounts/entry/")
    from tests.e2e.c02.helpers import entry, verify

    await verify(page, await entry(page, base, auth_runtime, phone="۰۹۱۲۳۴۵۶۷۸۰"))
    # Request API denial without creating an expected-error browser console event.
    old_identifier = private_url.split("/baseline/")[1].split("/")[0]
    foreign = await page.request.get(
        base + f"/api/v1/athlete/baseline/{old_identifier}/"
    )
    missing = await page.request.get(
        base + f"/api/v1/athlete/baseline/{__import__('uuid').uuid4()}/"
    )
    assert (
        foreign.status == missing.status == 404
        and await foreign.body() == await missing.body()
    )


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_private_data_not_browser_cached(
    page, live_server, auth_runtime, browser_errors, viewport
):
    await page.set_viewport_size(viewport)
    await login(page, live_server.url, auth_runtime)
    await baseline_core(page, live_server.url)
    await quality(page, await page.reload())
    response = await page.request.post(
        live_server.url + "/api/v1/athlete/profile/",
        data={"operation_id": str(__import__("uuid").uuid4())},
    )
    assert response.status == 403 and "no-store" in response.headers["cache-control"]
