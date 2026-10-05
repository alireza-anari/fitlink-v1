"""Fresh operational switches; an enabled switch confers no object authority."""

from datetime import datetime
from uuid import UUID, uuid4

from django.core.exceptions import PermissionDenied
from django.db import DatabaseError, transaction

from apps.accounts.contracts import SecurityOutcome
from apps.accounts.sessions import AccountActor, locked_actor

from .audit import append_event
from .flag_models import FEATURE_KEYS, FeatureFlag
from .outbox import append_outbox
from .staff import require_staff


def feature_enabled(key: str) -> bool:
    if key not in FEATURE_KEYS:
        return False
    try:
        return FeatureFlag.objects.get(key=key).enabled is True
    except (DatabaseError, FeatureFlag.DoesNotExist):
        return False


def professional_entry_enabled() -> bool:
    return feature_enabled("professional_registration")


def set_feature(
    actor: AccountActor,
    key: str,
    enabled: bool,
    expected_version: int,
    reason_code: str,
    step_up_id: UUID,
    at: datetime,
) -> None:
    if (
        key not in FEATURE_KEYS
        or type(enabled) is not bool
        or type(expected_version) is not int
        or expected_version < 1
    ):
        raise PermissionDenied("Feature action denied")
    with transaction.atomic():
        user = locked_actor(actor, "staff.command", at)
        try:
            flag_id = FeatureFlag.objects.get(key=key).id
        except FeatureFlag.DoesNotExist:
            raise PermissionDenied("Feature action denied") from None
        require_staff(user, "feature_flags", flag_id, step_up_id, reason_code, at)
        flag = FeatureFlag.objects.select_for_update().get(pk=flag_id)
        if flag.version != expected_version:
            raise PermissionDenied("Feature action denied")
        flag.enabled = enabled
        flag.version += 1
        flag.save(update_fields=["enabled", "version"])
        append_event(
            SecurityOutcome(
                "feature_flag.changed",
                "succeeded",
                flag.id,
                uuid4(),
                ("enabled", "version"),
                reason_code,
            ),
            actor_uuid=user.public_id,
            subject_type="flag",
        )
        append_outbox(
            "feature_flag.changed",
            flag.id,
            flag.version,
            {"flag_uuid": str(flag.id)},
            f"feature_flag.changed:{flag.id}:{flag.version}",
        )
