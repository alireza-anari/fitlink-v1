from uuid import uuid4

from django.shortcuts import redirect, render
from django.utils import timezone

from apps.accounts.forms import PrivacyForm
from apps.accounts.views import UI_ERRORS, current_actor, error_text, html_view
from config.use_cases import privacy


@html_view
def privacy_page(request):
    actor = current_actor(request, "privacy.status")
    if not actor:
        return redirect("/accounts/entry/")
    form = PrivacyForm(request.POST if request.method == "POST" else None)
    message = ""
    if request.method == "POST" and form.is_valid():
        try:
            privacy.request_privacy(
                actor,
                form.cleaned_data["kind"],
                uuid4(),
                timezone.now(),
                confirmed=form.cleaned_data["confirmed"],
            )
            if form.cleaned_data["kind"] == "delete":
                request.session.flush()
                return redirect("/accounts/entry/?notice=deletion")
            form = PrivacyForm()
            message = "درخواست ثبت شد؛ انجام درخواست پس از بررسی خواهد بود."
        except UI_ERRORS as exc:
            form.add_error(None, error_text(exc))
    rows = list(
        privacy.visible_requests(actor, timezone.now()).order_by("-created_at", "id")[
            :100
        ]
    )
    return render(
        request,
        "governance/privacy.html",
        {"form": form, "requests": rows, "message": message},
    )
