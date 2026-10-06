"""Native entry/control adapters sharing the reviewed C02 commands."""

from datetime import timedelta
from functools import wraps
from uuid import UUID

from django.core.exceptions import PermissionDenied, RequestDataTooBig
from django.db import DatabaseError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from config.use_cases import entry, identity, recovery

from . import forms
from .api import RECEIPT_COOKIE, RECEIPT_PATH
from .limiter import LimiterUnavailable
from .otp import OtpThrottled, OtpUnavailable
from .phone_change import PhoneChangeConflict
from .recovery import RecoveryConflict, RecoveryNotFound, RecoveryUnavailable
from .sessions import actor_user

UI_ERRORS = (
    ValueError,
    PermissionError,
    PermissionDenied,
    DatabaseError,
    LimiterUnavailable,
    OtpUnavailable,
    RecoveryUnavailable,
    OtpThrottled,
    RecoveryNotFound,
)


def html_view(view):
    @wraps(view)
    def bounded(request, *args, **kwargs):
        if request.method == "POST":
            try:
                if (
                    len(request.body) > 4096
                    or request.content_type != "application/x-www-form-urlencoded"
                    or request.FILES
                ):
                    return HttpResponse("درخواست معتبر نیست.", status=400)
            except RequestDataTooBig:
                return HttpResponse("درخواست معتبر نیست.", status=400)
        return view(request, *args, **kwargs)

    return cache_control(no_store=True)(
        csrf_protect(require_http_methods(["GET", "POST"])(bounded))
    )


def current_actor(request, action="account.self"):
    actor = getattr(request, "account_actor", None)
    if actor is not None:
        try:
            actor_user(actor, action, timezone.now())
            return actor
        except PermissionError:
            pass
    return None


def error_text(exc):
    if isinstance(exc, OtpThrottled):
        seconds = max(1, min(exc.retry_after, 86400))
        return f"لطفاً {seconds} ثانیه صبر کنید و سپس دوباره تلاش کنید."
    if isinstance(
        exc, (DatabaseError, LimiterUnavailable, OtpUnavailable, RecoveryUnavailable)
    ):
        return "این درخواست فعلاً قابل انجام نیست؛ کمی بعد دوباره تلاش کنید."
    if isinstance(exc, (PhoneChangeConflict, RecoveryConflict)):
        return "وضعیت درخواست تغییر کرده است؛ صفحه را تازه کنید."
    return "درخواست معتبر نیست یا دسترسی لازم وجود ندارد."


def clear_proof_error(exc, *, prefix=None):
    form = forms.VerifyForm(prefix=prefix)
    form.add_error(None, error_text(exc))
    return form


def entry_context(request, form, professional, message=""):
    return {
        "form": form,
        "professional": professional,
        "message": message
        or (
            "درخواست حذف دریافت شد؛ دسترسی حساب محدود است "
            "و انجام درخواست پس از بررسی خواهد بود."
            if request.GET.get("notice") == "deletion"
            else ""
        ),
    }


@html_view
def entry_page(request):
    professional = entry.professional_entry_available()
    form = forms.EntryForm(
        request.POST if request.method == "POST" else None,
        professional_enabled=professional,
    )
    if request.method == "POST" and form.is_valid():
        from django.conf import settings

        from .client_ip import client_ip

        try:
            ip = client_ip(
                request.META.get("REMOTE_ADDR", ""),
                request.META.get("HTTP_X_FORWARDED_FOR"),
                settings.ACCOUNT_SECURITY.trusted_proxy_cidrs,
            )
            result = identity.request_login_otp(form.cleaned_data["phone"], ip)
            at = timezone.now()
            request.session["c02_entry"] = {
                "phone": form.cleaned_data["phone"],
                "birth_date": form.cleaned_data["birth_date"].isoformat(),
                "challenge_id": str(result.challenge_id),
                "entry_hint": form.cleaned_data["entry_hint"],
                "resend_at": (
                    at + timedelta(seconds=result.resend_after_seconds)
                ).isoformat(),
            }
            request.session.set_expiry(settings.ACCOUNT_SECURITY.policy.expiry_seconds)
            return redirect("/accounts/verify/")
        except UI_ERRORS as exc:
            form.add_error(None, error_text(exc))
    return render(
        request, "accounts/entry.html", entry_context(request, form, professional)
    )


