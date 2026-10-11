"""Assigned staff native read transport; domain selectors recheck all authority."""

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.assets.views import private_page, valid

from .staff_forms import AccessForm
from .verification_selectors import (
    assigned_verification_detail,
    submitted_verification_queue,
)


def reference(request, key):
    from uuid import UUID

    item = request.session.get("c03_staff_refs", {}).get(key)
    return (
        {"step_up_id": UUID(item["step_up_id"]), "reason_code": item["reason_code"]}
        if item
        else None
    )


def remember(request, key, values):
    refs = dict(request.session.get("c03_staff_refs", {}))
    if key not in refs and len(refs) >= 25:
        del refs[next(iter(refs))]
    refs[key] = {
        "step_up_id": str(values["step_up_id"]),
        "reason_code": values["reason_code"],
    }
    request.session["c03_staff_refs"] = refs


def page(request, actor, verification_uuid=None):
    key = str(verification_uuid) if verification_uuid else "queue"
    path = "/staff/professional-verification/" + (
        str(verification_uuid) + "/" if verification_uuid else "queue/"
    )
    try:
        values = (
            valid(AccessForm(request.POST))
            if request.method == "POST"
            else reference(request, key)
        )
        result = None
        if values:
            if verification_uuid:
                result = assigned_verification_detail(
                    actor, verification_uuid, at=timezone.now(), **values
                )
            else:
                result = submitted_verification_queue(
                    actor, cursor=None, at=timezone.now(), **values
                )
        if request.method == "POST":
            remember(request, key, values)
            return redirect(path)
        return render(
            request,
            "professionals/staff_verification.html"
            if verification_uuid
            else "professionals/staff_verification_queue.html",
            {
                "case": result if verification_uuid else None,
                "queue": result if not verification_uuid else None,
                "form": AccessForm(),
            },
        )
    except PermissionDenied:
        return HttpResponse("دسترسی مجاز نیست.", status=403)


@private_page("staff.command")
def queue(request, actor):
    return page(request, actor)


@private_page("staff.command")
def case(request, actor, verification_uuid):
    return page(request, actor, verification_uuid)
