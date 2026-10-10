"""Case-authorized temporary capability restrictions, separate from evidence."""

from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from apps.accounts.contracts import SecurityOutcome

from .contracts import ProfileConflict, ProfileNotFound
from .models import ProfessionalRoleRestriction, RoleRestrictionHistory


@dataclass(frozen=True)
class RestrictionToken:
    # Including released episodes prevents an ABA apply/release from reusing
    # an old unrestricted token. No wall-clock ordering is authoritative.
    episodes: tuple[tuple[UUID, int, bool], ...]


def restriction_token(role):
    if role is None:
        return None
    return RestrictionToken(
        tuple(
            (row.id, row.version, row.released_at is not None)
            for row in ProfessionalRoleRestriction.objects.select_for_update()
            .filter(role=role)
            .order_by("id")
        )
    )


def _change(
    actor,
    verification_uuid,
    role_uuid,
    expected_case_version,
    expected_role_version,
    expected_restriction_token,
    step_up_id,
    reason_code,
    operation_id,
    at,
    *,
    release,
    record,
    emit,
):
    from .setup import receipt, remember, request_hash
    from .verification import _context, _staff_anchors, _staff_dto

    _context(actor, expected_case_version, operation_id, at, record, emit)
    if type(expected_role_version) is not int or expected_role_version < 1:
        raise ValueError("Invalid role version")
    if reason_code != ("restriction_removed" if release else "role_restricted"):
        raise ValueError("Invalid restriction reason")
    command = "role.release_restriction" if release else "role.restrict"
    with transaction.atomic():
        user, _, _, roles, _, case, targets, assignments, _ = _staff_anchors(
            actor, verification_uuid, step_up_id, reason_code, at
        )
        role = next((r for r in roles if r.id == role_uuid), None)
        if role is None or not any(t.role_id == role.id for t in targets):
            raise ProfileNotFound("Verification unavailable")
        digest = request_hash(
            command,
            {
                "case": case.id,
                "role": role.id,
                "case_version": expected_case_version,
                "role_version": expected_role_version,
                "restriction": expected_restriction_token,
                "reason": reason_code,
            },
        )
        if receipt(user, operation_id, command, digest, case.id):
            return _staff_dto(case, targets, assignments)
        if (
            case.version != expected_case_version
            or role.version != expected_role_version
            or expected_restriction_token != restriction_token(role)
        ):
            raise ProfileConflict("Restriction version conflict")
        current = ProfessionalRoleRestriction.objects.filter(
            role=role, released_at__isnull=True
        ).first()
        if release:
            if current is None:
                raise ProfileConflict("Restriction unavailable")
            prior = current.version
            current.version += 1
            current.released_at, current.released_by = at, user
            current.save(
                update_fields=["version", "released_at", "released_by", "updated_at"]
            )
        else:
            if current is not None:
                raise ProfileConflict("Restriction already applied")
            prior = 1
            current = ProfessionalRoleRestriction.objects.create(
                role=role,
                verification=case,
                applied_by=user,
                reason_code=reason_code,
                applied_at=at,
                version=2,
                created_at=at,
            )
        RoleRestrictionHistory.objects.create(
            restriction=current,
            actor=user,
            event="released" if release else "applied",
            reason_code=reason_code,
            prior_version=prior,
            new_version=current.version,
            at=at,
            created_at=at,
            updated_at=at,
        )
        role.version += 1
        role.save(update_fields=["version", "updated_at"])
        case.version += 1
        case.save(update_fields=["version", "updated_at"])
        remember(
            user, operation_id, command, digest, case.id, current.id, case.version, at
        )
        record(
            SecurityOutcome(
                "professional.role_released"
                if release
                else "professional.role_restricted",
                "succeeded",
                role.id,
                operation_id,
                ("version",),
                reason_code,
            )
        )
        emit(case)
        return _staff_dto(case, targets, assignments)


def restrict_professional_role(*args, record, emit):
    return _change(*args, release=False, record=record, emit=emit)


def release_professional_role_restriction(*args, record, emit):
    return _change(*args, release=True, record=record, emit=emit)