def peer_ip(request):
    from django.conf import settings

    from .client_ip import client_ip

    return client_ip(
        request.META.get("REMOTE_ADDR", ""),
        request.META.get("HTTP_X_FORWARDED_FOR"),
        settings.ACCOUNT_SECURITY.trusted_proxy_cidrs,
    )


@html_view
def verify_page(request):
    pending = request.session.get("c02_entry")
    if (
        not isinstance(pending, dict)
        or not {"phone", "birth_date", "challenge_id", "resend_at", "entry_hint"}
        <= pending.keys()
    ):
        return redirect("/accounts/entry/")
    form = forms.VerifyForm()
    if request.method == "POST":
        try:
            if request.POST.get("action") == "resend":
                from django.conf import settings

                result = identity.request_login_otp(pending["phone"], peer_ip(request))
                pending["challenge_id"] = str(result.challenge_id)
                pending["resend_at"] = (
                    timezone.now() + timedelta(seconds=result.resend_after_seconds)
                ).isoformat()
                request.session["c02_entry"] = pending
                request.session.set_expiry(
                    settings.ACCOUNT_SECURITY.policy.expiry_seconds
                )
            elif request.POST.get("action") == "verify":
                form = forms.VerifyForm(request.POST)
                if form.is_valid():
                    from .dates import parse_birth_date

                    result = identity.verify_login_otp(
                        request,
                        pending["phone"],
                        UUID(pending["challenge_id"]),
                        form.cleaned_data["code"],
                        peer_ip(request),
                        birth_date=parse_birth_date(pending["birth_date"], "gregorian"),
                        adult_attested=True,
                    )
                    if result.valid:
                        return redirect("/accounts/me/")
                    form = forms.VerifyForm()
                    form.add_error(
                        None, "کد معتبر نیست؛ کد و زمان اعتبار آن را بررسی کنید."
                    )
            else:
                raise ValueError("Invalid action")
        except UI_ERRORS as exc:
            form = clear_proof_error(exc)
    try:
        from datetime import datetime

        remaining = max(
            0,
            int(
                (
                    datetime.fromisoformat(pending["resend_at"]) - timezone.now()
                ).total_seconds()
            ),
        )
    except (ValueError, TypeError):
        remaining = 0
    return render(
        request, "accounts/verify.html", {"form": form, "remaining": remaining}
    )


@html_view
def account_page(request):
    actor = current_actor(request)
    if not actor:
        return redirect("/accounts/entry/")
    info = identity.account_display(actor, timezone.now())
    form = forms.PreferencesForm(
        initial={"locale": info["locale"], "timezone": info["timezone"]}
    )
    message = ""
    if request.method == "POST":
        try:
            action = request.POST.get("action")
            if action in {"logout", "logout_all"}:
                identity.logout_account(
                    request, actor, action == "logout_all", timezone.now()
                )
                return redirect("/accounts/entry/")
            if action != "preferences":
                raise ValueError("Invalid action")
            form = forms.PreferencesForm(request.POST)
            if form.is_valid():
                identity.update_preferences(actor, form.cleaned_data, timezone.now())
                message = "ترجیحات ذخیره شد."
        except UI_ERRORS as exc:
            form.add_error(None, error_text(exc))
    return render(
        request,
        "accounts/me.html",
        {
            "form": form,
            "account": info,
            "message": message,
            "control_only": str(actor.scope) == "account_control",
        },
    )


