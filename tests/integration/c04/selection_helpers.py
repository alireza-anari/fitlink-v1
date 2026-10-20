"""Actual database session and owned-athlete fixtures for C04 selection tests."""

from uuid import uuid4

from django.utils import timezone

from tests.integration.c03.profile_helpers import create, make_actor
from tests.integration.c04.publication_helpers import module


def api():
    return module("config.use_cases.marketplace")


def require(name):
    fn = getattr(api(), name, None)
    assert callable(fn), f"Missing owned selection boundary: {name}"
    return fn


def athlete(phone="+989155550001"):
    person = make_actor(phone)
    create("athletes", person.actor, uuid4(), timezone.now())
    return person


def scope(person):
    return require("comparison_scope")(person.request, timezone.now())


def change(person, command, target, version, operation=None):
    return require("change_comparison")(
        scope(person), command, target, version, operation or uuid4(), timezone.now()
    )
