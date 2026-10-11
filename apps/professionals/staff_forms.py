"""Strict command inputs; all state, authority and bindings belong to services."""

from django import forms
from django.core.serializers.json import DjangoJSONEncoder

from apps.assets.views import CommandForm

from . import serializers as schema

REASON_LABELS = {
    "verification_review": "بررسی مدارک",
    "staff_assigned": "واگذاری پرونده",
    "credentials_approved": "مدارک پذیرفته شد",
    "credentials_invalid": "مدارک معتبر نیست",
    "evidence_incomplete": "مدارک کامل نیست",
    "evidence_expired": "اعتبار مدارک پایان یافته",
    "evidence_revoked": "ابطال تأیید مدارک",
    "role_restricted": "محدودیت موقت نقش",
    "restriction_removed": "رفع محدودیت موقت",
}


class AccessForm(CommandForm):
    operation_id = None  # type: ignore[assignment]
    expected_version = None  # type: ignore[assignment]
    step_up_id = forms.UUIDField(label="شناسهٔ احراز تازه")
    reason_code = forms.ChoiceField(
        label="دلیل بررسی",
        choices=[
            (name, REASON_LABELS.get(name, "دلیل ثبت‌شده: " + name))
            for name in schema.STAFF_REASONS
        ],
        initial="verification_review",
    )


class StartForm(AccessForm):
    expected_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)  # type: ignore[assignment]
    step_up_id = forms.UUIDField(widget=forms.HiddenInput)


class QueueForm(AccessForm):
    cursor_at = forms.DateTimeField(required=False, widget=forms.HiddenInput)
    cursor_uuid = forms.UUIDField(required=False, widget=forms.HiddenInput)

    def clean(self):
        values = super().clean()
        if bool(values.get("cursor_at")) != bool(values.get("cursor_uuid")):
            raise forms.ValidationError("درخواست معتبر نیست.")
        return values


class DecisionForm(CommandForm):
    expected_version = None  # type: ignore[assignment]
    expected_case_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    target_uuid = forms.UUIDField(widget=forms.HiddenInput)
    expected_target_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    expected_binding = forms.JSONField(
        widget=forms.HiddenInput, encoder=DjangoJSONEncoder
    )
    step_up_id = forms.UUIDField(widget=forms.HiddenInput)
    reason_code = forms.ChoiceField(
        label="دلیل تصمیم",
        choices=[
            (name, REASON_LABELS[name])
            for name in (
                "credentials_approved",
                "credentials_invalid",
                "evidence_incomplete",
                "evidence_expired",
            )
        ],
    )
    decision = forms.ChoiceField(
        label="تصمیم", choices=[("approve", "تأیید این هدف"), ("reject", "رد این هدف")]
    )
    explanation = forms.CharField(
        label="توضیح خصوصی تصمیم",
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )
    input_schema = schema.StaffDecision

    def clean(self):
        values = super().clean()
        if self.errors:
            return values
        serializer = self.input_schema(data=values)
        if not serializer.is_valid():
            raise forms.ValidationError("درخواست معتبر نیست.")
        return serializer.validated_data


class RevokeForm(DecisionForm):
    decision = None  # type: ignore[assignment]
    effective_approval_uuid = forms.UUIDField(widget=forms.HiddenInput)
    reason_code = forms.ChoiceField(
        label="دلیل ابطال", choices=[("evidence_revoked", "ابطال تأیید مدارک")]
    )
    explanation = forms.CharField(
        label="توضیح خصوصی ابطال",
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )
    input_schema = schema.StaffRevoke


class RoleForm(CommandForm):
    expected_version = None  # type: ignore[assignment]
    expected_case_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    role_uuid = forms.UUIDField(widget=forms.HiddenInput)
    expected_role_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    expected_restriction_token = forms.JSONField(
        widget=forms.HiddenInput, encoder=DjangoJSONEncoder
    )
    step_up_id = forms.UUIDField(widget=forms.HiddenInput)
    reason_code = forms.ChoiceField(
        label="دلیل محدودیت",
        choices=[
            ("role_restricted", "محدودیت موقت نقش"),
            ("restriction_removed", "رفع محدودیت موقت"),
        ],
    )

    def clean(self):
        values = super().clean()
        if self.errors:
            return values
        serializer = schema.StaffRole(data=values)
        if not serializer.is_valid():
            raise forms.ValidationError("درخواست معتبر نیست.")
        return serializer.validated_data
