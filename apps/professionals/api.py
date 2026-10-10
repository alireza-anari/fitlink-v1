"""Parse/call/render owner setup and verification adapters."""

from dataclasses import asdict
from datetime import date
from uuid import UUID

from django.utils import timezone
from rest_framework.response import Response  # type: ignore[import-untyped]

from apps.assets.api import UploadView
from config.use_cases import (
    professional_profile as commands,
)
from config.use_cases import (
    professional_verification as verification,
)

from . import serializers as schema
from .contracts import (
    CredentialInput,
    ProfessionalStepInput,
    ProfileConflict,
    ProfileNotFound,
)
from .selectors import own_professional_profile, own_verification, owner_preview


def profile_payload(result):
    values = asdict(result)
    values["roles"] = [
        {
            "id": r.id,
            "role": r.role,
            "declared_active": r.declared_active,
            "version": r.version,
        }
        for r in result.roles
    ]
    return values


def credential_values(values):
    values = dict(values)
    for name in ("issued_on", "expires_on"):
        if values.get(name) is not None:
            if not isinstance(values[name], str):
                raise ValueError("Invalid credential date")
            values[name] = date.fromisoformat(values[name])
    if values.get("source_asset") is not None:
        if not isinstance(values["source_asset"], str):
            raise ValueError("Invalid private asset")
        values["source_asset"] = UUID(values["source_asset"])
    return CredentialInput(values)


class ProfessionalView(UploadView):
    account_action = "professional.profile_read"

    def handle_exception(self, error):
        if isinstance(error, ProfileConflict):
            return Response({"status": "conflict"}, status=409)
        return super().handle_exception(error)


class ProfileView(ProfessionalView):
    def get(self, request):
        return Response(
            profile_payload(
                own_professional_profile(self.actor(request), timezone.now())
            )
        )

    def post(self, request):
        actor, at = self.actor(request), timezone.now()
        values = self.payload(request, schema.Create)
        exists = True
        try:
            own_professional_profile(actor, at)
        except ProfileNotFound:
            exists = False
        result = commands.create_professional_profile(actor, at=at, **values)
        return Response(profile_payload(result), status=200 if exists else 201)


class StepView(ProfessionalView):
    account_action = "professional.profile_write"

    def post(self, request, step):
        values = self.payload(request, schema.Step)
        if step == "branding":
            for name in ("avatar", "cover", "logo"):
                if values["values"].get(name) is not None:
                    if not isinstance(values["values"][name], str):
                        raise ValueError("Invalid private asset")
                    values["values"][name] = UUID(values["values"][name])
        result = commands.save_professional_step(
            self.actor(request),
            step,
            ProfessionalStepInput(values.pop("values")),
            at=timezone.now(),
            **values,
        )
        return Response(profile_payload(result))


class PreviewView(ProfessionalView):
    def get(self, request):
        return Response(asdict(owner_preview(self.actor(request), timezone.now())))


class CredentialView(ProfessionalView):
    account_action = "professional.profile_write"
    command = "create"

    def post(self, request, credential_uuid=None):
        values = self.payload(
            request,
            schema.Credential
            if self.command == "create"
            else schema.Revision
            if self.command == "revise"
            else schema.Command,
        )
        if self.command != "withdraw":
            values["payload"] = credential_values(values.pop("values"))
        function = {
            "create": commands.create_credential,
            "revise": commands.revise_credential,
            "withdraw": commands.withdraw_credential,
        }[self.command]
        if credential_uuid is not None:
            values["credential_uuid"] = credential_uuid
        return Response(
            asdict(function(self.actor(request), at=timezone.now(), **values))
        )


class VerificationView(ProfessionalView):
    def get(self, request, verification_uuid):
        return Response(
            asdict(
                own_verification(self.actor(request), verification_uuid, timezone.now())
            )
        )


class VerificationCommandView(ProfessionalView):
    account_action = "professional.profile_write"
    command = "prepare"

    def post(self, request, verification_uuid=None):
        values = self.payload(
            request,
            schema.Prepare
            if self.command == "prepare"
            else schema.Withdraw
            if self.command == "withdraw"
            else schema.Command,
        )
        if "requested_targets" in values:
            values["requested_targets"] = tuple(values["requested_targets"])
        if verification_uuid is not None:
            values["verification_uuid"] = verification_uuid
        function = {
            "prepare": verification.prepare_verification,
            "submit": verification.submit_verification,
            "withdraw": verification.withdraw_verification_target,
        }[self.command]
        return Response(
            asdict(function(self.actor(request), at=timezone.now(), **values))
        )
