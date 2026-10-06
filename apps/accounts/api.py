"""Bounded same-origin adapters for reviewed C02 commands only."""

from django.conf import settings
from django.core.exceptions import PermissionDenied, RequestDataTooBig
from django.db import DatabaseError
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_GET
from rest_framework import exceptions, parsers  # type: ignore[import-untyped]
from rest_framework.response import Response  # type: ignore[import-untyped]
from rest_framework.views import APIView  # type: ignore[import-untyped]

from config.authentication import AccountSessionAuthentication
from config.permissions import AccountActionPermission
from config.use_cases import identity, privacy, recovery

from . import serializers as schema
from .client_ip import client_ip
from .otp import OtpThrottled, OtpUnavailable
from .phone_change import PhoneChangeConflict
from .recovery import RecoveryConflict, RecoveryNotFound, RecoveryUnavailable


@cache_control(no_store=True)
@require_GET
@ensure_csrf_cookie
def entry_bootstrap(request):
    token = get_token(request)
    response = HttpResponse(
        '<html lang="fa" dir="rtl"><form method="post">'
        '<input type="hidden" name="csrfmiddlewaretoken" '
        f'value="{token}"></form></html>'
    )
    response["Cache-Control"] = "no-store"
    return response


@method_decorator(csrf_protect, name="dispatch")
class CommandView(APIView):
    authentication_classes: list[type] = []
    permission_classes: list[type] = []
    parser_classes = [parsers.JSONParser, parsers.FormParser]

    def payload(self, request, serializer, *, query=False):
        try:
            if not query and len(request._request.body) > 4096:
                raise exceptions.ValidationError("Invalid request")
        except RequestDataTooBig:
            raise exceptions.ValidationError("Invalid request") from None
        value = serializer(data=request.query_params if query else request.data)
        value.is_valid(raise_exception=True)
        return value.validated_data

    def ip(self, request):
        return client_ip(
            request.META.get("REMOTE_ADDR", ""),
            request.META.get("HTTP_X_FORWARDED_FOR"),
            settings.ACCOUNT_SECURITY.trusted_proxy_cidrs,
        )

    def handle_exception(self, exc):
        if isinstance(
            exc, (exceptions.NotAuthenticated, exceptions.AuthenticationFailed)
        ):
            # These adapters authenticate with sessions, which have no bearer
            # challenge. Preserve DRF's SessionAuthentication 403 convention.
            return Response({"status": "denied"}, status=403)
        if isinstance(exc, OtpThrottled):
            return Response(
                {"status": "throttled"},
                status=429,
                headers={"Retry-After": str(max(1, min(exc.retry_after, 86400)))},
            )
        if isinstance(exc, (DatabaseError, OtpUnavailable, RecoveryUnavailable)):
            return Response({"status": "unavailable"}, status=503)
        if isinstance(exc, (PhoneChangeConflict, RecoveryConflict)):
            return Response({"status": "conflict"}, status=409)
        if isinstance(exc, RecoveryNotFound):
            return Response({"status": "not_found"}, status=404)
        if isinstance(exc, (PermissionError, PermissionDenied)):
            return Response({"status": "denied"}, status=403)
        if isinstance(exc, ValueError):
            return Response({"status": "invalid"}, status=400)
        if isinstance(exc, exceptions.APIException):
            return Response(
                {
                    "status": "denied"
                    if exc.status_code == 403
                    else "not_found"
                    if exc.status_code == 404
                    else "unavailable"
                    if exc.status_code == 503
                    else "invalid"
                },
                status=exc.status_code,
            )
        return super().handle_exception(exc)

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Cache-Control"] = "no-store"
        return response


class PrivateView(CommandView):
    authentication_classes = [AccountSessionAuthentication]
    permission_classes = [AccountActionPermission]
    account_action = "account.self"

    def actor(self, request):
        return request._request.account_actor


