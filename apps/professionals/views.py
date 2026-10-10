"""Private Persian pages; all facts come from approved owner selectors."""

from uuid import UUID, uuid4

from django.shortcuts import redirect, render
from django.utils import timezone

from apps.assets.views import CommandForm, private_page, valid
from config.use_cases import (
    entry,
    profile_assets,
)
from config.use_cases import (
    professional_profile as commands,
)
from config.use_cases import (
    professional_verification as verification,
)

from .contracts import ProfessionalStepInput, ProfileConflict, ProfileNotFound
from .forms import (
    CredentialForm,
    ProfessionalStepForm,
    UploadForm,
    VerificationForm,
    WithdrawCredentialForm,
)
from .selectors import (
    own_credential,
    own_professional_profile,
    own_verification,
    owner_preview,
)
from .validation import STEP_FIELDS

STEP_LABELS = {
    "identity": "نام و نقش‌ها",
    "description": "معرفی",
    "locations": "محدودهٔ خدمت",
    "branding": "ظاهر نمایه",
    "credentials": "مدارک",
    "preview": "پیش‌نمایش",
}
STATE_LABELS = {
    "pending_upload": "منتظر دریافت پرونده",
    "receiving": "در حال دریافت پرونده",
    "quarantined": "در قرنطینه",
    "processing": "در حال پردازش",
    "ready": "آماده",
    "rejected": "رد شده",
    "revoked": "لغو شده",
    "abandoned": "رها شده",
}


def session_key(actor, kind):
    return f"c03_{kind}:{actor.user_uuid}"


@private_page("professional.profile_read", (ProfileConflict,))
def setup(request, actor):
    try:
        profile = own_professional_profile(actor, timezone.now())
    except ProfileNotFound:
        profile = None
    step = request.GET.get("step", profile.setup_step if profile else "identity")
    if step not in STEP_FIELDS:
        raise ValueError("Invalid step")
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create":
            values = CommandForm(request.POST).command()
            values.pop("expected_version", None)
            commands.create_professional_profile(actor, at=timezone.now(), **values)
        elif action == "save":
            form = ProfessionalStepForm(step, request.POST)
            valid(form)
            commands.save_professional_step(
                actor,
                step,
                ProfessionalStepInput(form.payload()),
                at=timezone.now(),
                **form.command(),
            )
        elif action in {"credential_create", "credential_revise"}:
            form = CredentialForm(request.POST)
            data = valid(form)
            values = form.command()
            if action == "credential_create":
                values.pop("expected_version", None)
                if data["expected_profile_version"] is None:
                    raise ValueError("Invalid profile version")
                values["expected_profile_version"] = data["expected_profile_version"]
                result = commands.create_credential(
                    actor, form.payload(), at=timezone.now(), **values
                )
            else:
                result = commands.revise_credential(
                    actor,
                    data["credential_uuid"],
                    form.payload(),
                    at=timezone.now(),
                    **values,
                )
            request.session[session_key(actor, "credential")] = str(result.id)
        elif action == "credential_withdraw":
            form = WithdrawCredentialForm(request.POST)
            values = form.command()
            commands.withdraw_credential(
                actor, form.cleaned_data["credential_uuid"], at=timezone.now(), **values
            )
        elif action == "upload_begin":
            form = UploadForm(request.POST)
            data = valid(form)
            values = form.command()
            values.pop("expected_version", None)
            if profile is None:
                raise ProfileNotFound("Profile unavailable")
            subject = (
                data["subject_uuid"]
                if data["purpose"].endswith("evidence")
                else profile.id
            )
            result = profile_assets.begin_profile_upload(
                actor,
                data["purpose"],
                subject,
                at=timezone.now(),
                declared_size=data["declared_size"],
                declared_type=data["declared_type"],
                **values,
            )
            request.session[session_key(actor, "asset")] = str(result.id)
        elif action == "attach_avatar":
            values = CommandForm(request.POST).command()
            identifier = request.session.get(session_key(actor, "asset"))
            if identifier is None:
                raise ProfileNotFound("Asset unavailable")
            commands.save_professional_step(
                actor,
                "branding",
                ProfessionalStepInput({"avatar": UUID(identifier)}),
                at=timezone.now(),
                **values,
            )
        else:
            raise ValueError("Invalid action")
        return redirect(f"/professional/setup/?step={step}")
    initial = dict(profile.fields) if profile else {}
    if profile:
        initial.update(
            expected_version=profile.version,
            roles=[r.role for r in profile.roles if r.declared_active],
            locations=[
                {
                    "country_code": r.country_code,
                    "region": r.region,
                    "city": r.city,
                    "modes": list(r.modes),
                }
                for r in profile.locations
            ],
        )
        for name in ("specialties", "languages"):
            initial[name] = "\n".join(initial.get(name, []))
        initial["locations"] = "\n".join(
            " | ".join(
                (
                    r.country_code,
                    r.region,
                    r.city,
                    "،".join(
                        "آنلاین" if mode == "online" else "حضوری" for mode in r.modes
                    ),
                )
            )
            for r in profile.locations
        )
    asset = None
    identifier = request.session.get(session_key(actor, "asset"))
    if identifier:
        try:
            asset = profile_assets.own_profile_upload_status(
                actor, UUID(identifier), timezone.now()
            )
        except LookupError:
            request.session.pop(session_key(actor, "asset"), None)
    credential = None
    identifier = request.GET.get("credential") or request.session.get(
        session_key(actor, "credential")
    )
    if identifier:
        credential = own_credential(actor, UUID(identifier), timezone.now())
    credential_initial = {
        "expected_version": profile.version if profile else None,
        "expected_profile_version": profile.version if profile else None,
    }
    if credential:
        credential_initial.update(
            {
                name: getattr(credential, name)
                for name in ("category", "role", "type_code", "issuer", "title")
            }
        )
        credential_initial.update(
            credential_uuid=credential.id,
            expected_version=credential.version,
            calendar="gregorian",
            issued_on=credential.issued_on.isoformat() if credential.issued_on else "",
            expires_on=credential.expires_on.isoformat()
            if credential.expires_on
            else "",
        )
    return render(
        request,
        "professionals/setup.html",
        {
            "profile": profile,
            "can_create": entry.professional_entry_available(),
            "step": step,
            "steps": STEP_LABELS.items(),
            "form": ProfessionalStepForm(step, initial=initial),
            "create_form": CommandForm(),
            "upload_form": UploadForm(
                initial={"purpose": "avatar", "declared_type": "image/png"}
            ),
            "asset": asset,
            "asset_state": STATE_LABELS.get(asset.state, "نامشخص") if asset else "",
            "asset_operation": uuid4(),
            "can_finalize": bool(
                asset
                and asset.state == "quarantined"
                and request.session.get(f"c03_finalized:{actor.user_uuid}:{asset.id}")
                != asset.version
            ),
            "command_form": CommandForm(
                initial={"expected_version": profile.version if profile else None}
            ),
            "credential": credential,
            "credential_form": CredentialForm(initial=credential_initial),
            "credential_command": WithdrawCredentialForm(
                initial={
                    "expected_version": credential.version if credential else None,
                    "credential_uuid": credential.id if credential else None,
                }
            ),
        },
    )


