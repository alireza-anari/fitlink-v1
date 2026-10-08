"""Bounded snapshot inputs exclude future health and attachment domains."""

import importlib
import importlib.util
from datetime import UTC, datetime
from decimal import Decimal

import pytest

pytestmark = pytest.mark.unit


def normalize(step, values):
    assert importlib.util.find_spec("apps.athletes.validation"), (
        "Missing baseline field validator"
    )
    validator = importlib.import_module("apps.athletes.validation")
    contracts = importlib.import_module("apps.athletes.contracts")
    return validator.normalize_step(step, contracts.BaselineStepInput(values))


@pytest.mark.parametrize(
    ("step", "values"),
    [
        ("basics", {"height_cm": "50.0", "weight_kg": "400.0"}),
        ("goals", {"goals": ["strength", "general_fitness"]}),
        ("experience", {"experience": "beginner", "training_experience_months": 0}),
        ("availability", {"available_days": [1, 7]}),
        ("facilities", {"facilities": ["home"], "equipment": ["bodyweight"]}),
        ("context", {"sleep_hours": "24.0", "energy": 10, "lifestyle": "mixed"}),
        (
            "habits",
            {"meals_per_day": 0, "hydration_habit": "unknown", "nutrition_habits": ""},
        ),
        ("measures", {"waist_cm": "250.0", "approximate_records": []}),
    ],
)
def test_bounded_fields_accept_engineering_limits(step, values):
    assert normalize(step, values).keys() == values.keys()


def test_decimal_is_exact_and_optional_null_means_clear():
    assert normalize("basics", {"height_cm": "170.1"}) == {
        "height_cm": Decimal("170.1")
    }
    assert normalize("basics", {"height_cm": None}) == {"height_cm": None}
    assert normalize("basics", {}) == {}


@pytest.mark.parametrize(
    ("step", "values"),
    [
        ("basics", {"height_cm": "49.9"}),
        ("basics", {"weight_kg": "400.1"}),
        ("basics", {"height_cm": "NaN"}),
        ("basics", {"height_cm": 170.1}),
        ("basics", {"height_cm": "170.11"}),
        ("context", {"sleep_hours": "24.1"}),
        ("context", {"energy": True}),
        ("habits", {"meals_per_day": -1}),
        ("experience", {"training_experience_months": 1201}),
        ("goals", {"goals": ["strength", "strength"]}),
        ("availability", {"available_days": [True]}),
        ("availability", {"available_days": [0]}),
        ("facilities", {"facilities": ["hospital"]}),
        ("habits", {"nutrition_habits": "<script>bad</script>"}),
        (
            "measures",
            {
                "approximate_records": [
                    {
                        "label": "lift",
                        "value": "12.00",
                        "unit": "kg",
                        "observed_at": "2026-01-01T00:00:00+00:00",
                        "provenance": "verified",
                    }
                ]
            },
        ),
        (
            "measures",
            {
                "approximate_records": [
                    {
                        "label": "lift",
                        "value": "12.00",
                        "unit": "kg",
                        "observed_at": "2026-01-01T00:00:00",
                        "provenance": "self_reported",
                    }
                ]
            },
        ),
        ("goals", {"goals": None}),
        ("unknown", {}),
    ],
)
def test_bad_units_tokens_types_and_active_text_rejected(step, values):
    with pytest.raises(ValueError):
        normalize(step, values)


@pytest.mark.parametrize(
    "key",
    [
        "injury",
        "injuries",
        "allergies",
        "medications",
        "supplements",
        "photo",
        "health_document",
        "age",
        "owner",
        "consent",
        "diagnosis",
    ],
)
def test_health_photo_unknown_fields_rejected(key):
    with pytest.raises(ValueError):
        normalize("basics", {key: "arbitrary"})


def test_approximate_record_is_bounded_dated_self_report():
    record = {
        "label": "lift",
        "value": "12.20",
        "unit": "kg",
        "observed_at": "2026-01-01T00:00:00+00:00",
        "provenance": "self_reported",
    }
    normalized = normalize("measures", {"approximate_records": [record]})
    assert normalized["approximate_records"][0]["value"] == "12.20"
    assert (
        datetime.fromisoformat(
            normalized["approximate_records"][0]["observed_at"]
        ).tzinfo
        == UTC
    )
    with pytest.raises(ValueError):
        normalize("measures", {"approximate_records": [record] * 6})
    with pytest.raises(ValueError):
        normalize("measures", {"approximate_records": [{**record, "injury": "hidden"}]})


def test_record_decimal_eight_two_upper_limit():
    record = {
        "label": "lift",
        "value": "999999.99",
        "unit": "reps",
        "observed_at": "2026-01-01T00:00:00+00:00",
        "provenance": "self_reported",
    }
    assert (
        normalize("measures", {"approximate_records": [record]})["approximate_records"][
            0
        ]["value"]
        == "999999.99"
    )


def test_private_projection_defaults_cannot_carry_another_results_values(monkeypatch):
    from types import SimpleNamespace
    from uuid import uuid4

    from apps.athletes.baseline import project
    from apps.athletes.validation import OPTIONAL_DEFAULTS

    monkeypatch.setitem(OPTIONAL_DEFAULTS, "approximate_records", [])
    row = SimpleNamespace(
        id=uuid4(),
        athlete_id=uuid4(),
        version=1,
        state="draft",
        schema_version=1,
        sequence=1,
        parent_id=None,
        observed_at=datetime(2026, 1, 1, tzinfo=UTC),
        age_at_assessment=36,
        submitted_at=None,
        updated_at=datetime(2026, 1, 1, tzinfo=UTC),
        goals=[],
        experience="",
        available_days=[],
        equipment=[],
        equipment_other="",
        facilities=[],
    )
    first = project(SimpleNamespace(), row, row.observed_at, lambda *_: False)
    first.answers["approximate_records"].append({"label": "private"})
    second = project(SimpleNamespace(), row, row.observed_at, lambda *_: False)
    assert second.answers["approximate_records"] == []
