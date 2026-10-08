"""Independent PostgreSQL connections serialize snapshot and consent commands."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event
from uuid import uuid4

import pytest

from apps.athletes.baseline_models import BaselineAssessment

from .baseline_helpers import command, grant, input_value, read, required, setup
from .profile_helpers import in_connection

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def race(*functions):
    barrier = Barrier(len(functions))

    def run(fn):
        def execute():
            barrier.wait(timeout=15)
            try:
                return ("ok", fn())
            except (ValueError, PermissionError) as exc:
                return ("denied", exc)

        return in_connection(execute)

    with ThreadPoolExecutor(max_workers=len(functions)) as pool:
        return list(pool.map(run, functions))


def test_concurrent_save_submit():
    ctx, row = setup()
    row = required(ctx, row)
    results = race(
        lambda: command(
            "save_baseline_step",
            ctx.actor,
            row.id,
            "goals",
            input_value({"goals": ["endurance"]}),
            row.version,
            uuid4(),
            ctx.at,
        ),
        lambda: command(
            "submit_baseline", ctx.actor, row.id, row.version, uuid4(), ctx.at
        ),
    )
    assert sorted(status for status, _ in results) == ["denied", "ok"]
    stored = BaselineAssessment.objects.get(pk=row.id)
    if stored.state == "submitted":
        assert stored.goals == ["strength"]
    else:
        assert stored.goals == ["endurance"]


def test_concurrent_save_revoke():
    ctx, row = setup()
    consent_id = grant(ctx, row)
    results = race(
        lambda: command(
            "save_baseline_step",
            ctx.actor,
            row.id,
            "basics",
            input_value({"height_cm": "170.0"}),
            row.version,
            uuid4(),
            ctx.at,
        ),
        lambda: command(
            "revoke_baseline_storage", ctx.actor, row.id, consent_id, 1, uuid4(), ctx.at
        ),
    )
    assert results[1][0] == "ok"
    assert read(ctx, row).answers["height_cm"] is None
    assert not read(ctx, row).optional_access


def test_concurrent_begin_has_one_owned_draft():
    ctx, row = setup()
    profile = row.athlete_id
    from apps.athletes.models import AthleteProfile

    version = AthleteProfile.objects.get(pk=profile).version
    results = race(
        *(
            lambda: command("begin_baseline", ctx.actor, version, uuid4(), ctx.at)
            for _ in range(2)
        )
    )
    assert all(status == "ok" for status, _ in results)
    assert all(result.id == row.id for _, result in results)
    assert (
        BaselineAssessment.objects.filter(athlete_id=profile, state="draft").count()
        == 1
    )


@pytest.mark.parametrize("first", ["save", "revoke"])
def test_save_revoke_both_committed_orders(first, monkeypatch):
    ctx, row = setup()
    consent_id = grant(ctx, row)
    wiring = __import__("config.use_cases.athlete_profile", fromlist=["append_event"])
    consent_wiring = __import__("config.use_cases.consent", fromlist=["append_event"])
    entered, release = Event(), Event()
    target = wiring if first == "save" else consent_wiring
    actual = target.append_event

    def pause(*args, **kwargs):
        result = actual(*args, **kwargs)
        entered.set()
        assert release.wait(timeout=15)
        return result

    monkeypatch.setattr(target, "append_event", pause)

    def save_call():
        return command(
            "save_baseline_step",
            ctx.actor,
            row.id,
            "basics",
            input_value({"height_cm": "170.0"}),
            row.version,
            uuid4(),
            ctx.at,
        )

    def revoke_call():
        return command(
            "revoke_baseline_storage", ctx.actor, row.id, consent_id, 1, uuid4(), ctx.at
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        first_call = pool.submit(
            in_connection, save_call if first == "save" else revoke_call
        )
        assert entered.wait(timeout=15)
        second_call = pool.submit(
            in_connection, revoke_call if first == "save" else save_call
        )
        release.set()
        first_call.result(timeout=20)
        if first == "revoke":
            with pytest.raises(PermissionError):
                second_call.result(timeout=20)
        else:
            second_call.result(timeout=20)
    assert not read(ctx, row).optional_access
    assert read(ctx, row).answers["height_cm"] is None
