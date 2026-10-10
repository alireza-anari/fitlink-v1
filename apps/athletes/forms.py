"""Persian native controls; missing optional inputs never mean implicit clear."""

from decimal import Decimal

from django import forms

from apps.assets.views import CommandForm

from .contracts import BaselineStepInput
from .validation import DECIMALS, INTEGERS, STEP_FIELDS, TEXT, TOKENS, normalize_step

LABELS = {
    "height_cm": "قد (سانتی‌متر)",
    "weight_kg": "وزن (کیلوگرم)",
    "goals": "هدف‌ها",
    "experience": "تجربه",
    "training_experience_months": "ماه‌های تجربهٔ تمرین",
    "available_days": "روزهای در دسترس",
    "equipment": "تجهیزات",
    "equipment_other": "تجهیزات دیگر",
    "facilities": "امکانات",
    "lifestyle": "سبک زندگی",
    "sleep_hours": "ساعت خواب",
    "energy": "سطح انرژی",
    "meals_per_day": "تعداد وعده‌ها",
    "hydration_habit": "عادت نوشیدن آب",
    "nutrition_habits": "عادت‌های غذایی",
    "waist_cm": "دور کمر (سانتی‌متر)",
    "approximate_records": "رکوردهای تقریبی",
}
TOKEN_LABELS = {
    "general_fitness": "تناسب عمومی",
    "strength": "قدرت",
    "endurance": "استقامت",
    "muscle_gain": "افزایش عضله",
    "weight_management": "مدیریت وزن",
    "beginner": "مبتدی",
    "intermediate": "متوسط",
    "advanced": "پیشرفته",
    "home": "خانه",
    "gym": "باشگاه",
    "outdoors": "فضای باز",
    "other": "دیگر",
    "bodyweight": "وزن بدن",
    "dumbbells": "دمبل",
    "barbell": "هالتر",
    "machines": "دستگاه",
    "bands": "کش",
    "sedentary": "کم‌تحرک",
    "mixed": "متوسط",
    "active": "فعال",
    "low": "کم",
    "regular": "منظم",
    "unknown": "نامشخص",
}


class BaselineStepForm(CommandForm):
    def __init__(self, step, data=None, **kwargs):
        if step not in STEP_FIELDS:
            raise ValueError("Invalid step")
        self.step = step
        super().__init__(data, **kwargs)
        self.fields["expected_version"].required = True
        for name in STEP_FIELDS[step]:
            label = LABELS[name]
            if name in DECIMALS or name in INTEGERS:
                field = forms.CharField(label=label, max_length=32, required=False)
                self.fields["clear_" + name] = forms.BooleanField(
                    label="پاک کردن " + label, required=False
                )
            elif name == "available_days":
                field = forms.MultipleChoiceField(
                    label=label,
                    choices=[(str(i), str(i)) for i in range(1, 8)],
                    required=False,
                )
            elif name in TOKENS:
                choices = [(x, TOKEN_LABELS[x]) for x in sorted(TOKENS[name])]
                field = (
                    forms.MultipleChoiceField
                    if name in {"goals", "equipment", "facilities"}
                    else forms.ChoiceField
                )(label=label, choices=choices, required=False)
            elif name == "approximate_records":
                field = forms.CharField(
                    label=label,
                    required=False,
                    max_length=1500,
                    widget=forms.Textarea(
                        attrs={"rows": 3, "class": "w-full max-w-full"}
                    ),
                    help_text=(
                        "اختیاری؛ حداکثر پنج خط: عنوان | مقدار | واحد "
                        "(kg، reps، seconds، metres) | تاریخ و زمان با اختلاف ساعت."
                    ),
                )
            else:
                field = forms.CharField(
                    label=label, max_length=TEXT[name], required=False
                )
            self.fields[name] = field

    def payload(self):
        values = {}
        for name in STEP_FIELDS[self.step]:
            value = self.cleaned_data.get(name)
            if self.cleaned_data.get("clear_" + name):
                values[name] = None
            elif value not in (None, "", []):
                values[name] = (
                    int(value)
                    if name in INTEGERS
                    else [int(v) for v in value]
                    if name == "available_days"
                    else value
                )
        if "approximate_records" in values:
            records = []
            for line in values["approximate_records"].splitlines():
                parts = [p.strip() for p in line.split("|")]
                if len(parts) != 4:
                    raise ValueError("Invalid record")
                records.append(
                    dict(
                        zip(
                            ("label", "value", "unit", "observed_at"),
                            parts,
                            strict=True,
                        ),
                        provenance="self_reported",
                    )
                )
            values["approximate_records"] = records
        normalized = normalize_step(self.step, BaselineStepInput(values))
        return {
            name: str(value) if isinstance(value, Decimal) else value
            for name, value in normalized.items()
        }

    def clean(self):
        data = super().clean()
        if not self.errors:
            try:
                self.cleaned_data = data
                self.payload()
            except (ValueError, TypeError):
                raise forms.ValidationError("مقدار معتبر نیست.") from None
        return data


class ConsentForm(CommandForm):
    confirmed = forms.BooleanField(
        label="با نگهداری خصوصی داده‌های اختیاری این ارزیابی برای خودم موافقم.",
        required=False,
    )


class RevokeConsentForm(CommandForm):
    consent_uuid = forms.UUIDField(label="شناسهٔ رسید اجازهٔ نگهداری")
    expected_consent_version = forms.IntegerField(
        label="نسخهٔ رسید اجازه", min_value=1, initial=1
    )
