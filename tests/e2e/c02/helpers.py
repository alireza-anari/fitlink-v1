from playwright.sync_api import expect

VIEWPORTS = [{"width": 1280, "height": 900}, {"width": 390, "height": 844}]


def entry(page, base, provider, *, calendar="jalali", phone="۰۹۱۲۳۴۵۶۷۸۹"):
    response = page.goto(base + "/accounts/entry/", wait_until="networkidle")
    assert response.status == 200
    assert response.headers["cross-origin-opener-policy"] == "same-origin"
    assert page.evaluate("window.isSecureContext") is True
    expect(page.locator("html")).to_have_attribute("lang", "fa")
    expect(page.locator("html")).to_have_attribute("dir", "rtl")
    page.get_by_label("شمارهٔ همراه").fill(phone)
    page.get_by_label("تقویم تاریخ تولد").select_option(calendar)
    page.get_by_label("تاریخ تولد", exact=True).fill(
        "۱۳۶۸-۱۰-۱۱" if calendar == "jalali" else "1990-01-01"
    )
    page.get_by_label("اعلام می‌کنم حداقل ۱۸ سال دارم").check()
    page.get_by_role("button", name="درخواست کد ورود", exact=True).click()
    expect(page.get_by_role("heading", name="تأیید شمارهٔ همراه")).to_be_visible()
    messages = provider.drain()
    assert len(messages) == 1
    return messages[0].code


def verify(page, code):
    page.get_by_label("کد شش‌رقمی").fill(code)
    page.get_by_role("button", name="تأیید و ورود", exact=True).click()
    expect(page.get_by_role("heading", name="حساب من", exact=True)).to_be_visible()


def assets_and_layout(page, base, *, enhanced=True):
    for selector, attribute in (
        ("link[rel=stylesheet]", "href"),
        ("script[src$='accounts.js']", "src"),
    ):
        url = page.locator(selector).get_attribute(attribute)
        response = page.request.get(base + url)
        assert response.status == 200 and response.body()
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    assert page.evaluate("localStorage.length + sessionStorage.length") == 0
    assert page.evaluate("indexedDB.databases().then(d => d.length)") == 0
    if enhanced:
        expect(page.locator("html")).to_have_attribute("data-accounts-enhanced", "true")
