import pytest
from django.apps import apps
from helpers import VIEWPORTS, assets_and_layout, entry, verify
from playwright.sync_api import expect

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_export_confirmation_delete_and_old_cookie_denial(
    page, live_server, auth_runtime, browser_errors, viewport
):
    page.set_viewport_size(viewport)
    verify(page, entry(page, live_server.url, auth_runtime))
    old_session = next(
        c["value"] for c in page.context.cookies() if c["name"] == "sessionid"
    )
    page.get_by_role("link", name="درخواست‌های حریم خصوصی", exact=True).click()
    page.get_by_label("نوع درخواست").select_option("export")
    page.get_by_role("button", name="ثبت درخواست", exact=True).click()
    assert not apps.get_model("governance", "PrivacyRequest").objects.exists()
    page.get_by_label("این درخواست را صریحاً تأیید می‌کنم").check()
    page.get_by_role("button", name="ثبت درخواست", exact=True).click()
    expect(page.get_by_text("در انتظار اجرا", exact=True)).to_be_visible()
    assets_and_layout(page, live_server.url)
    page.get_by_label("نوع درخواست").select_option("delete")
    page.get_by_label("این درخواست را صریحاً تأیید می‌کنم").check()
    page.get_by_role("button", name="ثبت درخواست", exact=True).click()
    expect(
        page.get_by_role("heading", name="ورود به فیت‌لینک", exact=True)
    ).to_be_visible()
    assert page.request.get(live_server.url + "/api/v1/account/me/").status == 403
    assert (
        page.request.get(
            live_server.url + "/api/v1/account/me/",
            headers={"Cookie": f"sessionid={old_session}"},
        ).status
        == 403
    )
    user = apps.get_model("accounts", "User").objects.get()
    assert user.state == "pending_deletion"
    assert not {"ErasureMarker", "ExportFile"} & {m.__name__ for m in apps.get_models()}


@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_anonymous_recovery_receipt_and_new_phone_proof_do_not_login(
    page, live_server, auth_runtime, browser_errors, viewport
):
    page.set_viewport_size(viewport)
    page.goto(live_server.url + "/accounts/recovery/")
    page.get_by_label("شمارهٔ پیشین").fill("09123456789")
    page.get_by_label("شمارهٔ جدید").fill("09123456780")
    page.get_by_role("button", name="ثبت درخواست بازیابی", exact=True).click()
    expect(page.get_by_text("درخواست دریافت شده است.", exact=True)).to_be_visible()
    page.get_by_role("button", name="درخواست کد شمارهٔ جدید", exact=True).click()
    messages = auth_runtime.drain()
    assert len(messages) == 1
    page.get_by_label("کد شش‌رقمی").fill(messages[0].code)
    page.get_by_role("button", name="تأیید شمارهٔ جدید", exact=True).click()
    expect(
        page.get_by_text(
            "مالکیت شمارهٔ جدید تأیید شد؛ بررسی مجاز کارکنان همچنان لازم است.",
            exact=True,
        )
    ).to_be_visible()
    assert page.request.get(live_server.url + "/api/v1/account/me/").status == 403
    cookies = page.context.cookies()
    cookie = next(c for c in cookies if c["name"] == "fitlink_recovery_receipt")
    assert cookie["httpOnly"] and cookie["secure"] and cookie["sameSite"] == "Strict"
    assert cookie["value"] not in page.content()
    assets_and_layout(page, live_server.url)


@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_dual_phone_change_proofs_and_session_invalidation(
    page, live_server, auth_runtime, browser_errors, viewport
):
    page.set_viewport_size(viewport)
    verify(page, entry(page, live_server.url, auth_runtime))
    old_session = next(
        c["value"] for c in page.context.cookies() if c["name"] == "sessionid"
    )
    page.get_by_role("link", name="تغییر شمارهٔ همراه", exact=True).click()
    page.get_by_label("شمارهٔ جدید").fill("09123456780")
    page.get_by_role("button", name="شروع تغییر شماره", exact=True).click()
    for kind, label in (("old", "پیشین"), ("new", "جدید")):
        page.get_by_role("button", name=f"درخواست کد شمارهٔ {label}", exact=True).click()
        messages = auth_runtime.drain()
        assert len(messages) == 1
        page.locator(f"form[data-proof='{kind}']").get_by_label("کد شش‌رقمی").fill(
            messages[0].code
        )
        page.get_by_role("button", name=f"تأیید شمارهٔ {label}", exact=True).click()
    page.get_by_role("button", name="اعمال تغییر و خروج", exact=True).click()
    expect(
        page.get_by_role("heading", name="ورود به فیت‌لینک", exact=True)
    ).to_be_visible()
    assert apps.get_model("accounts", "User").objects.get().phone == "+989123456780"
    assert page.request.get(live_server.url + "/api/v1/account/me/").status == 403
    assert (
        page.request.get(
            live_server.url + "/api/v1/account/me/",
            headers={"Cookie": f"sessionid={old_session}"},
        ).status
        == 403
    )
