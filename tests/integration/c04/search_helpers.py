"""Corpus uses real account, setup, evidence, decisions and explicit publication."""

from itertools import count

import pytest
from django.utils import timezone

from tests.integration.c03 import verification_helpers
from tests.integration.c03.profile_helpers import make_actor
from tests.integration.c03.test_professional_setup import owner, save
from tests.integration.c03.test_verification_decisions import (
    approved,
    decision,
    review,
)
from tests.integration.c04.publication_helpers import configure, confirm, prepare
from tests.integration.c04.test_postgresql_search import search
from tests.integration.c04.test_public_projection import api


@pytest.fixture
def corpus(settings, monkeypatch):
    numbers = count(1000)

    def phone():
        return f"+98912{next(numbers):07d}"

    monkeypatch.setattr(
        verification_helpers,
        "make_actor",
        lambda *args, **kwargs: make_actor(phone(), **kwargs),
    )

    def create(
        name="کیان",
        biography="مربی قدرت",
        specialties=("قدرت",),
        locations=(),
        modes=("online",),
        languages=("fa",),
        experience=8,
        roles=("coach",),
        valid_until=None,
        nutritionist_expiry=None,
    ):
        def new_owner():
            s = owner(phone())
            save(
                s,
                "description",
                {
                    "biography": biography,
                    "specialties": list(specialties),
                    "experience_years": experience,
                },
            )
            return s

        def configured_save(s, step, values, *args, **kwargs):
            if step == "identity":
                values = {**values, "display_name": name}
            elif step == "locations":
                values = {
                    **values,
                    "locations": list(locations),
                    "service_modes": list(modes),
                    "languages": list(languages),
                }
            return save(s, step, values, *args, **kwargs)

        with monkeypatch.context() as patch:
            patch.setattr(verification_helpers, "owner", new_owner)
            patch.setattr(verification_helpers, "save", configured_save)
            if nutritionist_expiry is None:
                subject = approved(settings)
            else:
                subject = review(settings, nutritionist_expiry=nutritionist_expiry)
                for role in ("identity", "coach", "nutritionist"):
                    decision(subject, role)
        configure(settings)
        draft = prepare(
            subject,
            fields=(
                "display_name",
                "biography",
                "specialties",
                "experience_years",
                "service_modes",
                "languages",
                "locations",
            ),
            roles=roles,
            valid_until=valid_until,
        )
        confirm(subject, draft)
        api().refresh_public_projection(subject.profile.id, timezone.now())
        return subject, draft

    return create


def names(page):
    return [row.as_public_dict()["display_name"] for row in page.items]


__all__ = ["corpus", "names", "search"]
