"""Exact command allowlists; no owner, key, publication or safety inputs."""

from rest_framework import serializers  # type: ignore[import-untyped]

from apps.accounts.serializers import StrictSerializer

from .validation import MAX_BYTES, MEDIA_TYPES, PURPOSES


class PositiveInteger(serializers.IntegerField):
    def to_internal_value(self, value):
        if isinstance(value, (bool, float)):
            raise serializers.ValidationError("Invalid integer")
        return super().to_internal_value(value)


class BeginUpload(StrictSerializer):
    purpose = serializers.ChoiceField(choices=sorted(PURPOSES))
    subject_uuid = serializers.UUIDField()
    operation_id = serializers.UUIDField()
    declared_size = PositiveInteger(min_value=1, max_value=MAX_BYTES)
    declared_type = serializers.ChoiceField(choices=sorted(MEDIA_TYPES))


class UploadCommand(StrictSerializer):
    expected_version = PositiveInteger(min_value=1)
    operation_id = serializers.UUIDField()


class UploadBody(StrictSerializer):
    expected_version = PositiveInteger(min_value=1)
    file = serializers.FileField(max_length=128, allow_empty_file=False)
