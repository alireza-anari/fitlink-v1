from datetime import timedelta

import pytest
from conftest import adult_user
from django.apps import apps
from django.utils import timezone
from helpers import VIEWPORTS, assets_and_layout, database, entry, verify
from playwright.async_api import expect

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.asyncio,
    pytest.mark.django_db(transaction=True),
]


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_entry_preferences_logout_and_no_browser_credentials(
    page, live_server, auth_runtime, browser_errors, viewport
):
    await page.set_viewport_size(viewport)
    base = live_server.url
    code = await entry(page, base, auth_runtime)
    await verify(page, code)
    await expect(page.get_by_text("+98912*****89", exact=True)).to_be_visible()
    await assets_and_layout(page, base)
    await page.get_by_label("زبان").select_option("en")
    await page.get_by_label("منطقهٔ زمانی").fill("UTC")
    await page.get_by_role("button", name="ذخیرهٔ ترجیحات").click()
    await expect(page.get_by_text("ترجیحات ذخیره شد.", exact=True)).to_be_visible()
    row = await database(lambda: apps.get_model("accounts", "User").objects.get())
    assert row.locale == "en" and row.timezone == "UTC" and (not row.is_staff)
    # C03 installs optional metadata; account entry/preferences must not create it.
    for label, name in (
        ("athletes", "AthleteProfile"),
        ("professionals", "ProfessionalProfile"),
    ):
        assert not await database(
            lambda label=label, name=name: apps.get_model(label, name).objects.exists()
        )
    await page.get_by_role("button", name="خروج از این نشست", exact=True).click()
    await expect(
        page.get_by_role("heading", name="ورود به فیت\u200cلینک", exact=True)
    ).to_be_visible()
    assert (await page.request.get(base + "/api/v1/account/me/")).status == 403


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_under18_stops_before_sms_or_identity(
    page, live_server, auth_runtime, browser_errors, viewport
):
    await page.set_viewport_size(viewport)
    await page.goto(live_server.url + "/accounts/entry/")
    await page.get_by_label("شمارهٔ همراه").fill("09123456789")
    await page.get_by_label("تقویم تاریخ تولد").select_option("gregorian")
    await page.get_by_role("textbox", name="تاریخ تولد").fill("2020-01-01")
    await page.get_by_label("اعلام می\u200cکنم حداقل ۱۸ سال دارم").check()
    await page.get_by_role("button", name="درخواست کد ورود", exact=True).click()
    await expect(page.get_by_role("alert")).to_be_visible()
    assert auth_runtime.drain() == ()
    assert not await database(
        lambda: apps.get_model("accounts", "User").objects.exists()
    )
    assert not await database(
        lambda: apps.get_model("accounts", "OTPChallenge").objects.exists()
    )
    assert (
        await page.request.get(live_server.url + "/api/v1/account/me/")
    ).status == 403
    await assets_and_layout(page, live_server.url)


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_expired_code_and_resend_are_server_rejected(
    page, live_server, auth_runtime, browser_errors, viewport
):
    await page.set_viewport_size(viewport)
    code = await entry(page, live_server.url, auth_runtime, calendar="gregorian")
    await page.locator("button[data-resend]").evaluate(
        "button => { button.disabled = false; button.dataset.remaining = '0'; "
        "button.click(); }"
    )
    await page.wait_for_load_state("networkidle")
    await expect(page.get_by_role("alert")).to_contain_text("لطفاً")
    assert auth_runtime.drain() == ()
    at = timezone.now()
    await database(
        lambda: apps.get_model("accounts", "OTPChallenge").objects.update(
            issued_at=at - timedelta(seconds=301), expires_at=at - timedelta(seconds=1)
        )
    )
    await page.get_by_label("کد شش\u200cرقمی").fill(code)
    await page.get_by_role("button", name="تأیید و ورود", exact=True).click()
    await expect(page.get_by_role("alert")).to_contain_text("کد معتبر نیست")
    assert not await database(
        lambda: apps.get_model("accounts", "User").objects.exists()
    )
    assert (
        await page.request.get(live_server.url + "/api/v1/account/me/")
    ).status == 403


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_native_form_without_javascript(
    browser, live_server, auth_runtime, viewport
):
    context = await browser.new_context(java_script_enabled=False, viewport=viewport)
    page = await context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on(
        "console",
        lambda message: (
            errors.append(message.text) if message.type == "error" else None
        ),
    )
    try:
        code = await entry(page, live_server.url, auth_runtime, calendar="gregorian")
        await verify(page, code)
        await assets_and_layout(page, live_server.url, enhanced=False)
        assert errors == []
    finally:
        await context.close()


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_csrf_reload_rotation_and_old_token_denial(
    page, live_server, auth_runtime, browser_errors, viewport
):
    await page.set_viewport_size(viewport)
    code = await entry(page, live_server.url, auth_runtime)
    old = next(
        c["value"] for c in await page.context.cookies() if c["name"] == "csrftoken"
    )
    await page.reload(wait_until="networkidle")
    await verify(page, code)
    new = next(
        c["value"] for c in await page.context.cookies() if c["name"] == "csrftoken"
    )
    assert old != new
    response = await page.request.post(
        live_server.url + "/accounts/me/",
        form={"action": "preferences", "locale": "en", "timezone": "UTC"},
        headers={"X-CSRFToken": old},
    )
    assert response.status == 403
    assert (
        await database(lambda: apps.get_model("accounts", "User").objects.get())
    ).locale == "fa"
    await page.get_by_label("زبان").select_option("en")
    await page.get_by_role("button", name="ذخیرهٔ ترجیحات").click()
    await expect(page.get_by_text("ترجیحات ذخیره شد.", exact=True)).to_be_visible()


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_existing_and_unknown_wrong_code_copy_is_uniform(
    page, live_server, auth_runtime, browser_errors, viewport
):
    await page.set_viewport_size(viewport)
    await database(lambda: adult_user("+989123456789"))
    copies = []
    for phone in ("09123456789", "09123456781"):
        await page.context.clear_cookies()
        code = await entry(page, live_server.url, auth_runtime, phone=phone)
        wrong = str((int(code) + 1) % 1000000).zfill(6)
        await page.get_by_label("کد شش\u200cرقمی").fill(wrong)
        await page.get_by_role("button", name="تأیید و ورود", exact=True).click()
        await expect(page.get_by_role("alert")).to_contain_text("کد معتبر نیست")
        copies.append(await page.get_by_role("alert").inner_text())
        assert (
            await page.request.get(live_server.url + "/api/v1/account/me/")
        ).status == 403
    assert copies[0] == copies[1]
    assert (
        await database(lambda: apps.get_model("accounts", "User").objects.count()) == 1
    )


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_restricted_account_has_only_current_control_flows(
    page, live_server, auth_runtime, browser_errors, viewport
):
    await page.set_viewport_size(viewport)
    await database(lambda: adult_user("+989123456789", state="restricted"))
    await verify(page, await entry(page, live_server.url, auth_runtime))
    await expect(
        page.get_by_text(
            "دسترسی این حساب به کنترل\u200cهای حساب و حریم خصوصی محدود شده است."
        )
    ).to_be_visible()
    assert (
        await page.get_by_role("link", name="تغییر شمارهٔ همراه", exact=True).count()
        == 0
    )
    assert (
        await page.request.get(live_server.url + "/accounts/phone-change/")
    ).url.endswith("/accounts/entry/")
    await page.get_by_label("منطقهٔ زمانی").fill("UTC")
    await page.get_by_role("button", name="ذخیرهٔ ترجیحات").click()
    await expect(page.get_by_text("ترجیحات ذخیره شد.", exact=True)).to_be_visible()
    await page.get_by_role(
        "link", name="درخواست\u200cهای حریم خصوصی", exact=True
    ).click()
    await expect(
        page.get_by_role("heading", name="درخواست\u200cهای حریم خصوصی", exact=True)
    ).to_be_visible()


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_suspension_invalidates_existing_browser_control(
    page, live_server, auth_runtime, browser_errors, viewport
):
    await page.set_viewport_size(viewport)
    await verify(page, await entry(page, live_server.url, auth_runtime))
    await database(
        lambda: apps.get_model("accounts", "User").objects.update(
            state="suspended", is_active=False
        )
    )
    await page.reload(wait_until="networkidle")
    await expect(
        page.get_by_role("heading", name="ورود به فیت\u200cلینک", exact=True)
    ).to_be_visible()
    assert (
        await page.request.get(live_server.url + "/api/v1/account/me/")
    ).status == 403
