"""Case-bound native recovery commands; authority stays in composition."""

from uuid import UUID

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from config.use_cases import recovery

from .forms import (
    StaffAuthorityForm,
    StaffDecisionForm,
    StaffEvidenceForm,
    StaffVersionForm,
)
from .views import UI_ERRORS, current_actor, error_text, html_view


@html_view
def staff_recovery_page(request, request_uuid: UUID):
    actor = current_actor(request, "staff.command")
    if not actor:
        return redirect("/accounts/entry/")
    data = request.POST if request.method == "POST" else request.GET
    authority = StaffAuthorityForm(data)
    if not authority.is_valid():
        return HttpResponse("درخواست در دسترس نیست.", status=404)
    step, reason = (
        authority.cleaned_data["step_up_id"],
        authority.cleaned_data["reason_code"],
    )
    evidence, decision = StaffEvidenceForm(), StaffDecisionForm()
    message = ""
    try:
        # Every read and command independently requires named capability,
        # assignment, case-bound fresh step-up and non-self authority.
        row = recovery.recovery_detail(
            actor, request_uuid, step, reason, timezone.now()
        )
    except PermissionError:
        return HttpResponse("درخواست در دسترس نیست.", status=404)
    except UI_ERRORS:
        return HttpResponse("درخواست موقتاً در دسترس نیست.", status=503)
    try:
        if request.method == "POST":
            version = StaffVersionForm(data)
            if not version.is_valid():
                raise ValueError("Invalid case version")
            common = {
                "actor": actor,
                "request_uuid": request_uuid,
                "expected_version": version.cleaned_data["expected_version"],
                "step_up_id": step,
                "reason_code": reason,
                "at": timezone.now(),
            }
            action = data.get("action")
            if action == "evidence":
                evidence = StaffEvidenceForm(data)
                if evidence.is_valid():
                    recovery.add_recovery_evidence(**common, **evidence.cleaned_data)
                    evidence = StaffEvidenceForm()
                    message = "فرادادهٔ بررسی ثبت شد."
            elif action == "decision":
                decision = StaffDecisionForm(data)
                if decision.is_valid():
                    recovery.decide_recovery(**common, **decision.cleaned_data)
                    decision = StaffDecisionForm()
                    message = "تصمیم ثبت شد."
            elif action == "apply":
                recovery.apply_recovery(**common)
                message = "تغییر مجاز اعمال شد."
            else:
                raise ValueError("Invalid action")
            row = recovery.recovery_detail(
                actor, request_uuid, step, reason, timezone.now()
            )
    except PermissionError:
        return HttpResponse("درخواست در دسترس نیست.", status=404)
    except UI_ERRORS as exc:
        # No domain exception text or claimant/evidence data is reflected.
        evidence.add_error(None, error_text(exc))
    return render(
        request,
        "accounts/staff_recovery.html",
        {
            "case_id": row.id,
            "case_state": row.state,
            "version": row.version,
            "step_up_id": step,
            "reason_code": reason,
            "evidence_form": evidence,
            "decision_form": decision,
            "message": message,
        },
    )
