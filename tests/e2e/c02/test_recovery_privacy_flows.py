import asyncio

import pytest
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
async def test_export_confirmation_delete_and_old_cookie_denial(
    page, live_server, auth_runtime, browser_errors, viewport
):
    await page.set_viewport_size(viewport)
    await verify(page, await entry(page, live_server.url, auth_runtime))
    old_session = next(
        c["value"] for c in await page.context.cookies() if c["name"] == "sessionid"
    )
    await page.get_by_role(
        "link", name="درخواست\u200cهای حریم خصوصی", exact=True
    ).click()
    await page.get_by_label("نوع درخواست").select_option("export")
    await page.get_by_role("button", name="ثبت درخواست", exact=True).click()
    assert not await database(
        lambda: apps.get_model("governance", "PrivacyRequest").objects.exists()
    )
    await page.get_by_label("این درخواست را صریحاً تأیید می\u200cکنم").check()
    await page.get_by_role("button", name="ثبت درخواست", exact=True).click()
    await expect(page.get_by_text("در انتظار اجرا", exact=True)).to_be_visible()
    await assets_and_layout(page, live_server.url)
    await page.get_by_label("نوع درخواست").select_option("delete")
    await page.get_by_label("این درخواست را صریحاً تأیید می\u200cکنم").check()
    await page.get_by_role("button", name="ثبت درخواست", exact=True).click()
    await expect(
        page.get_by_role("heading", name="ورود به فیت\u200cلینک", exact=True)
    ).to_be_visible()
    assert (
        await page.request.get(live_server.url + "/api/v1/account/me/")
    ).status == 403
    assert (
        await page.request.get(
            live_server.url + "/api/v1/account/me/",
            headers={"Cookie": f"sessionid={old_session}"},
        )
    ).status == 403
    user = await database(lambda: apps.get_model("accounts", "User").objects.get())
    assert user.state == "pending_deletion"
    assert not {"ErasureMarker", "ExportFile"} & {m.__name__ for m in apps.get_models()}


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_anonymous_recovery_receipt_and_new_phone_proof_do_not_login(
    page, live_server, auth_runtime, browser_errors, viewport
):
    await page.set_viewport_size(viewport)
    await page.goto(live_server.url + "/accounts/recovery/")
    await page.get_by_label("شمارهٔ پیشین").fill("09123456789")
    await page.get_by_label("شمارهٔ جدید").fill("09123456780")
    await page.get_by_role("button", name="ثبت درخواست بازیابی", exact=True).click()
    await expect(
        page.get_by_text("درخواست دریافت شده است.", exact=True)
    ).to_be_visible()
    await page.get_by_role("button", name="درخواست کد شمارهٔ جدید", exact=True).click()
    messages = auth_runtime.drain()
    assert len(messages) == 1
    await page.get_by_label("کد شش\u200cرقمی").fill(messages[0].code)
    await page.get_by_role("button", name="تأیید شمارهٔ جدید", exact=True).click()
    await expect(
        page.get_by_text(
            "مالکیت شمارهٔ جدید تأیید شد؛ بررسی مجاز کارکنان همچنان لازم است.",
            exact=True,
        )
    ).to_be_visible()
    assert (
        await page.request.get(live_server.url + "/api/v1/account/me/")
    ).status == 403
    cookies = await page.context.cookies()
    cookie = next(c for c in cookies if c["name"] == "fitlink_recovery_receipt")
    assert cookie["httpOnly"] and cookie["secure"] and (cookie["sameSite"] == "Strict")
    assert cookie["value"] not in await page.content()
    await assets_and_layout(page, live_server.url)


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_dual_phone_change_proofs_and_session_invalidation(
    page, live_server, auth_runtime, browser_errors, viewport
):
    await page.set_viewport_size(viewport)
    await verify(page, await entry(page, live_server.url, auth_runtime))
    old_session = next(
        c["value"] for c in await page.context.cookies() if c["name"] == "sessionid"
    )
    await page.get_by_role("link", name="تغییر شمارهٔ همراه", exact=True).click()
    await page.get_by_label("شمارهٔ جدید").fill("09123456780")
    await page.get_by_role("button", name="شروع تغییر شماره", exact=True).click()
    # The old phone just received its login OTP. Respect the same durable
    # cross-purpose cooldown; do not reset quota rows or weaken server policy.
    deadline = (
        await database(
            lambda: apps.get_model("accounts", "OTPPhoneState").objects.get(
                phone="+989123456789"
            )
        )
    ).next_send_at
    wait = max(0, (deadline - timezone.now()).total_seconds())
    assert wait <= 60
    await asyncio.sleep(wait + 0.1)
    for kind, label in (("old", "پیشین"), ("new", "جدید")):
        await page.get_by_role(
            "button", name=f"درخواست کد شمارهٔ {label}", exact=True
        ).click()
        messages = auth_runtime.drain()
        assert len(messages) == 1
        await (
            page.locator(f"form[data-proof='{kind}']")
            .get_by_label("کد شش\u200cرقمی")
            .fill(messages[0].code)
        )
        await page.get_by_role(
            "button", name=f"تأیید شمارهٔ {label}", exact=True
        ).click()
    await page.get_by_role("button", name="اعمال تغییر و خروج", exact=True).click()
    await expect(
        page.get_by_role("heading", name="ورود به فیت\u200cلینک", exact=True)
    ).to_be_visible()
    assert (
        await database(lambda: apps.get_model("accounts", "User").objects.get())
    ).phone == "+989123456780"
    assert (
        await page.request.get(live_server.url + "/api/v1/account/me/")
    ).status == 403
    assert (
        await page.request.get(
            live_server.url + "/api/v1/account/me/",
            headers={"Cookie": f"sessionid={old_session}"},
        )
    ).status == 403
