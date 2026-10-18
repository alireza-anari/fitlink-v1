"""C04 starts on actual PostgreSQL with inherited identity/history intact."""

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_task1_inherits_real_postgresql_c03_schema():
    assert connection.vendor == "postgresql"
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_setting('server_version_num')::integer")
        assert cursor.fetchone()[0] >= 140000
    tables = set(connection.introspection.table_names())
    assert {
        "accounts_user",
        "professionals_professionalprofile",
        "professionals_verificationdecision",
        "assets_asset",
        "governance_outboxevent",
    } <= tables
    assert "auth_user" not in tables
    executor = MigrationExecutor(connection)
    assert not executor.migration_plan(executor.loader.graph.leaf_nodes())
