"""Explicit assigned staff transport; no ORM or business authority in adapters."""

from dataclasses import asdict
from uuid import UUID

from django.http import HttpResponse
from django.utils import timezone
from rest_framework.response import Response

from .api import ProfessionalView
from .verification_selectors import (
    assigned_verification_detail,
    assigned_verification_evidence,
    submitted_verification_queue,
)


class StaffView(ProfessionalView):
    account_action = "staff.command"
    command = "detail"

    def context(self, request):
        return {
            "step_up_id": UUID(request.headers.get("X-Verification-Step-Up", "")),
            "reason_code": request.headers.get("X-Verification-Reason", ""),
        }

    def get(self, request, verification_uuid=None, asset_uuid=None):
        actor, values, at = self.actor(request), self.context(request), timezone.now()
        if self.command == "queue":
            result = submitted_verification_queue(actor, cursor=None, at=at, **values)
        elif asset_uuid is not None:
            result = assigned_verification_evidence(
                actor, verification_uuid, asset_uuid, at=at, **values
            )
            return HttpResponse(result.content, content_type=result.content_type)
        else:
            result = assigned_verification_detail(
                actor, verification_uuid, at=at, **values
            )
        return Response(asdict(result))

    def post(self, request, verification_uuid):
        return Response({"status": "invalid"}, status=400)
