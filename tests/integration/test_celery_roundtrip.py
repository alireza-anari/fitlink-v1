import pytest

from config.celery import app
from config.tasks import infrastructure_probe

pytestmark = pytest.mark.integration


def test_worker_non_eager_roundtrip():
    assert app.conf.task_always_eager is False
    result = infrastructure_probe.delay()
    try:
        assert result.get(timeout=15) == {"status": "ok"}
    finally:
        result.forget()
