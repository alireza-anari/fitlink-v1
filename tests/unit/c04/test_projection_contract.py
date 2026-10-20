"""Public projection contracts fail closed before any public adapter exists."""

import importlib
from pathlib import Path
from uuid import uuid4

import pytest

ROOT = Path(__file__).resolve().parents[3]


def boundary(name):
    assert (ROOT / (name.replace(".", "/") + ".py")).exists(), (
        "Missing fresh public projection boundary"
    )
    return importlib.import_module(name)


def test_public_dto_rejects_private_fields_and_defensive_snapshot():
    dto = boundary("apps.marketplace.contracts").PublicProfessionalDTO
    public = {"display_name": "Selected public name", "verified_roles": ["coach"]}
    result = dto(uuid4(), "public-test", public, ())
    public["display_name"] = "Unconfirmed change"
    assert result.as_public_dict()["display_name"] == "Selected public name"
    value = result.as_public_dict()
    value["display_name"] = "Mutation"
    assert result.as_public_dict()["display_name"] == "Selected public name"
    for name in ["user_uuid", "identity_name", "evidence_ids", "authority_hash"]:
        with pytest.raises(ValueError):
            dto(uuid4(), "public-test", {**public, name: "PRIVATE_SENTINEL"}, ())


def test_public_read_requires_server_current_authority():
    reader = boundary("apps.marketplace.selectors").public_professional
    from django.utils import timezone

    with pytest.raises(ValueError):
        reader(uuid4(), timezone.now())


def test_projection_due_batches_have_finite_bounds():
    reconcile = boundary("config.use_cases.marketplace").reconcile_publications
    from django.utils import timezone

    for limit in [0, 101, True, -1]:
        with pytest.raises(ValueError):
            reconcile(timezone.now(), limit)


def test_actual_flag_repository_error_is_distinct_from_disabled(monkeypatch):
    from django.db import OperationalError
    from django.utils import timezone

    from apps.governance.flag_models import FeatureFlag
    from config.use_cases.marketplace import current_source

    def unavailable(*args, **kwargs):
        raise OperationalError("PRIVATE_PROVIDER_DETAIL")

    monkeypatch.setattr(FeatureFlag.objects, "get", unavailable)
    with pytest.raises(OperationalError):
        current_source(uuid4(), timezone.now())


@pytest.mark.parametrize(
    "field,value",
    [
        ("biography", {"source_key": "PRIVATE_SENTINEL"}),
        ("specialties", [{"private": "PRIVATE_SENTINEL"}]),
        (
            "locations",
            [
                {
                    "country_code": "IR",
                    "region": "Broad",
                    "city": "Broad",
                    "modes": ["online"],
                    "latitude": 1,
                }
            ],
        ),
        ("experience_years", True),
    ],
)
def test_public_dto_rejects_nested_or_mistyped_fields(field, value):
    dto = boundary("apps.marketplace.contracts").PublicProfessionalDTO
    with pytest.raises(ValueError):
        dto(
            uuid4(),
            "public-test",
            {"display_name": "Public", "verified_roles": ["coach"], field: value},
            (),
        )
