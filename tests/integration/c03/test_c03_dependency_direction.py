"""Installed PostgreSQL schema and explicit upstream dependency guards."""

from pathlib import Path

import pytest
from django.apps import apps
from django.db import connection

from tests.unit.c03.test_scope_boundary import FUTURE, future_imports, imported_modules

pytestmark = [pytest.mark.integration, pytest.mark.django_db]
ROOT = Path(__file__).resolve().parents[3]


def reverse_imports(source, package="apps"):
    return [
        name
        for name in imported_modules(source, package)
        if any(
            name == f"apps.{domain}" or name.startswith(f"apps.{domain}.")
            for domain in ("athletes", "professionals")
        )
    ]


def test_upstream_domains_do_not_import_profile_authority():
    for domain in ("accounts", "governance", "assets"):
        for path in (ROOT / "apps" / domain).rglob("*.py"):
            package = ".".join(path.parent.relative_to(ROOT).parts)
            assert not reverse_imports(path.read_text(), package), path.relative_to(
                ROOT
            )
    for domain in ("athletes", "professionals"):
        for source in (
            f"from apps.{domain} import selectors",
            f"import apps.{domain}.models",
        ):
            assert reverse_imports(source)


def test_no_c04_or_c09_database_surface():
    assert connection.vendor == "postgresql"
    tables = connection.introspection.table_names()
    assert not any(
        table.startswith(tuple(f"{name}_" for name in FUTURE)) for table in tables
    )
    assert not any(
        "public_projection" in table or "search_index" in table for table in tables
    )
    models = apps.get_app_config("professionals").get_models()
    for model in models:
        assert not any(
            "trigram" in repr(index).lower() or "ginindex" in repr(index).lower()
            for index in model._meta.indexes
        )


def test_eligibility_input_only_no_public_copy():
    from apps.assets.models import Asset
    from apps.professionals.selectors import publication_eligibility

    from .test_professional_setup import owner

    s = owner()
    before = Asset.objects.count()
    facts = publication_eligibility(s.profile.id, s.at)
    assert not facts.eligible and facts.verified_roles == ()
    assert Asset.objects.count() == before
    assert not future_imports(
        (ROOT / "apps/professionals/selectors.py").read_text(), "apps.professionals"
    )
