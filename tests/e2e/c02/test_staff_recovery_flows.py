from datetime import timedelta
from uuid import uuid4

import pytest
from django.utils import timezone
from helpers import VIEWPORTS, assets_and_layout, entry, verify
from playwright.sync_api import expect

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


def case_url(base, values):
    return (
        f"{base}/staff/recovery/{values.case.id}/?step_up_id={values.step}"
        "&reason_code=identity_verified"
    )


@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_assigned_staff_metadata_decision_and_apply(
    page, live_server, auth_runtime, staff_case, browser_errors, viewport
):
    from apps.accounts.recovery_models import PhoneChangeHistory
    from config.use_cases import recovery

    page.set_viewport_size(viewport)
    values = staff_case
    verify(page, entry(page, live_server.url, auth_runtime, phone="09123456788"))
    response = page.goto(case_url(live_server.url, values), wait_until="networkidle")
    assert response.status == 200
    expect(
        page.get_by_role("heading", name="بررسی مجاز بازیابی", exact=True)
    ).to_be_visible()
    assert values.target.phone not in page.content()
    assets_and_layout(page, live_server.url)
    page.get_by_label("نوع فرادادهٔ بررسی").select_option("identity_match")
    page.get_by_label("نتیجهٔ بررسی").select_option("verified")
    page.get_by_label("چک‌سام مرجع").fill("a" * 64)
    reference = str(uuid4())
    page.get_by_label("شناسهٔ مرجع بررسی").fill(reference)
    page.get_by_role("button", name="ثبت فراداده", exact=True).click()
    expect(page.get_by_text("فرادادهٔ بررسی ثبت شد.", exact=True)).to_be_visible()
    assert reference not in page.content()
    page.get_by_label("تصمیم", exact=True).select_option("approved")
    page.get_by_role("button", name="ثبت تصمیم", exact=True).click()
    expect(page.get_by_text("تصمیم ثبت شد.", exact=True)).to_be_visible()
    # Separate claimant browser coverage proves native receipt/proof forms.
    # Here the same real proof command gives the approved case a fresh proof.
    requested = recovery.request_recovery_otp(
        values.case.id, values.receipt.raw_receipt, "127.0.0.1", timezone.now()
    )
    code = auth_runtime.drain()[0].code
    assert recovery.verify_recovery_otp(
        values.case.id,
        values.receipt.raw_receipt,
        requested.challenge_id,
        code,
        "127.0.0.1",
        timezone.now(),
    ).valid
    page.reload(wait_until="networkidle")
    page.get_by_role("button", name="اعمال بازیابی", exact=True).click()
    expect(page.get_by_text("تغییر مجاز اعمال شد.", exact=True)).to_be_visible()
    values.target.refresh_from_db()
    assert values.target.phone == "+989123456780"
    assert PhoneChangeHistory.objects.filter(user=values.target).count() == 1


@pytest.mark.parametrize("viewport", VIEWPORTS)
@pytest.mark.parametrize(
    "defect",
    [
        "superuser",
        "assignment",
        "stale_step",
        "foreign_case",
        "self_issuer",
        "self_grant",
        "self_target",
    ],
)
def test_staff_html_denies_missing_or_self_authority(
    page, live_server, auth_runtime, staff_case, browser_errors, viewport, defect
):
    from apps.governance.staff_models import StaffStepUpGrant

    values = staff_case
    page.set_viewport_size(viewport)
    verify(page, entry(page, live_server.url, auth_runtime, phone="09123456788"))
    if defect == "superuser":
        type(values.staff).objects.filter(pk=values.staff.pk).update(
            is_staff=True, is_superuser=True
        )
        values.grant.delete()
    elif defect == "assignment":
        type(values.case).objects.filter(pk=values.case.pk).update(assigned_staff=None)
    elif defect == "stale_step":
        at = timezone.now()
        StaffStepUpGrant.objects.filter(pk=values.step).update(
            verified_at=at - timedelta(hours=2), expires_at=at - timedelta(hours=1)
        )
    elif defect == "foreign_case":
        StaffStepUpGrant.objects.filter(pk=values.step).update(case_uuid=uuid4())
    elif defect == "self_issuer":
        StaffStepUpGrant.objects.filter(pk=values.step).update(
            trusted_issuer=values.staff
        )
    elif defect == "self_grant":
        type(values.grant).objects.filter(pk=values.grant.pk).update(
            granted_by=values.staff
        )
    else:
        type(values.case).objects.filter(pk=values.case.pk).update(
            target_user=values.staff
        )
    # APIRequestContext executes real authenticated browser HTTP without
    # navigating to an expected HTTP-error document; console checks stay strict.
    response = page.request.get(case_url(live_server.url, values))
    assert response.status == 404
    assert values.target.phone not in response.text()
    assert values.receipt.raw_receipt not in response.text()
    csrf = next(c["value"] for c in page.context.cookies() if c["name"] == "csrftoken")
    posted = page.request.post(
        f"{live_server.url}/staff/recovery/{values.case.id}/",
        form={
            "action": "apply",
            "step_up_id": str(values.step),
            "reason_code": "identity_verified",
            "expected_version": str(values.case.version),
        },
        headers={"X-CSRFToken": csrf},
    )
    assert posted.status == 404
    values.target.refresh_from_db()
    assert values.target.phone == "+989123456789"
