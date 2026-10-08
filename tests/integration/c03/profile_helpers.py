"""Real account sessions and synthetic profile fixtures; no auth mocks."""

import importlib
import importlib.util
from datetime import date
from types import SimpleNamespace
from uuid import uuid4

from django.contrib.sessions.backends.db import SessionStore
from django.db import connections, transaction
from django.http import HttpRequest
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.sessions import issue_session, resolve_session
from apps.governance.audit import append_event
from apps.governance.flag_models import FeatureFlag


def module(path):
    assert importlib.util.find_spec(path), f"Missing owned profile contract: {path}"
    return importlib.import_module(path)


def create(label, actor, operation_id, at):
    commands = module(f"config.use_cases.{label[:-1]}_profile")
    return getattr(commands, f"create_{label[:-1]}_profile")(actor, operation_id, at)


def read(label, actor, at):
    selectors = module(f"apps.{label}.selectors")
    return getattr(selectors, f"own_{label[:-1]}_profile")(actor, at)


def profile_model(label):
    models = importlib.import_module(f"apps.{label}.models")
    return models.AthleteProfile if label == "athletes" else models.ProfessionalProfile


def make_actor(phone="+989123456780", *, enable_registration=True):
    at = timezone.now()
    user = User.objects.create_user(
        phone,
        birth_date=date(1990, 1, 1),
        adult_attested_at=at,
        adult_attestation_version="adult-v1",
        timezone="Europe/London",
    )
    request = HttpRequest()
    request.session = SessionStore()
    with transaction.atomic():
        issue_session(request, user, "normal", at, append_event)
    actor = resolve_session(request, at)
    assert actor is not None
    FeatureFlag.objects.update_or_create(
        key="professional_registration", defaults={"enabled": enable_registration}
    )
    return SimpleNamespace(user=user, actor=actor, at=at, request=request)


def in_connection(fn):
    connections.close_all()
    try:
        return fn()
    finally:
        connections.close_all()


def independent_create(label, actor, barrier):
    def run():
        barrier.wait(timeout=10)
        return create(label, actor, uuid4(), timezone.now())

    return in_connection(run)
