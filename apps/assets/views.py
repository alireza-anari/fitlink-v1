"""Shared bounded native transport helpers, without storage/owner authority."""

from functools import wraps
from uuid import uuid4

from django import forms
from django.core.exceptions import RequestDataTooBig
from django.db import DatabaseError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from apps.accounts.views import current_actor

from .contracts import UploadConflict, UploadQuota, UploadUnavailable

DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def private_page(action, conflicts=()):
    def decorate(view):
        @wraps(view)
        def bounded(request, *args, **kwargs):
            try:
                if request.method == "POST" and (
                    len(request.body) > 4096
                    or request.content_type != "application/x-www-form-urlencoded"
                    or request.FILES
                ):
                    return HttpResponse("درخواست معتبر نیست.", status=400)
                actor = current_actor(request, action)
                if actor is None:
                    return redirect("/accounts/entry/")
                return view(request, actor, *args, **kwargs)
            except (DatabaseError, UploadUnavailable):
                return HttpResponse("سرویس موقتاً در دسترس نیست.", status=503)
            except (*conflicts, UploadConflict):
                return HttpResponse(
                    "وضعیت تغییر کرده است؛ صفحه را تازه کنید.", status=409
                )
            except LookupError:
                return HttpResponse("درخواست یافت نشد.", status=404)
            except PermissionError:
                return HttpResponse("دسترسی مجاز نیست.", status=403)
            except (ValueError, RequestDataTooBig, UploadQuota):
                return HttpResponse("درخواست معتبر نیست.", status=400)

        protected = csrf_protect(require_http_methods(["GET", "POST"])(bounded))

        @wraps(view)
        def private(request, *args, **kwargs):
            response = protected(request, *args, **kwargs)
            response["Cache-Control"] = "private, no-store"
            response["X-Robots-Tag"] = "noindex, nofollow"
            response["X-Content-Type-Options"] = "nosniff"
            return response

        return private

    return decorate


class CommandForm(forms.Form):
    operation_id = forms.UUIDField(widget=forms.HiddenInput, initial=uuid4)
    expected_version = forms.IntegerField(
        min_value=1, required=False, widget=forms.HiddenInput
    )

    def __init__(self, data=None, **kwargs):
        kwargs.setdefault("label_suffix", "")
        if data is not None:
            data = data.copy()
            for name in data:
                if hasattr(data, "getlist"):
                    data.setlist(
                        name,
                        [
                            v.translate(DIGITS) if isinstance(v, str) else v
                            for v in data.getlist(name)
                        ],
                    )
                elif isinstance(data[name], str):
                    data[name] = data[name].translate(DIGITS)
        super().__init__(data, **kwargs)

    def clean(self):
        values = super().clean()
        if self.data is not None:
            if set(self.data) - set(self.fields) - {"csrfmiddlewaretoken", "action"}:
                raise forms.ValidationError("فیلد مجاز نیست.")
            if hasattr(self.data, "getlist") and any(
                len(self.data.getlist(k)) != 1
                for k in self.data
                if not isinstance(self.fields.get(k), forms.MultipleChoiceField)
            ):
                raise forms.ValidationError("فیلد تکراری مجاز نیست.")
        return values

    def command(self):
        if not self.is_valid():
            raise ValueError("Invalid command")
        values = {"operation_id": self.cleaned_data["operation_id"]}
        if self.cleaned_data.get("expected_version") is not None:
            values["expected_version"] = self.cleaned_data["expected_version"]
        return values


def valid(form):
    if not form.is_valid():
        raise ValueError("Invalid native input")
    return form.cleaned_data