@html_view
def phone_change_page(request):
    actor = current_actor(request, "phone_change.apply")
    if not actor:
        return redirect("/accounts/entry/")
    form = forms.PhoneChangeForm()
    old_form, new_form = forms.VerifyForm(prefix="old"), forms.VerifyForm(prefix="new")
    message, error = "", ""
    raw = request.session.get("c02_change_uuid")
    try:
        change_id = UUID(raw) if isinstance(raw, str) else None
    except ValueError:
        change_id = None
    intent = (
        identity.phone_change_display(actor, change_id, timezone.now())
        if change_id
        else None
    )
    if request.method == "POST":
        try:
            action = request.POST.get("action")
            if action == "begin":
                form = forms.PhoneChangeForm(request.POST)
                if form.is_valid():
                    change_id = identity.begin_phone_change(
                        actor, form.cleaned_data["new_phone"], timezone.now()
                    )
                    request.session["c02_change_uuid"] = str(change_id)
                    intent = identity.phone_change_display(
                        actor, change_id, timezone.now()
                    )
            elif intent and action in {"request_old", "request_new"}:
                kind = "old" if action == "request_old" else "new"
                result = identity.request_phone_change_otp(
                    actor, change_id, kind, peer_ip(request), timezone.now()
                )
                request.session["c02_change_challenge_" + kind] = str(
                    result.challenge_id
                )
                message = "درخواست کد ثبت شد؛ در صورت دریافت پیامک، کد را وارد کنید."
            elif intent and action in {"verify_old", "verify_new"}:
                kind = "old" if action == "verify_old" else "new"
                proof_form = forms.VerifyForm(request.POST, prefix=kind)
                if proof_form.is_valid():
                    challenge = UUID(
                        request.session.get("c02_change_challenge_" + kind, "")
                    )
                    result = identity.verify_phone_change_otp(
                        actor,
                        change_id,
                        kind,
                        challenge,
                        proof_form.cleaned_data["code"],
                        peer_ip(request),
                        timezone.now(),
                    )
                    if not result.valid:
                        raise ValueError("Invalid proof")
                    message = "شماره تأیید شد."
                    intent = identity.phone_change_display(
                        actor, change_id, timezone.now()
                    )
                else:
                    error = "کد شش‌رقمی معتبر وارد کنید."
            elif intent and action == "apply":
                identity.apply_phone_change(actor, change_id, timezone.now())
                request.session.flush()
                return redirect("/accounts/entry/")
            else:
                raise ValueError("Invalid action")
        except UI_ERRORS as exc:
            error = error_text(exc)
    return render(
        request,
        "accounts/phone_change.html",
        {
            "form": form,
            "old_form": old_form,
            "new_form": new_form,
            "intent": intent,
            "message": message,
            "error": error,
        },
    )


@html_view
def recovery_page(request):
    from django.conf import settings

    form, proof_form = forms.RecoveryForm(), forms.VerifyForm()
    message, error, state = "", "", None
    receipt = request.COOKIES.get(RECEIPT_COOKIE, "")
    raw = request.session.get("c02_recovery_uuid")
    try:
        case_id = UUID(raw) if isinstance(raw, str) else None
    except ValueError:
        case_id = None
    if case_id:
        try:
            state = recovery.receipt_status(case_id, receipt, timezone.now())
        except UI_ERRORS as exc:
            error = error_text(exc)
            case_id = None
    if request.method == "POST":
        try:
            action = request.POST.get("action")
            if action == "intake":
                form = forms.RecoveryForm(request.POST)
                if form.is_valid():
                    result = recovery.open_recovery(
                        ip=peer_ip(request), at=timezone.now(), **form.cleaned_data
                    )
                    request.session["c02_recovery_uuid"] = str(result.request_uuid)
                    request.session.set_expiry(
                        settings.ACCOUNT_SECURITY.policy.recovery_receipt_seconds
                    )
                    response = redirect("/accounts/recovery/")
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
            elif case_id and action == "request_proof":
                result = recovery.request_recovery_otp(
                    case_id, receipt, peer_ip(request), timezone.now()
                )
                request.session["c02_recovery_challenge"] = str(result.challenge_id)
                message = "درخواست کد ثبت شد؛ در صورت دریافت پیامک، کد را وارد کنید."
            elif case_id and action == "verify_proof":
                proof_form = forms.VerifyForm(request.POST)
                if proof_form.is_valid():
                    result = recovery.verify_recovery_otp(
                        case_id,
                        receipt,
                        UUID(request.session.get("c02_recovery_challenge", "")),
                        proof_form.cleaned_data["code"],
                        peer_ip(request),
                        timezone.now(),
                    )
                    proof_form = forms.VerifyForm()
                    if not result.valid:
                        raise ValueError("Invalid proof")
                    message = (
                        "مالکیت شمارهٔ جدید تأیید شد؛ "
                        "بررسی مجاز کارکنان همچنان لازم است."
                    )
            else:
                raise ValueError("Invalid action")
        except UI_ERRORS as exc:
            proof_form = forms.VerifyForm()
            error = error_text(exc)
    return render(
        request,
        "accounts/recovery.html",
        {
            "form": form,
            "proof_form": proof_form,
            "state": state,
            "message": message,
            "error": error,
        },
    )
