"""Selection boundaries admit exact commands and expose only current targets."""

import importlib
import importlib.util
from uuid import uuid4

import pytest


def contracts():
    name = "apps.marketplace.selection_contracts"
    assert importlib.util.find_spec(name), "Missing bounded selection contracts"
    return importlib.import_module(name)


@pytest.mark.parametrize(
    "command,target,version,operation",
    [
        ("add", uuid4(), 1, uuid4()),
        ("remove", uuid4(), 1, uuid4()),
        ("clear", None, 1, uuid4()),
    ],
)
def test_exact_comparison_commands_admitted(command, target, version, operation):
    contracts().validate_comparison_command(command, target, version, operation)


@pytest.mark.parametrize(
    "command,target,version,operation",
    [
        ("replace", uuid4(), 1, uuid4()),
        ("add", None, 1, uuid4()),
        ("add", "forged", 1, uuid4()),
        ("clear", uuid4(), 1, uuid4()),
        ("add", uuid4(), True, uuid4()),
        ("add", uuid4(), 0, uuid4()),
        ("add", uuid4(), 1, "operation"),
    ],
)
def test_malformed_comparison_commands_rejected(command, target, version, operation):
    with pytest.raises(ValueError):
        contracts().validate_comparison_command(command, target, version, operation)


@pytest.mark.parametrize("selected", [0, 1, None, "true", [], {}])
def test_favorite_boolean_is_exact(selected):
    with pytest.raises(ValueError):
        contracts().validate_favorite(uuid4(), selected, uuid4())


def test_selection_outputs_have_no_owner_session_or_hidden_total():
    from dataclasses import fields

    assert {f.name for f in fields(contracts().ComparisonDTO)} == {"version", "items"}
    assert {f.name for f in fields(contracts().FavoriteDTO)} == {"selected"}
