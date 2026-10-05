from unittest.mock import patch

import pytest
from django.db import DatabaseError
from django.test import Client, override_settings

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_database_failure_is_generic_and_liveness_survives():
    with patch(
        "config.health.connection.cursor",
        side_effect=DatabaseError("secret-password private-host"),
    ):
        response = Client().get("/health/ready/")
        assert response.status_code == 503
        assert response.json() == {"status": "unavailable"}
        assert "secret" not in response.content.decode()
        assert Client().get("/health/live/").status_code == 200


@override_settings(REDIS_URL="redis://127.0.0.1:1/0")
def test_bounded_real_redis_connection_failure():
    response = Client().get("/health/ready/")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
    assert Client().get("/health/live/").status_code == 200
