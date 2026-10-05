from unittest.mock import patch

import pytest
from django.test import Client

pytestmark = pytest.mark.unit


def test_liveness_works_without_dependencies():
    response = Client().get("/health/live/")
    assert response.status_code == 200 and response.json() == {"status": "ok"}
    assert response.headers["Cache-Control"] == "no-store"


@pytest.mark.parametrize(
    "db,redis,status", [(True, True, 200), (False, True, 503), (True, False, 503)]
)
def test_readiness_generic(db, redis, status):
    with (
        patch("config.health.database_available", return_value=db),
        patch("config.health.redis_available", return_value=redis),
    ):
        response = Client().get("/health/ready/")
    assert response.status_code == status
    assert response.json() == {"status": "ok" if status == 200 else "unavailable"}


def test_versioned_status():
    response = Client().get("/api/v1/status/")
    assert response.status_code == 200
    assert response.json() == {
        "service": "fitlink",
        "api_version": "v1",
        "status": "ok",
    }


@pytest.mark.parametrize("dependency", ["postgresql", "redis"])
def test_dependency_failure_logs_safe_label(caplog, dependency):
    from django.db import DatabaseError
    from redis.exceptions import RedisError

    from config.health import database_available, redis_available

    if dependency == "postgresql":
        target = "config.health.connection.cursor"
        error = DatabaseError("private-credential")
        probe = database_available
    else:
        target = "config.health.Redis.from_url"
        error = RedisError("private-credential")
        probe = redis_available
    with patch(target, side_effect=error):
        assert probe() is False
    records = [
        record
        for record in caplog.records
        if getattr(record, "event", "") == "dependency.unavailable"
    ]
    assert len(records) == 1
    assert records[0].dependency == dependency
    from config.logging import JsonFormatter

    assert "private-credential" not in JsonFormatter().format(records[0])
