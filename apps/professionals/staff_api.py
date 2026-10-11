"""Exact assigned staff command transport; no ORM or local business rules."""

import json
from dataclasses import asdict
from datetime import datetime
from uuid import UUID

from django.http import HttpResponse
from django.utils import timezone
from rest_framework.response import Response  # type: ignore[import-untyped]

from config.use_cases import professional_verification as commands

from . import serializers as schema
from .api import ProfessionalView
from .staff_views import reference
from .verification_selectors import (
    assigned_verification_detail,
    assigned_verification_evidence,
    submitted_verification_queue,
)

COMMANDS = {
    "assign": (schema.StaffAssign, "assign_verification"),
    "start": (schema.StaffStart, "start_verification_review"),
    "decide": (schema.StaffDecision, "decide_verification_target"),
    "revoke": (schema.StaffRevoke, "revoke_verification_target"),
    "restrict-role": (schema.StaffRole, "restrict_professional_role"),
    "release-role-restriction": (
        schema.StaffRole,
        "release_professional_role_restriction",
    ),
}


class StaffView(ProfessionalView):
    account_action = "staff.command"
    command = "detail"

    def context(self, request, verification_uuid):
        if request.query_params:
            raise ValueError("Invalid staff read context")
        step = request.headers.get("X-Verification-Step-Up")
        reason = request.headers.get("X-Verification-Reason")
        values = (
            {"step_up_id": step, "reason_code": reason}
            if step or reason
            else reference(
                request._request,
                str(verification_uuid) if verification_uuid else "queue",
            )
        )
        serializer = schema.StaffAccess(data=values or {})
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def get(self, request, verification_uuid=None, asset_uuid=None):
        if self.command not in {"detail", "queue", "evidence"}:
            return Response({"status": "invalid"}, status=405)
        actor, values, at = (
            self.actor(request),
            self.context(request, verification_uuid),
            timezone.now(),
        )
        if self.command == "queue":
            raw = request.headers.get("X-Verification-Cursor", "")
            if len(raw) > 512:
                raise ValueError("Invalid cursor")
            cursor = None
            if raw:
                parsed = json.loads(raw)
                if (
                    not isinstance(parsed, list)
                    or len(parsed) != 2
                    or not all(isinstance(v, str) for v in parsed)
                ):
                    raise ValueError("Invalid cursor")
                cursor = (datetime.fromisoformat(parsed[0]), UUID(parsed[1]))
            result = submitted_verification_queue(actor, cursor=cursor, at=at, **values)
        elif asset_uuid is not None:
            result = assigned_verification_evidence(
                actor, verification_uuid, asset_uuid, at=at, **values
            )
            response = HttpResponse(result.content, content_type=result.content_type)
            response["Content-Disposition"] = (
                'inline; filename="evidence.png"'
                if result.content_type == "image/png"
                else 'inline; filename="evidence.jpg"'
            )
            return response
        else:
            result = assigned_verification_detail(
                actor, verification_uuid, at=at, **values
            )
        return Response(asdict(result))

    def post(self, request, verification_uuid):
        if self.command not in COMMANDS:
            return Response({"status": "invalid"}, status=405)
        serializer, name = COMMANDS[self.command]
        values = self.payload(request, serializer)
        result = getattr(commands, name)(
            self.actor(request),
            verification_uuid=verification_uuid,
            at=timezone.now(),
            **values,
        )
        return Response(asdict(result))
