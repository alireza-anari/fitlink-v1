"""Exact owner command transport fields; authority stays in use cases."""

from rest_framework import serializers  # type: ignore[import-untyped]

from apps.accounts.serializers import StrictSerializer
from apps.assets.serializers import PositiveInteger


class Create(StrictSerializer):
    operation_id = serializers.UUIDField()


class Draft(Create):
    expected_profile_version = PositiveInteger(min_value=1)


class Command(Create):
    expected_version = PositiveInteger(min_value=1)


class Step(Command):
    values = serializers.DictField()


class Grant(Command):
    confirmed = serializers.BooleanField(default=False)


class Revoke(Create):
    consent_uuid = serializers.UUIDField()
    expected_consent_version = PositiveInteger(min_value=1)
