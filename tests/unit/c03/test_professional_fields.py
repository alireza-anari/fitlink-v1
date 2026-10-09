import importlib
from uuid import uuid4

import pytest

pytestmark = pytest.mark.unit


def normalize(step, values):
    from apps.professionals import contracts

    assert hasattr(contracts, "ProfessionalStepInput"), "Professional fields absent"
    module = importlib.import_module("apps.professionals.validation")
    return module.normalize_step(step, contracts.ProfessionalStepInput(values))


def test_persian_fields_and_both_normalize_to_two_roles():
    value = normalize(
        "identity",
        {
            "display_name": " علی ",
            "identity_name": "علی",
            "roles": ["coach", "nutritionist"],
        },
    )
    assert value["display_name"] == "علی"
    assert value["roles"] == ["coach", "nutritionist"]


@pytest.mark.parametrize(
    ("step", "values"),
    [
        ("identity", {"roles": ["both"]}),
        ("identity", {"display_name": "<b>x</b>"}),
        ("identity", {"approved_roles": ["coach"]}),
        ("description", {"experience_years": True}),
        ("description", {"experience_years": 81}),
        ("description", {"specialties": ["a"] * 11}),
        (
            "locations",
            {"locations": [{"region": "تهران", "city": "تهران", "address": "x"}]},
        ),
        ("locations", {"languages": ["../../etc"]}),
        ("locations", {"service_modes": []}),
        ("branding", {"accent_color": "red;url(x)"}),
        ("branding", {"avatar": str(uuid4())}),
        ("preview", {"slug": "public"}),
    ],
)
def test_invalid_or_future_fields_denied(step, values):
    with pytest.raises(ValueError):
        normalize(step, values)


def test_online_only_needs_no_fake_location():
    assert (
        normalize("locations", {"service_modes": ["online"], "locations": []})[
            "locations"
        ]
        == []
    )


def test_all_declarations_can_be_deactivated_during_private_setup():
    assert normalize("identity", {"roles": []}) == {"roles": []}
