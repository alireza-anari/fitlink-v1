"""Explicit transport allowlists; never bind security models generically."""

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from rest_framework import serializers  # type: ignore[import-untyped]

from .dates import parse_birth_date
from .phone import normalize_iranian_mobile
from .recovery_models import EVIDENCE_OUTCOMES, EVIDENCE_TYPES


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if not hasattr(data, "keys") or set(data) - set(self.fields):
            raise serializers.ValidationError("Invalid fields")
        return super().to_internal_value(data)


class PhoneField(serializers.CharField):
    def __init__(self, **kwargs):
        super().__init__(max_length=32, trim_whitespace=False, **kwargs)

    def to_internal_value(self, data):
        try:
            return normalize_iranian_mobile(super().to_internal_value(data))
        except ValueError:
            raise serializers.ValidationError("Invalid phone") from None


class EmptySerializer(StrictSerializer):
    pass


class OtpRequestSerializer(StrictSerializer):
    phone = PhoneField()


class ProofSerializer(StrictSerializer):
    challenge_id = serializers.UUIDField()
    code = serializers.CharField(max_length=16, trim_whitespace=False)


class OtpVerifySerializer(ProofSerializer):
    phone = PhoneField()
    birth_date = serializers.CharField(max_length=10, required=False)
    calendar = serializers.ChoiceField(choices=["gregorian", "jalali"], required=False)
    adult_attested = serializers.BooleanField(default=False)

    def validate(self, data):
        if ("birth_date" in data) != ("calendar" in data):
            raise serializers.ValidationError("Labeled date required")
        if "birth_date" in data:
            try:
                data["birth_date"] = parse_birth_date(
                    data["birth_date"], data.pop("calendar")
                )
            except ValueError:
                raise serializers.ValidationError("Invalid date") from None
        return data


class AccountPreferencesSerializer(StrictSerializer):
    locale = serializers.ChoiceField(choices=["fa", "en"], required=False)
    timezone = serializers.CharField(max_length=64, required=False)

    def validate_timezone(self, value):
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError):
            raise serializers.ValidationError("Invalid timezone") from None
        return value


class PhoneChangeSerializer(StrictSerializer):
    new_phone = PhoneField()


class ChangeSerializer(StrictSerializer):
    change_uuid = serializers.UUIDField()


class ChangeRequestSerializer(ChangeSerializer):
    kind = serializers.ChoiceField(choices=["old", "new"])


class ChangeProofSerializer(ChangeRequestSerializer, ProofSerializer):
    pass


class RecoveryRequestSerializer(StrictSerializer):
    old_phone = PhoneField()
    new_phone = PhoneField()
    contact_preference = serializers.ChoiceField(
        choices=["new_phone"], default="new_phone"
    )


class StaffAuthoritySerializer(StrictSerializer):
    step_up_id = serializers.UUIDField()
    reason_code = serializers.RegexField(r"\A[a-z_]{1,32}\Z", max_length=32)


class StaffCommandSerializer(StaffAuthoritySerializer):
    expected_version = serializers.IntegerField(min_value=1, max_value=2**63 - 1)


class StaffEvidenceSerializer(StaffCommandSerializer):
    classification = serializers.ChoiceField(choices=EVIDENCE_TYPES)
    outcome = serializers.ChoiceField(choices=EVIDENCE_OUTCOMES)
    checksum = serializers.RegexField(r"\A[0-9a-f]{64}\Z", max_length=64)
    reference = serializers.UUIDField()


class StaffDecisionSerializer(StaffCommandSerializer):
    decision = serializers.ChoiceField(choices=["approved", "rejected"])


class PrivacyRequestSerializer(StrictSerializer):
    kind = serializers.ChoiceField(choices=["export", "delete"])
    request_id = serializers.UUIDField()
    confirmed = serializers.BooleanField(default=False)
