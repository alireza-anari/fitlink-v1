"""Current assigned, reasoned and case-step-up audited private reads."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.accounts.contracts import SecurityOutcome
from apps.accounts.sessions import locked_actor
from apps.governance import audit
from apps.governance.staff import require_staff

from .contracts import (
    ProfileNotFound,
    VerificationQueueDTO,
    VerificationQueueItem,
)
from .models import Verification
from .policies import validate_context
from .restrictions import RestrictionToken, restriction_token
from .verification import (
    _current_revisions,
    _hash_target,
    _staff_anchors,
    _staff_dto,
    _validate_revisions,
)


def assigned_verification_detail(actor, verification_uuid, step_up_id, reason_code, at):
    with transaction.atomic():
        *_, case, targets, assignments, receiver = _staff_anchors(
            actor, verification_uuid, step_up_id, reason_code, at
        )
        audit.append_event(
            SecurityOutcome(
                "verification.read", "succeeded", case.id, uuid4(), (), reason_code
            ),
            actor_uuid=actor.user_uuid,
            subject_type="verification",
        )
        return _staff_dto(case, targets, assignments)


def assigned_verification_evidence(
    actor, verification_uuid, asset_uuid, step_up_id, reason_code, at
):
    from apps.assets import delivery

    from .policies import ready_asset

    with transaction.atomic():
        (
            user,
            owner,
            profile,
            roles,
            credentials,
            case,
            targets,
            assignments,
            receiver,
        ) = _staff_anchors(actor, verification_uuid, step_up_id, reason_code, at)
        target = next(
            (
                t
                for t in targets
                if t.evidence.filter(
                    credential_revision__source_asset_id=asset_uuid
                ).exists()
            ),
            None,
        )
        if target is None or target.state in {"draft", "stale", "withdrawn"}:
            raise ProfileNotFound("Evidence unavailable")
        role = next((r for r in roles if r.id == target.role_id), None)
        revisions = _current_revisions(credentials, target.target)
        evidence_revision = (
            role.evidence_revision if role else profile.identity_evidence_revision
        )
        # Terminal decisions advance counters without changing submitted evidence.
        # Reconstruct their immutable hash with the submitted counters; current
        # evidence, identity name, source readiness and authority remain required.
        bound_target = (
            target if target.state in {"approved", "rejected", "revoked"} else None
        )
        if (
            evidence_revision != target.bound_evidence_revision
            or _hash_target(profile, role, revisions, bound_target=bound_target)
            != target.target_snapshot_hash
        ):
            raise ProfileNotFound("Evidence unavailable")
        if set(target.evidence.values_list("credential_revision_id", flat=True)) != {
            r.id for r in revisions
        }:
            raise ProfileNotFound("Evidence unavailable")
        _validate_revisions(owner, profile, revisions, at, ready_asset)
        # No bytes or delivery token escape until the required audit and the
        # domain transaction commit successfully. Assignment stays locked.
        audit.append_event(
            SecurityOutcome(
                "asset.read", "succeeded", asset_uuid, uuid4(), (), reason_code
            ),
            actor_uuid=actor.user_uuid,
            subject_type="asset",
        )
        return delivery.read_evidence_derivative(asset_uuid)


def submitted_verification_queue(actor, step_up_id, reason_code, cursor, at):
    validate_context(actor, at)
    if settings.SETTINGS_ENV not in {"test", "development"}:
        raise PermissionDenied("Verification unavailable")
    with transaction.atomic():
        user = locked_actor(actor, "staff.command", at)
        require_staff(
            user, "professional_verification", None, step_up_id, reason_code, at
        )
        if cursor is not None and (
            not isinstance(cursor, tuple)
            or len(cursor) != 2
            or not isinstance(cursor[0], datetime)
            or not timezone.is_aware(cursor[0])
            or not isinstance(cursor[1], UUID)
        ):
            raise ValueError("Invalid verification queue cursor")
        query = (
            Verification.objects.filter(
                state="submitted",
                profile__user__is_active=True,
                profile__user__state="active",
            )
            .exclude(profile__user=user)
            .exclude(profile__state="archived")
        )
        if cursor is not None:
            query = query.filter(
                Q(submitted_at__gt=cursor[0])
                | Q(submitted_at=cursor[0], id__gt=cursor[1])
            )
        rows = list(query.order_by("submitted_at", "id")[:26])
        page = rows[:25]
        audit.append_event(
            SecurityOutcome(
                "verification.read", "succeeded", None, uuid4(), (), reason_code
            ),
            actor_uuid=actor.user_uuid,
            subject_type="verification",
        )
        items = tuple(
            VerificationQueueItem(
                row.id,
                row.state,
                row.submitted_at,
                tuple(row.targets.order_by("target").values_list("target", flat=True)),
            )
            for row in page
        )
        next_cursor = (page[-1].submitted_at, page[-1].id) if len(rows) > 25 else None
        return VerificationQueueDTO(items, next_cursor)


@dataclass(frozen=True)
class TargetReviewBinding:
    evidence_revision: int
    decision_version: int
    declaration_version: int | None
    snapshot_hash: str = field(repr=False)
    restriction_token: RestrictionToken | None


def target_review_binding(profile, role, target):
    return TargetReviewBinding(
        role.evidence_revision if role else profile.identity_evidence_revision,
        role.decision_version if role else profile.identity_decision_version,
        role.declaration_version if role else None,
        target.target_snapshot_hash,
        restriction_token(role),
    )


def assigned_target_review_binding(
    actor, verification_uuid, target_uuid, step_up_id, reason_code, at
):
    with transaction.atomic():
        _, _, profile, roles, _, case, targets, _, _ = _staff_anchors(
            actor, verification_uuid, step_up_id, reason_code, at
        )
        target = next((t for t in targets if t.id == target_uuid), None)
        if target is None:
            raise ProfileNotFound("Verification unavailable")
        role = next((r for r in roles if r.id == target.role_id), None)
        audit.append_event(
            SecurityOutcome(
                "verification.read", "succeeded", case.id, uuid4(), (), reason_code
            ),
            actor_uuid=actor.user_uuid,
            subject_type="verification",
        )
        return target_review_binding(profile, role, target)
