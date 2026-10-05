import os

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.e2e


@pytest.mark.parametrize("viewport", [{"width": 1280, "height": 900}, {"width": 390, "height": 844}])
def test_foundation_smoke(page, viewport):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
    page.set_viewport_size(viewport)
    base = os.environ.get("E2E_BASE_URL", "http://127.0.0.1:8000")
    response = page.goto(base + "/", wait_until="networkidle")
    assert response.status == 200
    expect(page.locator("html")).to_have_attribute("lang", "fa")
    expect(page.locator("html")).to_have_attribute("dir", "rtl")
    expect(page.get_by_role("heading", name="زیرساخت فیت‌لینک آماده است")).to_be_visible()
    expect(page.locator("html")).to_have_attribute("data-enhanced", "true")
    for selector, attribute in (("link[rel=stylesheet]", "href"), ("script[type=module]", "src")):
        url = page.locator(selector).get_attribute(attribute)
        asset = page.request.get(base + url)
        assert asset.status == 200 and len(asset.body()) > 0
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    assert page.request.get(base + "/api/v1/status/").json() == {"status": "ok", "version": "v1"}
    assert page.request.get(base + "/health/ready/").status == 200
    assert errors == []
