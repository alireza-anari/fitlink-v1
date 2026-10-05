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
