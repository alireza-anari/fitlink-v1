from unittest.mock import patch

import pytest
from django.db import OperationalError

pytestmark = pytest.mark.unit


def test_database_timeout_is_bounded():
    from config.health import database_available

    with patch(
        "config.health.connection.cursor",
        side_effect=OperationalError("private-connection-secret"),
    ):
        assert database_available() is False
