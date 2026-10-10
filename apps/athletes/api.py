"""Session/CSRF owner adapters for installed athlete contracts."""

from dataclasses import asdict

from django.utils import timezone
from rest_framework.response import Response  # type: ignore[import-untyped]

from apps.assets.api import UploadView
from config.use_cases import athlete_profile as commands

from . import serializers as schema
from .contracts import BaselineStepInput, ProfileConflict, ProfileNotFound
from .selectors import own_athlete_profile


class AthleteView(UploadView):
    account_action = "athlete.profile_read"

    def handle_exception(self, error):
        if isinstance(error, ProfileConflict):
            return Response({"status": "conflict"}, status=409)
        return super().handle_exception(error)


class ProfileView(AthleteView):
    def get(self, request):
        return Response(
            asdict(own_athlete_profile(self.actor(request), timezone.now()))
        )

    def post(self, request):
        values = self.payload(request, schema.Create)
        actor, at = self.actor(request), timezone.now()
        exists = True
        try:
            own_athlete_profile(actor, at)
        except ProfileNotFound:
            exists = False
        result = commands.create_athlete_profile(actor, at=at, **values)
        return Response(asdict(result), status=200 if exists else 201)


class DraftView(AthleteView):
    account_action = "athlete.baseline_write"

    def post(self, request):
        result = commands.begin_baseline(
            self.actor(request),
            at=timezone.now(),
            **self.payload(request, schema.Draft),
        )
        return Response(asdict(result))


class BaselineView(AthleteView):
    account_action = "athlete.baseline_read"

    def get(self, request, baseline_uuid):
        return Response(
            asdict(
                commands.own_baseline(
                    self.actor(request), baseline_uuid, timezone.now()
                )
            )
        )


class StepView(AthleteView):
    account_action = "athlete.baseline_write"

    def post(self, request, baseline_uuid, step):
        values = self.payload(request, schema.Step)
        result = commands.save_baseline_step(
            self.actor(request),
            baseline_uuid,
            step,
            BaselineStepInput(values.pop("values")),
            at=timezone.now(),
            **values,
        )
        return Response(asdict(result))


class BaselineCommandView(AthleteView):
    account_action = "athlete.baseline_write"
    command = ""

    def post(self, request, baseline_uuid):
        function = {
            "submit": commands.submit_baseline,
            "correct": commands.correct_baseline,
            "clear-optional": commands.clear_optional_baseline,
            "storage-consent": commands.grant_baseline_storage,
            "revoke": commands.revoke_baseline_storage,
        }[self.command]
        serializer = (
            schema.Grant
            if self.command == "storage-consent"
            else schema.Revoke
            if self.command == "revoke"
            else schema.Command
        )
        result = function(
            self.actor(request),
            baseline_uuid,
            at=timezone.now(),
            **self.payload(request, serializer),
        )
        return Response(
            asdict(result)
            if hasattr(result, "__dataclass_fields__")
            else {"consent_uuid": result}
        )
