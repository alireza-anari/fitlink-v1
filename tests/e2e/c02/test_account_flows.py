from datetime import timedelta

import pytest
from conftest import adult_user
from django.apps import apps
from django.utils import timezone
from helpers import VIEWPORTS, assets_and_layout, entry, verify
from playwright.sync_api import expect

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_entry_preferences_logout_and_no_browser_credentials(
    page, live_server, auth_runtime, browser_errors, viewport
):
    page.set_viewport_size(viewport)
    base = live_server.url
    code = entry(page, base, auth_runtime)
    verify(page, code)
    expect(page.get_by_text("+98912*****89", exact=True)).to_be_visible()
    assets_and_layout(page, base)
    page.get_by_label("زبان").select_option("en")
    page.get_by_label("منطقهٔ زمانی").fill("UTC")
    page.get_by_role("button", name="ذخیرهٔ ترجیحات").click()
    expect(page.get_by_text("ترجیحات ذخیره شد.", exact=True)).to_be_visible()
    row = apps.get_model("accounts", "User").objects.get()
    assert row.locale == "en" and row.timezone == "UTC" and not row.is_staff
    assert not {"AthleteProfile", "ProfessionalProfile"} & {
        m.__name__ for m in apps.get_models()
    }
    page.get_by_role("button", name="خروج از این نشست", exact=True).click()
    expect(
        page.get_by_role("heading", name="ورود به فیت‌لینک", exact=True)
    ).to_be_visible()
    assert page.request.get(base + "/api/v1/account/me/").status == 403


@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_under18_stops_before_sms_or_identity(
    page, live_server, auth_runtime, browser_errors, viewport
):
    page.set_viewport_size(viewport)
    page.goto(live_server.url + "/accounts/entry/")
    page.get_by_label("شمارهٔ همراه").fill("09123456789")
    page.get_by_label("تقویم تاریخ تولد").select_option("gregorian")
    page.get_by_label("تاریخ تولد", exact=True).fill("2020-01-01")
    page.get_by_label("اعلام می‌کنم حداقل ۱۸ سال دارم").check()
    page.get_by_role("button", name="درخواست کد ورود", exact=True).click()
    expect(page.get_by_role("alert")).to_be_visible()
    assert auth_runtime.drain() == ()
    assert not apps.get_model("accounts", "User").objects.exists()
    assert not apps.get_model("accounts", "OTPChallenge").objects.exists()
    assert page.request.get(live_server.url + "/api/v1/account/me/").status == 403
    assets_and_layout(page, live_server.url)


@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_expired_code_and_resend_are_server_rejected(
    page, live_server, auth_runtime, browser_errors, viewport
):
    page.set_viewport_size(viewport)
    code = entry(page, live_server.url, auth_runtime, calendar="gregorian")
    # Tamper only presentation; the authoritative resend command still denies.
    page.locator("button[data-resend]").evaluate(
        "button => { button.disabled = false; button.dataset.remaining = '0'; "
        "button.click(); }"
    )
    page.wait_for_load_state("networkidle")
    expect(page.get_by_role("alert")).to_contain_text("لطفاً")
    assert auth_runtime.drain() == ()
    at = timezone.now()
    apps.get_model("accounts", "OTPChallenge").objects.update(
        issued_at=at - timedelta(seconds=301), expires_at=at - timedelta(seconds=1)
    )
    page.get_by_label("کد شش‌رقمی").fill(code)
    page.get_by_role("button", name="تأیید و ورود", exact=True).click()
    expect(page.get_by_role("alert")).to_contain_text("کد معتبر نیست")
    assert not apps.get_model("accounts", "User").objects.exists()
    assert page.request.get(live_server.url + "/api/v1/account/me/").status == 403


