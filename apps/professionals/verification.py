"""Task 6 bound-edit effects only. No submission or staff decision commands."""

from collections.abc import Callable
from datetime import datetime
from uuid import UUID

from django.db import connection
from django.db.models import Max

from apps.accounts.contracts import OutcomeRecorder, SecurityOutcome
from apps.accounts.models import User

from .models import ProfessionalProfile, ProfessionalRole
from .verification_models import (
    Verification,
    VerificationDecision,
    VerificationHistory,
    VerificationTarget,
)

VerificationEmitter = Callable[[Verification], None]


def _stale_pending(
    profile: ProfessionalProfile,
    kind: str,
    user: User,
    operation_id: UUID,
    at: datetime,
    record: OutcomeRecorder,
    emit: VerificationEmitter,
) -> None:
    if not connection.in_atomic_block:
        raise RuntimeError("Binding changes require owner transaction")
    cases = list(
        Verification.objects.select_for_update()
        .filter(profile=profile, state__in=["submitted", "under_review"])
        .order_by("id")
    )
    for case in cases:
        targets = list(
            VerificationTarget.objects.select_for_update()
            .filter(verification=case)
            .order_by("id")
        )
        changed = False
        for target in targets:
            if target.target != kind or target.state not in {
                "submitted",
                "under_review",
            }:
                continue
            prior = target.version
            target.state = "stale"
            target.version += 1
            target.save(update_fields=["state", "version", "updated_at"])
            sequence = (
                VerificationDecision.objects.filter(
                    profile=profile, target_kind=kind
                ).aggregate(value=Max("decision_sequence"))["value"]
                or 0
            ) + 1
            # Stale closes this pending request. It does not supersede an
            # evidence approval or advance the evidentiary decision counter.
            VerificationDecision.objects.create(
                target=target,
                profile=profile,
                target_kind=kind,
                actor=user,
                decision="stale",
                reason_code="material_changed",
                target_snapshot_hash=target.target_snapshot_hash,
                bound_evidence_revision=target.bound_evidence_revision,
                decision_sequence=sequence,
                decided_at=at,
                created_at=at,
                updated_at=at,
            )
            VerificationHistory.objects.create(
                verification=case,
                target=target,
                actor=user,
                event="target_stale",
                reason_code="material_changed",
                prior_version=prior,
                new_version=target.version,
                at=at,
                created_at=at,
                updated_at=at,
            )
            record(
                SecurityOutcome(
                    "verification.stale",
                    "succeeded",
                    target.id,
                    operation_id,
                    ("state", "version"),
                    "material_changed",
                )
            )
            changed = True
        if changed:
            case.version += 1
            if all(
                t.state in {"approved", "rejected", "stale", "withdrawn"}
                for t in targets
            ):
                case.state, case.decided_at = "decided", at
            case.save(update_fields=["state", "version", "decided_at", "updated_at"])
            emit(case)


def target_evidence_changed(
    profile: ProfessionalProfile,
    role: ProfessionalRole | None,
    user: User,
    operation_id: UUID,
    at: datetime,
    *,
    record: OutcomeRecorder,
    emit: VerificationEmitter,
) -> None:
    if not connection.in_atomic_block or (
        role is not None and role.profile_id != profile.id
    ):
        raise ValueError("Invalid binding anchor")
    if role is None:
        profile.identity_evidence_revision += 1
        profile.save(update_fields=["identity_evidence_revision", "updated_at"])
    else:
        role.evidence_revision += 1
        role.version += 1
        role.save(update_fields=["evidence_revision", "version", "updated_at"])
    _stale_pending(
        profile, role.role if role else "identity", user, operation_id, at, record, emit
    )


def target_declaration_changed(
    profile: ProfessionalProfile,
    role: ProfessionalRole,
    active: bool,
    user: User,
    operation_id: UUID,
    at: datetime,
    *,
    record: OutcomeRecorder,
    emit: VerificationEmitter,
) -> None:
    if (
        not connection.in_atomic_block
        or role.profile_id != profile.id
        or type(active) is not bool
    ):
        raise ValueError("Invalid declaration anchor")
    if role.declared_active == active:
        return
    role.declared_active = active
    role.declaration_version += 1
    role.version += 1
    role.save(
        update_fields=[
            "declared_active",
            "declaration_version",
            "version",
            "updated_at",
        ]
    )
    _stale_pending(profile, role.role, user, operation_id, at, record, emit)