def otp_response(result):
    return Response(
        {
            "status": result.status,
            "challenge_id": result.challenge_id,
            "resend_after_seconds": result.resend_after_seconds,
        }
    )


def proof_response(result):
    return Response(
        {"status": "verified" if result.valid else "invalid"},
        status=200 if result.valid else 400,
    )


class OtpRequestView(CommandView):
    def post(self, request):
        data = self.payload(request, schema.OtpRequestSerializer)
        return otp_response(identity.request_login_otp(data["phone"], self.ip(request)))


class OtpVerifyView(CommandView):
    def post(self, request):
        data = self.payload(request, schema.OtpVerifySerializer)
        result = identity.verify_login_otp(
            request._request, ip=self.ip(request), **data
        )
        if not result.valid:
            return proof_response(result)
        return Response(
            {
                "status": "verified",
                "account_uuid": result.user_uuid,
                "scope": request._request.session["fitlink_scope"],
            }
        )


class LogoutView(PrivateView):
    account_action = "account.logout"
    all_sessions = False

    def post(self, request):
        self.payload(request, schema.EmptySerializer)
        identity.logout_account(
            request._request, self.actor(request), self.all_sessions, timezone.now()
        )
        return Response({"status": "logged_out"})


class LogoutAllView(LogoutView):
    account_action = "account.logout_all"
    all_sessions = True


class AccountView(PrivateView):
    def get(self, request):
        return Response(identity.own_account(self.actor(request), timezone.now()))

    def patch(self, request):
        data = self.payload(request, schema.AccountPreferencesSerializer)
        return Response(
            identity.update_preferences(self.actor(request), data, timezone.now())
        )


class PhoneChangeView(PrivateView):
    account_action = "phone_change.begin"

    def post(self, request):
        data = self.payload(request, schema.PhoneChangeSerializer)
        return Response(
            {
                "change_uuid": identity.begin_phone_change(
                    self.actor(request), data["new_phone"], timezone.now()
                )
            },
            status=201,
        )


class OwnedChangeView(PrivateView):
    account_action = "phone_change.apply"

    def owned(self, request, data):
        if not identity.visible_phone_change(
            self.actor(request), data["change_uuid"], timezone.now()
        ):
            raise exceptions.NotFound()


class ChangeRequestView(OwnedChangeView):
    def post(self, request):
        data = self.payload(request, schema.ChangeRequestSerializer)
        self.owned(request, data)
        return otp_response(
            identity.request_phone_change_otp(
                self.actor(request), ip=self.ip(request), at=timezone.now(), **data
            )
        )


class ChangeProofView(OwnedChangeView):
    def post(self, request):
        data = self.payload(request, schema.ChangeProofSerializer)
        self.owned(request, data)
        return proof_response(
            identity.verify_phone_change_otp(
                self.actor(request), ip=self.ip(request), at=timezone.now(), **data
            )
        )


class ChangeApplyView(OwnedChangeView):
    def post(self, request):
        data = self.payload(request, schema.ChangeSerializer)
        self.owned(request, data)
        identity.apply_phone_change(
            self.actor(request), data["change_uuid"], timezone.now()
        )
        request._request.session.flush()
        return Response({"status": "applied"})


RECEIPT_COOKIE = "fitlink_recovery_receipt"
RECEIPT_PATH = "/api/v1/recovery/requests/"


class RecoveryIntakeView(CommandView):
    def post(self, request):
        data = self.payload(request, schema.RecoveryRequestSerializer)
        result = recovery.open_recovery(ip=self.ip(request), at=timezone.now(), **data)
        response = Response(
            {"request_id": result.request_uuid, "status": "received"}, status=202
        )
        response.set_cookie(
            RECEIPT_COOKIE,
            result.raw_receipt,
            max_age=settings.ACCOUNT_SECURITY.policy.recovery_receipt_seconds,
            path=RECEIPT_PATH,
            secure=True,
            httponly=True,
            samesite="Strict",
        )
        return response


