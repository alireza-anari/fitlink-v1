"""Native owner PRG pages backed by installed services and safe selectors."""

from uuid import UUID

from django.conf import settings
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.assets.views import CommandForm, private_page, valid
from config.use_cases import athlete_profile as commands

from .contracts import BaselineStepInput, ProfileConflict, ProfileNotFound
from .forms import BaselineStepForm, ConsentForm, RevokeConsentForm
from .selectors import own_athlete_profile
from .validation import STEP_FIELDS


@private_page("athlete.profile_read", (ProfileConflict,))
def setup(request, actor):
    at = timezone.now()
    try:
        profile = own_athlete_profile(actor, at)
    except ProfileNotFound:
        profile = None
    if request.method == "POST":
        form = CommandForm(request.POST)
        values = form.command()
        action = request.POST.get("action")
        if action == "create":
            values.pop("expected_version", None)
            commands.create_athlete_profile(actor, at=at, **values)
            return redirect("/athlete/setup/")
        if action == "begin":
            result = commands.begin_baseline(
                actor,
                expected_profile_version=values.pop("expected_version"),
                at=at,
                **values,
            )
            return redirect(f"/athlete/baseline/{result.id}/")
        raise ValueError("Invalid action")
    return render(
        request,
        "athletes/setup.html",
        {
            "profile": profile,
            "form": CommandForm(
                initial={"expected_version": profile.version if profile else None}
            ),
        },
    )


@private_page("athlete.baseline_read", (ProfileConflict,))
def baseline_page(request, actor, baseline_uuid):
    row = commands.own_baseline(actor, baseline_uuid, timezone.now())
    step = request.GET.get("step", "goals")
    if step not in STEP_FIELDS:
        raise ValueError("Invalid step")
    consent_key = f"c03_consent:{actor.user_uuid}:{baseline_uuid}"
    receipts = request.session.get(consent_key, [])
    if isinstance(receipts, str):
        receipts = [receipts]
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "save":
            form = BaselineStepForm(step, request.POST)
            valid(form)
            commands.save_baseline_step(
                actor,
                baseline_uuid,
                step,
                BaselineStepInput(form.payload()),
                at=timezone.now(),
                **form.command(),
            )
        elif action in {"submit", "correct", "clear"}:
            form = CommandForm(request.POST)
            function = {
                "submit": commands.submit_baseline,
                "correct": commands.correct_baseline,
                "clear": commands.clear_optional_baseline,
            }[action]
            result = function(actor, baseline_uuid, at=timezone.now(), **form.command())
            return redirect(f"/athlete/baseline/{result.id}/?step={step}")
        elif action == "grant":
            form = ConsentForm(request.POST)
            data = valid(form)
            identifier = commands.grant_baseline_storage(
                actor,
                baseline_uuid,
                confirmed=data["confirmed"],
                at=timezone.now(),
                **form.command(),
            )
            request.session[consent_key] = [*receipts, str(identifier)]
        elif action == "revoke":
            form = RevokeConsentForm(request.POST)
            data = valid(form)
            commands.revoke_baseline_storage(
                actor,
                baseline_uuid,
                data["consent_uuid"],
                data["expected_consent_version"],
                data["operation_id"],
                timezone.now(),
            )
            request.session[consent_key] = [
                r for r in receipts if r != str(data["consent_uuid"])
            ]
        else:
            raise ValueError("Invalid action")
        return redirect(f"/athlete/baseline/{baseline_uuid}/?step={step}")
    initial = dict(row.answers)
    initial["approximate_records"] = "\n".join(
        " | ".join(r[name] for name in ("label", "value", "unit", "observed_at"))
        for r in initial.get("approximate_records", [])
    )
    initial["expected_version"] = row.version
    stored = receipts[-1] if receipts else None
    consent = ConsentForm(
        initial={
            "expected_version": row.version,
            "consent_uuid": UUID(stored) if stored else None,
            "expected_consent_version": 1,
        }
    )
    return render(
        request,
        "athletes/baseline.html",
        {
            "baseline": row,
            "step": step,
            "steps": [
                (
                    name,
                    {
                        "basics": "اندازه‌ها",
                        "goals": "هدف‌ها",
                        "experience": "تجربه",
                        "availability": "زمان",
                        "facilities": "امکانات",
                        "context": "سبک زندگی",
                        "habits": "عادت‌ها",
                        "measures": "اندازه‌ها و رکوردها",
                    }[name],
                )
                for name in STEP_FIELDS
            ],
            "form": BaselineStepForm(step, initial=initial),
            "command_form": CommandForm(initial={"expected_version": row.version}),
            "consent_form": consent,
            "receipts": receipts,
            "revoke_form": RevokeConsentForm(
                initial={
                    "consent_uuid": UUID(stored) if stored else None,
                    "expected_consent_version": 1,
                }
            ),
            "can_revoke": bool(stored),
            "storage_seconds": getattr(
                settings, "BASELINE_STORAGE_CONSENT_SECONDS", None
            ),
        },
    )
