import pytest

pytestmark = pytest.mark.unit


def test_celery_loads_django_namespace():
    from config.celery import app

    assert app.main == "fitlink"
    assert app.conf.task_always_eager is False
    assert app.conf.result_expires == 86400


def test_celery_json_only():
    from config.celery import app

    assert app.conf.task_serializer == "json"
    assert app.conf.accept_content == ["json"]


def test_beat_has_no_product_schedules():
    from config.celery import app

    assert app.conf.beat_schedule == {}


def test_probe_eager_returns_ok():
    from config.tasks import infrastructure_probe

    assert infrastructure_probe.apply().get() == {"status": "ok"}
