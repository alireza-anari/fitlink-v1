from uuid import uuid4

import pytest
from django.db import transaction
from django.utils import timezone

from apps.professionals import contracts
from apps.professionals.models import (
    AssistantMembership,
    ProfessionalProfile,
    ProfessionalRole,
)
from config.use_cases import professional_profile

from .profile_helpers import make_actor

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def owner(phone="+989123456780"):
    s = make_actor(phone)
    s.dto = professional_profile.create_professional_profile(s.actor, uuid4(), s.at)
    s.profile = ProfessionalProfile.objects.get(pk=s.dto.id)
    return s


def save(s, step, values, version=None, operation=None):
    assert hasattr(professional_profile, "save_professional_step"), (
        "Resumable setup absent"
    )
    s.profile.refresh_from_db()
    return professional_profile.save_professional_step(
        s.actor,
        step,
        contracts.ProfessionalStepInput(values),
        version or s.profile.version,
        operation or uuid4(),
        timezone.now(),
    )


@pytest.mark.parametrize(
    "roles", [["coach"], ["nutritionist"], ["coach", "nutritionist"]]
)
def test_coach_nutritionist_both_are_rows_not_auth(roles):
    s = owner()
    prior = s.user.auth_version
    dto = save(
        s, "identity", {"display_name": "علی", "identity_name": "علی", "roles": roles}
    )
    assert set(
        ProfessionalRole.objects.filter(
            profile=s.profile, declared_active=True
        ).values_list("role", flat=True)
    ) == set(roles)
    s.user.refresh_from_db()
    assert s.user.auth_version == prior
    assert not s.user.is_staff
    assert dto.state == "setup"


def test_resume_and_in_person_location_gate():
    s = owner()
    save(
        s,
        "identity",
        {"display_name": "علی", "identity_name": "علی", "roles": ["coach"]},
    )
    with pytest.raises(ValueError):
        save(s, "locations", {"service_modes": ["in_person"], "locations": []})
    save(
        s,
        "description",
        {"biography": "شرح", "experience_years": 2, "specialties": ["قدرت"]},
    )
    save(
        s,
        "locations",
        {"service_modes": ["online"], "languages": ["fa"], "locations": []},
    )
    dto = save(s, "preview", {})
    assert dto.state == "private_ready"
    assert dto.fields["biography"] == "شرح"
    assert dto.roles[0].role == "coach"
    assert not dto.locations
    dto = save(
        s,
        "locations",
        {
            "service_modes": ["in_person"],
            "locations": [
                {
                    "country_code": "IR",
                    "region": "تهران",
                    "city": "تهران",
                    "modes": ["in_person"],
                }
            ],
        },
    )
    assert dto.locations[0].city == "تهران"


def test_version_receipt_payload_and_current_projection():
    s = owner()
    operation = uuid4()
    dto = save(s, "identity", {"display_name": "الف"}, version=1, operation=operation)
    assert (
        save(
            s, "identity", {"display_name": "الف"}, version=1, operation=operation
        ).version
        == dto.version
    )
    with pytest.raises(contracts.ProfileConflict):
        save(s, "identity", {"display_name": "ب"}, version=1, operation=operation)
    with pytest.raises(contracts.ProfileConflict):
        save(s, "identity", {"display_name": "ب"}, version=1)
    save(s, "identity", {"display_name": "ب"})
    assert (
        save(
            s, "identity", {"display_name": "الف"}, version=1, operation=operation
        ).fields["display_name"]
        == "ب"
    )


def test_cosmetic_change_retains_binding():
    s = owner()
    save(s, "identity", {"identity_name": "علی", "roles": ["coach", "nutritionist"]})
    s.profile.refresh_from_db()
    binding = (
        s.profile.identity_evidence_revision,
        list(
            s.profile.roles.order_by("role").values_list(
                "evidence_revision", "decision_version", "declaration_version"
            )
        ),
    )
    for step, values in [
        ("identity", {"display_name": "نام"}),
        (
            "description",
            {"biography": "شرح", "specialties": ["قدرت"], "experience_years": 10},
        ),
        ("locations", {"service_modes": ["online"], "languages": ["fa", "en"]}),
        ("branding", {"accent_color": "#aabbcc", "welcome_message": "سلام"}),
    ]:
        save(s, step, values)
    s.profile.refresh_from_db()
    assert binding == (
        s.profile.identity_evidence_revision,
        list(
            s.profile.roles.order_by("role").values_list(
                "evidence_revision", "decision_version", "declaration_version"
            )
        ),
    )


def test_assistant_role_has_no_setup_access():
    s = owner()
    other = make_actor("+989123456781")
    AssistantMembership.objects.create(profile=s.profile, assistant=other.user)
    with pytest.raises(contracts.ProfileNotFound):
        with transaction.atomic():
            professional_profile.save_professional_step(
                other.actor,
                "identity",
                contracts.ProfessionalStepInput({"display_name": "bad"}),
                1,
                uuid4(),
                timezone.now(),
            )
    s.profile.refresh_from_db()
    assert s.profile.display_name == ""