@private_page("professional.profile_read", (ProfileConflict,))
def preview(request, actor):
    if request.method != "GET":
        raise ValueError("Read only")
    return render(
        request,
        "professionals/preview.html",
        {"preview": owner_preview(actor, timezone.now())},
    )


@private_page("professional.profile_read", (ProfileConflict,))
def verification_page(request, actor):
    profile = own_professional_profile(actor, timezone.now())
    key = session_key(actor, "verification")
    identifier = request.GET.get("verification") or request.session.get(key)
    case = (
        own_verification(actor, UUID(identifier), timezone.now())
        if identifier
        else None
    )
    if request.method == "POST":
        form = VerificationForm(request.POST)
        data = valid(form)
        values = form.command()
        action = request.POST.get("action")
        if action == "prepare":
            values["expected_profile_version"] = values.pop("expected_version")
            result = verification.prepare_verification(
                actor, tuple(data["requested_targets"]), at=timezone.now(), **values
            )
        elif action in {"submit", "withdraw"}:
            identifier = data["verification_uuid"]
            if action == "submit":
                result = verification.submit_verification(
                    actor, identifier, at=timezone.now(), **values
                )
            else:
                result = verification.withdraw_verification_target(
                    actor, identifier, data["target_uuid"], at=timezone.now(), **values
                )
        else:
            raise ValueError("Invalid action")
        request.session[key] = str(result.id)
        return redirect("/professional/verification/")
    return render(
        request,
        "professionals/verification.html",
        {
            "case": case,
            "form": VerificationForm(
                initial={
                    "expected_version": case.version if case else profile.version,
                    "verification_uuid": case.id if case else None,
                }
            ),
        },
    )
