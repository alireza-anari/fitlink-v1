import asyncio
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest
from django.utils.asyncio import async_unsafe

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_browser_database_callback_runs_outside_event_loop(monkeypatch):
    monkeypatch.delenv("DJANGO_ALLOW_ASYNC_UNSAFE", raising=False)
    path = Path(__file__).parents[2] / "e2e/c02/helpers.py"
    spec = importlib.util.spec_from_file_location("c02_browser_helpers", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    @async_unsafe
    def guarded_database_operation():
        return 42

    assert await module.database(guarded_database_operation) == 42


@pytest.mark.asyncio
@pytest.mark.parametrize("has_error", [False, True])
async def test_browser_diagnostics_register_in_loop_and_reject_console_errors(
    has_error,
):
    path = Path(__file__).parents[2] / "e2e/c02/conftest.py"
    spec = importlib.util.spec_from_file_location("c02_browser_fixtures", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class PageBoundary:
        def __init__(self):
            self.handlers = {}

        def on(self, event, handler):
            asyncio.get_running_loop()
            self.handlers[event] = handler

    page = PageBoundary()
    fixture = module.browser_errors.__wrapped__(page)
    await fixture.__anext__()
    if has_error:
        page.handlers["console"](SimpleNamespace(type="error", text="browser error"))
        with pytest.raises(AssertionError):
            await fixture.__anext__()
    else:
        with pytest.raises(StopAsyncIteration):
            await fixture.__anext__()
