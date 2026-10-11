"""Bounded references from trusted staff operations, never authority themselves."""

from django import forms

from apps.assets.views import CommandForm


class AccessForm(CommandForm):
    operation_id = None
    expected_version = None
    step_up_id = forms.UUIDField(label="شناسهٔ احراز تازه")
    reason_code = forms.ChoiceField(
        label="دلیل بررسی", choices=[("verification_review", "بررسی مدارک")]
    )
