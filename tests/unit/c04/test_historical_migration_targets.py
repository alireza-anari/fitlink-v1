"""Historical checks must not inherit future migration leaves."""

import ast
import importlib
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[3]
EXPECTED = [
    ("accounts", "0013_invitereferrallink_referralattribution_and_more"),
    ("auth", "0012_alter_user_first_name_max_length"),
    ("contenttypes", "0002_remove_content_type_name"),
    ("governance", "0010_outboxdeliveryreceipt"),
    ("sessions", "0001_initial"),
]


def test_historical_test_selects_c02_even_when_future_apps_depend_on_c03():
    source = ROOT / "tests/integration/c03/test_c03_migrations.py"
    tree = ast.parse(source.read_text())
    function = next(
        n
        for n in tree.body
        if isinstance(n, ast.FunctionDef)
        and n.name == "test_optional_profiles_not_created"
    )
    selection = next(
        n.value
        for n in ast.walk(function)
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "c02" for t in n.targets)
    )
    namespace = vars(
        importlib.import_module("tests.integration.c03.test_c03_migrations")
    ).copy()
    namespace.update(
        latest=[(app, "9999_future_leaf") for app, _ in EXPECTED]
        + [
            ("professionals", "0017_owner_anchor_guards"),
            ("assets", "0009_processing_algorithm_prompts"),
            ("athletes", "0010_task3_baseline_command_contracts"),
            ("marketplace", "0001_public_projection"),
        ],
        domains={"assets", "athletes", "professionals"},
    )
    # Evaluate only the trusted test's target expression, without executing DB IO.
    selected = eval(compile(ast.Expression(selection), str(source), "eval"), namespace)
    assert selected == EXPECTED


def test_only_installed_c04_dependents_are_unapplied():
    from tests.integration.c04.migration_history import historical_unapply_targets

    assert historical_unapply_targets(
        EXPECTED
        + [
            ("professionals", "0018_c04_publication"),
            ("marketplace", "0001_public_projection"),
        ]
    ) == [("marketplace", None), ("professionals", None)]
    with pytest.raises(ValueError, match="Unexpected migration domain"):
        historical_unapply_targets(EXPECTED + [("billing", "0001_unapproved")])


@pytest.mark.parametrize(
    "vendor,atomic,autocommit",
    [
        ("sqlite", False, True),
        ("postgresql", True, False),
        ("postgresql", False, False),
    ],
)
def test_history_probe_refuses_non_postgres_or_transactional_admin(
    vendor, atomic, autocommit
):
    from types import SimpleNamespace

    from tests.integration.c04.migration_history import isolated_history_database

    parent = SimpleNamespace(
        vendor=vendor, in_atomic_block=atomic, get_autocommit=lambda: autocommit
    )
    with pytest.raises(RuntimeError, match="autocommit PostgreSQL"):
        with isolated_history_database(parent):
            pytest.fail("Unsafe parent probe accepted")
