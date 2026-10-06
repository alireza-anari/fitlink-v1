import importlib.util
from pathlib import Path

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
