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
