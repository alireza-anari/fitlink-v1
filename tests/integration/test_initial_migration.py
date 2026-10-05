import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_empty_database_migrates_without_auth_user():
    # pytest-django creates a new disposable PostgreSQL test database and applies
    # all migrations from zero; CI also migrates a fresh isolated Compose volume.
    assert connection.vendor == "postgresql"
    assert connection.settings_dict["NAME"] == "test_fitlink"
    tables = connection.introspection.table_names()
    assert "accounts_user" in tables
    assert "auth_user" not in tables
    executor = MigrationExecutor(connection)
    assert ("accounts", "0001_initial") in executor.loader.applied_migrations
    state = executor.loader.project_state()
    assert state.apps.get_model("accounts", "User")._meta.db_table == "accounts_user"


def test_all_auth_relations_use_custom_user():
    model = get_user_model()
    assert model._meta.label == "accounts.User"
    assert model.groups.through._meta.get_field("user").remote_field.model is model
    assert (
        model.user_permissions.through._meta.get_field("user").remote_field.model
        is model
    )
