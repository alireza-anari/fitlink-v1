from unittest.mock import patch

import pytest
from django.conf import settings
from redis.exceptions import ConnectionError

pytestmark = pytest.mark.unit


def test_redis_urls_are_separate():
    assert (
        len(
            {
                settings.REDIS_URL,
                settings.CELERY_BROKER_URL,
                settings.CELERY_RESULT_BACKEND,
                settings.CHANNEL_REDIS_URL,
            }
        )
        == 4
    )


def test_redis_probe_timeout_returns_false():
    from config.health import redis_available

    with patch(
        "config.health.Redis.from_url", side_effect=ConnectionError("secret-url")
    ):
        assert redis_available() is False
