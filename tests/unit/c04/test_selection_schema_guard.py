"""Current schema adaptation remains an exact finite allowlist."""

from tests.integration.c03 import test_c03_dependency_direction as guard


def test_task6_schema_guard_accepts_only_nine_approved_tables():
    check = getattr(guard, "current_marketplace_surface", None)
    assert callable(check), "Missing exact current-stage selection schema guard"
    tables = {
        "marketplace_publicprofessionalprojection",
        "marketplace_publiclocation",
        "marketplace_projectionrefreshstate",
        "marketplace_publicationscancursor",
        "marketplace_favorite",
        "marketplace_favoritereceipt",
        "marketplace_comparisoncollection",
        "marketplace_comparisonentry",
        "marketplace_comparisonreceipt",
    }
    assert check(tables)
    assert not check(tables | {"marketplace_private_directory"})
    for name in tables:
        assert not check(tables - {name})
