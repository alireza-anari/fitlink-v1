"""Native command transport; fresh selectors own every assigned case fact."""

from dataclasses import asdict
from datetime import datetime
from uuid import UUID

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.assets.views import private_page, valid
from config.use_cases import professional_verification as commands

from .contracts import ProfileConflict
from .staff_forms import (
    AccessForm,
    DecisionForm,
    QueueForm,
    RevokeForm,
    RoleForm,
    StartForm,
)
from .verification_selectors import (
    assigned_verification_detail,
    submitted_verification_queue,
)

COMMANDS = {
    "start": (StartForm, "start_verification_review"),
    "decide": (DecisionForm, "decide_verification_target"),
    "revoke": (RevokeForm, "revoke_verification_target"),
    "restrict": (RoleForm, "restrict_professional_role"),
    "release": (RoleForm, "release_professional_role_restriction"),
}


def reference(request, key):
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
        if request.GET:
            raise ValueError("Invalid staff read context")
        action = request.POST.get("action", "open")
        if request.method == "POST" and action != "open":
            if verification_uuid is None or action not in COMMANDS:
                raise ValueError("Invalid staff action")
            form_type, command = COMMANDS[action]
            values = valid(form_type(request.POST))
            getattr(commands, command)(
                actor, verification_uuid=verification_uuid, at=timezone.now(), **values
            )
            remember(request, key, values)
            return redirect(path)
        values = (
            valid((AccessForm if verification_uuid else QueueForm)(request.POST))
            if request.method == "POST"
            else reference(request, key)
        )
        result = None
        cursor = None
        if not verification_uuid:
            if request.method == "POST" and values:
                if values.get("cursor_at"):
                    cursor = (values.pop("cursor_at"), values.pop("cursor_uuid"))
                else:
                    values.pop("cursor_at", None)
                    values.pop("cursor_uuid", None)
                request.session["c03_staff_queue_cursor"] = (
                    [cursor[0].isoformat(), str(cursor[1])] if cursor else None
                )
            else:
                stored = request.session.get("c03_staff_queue_cursor")
                if stored:
                    cursor = (datetime.fromisoformat(stored[0]), UUID(stored[1]))
        if values:
            if verification_uuid:
                result = assigned_verification_detail(
                    actor, verification_uuid, at=timezone.now(), **values
                )
            else:
                result = submitted_verification_queue(
                    actor, cursor=cursor, at=timezone.now(), **values
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
                "form": AccessForm() if verification_uuid else QueueForm(),
                **(case_forms(result, values) if verification_uuid and result else {}),
                "next_form": QueueForm(
                    initial={
                        **(values or {}),
                        "cursor_at": result.next_cursor[0],
                        "cursor_uuid": result.next_cursor[1],
                    }
                )
                if not verification_uuid and result and result.next_cursor
                else None,
            },
        )
    except PermissionDenied:
        return HttpResponse("دسترسی مجاز نیست.", status=403)


def case_forms(result, values):
    """Only immutable selector facts enter forms; commands validate submitted input."""
    access = {"step_up_id": values["step_up_id"], "reason_code": "verification_review"}
    rows = []
    for target in result.review_targets:
        common = {
            **access,
            "expected_case_version": result.version,
            "target_uuid": target.id,
            "expected_target_version": target.version,
            "expected_binding": asdict(target.binding),
            "reason_code": "credentials_approved",
        }
        role = {
            **access,
            "expected_case_version": result.version,
            "role_uuid": target.role_uuid,
            "expected_role_version": target.role_version,
            "expected_restriction_token": asdict(target.binding.restriction_token)
            if target.binding.restriction_token
            else None,
        }

        def form(cls, initial, action, target=target):
            return cls(initial=initial, auto_id=f"id_{action}_{target.id}_%s")

        rows.append(
            {
                "target": target,
                "restricted": bool(
                    target.binding.restriction_token
                    and any(
                        not released
                        for _, _, released in target.binding.restriction_token.episodes
                    )
                ),
                "decision_form": form(DecisionForm, common, "decide"),
                "revoke_form": form(
                    RevokeForm,
                    {
                        **common,
                        "effective_approval_uuid": target.effective_approval_uuid,
                        "reason_code": "evidence_revoked",
                    },
                    "revoke",
                ),
                "restrict_form": form(
                    RoleForm, {**role, "reason_code": "role_restricted"}, "restrict"
                ),
                "release_form": form(
                    RoleForm, {**role, "reason_code": "restriction_removed"}, "release"
                ),
            }
        )
    return {
        "review_rows": rows,
        "start_form": StartForm(initial={**access, "expected_version": result.version}),
    }


@private_page("staff.command", conflicts=(ProfileConflict,))
def queue(request, actor):
    return page(request, actor)


@private_page("staff.command", conflicts=(ProfileConflict,))
def case(request, actor, verification_uuid):
    return page(request, actor, verification_uuid)
