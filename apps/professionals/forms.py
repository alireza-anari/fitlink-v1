"""Bounded native setup, credentials and verification transport."""

from django import forms

from apps.accounts.dates import parse_birth_date
from apps.assets.views import CommandForm

from .contracts import CredentialInput, ProfessionalStepInput
from .validation import STEP_FIELDS, normalize_credential, normalize_step


class ProfessionalStepForm(CommandForm):
    def __init__(self, step, data=None, **kwargs):
        if step not in STEP_FIELDS:
            raise ValueError("Invalid step")
        self.step = step
        super().__init__(data, **kwargs)
        self.fields["expected_version"].required = True
        fields = {
            "display_name": forms.CharField(label="نام نمایشی", max_length=120),
            "identity_name": forms.CharField(label="نام هویتی خصوصی", max_length=120),
            "roles": forms.MultipleChoiceField(
                label="نقش‌های اعلام‌شده",
                choices=[("coach", "مربی"), ("nutritionist", "متخصص تغذیه")],
                required=False,
            ),
            "biography": forms.CharField(
                label="معرفی",
                max_length=2000,
                required=False,
                widget=forms.Textarea(attrs={"rows": 4, "class": "w-full max-w-full"}),
            ),
            "specialties": forms.CharField(
                label="تخصص‌های اعلام‌شده (هر خط یک مورد)",
                max_length=650,
                required=False,
                widget=forms.Textarea(attrs={"rows": 3, "class": "w-full max-w-full"}),
            ),
            "experience_years": forms.IntegerField(
                label="سال‌های تجربهٔ اعلام‌شده", min_value=0, max_value=80, required=False
            ),
            "service_modes": forms.MultipleChoiceField(
                label="شیوهٔ خدمت",
                choices=[("online", "آنلاین"), ("in_person", "حضوری")],
            ),
            "languages": forms.CharField(
                label="کد زبان‌ها (هر خط یک مورد؛ مانند fa)", max_length=180
            ),
            "locations": forms.CharField(
                label="محدوده‌های خدمت",
                required=False,
                max_length=2500,
                widget=forms.Textarea(attrs={"rows": 3, "class": "w-full max-w-full"}),
                help_text=(
                    "حداکثر ده خط: کد کشور | استان | شهر | آنلاین یا حضوری. "
                    "برای هر دو شیوه از ویرگول استفاده کنید؛ نشانی دقیق لازم نیست."
                ),
            ),
            "avatar": forms.UUIDField(label="شناسهٔ تصویر نمایهٔ آماده", required=False),
            "cover": forms.UUIDField(label="شناسهٔ تصویر جلد آماده", required=False),
            "logo": forms.UUIDField(label="شناسهٔ نشان آماده", required=False),
            "accent_color": forms.CharField(
                label="رنگ (مانند #008080)", max_length=7, required=False
            ),
            "welcome_message": forms.CharField(
                label="پیام خوش‌آمد", max_length=500, required=False
            ),
        }
        for name in sorted(STEP_FIELDS[step]):
            self.fields[name] = fields[name]
            if name in {"avatar", "cover", "logo", "experience_years"}:
                self.fields["clear_" + name] = forms.BooleanField(
                    label="پاک کردن " + fields[name].label, required=False
                )

    def payload(self):
        values = {}
        for name in STEP_FIELDS[self.step]:
            value = self.cleaned_data.get(name)
            if self.cleaned_data.get("clear_" + name):
                values[name] = None
            elif (
                name in {"avatar", "cover", "logo", "experience_years"}
                and value is None
            ):
                continue
            elif name in {"specialties", "languages"}:
                values[name] = [x.strip() for x in value.splitlines() if x.strip()]
            elif name == "locations":
                locations = []
                for line in value.splitlines():
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) != 4:
                        raise ValueError("Invalid location")
                    modes = {"آنلاین": "online", "حضوری": "in_person"}
                    try:
                        selected = [
                            modes[p.strip()]
                            for p in parts[3].replace("،", ",").split(",")
                        ]
                    except KeyError:
                        raise ValueError("Invalid service mode") from None
                    locations.append(
                        {
                            "country_code": parts[0],
                            "region": parts[1],
                            "city": parts[2],
                            "modes": selected,
                        }
                    )
                values[name] = locations
            else:
                values[name] = value if value is not None else []
        return normalize_step(self.step, ProfessionalStepInput(values))

    def clean(self):
        values = super().clean()
        if not self.errors:
            try:
                self.cleaned_data = values
                self.payload()
            except (ValueError, TypeError):
                raise forms.ValidationError("دادهٔ مرحله معتبر نیست.") from None
        return values


