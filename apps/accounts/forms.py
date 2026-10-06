"""Native Persian forms; identity eligibility remains server-owned."""

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django import forms
from django.utils import timezone

from .dates import parse_birth_date, require_adult
from .otp import normalize_code
from .phone import normalize_iranian_mobile
from .recovery_models import EVIDENCE_OUTCOMES, EVIDENCE_TYPES

PHONE_ATTRS = {"dir": "ltr", "inputmode": "tel", "autocomplete": "tel"}


class PersianForm(forms.Form):
    def add_error(self, field, error):
        # Domain errors also need to render on a fresh, empty proof form.
        if not self.is_bound:
            self.cleaned_data = {}
        super().add_error(field, error)


class PhoneInput(forms.CharField):
    def __init__(self, **kwargs):
        super().__init__(
            max_length=32, widget=forms.TextInput(attrs=PHONE_ATTRS), **kwargs
        )

    def clean(self, value):
        try:
            return normalize_iranian_mobile(super().clean(value))
        except ValueError:
            raise forms.ValidationError("شمارهٔ همراه معتبر وارد کنید.") from None


class EntryForm(PersianForm):
    phone = PhoneInput(label="شمارهٔ همراه")
    calendar = forms.ChoiceField(
        label="تقویم تاریخ تولد", choices=[("jalali", "شمسی"), ("gregorian", "میلادی")]
    )
    birth_date = forms.CharField(
        label="تاریخ تولد",
        max_length=10,
        help_text="سال-ماه-روز؛ نمونهٔ شمسی: ۱۳۶۸-۱۰-۱۱",
        widget=forms.TextInput(
            attrs={"dir": "ltr", "inputmode": "numeric", "placeholder": "۱۳۶۸-۱۰-۱۱"}
        ),
    )
    adult_attested = forms.BooleanField(label="اعلام می‌کنم حداقل ۱۸ سال دارم")
    entry_hint = forms.ChoiceField(
        label="مسیر ورود",
        choices=[("athlete", "ورود معمولی"), ("professional", "ورود حرفه‌ای")],
        initial="athlete",
    )

    def __init__(self, *args, professional_enabled=True, **kwargs):
        super().__init__(*args, **kwargs)
        if not professional_enabled:
            self.fields["entry_hint"].choices = [("athlete", "ورود معمولی")]

    def clean(self):
        data = super().clean()
        if data and {"birth_date", "calendar", "adult_attested"} <= data.keys():
            try:
                parsed = parse_birth_date(data["birth_date"], data["calendar"])
                require_adult(parsed, data["adult_attested"], timezone.now())
                data["birth_date"] = parsed
            except ValueError:
                raise forms.ValidationError(
                    "ورود فقط برای افراد حداقل ۱۸ سال با تاریخ تولد معتبر "
                    "و اعلام صریح سن امکان‌پذیر است."
                ) from None
        return data


class VerifyForm(PersianForm):
    code = forms.CharField(
        label="کد شش‌رقمی",
        max_length=16,
        widget=forms.TextInput(
            attrs={
                "dir": "ltr",
                "inputmode": "numeric",
                "autocomplete": "one-time-code",
            }
        ),
    )

    def clean_code(self):
        try:
            return normalize_code(self.cleaned_data["code"])
        except ValueError:
            raise forms.ValidationError("کد شش‌رقمی معتبر وارد کنید.") from None


class PreferencesForm(PersianForm):
    locale = forms.ChoiceField(
        label="زبان", choices=[("fa", "فارسی"), ("en", "English")]
    )
    timezone = forms.CharField(
        label="منطقهٔ زمانی", max_length=64, widget=forms.TextInput(attrs={"dir": "ltr"})
    )

    def clean_timezone(self):
        value = self.cleaned_data["timezone"]
        try:
            ZoneInfo(value)
        except (ValueError, ZoneInfoNotFoundError):
            raise forms.ValidationError("منطقهٔ زمانی معتبر وارد کنید.") from None
        return value


class PhoneChangeForm(PersianForm):
    new_phone = PhoneInput(label="شمارهٔ جدید")


class RecoveryForm(PersianForm):
    old_phone = PhoneInput(label="شمارهٔ پیشین")
    new_phone = PhoneInput(label="شمارهٔ جدید")

    def clean(self):
        data = super().clean()
        if data and data.get("old_phone") == data.get("new_phone"):
            raise forms.ValidationError("شمارهٔ جدید باید متفاوت باشد.")
        return data


class PrivacyForm(PersianForm):
    kind = forms.ChoiceField(
        label="نوع درخواست",
        choices=[
            ("export", "دریافت نسخه‌ای از داده‌ها"),
            ("delete", "حذف حساب و داده‌ها"),
        ],
    )
    confirmed = forms.BooleanField(
        label="این درخواست را صریحاً تأیید می‌کنم", required=True
    )


class StaffAuthorityForm(PersianForm):
    step_up_id = forms.UUIDField(label="شناسهٔ تأیید تازهٔ کارکنان")
    reason_code = forms.ChoiceField(
        label="علت اقدام",
        choices=[
            ("identity_verified", "هویت بررسی شده"),
            ("permission_denied", "درخواست رد شده"),
        ],
    )


class StaffEvidenceForm(PersianForm):
    classification = forms.ChoiceField(
        label="نوع فرادادهٔ بررسی",
        choices=[
            (
                v,
                {
                    "identity_match": "تطبیق هویت",
                    "phone_loss": "از دست رفتن شماره",
                    "ownership_review": "بررسی مالکیت",
                }[v],
            )
            for v in EVIDENCE_TYPES
        ],
    )
    outcome = forms.ChoiceField(
        label="نتیجهٔ بررسی",
        choices=[
            (
                v,
                {
                    "verified": "تأیید شده",
                    "unresolved": "نیازمند بررسی",
                    "rejected": "رد شده",
                }[v],
            )
            for v in EVIDENCE_OUTCOMES
        ],
    )
    checksum = forms.RegexField(r"\A[0-9a-f]{64}\Z", label="چک‌سام مرجع", max_length=64)
    reference = forms.UUIDField(label="شناسهٔ مرجع بررسی")


class StaffDecisionForm(PersianForm):
    decision = forms.ChoiceField(
        label="تصمیم", choices=[("approved", "تأیید"), ("rejected", "رد")]
    )


class StaffVersionForm(PersianForm):
    expected_version = forms.IntegerField(min_value=1, max_value=2**63 - 1)