class RecoveryStatusView(CommandView):
    def get(self, request, request_uuid):
        return Response(
            {
                "status": recovery.receipt_status(
                    request_uuid,
                    request.COOKIES.get(RECEIPT_COOKIE, ""),
                    timezone.now(),
                )
            }
        )


class RecoveryOtpRequestView(CommandView):
    def post(self, request, request_uuid):
        self.payload(request, schema.EmptySerializer)
        return otp_response(
            recovery.request_recovery_otp(
                request_uuid,
                request.COOKIES.get(RECEIPT_COOKIE, ""),
                self.ip(request),
                timezone.now(),
            )
        )


class RecoveryOtpProofView(CommandView):
    def post(self, request, request_uuid):
        data = self.payload(request, schema.ProofSerializer)
        return proof_response(
            recovery.verify_recovery_otp(
                request_uuid,
                request.COOKIES.get(RECEIPT_COOKIE, ""),
                ip=self.ip(request),
                at=timezone.now(),
                **data,
            )
        )


class StaffRecoveryView(PrivateView):
    account_action = "staff.command"

    def handle_exception(self, exc):
        if type(exc) is PermissionError:
            return Response({"status": "not_found"}, status=404)
        return super().handle_exception(exc)

    def get(self, request, request_uuid):
        data = self.payload(request, schema.StaffAuthoritySerializer, query=True)
        row = recovery.recovery_detail(
            self.actor(request), request_uuid, at=timezone.now(), **data
        )
        return Response(
            {
                "request_id": row.id,
                "state": row.state,
                "version": row.version,
                "evidence_status": row.evidence_decision,
            }
        )


class StaffEvidenceView(StaffRecoveryView):
    def get(self, request, request_uuid):
        raise exceptions.MethodNotAllowed("GET")

    def post(self, request, request_uuid):
        data = self.payload(request, schema.StaffEvidenceSerializer)
        result = recovery.add_recovery_evidence(
            self.actor(request), request_uuid, at=timezone.now(), **data
        )
        return Response({"evidence_id": result}, status=201)


class StaffDecisionView(StaffRecoveryView):
    def get(self, request, request_uuid):
        raise exceptions.MethodNotAllowed("GET")

    def post(self, request, request_uuid):
        data = self.payload(request, schema.StaffDecisionSerializer)
        recovery.decide_recovery(
            self.actor(request), request_uuid, at=timezone.now(), **data
        )
        return Response({"status": "recorded"})


class StaffApplyView(StaffRecoveryView):
    def get(self, request, request_uuid):
        raise exceptions.MethodNotAllowed("GET")

    def post(self, request, request_uuid):
        data = self.payload(request, schema.StaffCommandSerializer)
        recovery.apply_recovery(
            self.actor(request), request_uuid, at=timezone.now(), **data
        )
        return Response({"status": "applied"})


class PrivacyView(PrivateView):
    account_action = "privacy.status"

    def get(self, request, request_uuid=None):
        rows = privacy.visible_requests(self.actor(request), timezone.now())
        if request_uuid is not None:
            if not rows.filter(pk=request_uuid).exists():
                raise exceptions.NotFound()
            return Response(
                privacy.privacy_status(
                    self.actor(request), request_uuid, timezone.now()
                )
            )
        return Response(
            {
                "requests": [
                    {"request_id": row.id, "kind": row.kind, "status": row.status}
                    for row in rows.order_by("-created_at", "id")[:100]
                ]
            }
        )

    def post(self, request, request_uuid=None):
        if request_uuid is not None:
            raise exceptions.MethodNotAllowed("POST")
        data = self.payload(request, schema.PrivacyRequestSerializer)
        result = privacy.request_privacy(self.actor(request), at=timezone.now(), **data)
        return Response(
            {
                "request_id": result,
                "status": "pending_execution"
                if data["kind"] == "export"
                else "pending_deletion",
            },
            status=201,
        )