class CredentialForm(CommandForm):
    expected_profile_version = forms.IntegerField(
        min_value=1, required=False, widget=forms.HiddenInput
    )
    credential_uuid = forms.UUIDField(
        label="شناسهٔ مدرک برای اصلاح یا انصراف", required=False
    )
    category = forms.ChoiceField(
        label="دستهٔ مدرک",
        choices=[("identity", "هویتی"), ("qualification", "صلاحیت حرفه‌ای")],
    )
    role = forms.ChoiceField(
        label="نقش مدرک حرفه‌ای",
        choices=[("", "بدون نقش"), ("coach", "مربی"), ("nutritionist", "متخصص تغذیه")],
        required=False,
    )
    type_code = forms.CharField(label="نوع مدرک", max_length=64)
    issuer = forms.CharField(label="صادرکننده", max_length=160)
    title = forms.CharField(label="عنوان مدرک", max_length=160)
    issued_on = forms.CharField(
        label="تاریخ صدور (سال-ماه-روز)", max_length=10, required=False
    )
    expires_on = forms.CharField(
        label="تاریخ انقضا (سال-ماه-روز)", max_length=10, required=False
    )
    calendar = forms.ChoiceField(
        label="تقویم تاریخ‌های مدرک",
        choices=[("jalali", "شمسی"), ("gregorian", "میلادی")],
    )
    source_asset = forms.UUIDField(label="شناسهٔ شواهد خصوصی آماده", required=False)

    def payload(self):
        values = {
            name: self.cleaned_data[name]
            for name in (
                "category",
                "role",
                "type_code",
                "issuer",
                "title",
                "source_asset",
            )
        }
        values["role"] = values["role"] or None
        for name in ("issued_on", "expires_on"):
            values[name] = (
                parse_birth_date(self.cleaned_data[name], self.cleaned_data["calendar"])
                if self.cleaned_data[name]
                else None
            )
        return CredentialInput(normalize_credential(CredentialInput(values)))


class UploadForm(CommandForm):
    purpose = forms.ChoiceField(
        label="کاربرد پروندهٔ خصوصی",
        choices=[
            ("avatar", "تصویر نمایه"),
            ("cover", "جلد"),
            ("logo", "نشان"),
            ("identity_evidence", "شواهد هویتی"),
            ("credential_evidence", "شواهد مدرک حرفه‌ای"),
        ],
    )
    subject_uuid = forms.UUIDField(label="شناسهٔ مدرک برای شواهد", required=False)
    declared_size = forms.IntegerField(
        label="اندازهٔ پرونده (بایت)", min_value=1, max_value=10000000
    )
    declared_type = forms.ChoiceField(
        label="نوع پرونده", choices=[("image/png", "PNG"), ("image/jpeg", "JPEG")]
    )


class VerificationForm(CommandForm):
    expected_profile_version = forms.IntegerField(
        min_value=1, required=False, widget=forms.HiddenInput
    )
    requested_targets = forms.MultipleChoiceField(
        label="هدف‌های بررسی",
        choices=[
            ("identity", "هویت"),
            ("coach", "مربی"),
            ("nutritionist", "متخصص تغذیه"),
        ],
        required=False,
    )
    verification_uuid = forms.UUIDField(label="شناسهٔ درخواست", required=False)
    target_uuid = forms.UUIDField(label="شناسهٔ هدف برای انصراف", required=False)


class WithdrawCredentialForm(CommandForm):
    credential_uuid = forms.UUIDField(widget=forms.HiddenInput)
