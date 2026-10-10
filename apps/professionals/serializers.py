"""Owner-only field allowlists; no staff decision/publication transport."""

from rest_framework import serializers  # type: ignore[import-untyped]

from apps.accounts.serializers import StrictSerializer
from apps.assets.serializers import PositiveInteger


class Create(StrictSerializer):
    operation_id = serializers.UUIDField()


class Command(Create):
    expected_version = PositiveInteger(min_value=1)


class Step(Command):
    values = serializers.DictField()


class Credential(Create):
    expected_profile_version = PositiveInteger(min_value=1)
    values = serializers.DictField()


class Revision(Step):
    pass


class Prepare(Create):
    expected_profile_version = PositiveInteger(min_value=1)
    requested_targets = serializers.ListField(
        child=serializers.ChoiceField(choices=["identity", "coach", "nutritionist"]),
        max_length=3,
        min_length=1,
    )


class Withdraw(Command):
    target_uuid = serializers.UUIDField()
