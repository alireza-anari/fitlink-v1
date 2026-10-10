"""Real server/PostgreSQL/browser; inherited async account harness remains intact."""

import pytest
import pytest_asyncio

from tests.e2e.c02 import conftest as inherited

browser = inherited.browser
auth_runtime = inherited.auth_runtime
browser_errors = inherited.browser_errors


@pytest_asyncio.fixture
async def page(browser):
    context = await browser.new_context()
    page = await context.new_page()
    page.set_default_timeout(5000)
    page.set_default_navigation_timeout(15000)
    yield page
    await context.close()


@pytest.fixture(autouse=True)
def private_runtime(settings, auth_runtime):
    settings.STORAGE_BACKEND = "s3"
    settings.BASELINE_STORAGE_CONSENT_SECONDS = 3600
    settings.ASSET_PROCESSING_ENABLED = True
