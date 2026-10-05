from django.core import signing
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.views.decorators.http import require_GET

from apps.accounts.referrals import REFERRAL_SECONDS

from .use_cases.referral import resolve_referral


@require_GET
def referral_landing(request, token):
    # The redirect is a server constant; neither token nor query controls a URL.
    response = HttpResponseRedirect("/")
    response["Referrer-Policy"] = "no-referrer"
    response["Cache-Control"] = "no-store"
    descriptor = resolve_referral(token, timezone.now())
    if descriptor:
        value = signing.dumps(
            {"link": str(descriptor.link_uuid)}, salt="fitlink.referral"
        )
        response.set_cookie(
            "fitlink_referral",
            value,
            max_age=REFERRAL_SECONDS,
            secure=True,
            httponly=True,
            samesite="Strict",
        )
    else:
        response.delete_cookie("fitlink_referral", samesite="Strict")
    return response
