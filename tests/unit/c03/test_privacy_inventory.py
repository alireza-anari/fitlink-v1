"""Closed lifetime interfaces; metadata is never a private read grant."""

import importlib
import importlib.util
import inspect
from datetime import datetime
from uuid import uuid4

import pytest
from django.utils import timezone

from apps.governance import retention

pytestmark = pytest.mark.unit


def installed(path):
    assert importlib.util.find_spec(path), f"Missing Task 9 interface: {path}"
    return importlib.import_module(path)


@pytest.mark.parametrize(
    "path,name",
    [
        ("apps.assets.privacy", "enumerate_asset_inventory"),
        ("apps.assets.cleanup", "cleanup_asset"),
        ("apps.professionals.privacy", "enumerate_professional_inventory"),
        ("config.use_cases.c03_privacy", "inventory_c03_owner"),
        ("config.use_cases.c03_privacy", "validate_c03_hold_subject"),
        ("config.use_cases.c03_privacy", "validate_c03_hold_case"),
        ("apps.assets.processing_worker", "scan_cleanup_assets"),
    ],
)
def test_installed_lifetime_interfaces(path, name):
    assert callable(getattr(installed(path), name, None))


@pytest.mark.parametrize("name", ["is_record_held", "apply_hold", "release_hold"])
def test_retention_callbacks_are_server_supplied_and_optional(name):
    parameter = inspect.signature(getattr(retention, name)).parameters.get(
        "subject_validator"
    )
    assert parameter is not None and parameter.default is None
    assert parameter.kind == inspect.Parameter.KEYWORD_ONLY
    if name == "apply_hold":
        case = inspect.signature(retention.apply_hold).parameters.get("case_validator")
        assert case is not None and case.default is None


@pytest.mark.parametrize("kind", ["health", "coaching_request", "user", "", None])
def test_unknown_subject_kinds_fail_closed_without_domain_queries(kind):
    module = installed("config.use_cases.c03_privacy")
    validator = getattr(module, "validate_c03_hold_subject", None)
    assert callable(validator)
    subject = retention.ValidatedRecordSubject(kind, uuid4(), uuid4(), 1)
    assert validator(subject) is False


@pytest.mark.parametrize("version", [0, -1, True, "1", None])
def test_forged_subject_versions_fail_closed_without_queries(version):
    module = installed("config.use_cases.c03_privacy")
    validator = getattr(module, "validate_c03_hold_subject", None)
    assert callable(validator)
    subject = retention.ValidatedRecordSubject(
        "profile_asset", uuid4(), uuid4(), version
    )
    assert validator(subject) is False


def test_cleanup_has_no_implicit_destructive_authority():
    module = installed("apps.assets.cleanup")
    assert module.cleanup_asset(uuid4(), 1, uuid4(), timezone.now()) == "denied"


def test_inventory_requires_aware_time():
    module = installed("config.use_cases.c03_privacy")
    inventory = getattr(module, "inventory_c03_owner", None)
    assert callable(inventory)
    with pytest.raises(ValueError):
        inventory(uuid4(), datetime(2026, 1, 1))
