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


# Closed input vocabulary from the installed domain contract, not staff authority.
from uuid import UUID  # noqa: E402

from .restrictions import RestrictionToken  # noqa: E402
from .verification_models import VERIFICATION_REASONS  # noqa: E402
from .verification_selectors import TargetReviewBinding  # noqa: E402

STAFF_REASONS = VERIFICATION_REASONS


class StaffToken(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, dict) or set(data) != {"episodes"}:
            raise serializers.ValidationError("Invalid restriction token")
        episodes = data["episodes"]
        if not isinstance(episodes, (list, tuple)) or len(episodes) > 100:
            raise serializers.ValidationError("Invalid restriction token")
        parsed = []
        try:
            for item in episodes:
                if (
                    len(item) != 3
                    or type(item[1]) is not int
                    or item[1] < 1
                    or type(item[2]) is not bool
                ):
                    raise ValueError("Invalid episode")
                parsed.append((UUID(str(item[0])), item[1], item[2]))
        except (TypeError, ValueError, AttributeError):
            raise serializers.ValidationError("Invalid restriction token") from None
        return RestrictionToken(tuple(parsed))


class StaffBinding(StrictSerializer):
    evidence_revision = PositiveInteger(min_value=1)
    decision_version = PositiveInteger(min_value=1)
    declaration_version = PositiveInteger(min_value=1, allow_null=True)
    snapshot_hash = serializers.RegexField(r"^[0-9a-f]{64}$", max_length=64)
    restriction_token = StaffToken(allow_null=True)

    def validate(self, attrs):
        return TargetReviewBinding(**attrs)


class StaffAccess(StrictSerializer):
    step_up_id = serializers.UUIDField()
    reason_code = serializers.ChoiceField(choices=STAFF_REASONS)


class StaffCommand(StaffAccess):
    expected_case_version = PositiveInteger(min_value=1)
    operation_id = serializers.UUIDField()


class StaffStart(StaffAccess):
    expected_version = PositiveInteger(min_value=1)


class StaffAssign(StaffStart):
    assignee_uuid = serializers.UUIDField()


class StaffTargetCommand(StaffCommand):
    target_uuid = serializers.UUIDField()
    expected_target_version = PositiveInteger(min_value=1)
    expected_binding = StaffBinding()
    explanation = serializers.CharField(
        max_length=1000, allow_blank=True, trim_whitespace=False
    )


class StaffDecision(StaffTargetCommand):
    decision = serializers.ChoiceField(choices=["approve", "reject"])


class StaffRevoke(StaffTargetCommand):
    effective_approval_uuid = serializers.UUIDField()


class StaffRole(StaffCommand):
    role_uuid = serializers.UUIDField()
    expected_role_version = PositiveInteger(min_value=1)
    expected_restriction_token = StaffToken()
