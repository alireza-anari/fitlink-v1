import pytest
from django.db import connection

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_postgres_select_one():
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        assert cursor.fetchone() == (1,)


def test_database_is_postgresql():
    assert connection.vendor == "postgresql"


def test_test_db_is_separate():
    assert connection.settings_dict["NAME"] == "test_fitlink"


def test_database_timeout_is_bounded():
    assert connection.settings_dict["OPTIONS"]["connect_timeout"] == 2