@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_native_form_without_javascript(browser, live_server, auth_runtime, viewport):
    context = browser.new_context(java_script_enabled=False, viewport=viewport)
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on(
        "console",
        lambda message: (
            errors.append(message.text) if message.type == "error" else None
        ),
    )
    try:
        code = entry(page, live_server.url, auth_runtime, calendar="gregorian")
        verify(page, code)
        assets_and_layout(page, live_server.url, enhanced=False)
        assert errors == []
    finally:
        context.close()


@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_csrf_reload_rotation_and_old_token_denial(
    page, live_server, auth_runtime, browser_errors, viewport
):
    page.set_viewport_size(viewport)
    code = entry(page, live_server.url, auth_runtime)
    old = next(c["value"] for c in page.context.cookies() if c["name"] == "csrftoken")
    page.reload(wait_until="networkidle")
    verify(page, code)
    new = next(c["value"] for c in page.context.cookies() if c["name"] == "csrftoken")
    assert old != new
    response = page.request.post(
        live_server.url + "/accounts/me/",
        form={"action": "preferences", "locale": "en", "timezone": "UTC"},
        headers={"X-CSRFToken": old},
    )
    assert response.status == 403
    assert apps.get_model("accounts", "User").objects.get().locale == "fa"
    page.get_by_label("زبان").select_option("en")
    page.get_by_role("button", name="ذخیرهٔ ترجیحات").click()
    expect(page.get_by_text("ترجیحات ذخیره شد.", exact=True)).to_be_visible()


@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_existing_and_unknown_wrong_code_copy_is_uniform(
    page, live_server, auth_runtime, browser_errors, viewport
):
    page.set_viewport_size(viewport)
    adult_user("+989123456789")
    copies = []
    for phone in ("09123456789", "09123456781"):
        page.context.clear_cookies()
        code = entry(page, live_server.url, auth_runtime, phone=phone)
        wrong = str((int(code) + 1) % 1_000_000).zfill(6)
        page.get_by_label("کد شش‌رقمی").fill(wrong)
        page.get_by_role("button", name="تأیید و ورود", exact=True).click()
        expect(page.get_by_role("alert")).to_contain_text("کد معتبر نیست")
        copies.append(page.get_by_role("alert").inner_text())
        assert page.request.get(live_server.url + "/api/v1/account/me/").status == 403
    assert copies[0] == copies[1]
    assert apps.get_model("accounts", "User").objects.count() == 1


@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_restricted_account_has_only_current_control_flows(
    page, live_server, auth_runtime, browser_errors, viewport
):
    page.set_viewport_size(viewport)
    adult_user("+989123456789", state="restricted")
    verify(page, entry(page, live_server.url, auth_runtime))
    expect(
        page.get_by_text("دسترسی این حساب به کنترل‌های حساب و حریم خصوصی محدود شده است.")
    ).to_be_visible()
    assert page.get_by_role("link", name="تغییر شمارهٔ همراه", exact=True).count() == 0
    assert page.request.get(live_server.url + "/accounts/phone-change/").url.endswith(
        "/accounts/entry/"
    )
    page.get_by_label("منطقهٔ زمانی").fill("UTC")
    page.get_by_role("button", name="ذخیرهٔ ترجیحات").click()
    expect(page.get_by_text("ترجیحات ذخیره شد.", exact=True)).to_be_visible()
    page.get_by_role("link", name="درخواست‌های حریم خصوصی", exact=True).click()
    expect(
        page.get_by_role("heading", name="درخواست‌های حریم خصوصی", exact=True)
    ).to_be_visible()


@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_suspension_invalidates_existing_browser_control(
    page, live_server, auth_runtime, browser_errors, viewport
):
    page.set_viewport_size(viewport)
    verify(page, entry(page, live_server.url, auth_runtime))
    apps.get_model("accounts", "User").objects.update(
        state="suspended", is_active=False
    )
    page.reload(wait_until="networkidle")
    expect(
        page.get_by_role("heading", name="ورود به فیت‌لینک", exact=True)
    ).to_be_visible()
    assert page.request.get(live_server.url + "/api/v1/account/me/").status == 403
