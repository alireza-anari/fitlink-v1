"""Native adapters must deny future/state fields and normalize Persian digits."""

import importlib
from uuid import uuid4

import pytest

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "domain,step", [("athletes", "experience"), ("professionals", "description")]
)
def test_native_form_unknown_owner_state_fields_denied(domain, step):
    module = importlib.import_module(f"apps.{domain}.forms")
    cls = (
        module.BaselineStepForm if domain == "athletes" else module.ProfessionalStepForm
    )
    form = cls(
        step,
        data={
            "operation_id": str(uuid4()),
            "expected_version": "1",
            "state": "approved",
        },
    )
    assert not form.is_valid()


def test_persian_digits_and_explicit_clear():
    module = importlib.import_module("apps.athletes.forms")
    form = module.BaselineStepForm(
        "basics",
        data={
            "operation_id": str(uuid4()),
            "expected_version": "۱",
            "height_cm": "۱۷۰.۰",
            "clear_weight_kg": "on",
        },
    )
    assert form.is_valid()
    assert form.payload() == {"height_cm": "170.0", "weight_kg": None}


def test_native_measurement_label_has_exact_accessible_name():
    from apps.athletes.forms import BaselineStepForm

    label = BaselineStepForm("basics")["height_cm"].label_tag()
    assert ">قد (سانتی‌متر)</label>" in label


def test_native_locations_use_bounded_human_lines():
    from apps.professionals.forms import ProfessionalStepForm

    form = ProfessionalStepForm(
        "locations",
        data={
            "operation_id": str(uuid4()),
            "expected_version": "1",
            "service_modes": ["in_person"],
            "languages": "fa",
            "locations": "IR | تهران | تهران | حضوری",
        },
    )
    assert form.is_valid()
    assert form.payload()["locations"] == [
        {
            "country_code": "IR",
            "region": "تهران",
            "city": "تهران",
            "modes": ["in_person"],
        }
    ]


def test_native_approximate_records_use_bounded_human_lines():
    from apps.athletes.forms import BaselineStepForm

    form = BaselineStepForm(
        "measures",
        data={
            "operation_id": str(uuid4()),
            "expected_version": "1",
            "approximate_records": "دویدن | ۱۰۰ | metres | 2026-01-01T10:00:00+03:30",
        },
    )
    assert form.is_valid()
    assert form.payload()["approximate_records"][0]["provenance"] == "self_reported"
