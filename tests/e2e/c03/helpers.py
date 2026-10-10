"""No private page body, screenshot, trace or token diagnostic artifacts."""

from urllib.parse import urljoin

from playwright.async_api import expect

from tests.e2e.c02.helpers import VIEWPORTS, database, entry, verify  # noqa: F401


async def quality(page, response):
    assert response.status == 200
    assert "no-store" in response.headers["cache-control"]
    await expect(page.locator("html")).to_have_attribute("lang", "fa")
    await expect(page.locator("html")).to_have_attribute("dir", "rtl")
    assert await page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    assert await page.evaluate("localStorage.length + sessionStorage.length") == 0
    assert await page.evaluate("indexedDB.databases().then(d => d.length)") == 0
    assert await page.evaluate("caches.keys().then(k => k.length)") == 0
    assert await page.evaluate(
        "Array.from(document.querySelectorAll("
        "'input:not([type=hidden]),select,textarea'))"
        ".every(e => e.labels.length > 0)"
    )
    for tag, attr in (
        ("link[rel=stylesheet]", "href"),
        ("script[src$='profiles.js']", "src"),
    ):
        url = await page.locator(tag).get_attribute(attr)
        assert (await page.request.get(urljoin(page.url, url))).status == 200


async def login(page, base, provider):
    await verify(page, await entry(page, base, provider))


async def baseline_core(page, base):
    await page.goto(base + "/athlete/setup/")
    await page.get_by_role("button", name="ایجاد نمایهٔ ورزشکار", exact=True).click()
    await page.get_by_role("button", name="شروع یا ادامهٔ ارزیابی", exact=True).click()
    for step, fields in (
        ("goals", {"goals": "general_fitness"}),
        ("experience", {"experience": "beginner"}),
        ("availability", {"available_days": "1"}),
        ("facilities", {"facilities": "home"}),
    ):
        await page.goto(page.url.split("?")[0] + "?step=" + step)
        for name, value in fields.items():
            await page.locator(f'[name="{name}"]').select_option(value)
        await page.get_by_role("button", name="ذخیرهٔ مرحله", exact=True).click()
    await page.get_by_role("button", name="ثبت ارزیابی", exact=True).click()
    await expect(page.get_by_text("ثبت شده", exact=True)).to_be_visible()
