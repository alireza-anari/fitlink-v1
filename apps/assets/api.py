"""Bounded same-origin private upload parsing."""

from dataclasses import asdict
from io import BytesIO

from django.http import JsonResponse
from django.utils import timezone
from rest_framework import exceptions, parsers  # type: ignore[import-untyped]
from rest_framework.response import Response  # type: ignore[import-untyped]

from apps.accounts.api import PrivateView
from config.use_cases import profile_assets

from . import serializers as schema
from .contracts import UploadConflict, UploadQuota, UploadUnavailable
from .storage import limited_spool
from .validation import MAX_BYTES, validate_declaration, validate_filename


class BoundedMultipartParser(parsers.MultiPartParser):
    def parse(self, stream, media_type=None, parser_context=None):
        context = parser_context or {}
        request = context.get("request")
        if request is None:
            raise exceptions.ParseError("Invalid request")
        try:
            with limited_spool(stream, MAX_BYTES) as body:
                body.seek(0, 2)
                size = body.tell()
                body.seek(0)
                request.META["CONTENT_LENGTH"] = str(size)
                return super().parse(body, media_type, context)
        except ValueError:
            raise exceptions.ParseError("Invalid request") from None


class UploadView(PrivateView):
    account_action = "asset.owner_write"

    def handle_exception(self, error):
        if isinstance(error, LookupError):
            return Response({"status": "not_found"}, status=404)
        if isinstance(error, UploadConflict):
            return Response({"status": "conflict"}, status=409)
        if isinstance(error, UploadQuota):
            return Response({"status": "throttled"}, status=429)
        if isinstance(error, UploadUnavailable):
            return Response({"status": "unavailable"}, status=503)
        return super().handle_exception(error)


class BeginUploadView(UploadView):
    def post(self, request):
        data = self.payload(request, schema.BeginUpload)
        result = profile_assets.begin_profile_upload(
            self.actor(request), at=timezone.now(), **data
        )
        return Response(asdict(result), status=201)


class UploadBodyView(UploadView):
    parser_classes = [BoundedMultipartParser]

    def dispatch(self, request, *args, **kwargs):
        # Bound before CSRF's native multipart parsing, including on WSGI.
        if request.method == "POST":
            try:
                with limited_spool(request, MAX_BYTES) as content:
                    request._body = content.read()
                    request._stream = BytesIO(request._body)
            except ValueError:
                result = JsonResponse({"status": "invalid"}, status=400)
                result["Cache-Control"] = "no-store"
                return result
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, asset_uuid):
        if request._request.content_type != "multipart/form-data":
            raise exceptions.ParseError("Invalid request")
        parsed = BoundedMultipartParser().parse(
            BytesIO(request._request.body),
            request.META.get("CONTENT_TYPE"),
            {**self.get_parser_context(request), "request": request},
        )
        try:
            data = parsed.data.copy()
            data.update(parsed.files)
            if any(len(data.getlist(key)) != 1 for key in data):
                raise exceptions.ParseError("Invalid request")
            value = schema.UploadBody(data=data)
            value.is_valid(raise_exception=True)
            values = value.validated_data
            source = values["file"]
            validate_declaration(source.size, source.content_type)
            validate_filename(source.name, source.content_type)
            result = profile_assets.receive_profile_upload(
                self.actor(request),
                asset_uuid,
                values["expected_version"],
                source,
                timezone.now(),
            )
            return Response(asdict(result))
        finally:
            for key in parsed.files:
                for source in parsed.files.getlist(key):
                    source.close()


class FinalizeUploadView(UploadView):
    def post(self, request, asset_uuid):
        data = self.payload(request, schema.UploadCommand)
        result = profile_assets.finalize_profile_upload(
            self.actor(request), asset_uuid, at=timezone.now(), **data
        )
        return Response(asdict(result), status=202)


class AbandonUploadView(UploadView):
    def post(self, request, asset_uuid):
        data = self.payload(request, schema.UploadCommand)
        result = profile_assets.abandon_profile_upload(
            self.actor(request), asset_uuid, at=timezone.now(), **data
        )
        return Response(asdict(result))
