from asgiref.sync import sync_to_async
from django.db import connections
from playwright.async_api import expect


async def database(operation):
    """Real ORM work off the browser loop, with Django's guard still enabled."""

    def run():
        try:
            return operation()
        finally:
            connections.close_all()

    return await sync_to_async(run, thread_sensitive=True)()


VIEWPORTS = [{"width": 1280, "height": 900}, {"width": 390, "height": 844}]


async def entry(page, base, provider, *, calendar="jalali", phone="۰۹۱۲۳۴۵۶۷۸۹"):
    response = await page.goto(base + "/accounts/entry/", wait_until="networkidle")
    assert response.status == 200
    assert response.headers["cross-origin-opener-policy"] == "same-origin"
    assert await page.evaluate("window.isSecureContext") is True
    await expect(page.locator("html")).to_have_attribute("lang", "fa")
    await expect(page.locator("html")).to_have_attribute("dir", "rtl")
    await page.get_by_label("شمارهٔ همراه").fill(phone)
    await page.get_by_label("تقویم تاریخ تولد").select_option(calendar)
    await page.get_by_role("textbox", name="تاریخ تولد").fill(
        "۱۳۶۸-۱۰-۱۱" if calendar == "jalali" else "1990-01-01"
    )
    await page.get_by_label("اعلام می\u200cکنم حداقل ۱۸ سال دارم").check()
    await page.get_by_role("button", name="درخواست کد ورود", exact=True).click()
    await expect(page.get_by_role("heading", name="تأیید شمارهٔ همراه")).to_be_visible()
    messages = provider.drain()
    assert len(messages) == 1
    return messages[0].code


async def verify(page, code):
    await page.get_by_label("کد شش\u200cرقمی").fill(code)
    await page.get_by_role("button", name="تأیید و ورود", exact=True).click()
    await expect(
        page.get_by_role("heading", name="حساب من", exact=True)
    ).to_be_visible()


async def assets_and_layout(page, base, *, enhanced=True):
    for selector, attribute in (
        ("link[rel=stylesheet]", "href"),
        ("script[src$='accounts.js']", "src"),
    ):
        url = await page.locator(selector).get_attribute(attribute)
        response = await page.request.get(base + url)
        assert response.status == 200 and await response.body()
    assert await page.evaluate(
        "document.documentElement.scrollWidth <= window.innerWidth"
    )
    assert await page.evaluate("localStorage.length + sessionStorage.length") == 0
    assert await page.evaluate("indexedDB.databases().then(d => d.length)") == 0
    if enhanced:
        await expect(page.locator("html")).to_have_attribute(
            "data-accounts-enhanced", "true"
        )
