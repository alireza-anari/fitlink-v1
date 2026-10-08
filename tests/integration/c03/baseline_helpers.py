"""Real account and command fixtures; no mocked consent or authorization."""

from uuid import uuid4

from django.test import override_settings

from .profile_helpers import create, make_actor, module


def command(name, *args, **kwargs):
    composition = module("config.use_cases.athlete_profile")
    assert hasattr(composition, name), f"Missing baseline command: {name}"
    return getattr(composition, name)(*args, **kwargs)


def input_value(values):
    contracts = module("apps.athletes.contracts")
    assert hasattr(contracts, "BaselineStepInput"), "Missing bounded baseline input"
    return contracts.BaselineStepInput(values)


def setup():
    ctx = make_actor()
    profile = create("athletes", ctx.actor, uuid4(), ctx.at)
    row = command("begin_baseline", ctx.actor, profile.version, uuid4(), ctx.at)
    return ctx, row


def save(ctx, row, step, values, operation_id=None):
    return command(
        "save_baseline_step",
        ctx.actor,
        row.id,
        step,
        input_value(values),
        row.version,
        operation_id or uuid4(),
        ctx.at,
    )


def required(ctx, row):
    for step, values in [
        ("goals", {"goals": ["strength"]}),
        ("experience", {"experience": "beginner"}),
        ("availability", {"available_days": [1, 3]}),
        ("facilities", {"facilities": ["home"], "equipment": ["bodyweight"]}),
    ]:
        row = save(ctx, row, step, values)
    return row


def grant(ctx, row, operation_id=None):
    with override_settings(BASELINE_STORAGE_CONSENT_SECONDS=86400):
        return command(
            "grant_baseline_storage",
            ctx.actor,
            row.id,
            row.version,
            True,
            operation_id or uuid4(),
            ctx.at,
        )


def read(ctx, row, at=None):
    selectors = module("apps.athletes.selectors")
    assert hasattr(selectors, "own_baseline"), "Missing current baseline selector"
    return selectors.own_baseline(ctx.actor, row.id, at or ctx.at)
