from io import BytesIO

import pytest
from django.utils import timezone
from PIL import Image
from playwright.async_api import expect

from tests.e2e.c03.helpers import VIEWPORTS, database, login, quality

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.asyncio,
    pytest.mark.django_db(transaction=True),
]


@pytest.mark.parametrize("viewport", VIEWPORTS)
async def test_upload_quarantine_status_and_private_preview(
    page, live_server, auth_runtime, browser_errors, viewport
):
    await page.set_viewport_size(viewport)
    base = live_server.url
    await login(page, base, auth_runtime)
    from apps.governance.flag_models import FeatureFlag

    await database(
        lambda: FeatureFlag.objects.update_or_create(
            key="professional_registration", defaults={"enabled": True}
        )
    )
    await page.goto(base + "/professional/setup/")
    await page.get_by_role("button", name="ایجاد نمایهٔ حرفه‌ای", exact=True).click()
    output = BytesIO()
    Image.new("RGB", (64, 48), (12, 96, 144)).save(output, format="PNG")
    data = output.getvalue()
    await page.get_by_label("اندازهٔ پرونده (بایت)").fill(str(len(data)))
    await page.get_by_role("button", name="شروع بارگذاری خصوصی", exact=True).click()
    await page.get_by_label("پروندهٔ خصوصی PNG یا JPEG").set_input_files(
        {"name": "private.png", "mimeType": "image/png", "buffer": data}
    )
    await page.get_by_role("button", name="دریافت پرونده", exact=True).click()
    await page.get_by_role("button", name="ارسال برای پردازش", exact=True).click()
    await expect(page.get_by_text("در قرنطینه", exact=True)).to_be_visible()
    assert await page.locator("img").count() == 0
    from apps.assets.models import Asset, AssetProcessingAttempt
    from apps.governance.outbox_models import OutboxEvent
    from config.use_cases import asset_processing

    def process():
        asset = Asset.objects.get()
        event = OutboxEvent.objects.get(event_type="asset.processing_requested")
        asset_processing.request_processing(event, timezone.now())
        asset_processing.scan_due_assets(timezone.now(), 1, enqueue=lambda *args: None)
        attempt = AssetProcessingAttempt.objects.get(asset=asset, state="running")
        assert (
            asset_processing.process_asset(
                asset.id, asset.processing_version, attempt.lease_uuid, timezone.now()
            )
            == "ready"
        )
        return asset.id

    identifier = await database(process)
    response = await page.reload()
    await quality(page, response)
    await expect(page.get_by_text("آماده", exact=True)).to_be_visible()
    await page.get_by_role(
        "button", name="استفاده به‌عنوان تصویر نمایه", exact=True
    ).click()
    response = await page.goto(base + "/professional/preview/")
    await quality(page, response)
    image = page.get_by_alt_text("تصویر خصوصی نمایه")
    await expect(image).to_be_visible()
    source = await image.get_attribute("src")
    assert source == f"/api/v1/profile-assets/{identifier}/content/"
    content = await page.request.get(base + source)
    assert content.status == 200 and "no-store" in content.headers["cache-control"]
    assert content.headers["content-type"] in {"image/png", "image/jpeg"}
    anonymous = await page.context.browser.new_context()
    try:
        assert (await anonymous.request.get(base + source)).status == 403
    finally:
        await anonymous.close()
