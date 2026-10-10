"""Independent evidence bindings, intake and case-authorized terminal decisions."""

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


# Intake commands share the target anchors with terminal decisions.
def _context(actor, version, operation, at, record, emit):
    from .policies import validate_context

    validate_context(actor, at)
    if (
        type(version) is not int
        or version < 1
        or not isinstance(operation, UUID)
        or not callable(record)
        or not callable(emit)
    ):
        raise ValueError("Invalid verification command")


def _owner_anchors(actor, at):
    from apps.accounts.sessions import locked_actor

    from .models import Credential
    from .setup import locked_profile, locked_roles

    user = locked_actor(actor, "professional.verify_submit", at)
    profile = locked_profile(user)
    roles = locked_roles(profile)
    credentials = list(
        Credential.objects.select_for_update().filter(profile=profile).order_by("id")
    )
    return user, profile, roles, credentials


def _case(profile, identifier):
    from .contracts import ProfileNotFound

    if not isinstance(identifier, UUID):
        raise ProfileNotFound("Verification unavailable")
    case = (
        Verification.objects.select_for_update()
        .filter(pk=identifier, profile=profile)
        .first()
    )
    if case is None:
        raise ProfileNotFound("Verification unavailable")
    return case


def _targets(case):
    return list(
        VerificationTarget.objects.select_for_update()
        .filter(verification=case)
        .order_by("id")
    )


def _current_revisions(credentials, kind):
    from .models import CredentialRevision

    rows = []
    for credential in credentials:
        if credential.withdrawn_at is not None:
            continue
        matching = (
            credential.category == "identity"
            if kind == "identity"
            else (
                credential.category == "qualification" and credential.role.role == kind
            )
        )
        if not matching:
            continue
        if credential.current_revision_id is None:
            raise ValueError("Verification evidence incomplete")
        revision = CredentialRevision.objects.get(
            pk=credential.current_revision_id, credential=credential
        )
        if any(
            getattr(credential, name) != getattr(revision, name)
            for name in (
                "category",
                "type_code",
                "issuer",
                "title",
                "issued_on",
                "expires_on",
            )
        ):
            raise ValueError("Verification evidence inconsistent")
        rows.append(revision)
    return sorted(rows, key=lambda row: row.id)


def _hash_target(profile, role, revisions, *, bound_target=None):
    from .setup import request_hash

    return request_hash(
        "verification.snapshot",
        {
            "target": role.role if role else "identity",
            "role": role.id if role else None,
            "identity_name": "" if role else profile.identity_name,
            "evidence_revision": bound_target.bound_evidence_revision
            if bound_target is not None
            else (
                role.evidence_revision if role else profile.identity_evidence_revision
            ),
            "decision_version": bound_target.bound_decision_version
            if bound_target is not None
            else (role.decision_version if role else profile.identity_decision_version),
            "declaration_version": bound_target.bound_declaration_version
            if bound_target is not None
            else (role.declaration_version if role else None),
            "revisions": [
                (row.id, row.revision_hash, row.source_asset_id, row.source_sha256)
                for row in revisions
            ],
        },
    )


def _validate_revisions(user, profile, revisions, at, asset_validator):
    from datetime import UTC

    if not revisions:
        raise ValueError("Verification evidence incomplete")
    day = at.astimezone(UTC).date()
    for revision in sorted(revisions, key=lambda row: row.source_asset_id):
        if revision.expires_on is not None and revision.expires_on < day:
            raise ValueError("Verification evidence expired")
        if revision.issued_on is not None and revision.issued_on > day:
            raise ValueError("Verification evidence not current")
        asset = asset_validator(
            user,
            profile,
            revision.source_asset_id,
            "identity_evidence"
            if revision.category == "identity"
            else "credential_evidence",
            revision.credential_id,
        )
        if asset.sha256 != revision.source_sha256:
            raise ValueError("Verification source binding changed")


def _identity_current(user, profile, credentials, at, asset_validator):
    # Submission-only prerequisite: reuse a historical effective shared identity
    # approval. This does not expose eligibility or grant any role authority.
    decision = (
        VerificationDecision.objects.filter(
            profile=profile,
            target_kind="identity",
            decision__in=["approve", "reject", "revoke"],
        )
        .order_by("-decision_sequence")
        .first()
    )
    if (
        decision is None
        or decision.decision != "approve"
        or decision.bound_evidence_revision != profile.identity_evidence_revision
    ):
        return False
    target = decision.target
    if (
        target.identity_name != profile.identity_name
        or target.target_snapshot_hash != decision.target_snapshot_hash
    ):
        return False
    revisions = _current_revisions(credentials, "identity")
    if set(target.evidence.values_list("credential_revision_id", flat=True)) != {
        r.id for r in revisions
    }:
        return False
    try:
        _validate_revisions(user, profile, revisions, at, asset_validator)
    except (ValueError, LookupError):
        return False
    return True


def _bind(profile, roles, credentials, case, requested):
    from .models import VerificationEvidence

    targets = []
    for kind in requested:
        role = next((r for r in roles if r.role == kind), None)
        revisions = _current_revisions(credentials, kind)
        target = VerificationTarget.objects.create(
            verification=case,
            target=kind,
            role=role,
            bound_evidence_revision=role.evidence_revision
            if role
            else profile.identity_evidence_revision,
            bound_decision_version=role.decision_version
            if role
            else profile.identity_decision_version,
            bound_declaration_version=role.declaration_version if role else None,
            target_snapshot_hash=_hash_target(profile, role, revisions),
            identity_name=profile.identity_name if role is None else "",
        )
        for revision in revisions:
            VerificationEvidence.objects.create(
                target=target, credential_revision=revision, category=revision.category
            )
        targets.append(target)
    return targets


def _owner_dto(case):
    from .contracts import VerificationOwnerDTO, VerificationTargetDTO

    return VerificationOwnerDTO(
        case.id,
        case.sequence,
        case.state,
        case.version,
        case.submitted_at,
        tuple(
            VerificationTargetDTO(t.id, t.target, t.state, t.version)
            for t in case.targets.order_by("target")
        ),
        tuple((h.event, h.target_id, h.at) for h in case.history.order_by("at", "id")),
    )


def _history(case, user, event, reason, prior, at, target=None):
    VerificationHistory.objects.create(
        verification=case,
        target=target,
        actor=user,
        event=event,
        reason_code=reason,
        prior_version=prior,
        new_version=target.version if target else case.version,
        at=at,
        created_at=at,
        updated_at=at,
    )


def prepare_verification(
    actor,
    requested_targets,
    expected_profile_version,
    operation_id,
    at,
    *,
    record,
    emit,
    asset_validator,
):
    from django.db import transaction

    from .contracts import ProfileConflict
    from .models import VerificationEvidence
    from .setup import receipt, remember, request_hash

    _context(actor, expected_profile_version, operation_id, at, record, emit)
    with transaction.atomic():
        user, profile, roles, credentials = _owner_anchors(actor, at)
        if (
            not isinstance(requested_targets, tuple)
            or not requested_targets
            or any(
                type(k) is not str or k not in {"identity", "coach", "nutritionist"}
                for k in requested_targets
            )
            or len(set(requested_targets)) != len(requested_targets)
        ):
            raise ValueError("Invalid requested verification targets")
        requested = tuple(sorted(requested_targets))
        digest = request_hash(
            "verification.prepare",
            {"targets": requested, "expected_version": expected_profile_version},
        )
        old = receipt(user, operation_id, "verification.prepare", digest, profile.id)
        if old:
            return _owner_dto(_case(profile, old.result_uuid))
        if profile.version != expected_profile_version:
            raise ProfileConflict("Profile version conflict")
        if any(
            kind != "identity"
            and not any(r.role == kind and r.declared_active for r in roles)
            for kind in requested
        ):
            raise ValueError("Verification target not declared")
        if "identity" not in requested and not _identity_current(
            user, profile, credentials, at, asset_validator
        ):
            raise ValueError("Shared identity review required")
        case = (
            Verification.objects.select_for_update()
            .filter(profile=profile, state__in=["draft", "submitted", "under_review"])
            .first()
        )
        if case is not None and case.state != "draft":
            raise ProfileConflict("Verification already pending")
        if case is None:
            seq = (
                Verification.objects.filter(profile=profile).aggregate(
                    value=Max("sequence")
                )["value"]
                or 0
            ) + 1
            case = Verification.objects.create(
                profile=profile, sequence=seq, created_at=at
            )
        else:
            targets = _targets(case)
            VerificationEvidence.objects.filter(target__in=targets).delete()
            VerificationTarget.objects.filter(pk__in=[t.id for t in targets]).delete()
            case.version += 1
            case.save(update_fields=["version", "updated_at"])
        _bind(profile, roles, credentials, case, requested)
        # Different preparations with the same profile CAS version cannot both
        # replace the draft target set. Receipt replay precedes this fence.
        profile.version += 1
        profile.save(update_fields=["version", "updated_at"])
        remember(
            user,
            operation_id,
            "verification.prepare",
            digest,
            profile.id,
            case.id,
            case.version,
            at,
        )
        record(
            SecurityOutcome(
                "verification.read",
                "succeeded",
                case.id,
                operation_id,
                (),
                "user_requested",
            )
        )
        emit(case)
        return _owner_dto(case)


def submit_verification(
    actor,
    verification_uuid,
    expected_version,
    operation_id,
    at,
    *,
    record,
    emit,
    asset_validator,
):
    from django.db import transaction

    from .contracts import ProfileConflict
    from .models import VerificationEvidence
    from .setup import complete, receipt, remember, request_hash

    _context(actor, expected_version, operation_id, at, record, emit)
    with transaction.atomic():
        user, profile, roles, credentials = _owner_anchors(actor, at)
        case = _case(profile, verification_uuid)
        digest = request_hash(
            "verification.submit",
            {"case": case.id, "expected_version": expected_version},
        )
        if receipt(user, operation_id, "verification.submit", digest, case.id):
            return _owner_dto(case)
        if case.version != expected_version or case.state != "draft":
            raise ProfileConflict("Verification version conflict")
        if profile.state != "private_ready" or not complete(profile):
            raise ValueError("Professional setup incomplete")
        old_targets = _targets(case)
        requested = tuple(sorted(t.target for t in old_targets))
        if not requested or any(
            kind != "identity"
            and not any(r.role == kind and r.declared_active for r in roles)
            for kind in requested
        ):
            raise ValueError("Verification targets unavailable")
        if "identity" not in requested and not _identity_current(
            user, profile, credentials, at, asset_validator
        ):
            raise ValueError("Shared identity review required")
        # Draft bindings may refresh; submitted bindings never do.
        VerificationEvidence.objects.filter(target__in=old_targets).delete()
        VerificationTarget.objects.filter(pk__in=[t.id for t in old_targets]).delete()
        targets = _bind(profile, roles, credentials, case, requested)
        all_revisions = []
        for target in targets:
            revisions = _current_revisions(credentials, target.target)
            if not revisions:
                raise ValueError("Verification evidence incomplete")
            all_revisions.extend(revisions)
        _validate_revisions(user, profile, all_revisions, at, asset_validator)
        for target in targets:
            target.state = "submitted"
            target.version += 1
            target.save(update_fields=["state", "version", "updated_at"])
        prior = case.version
        case.state, case.submitted_at = "submitted", at
        case.version += 1
        case.snapshot_hash = request_hash(
            "verification.bundle",
            {"targets": sorted((t.target, t.target_snapshot_hash) for t in targets)},
        )
        case.save(
            update_fields=[
                "state",
                "version",
                "submitted_at",
                "snapshot_hash",
                "updated_at",
            ]
        )
        _history(case, user, "submit", "verification_submitted", prior, at)
        remember(
            user,
            operation_id,
            "verification.submit",
            digest,
            case.id,
            case.id,
            case.version,
            at,
        )
        record(
            SecurityOutcome(
                "verification.submitted",
                "succeeded",
                case.id,
                operation_id,
                ("state", "version"),
                "verification_submitted",
            )
        )
        emit(case)
        return _owner_dto(case)


def withdraw_verification_target(
    actor,
    verification_uuid,
    target_uuid,
    expected_version,
    operation_id,
    at,
    *,
    record,
    emit,
):
    from django.db import transaction

    from .contracts import ProfileConflict, ProfileNotFound
    from .setup import receipt, remember, request_hash

    _context(actor, expected_version, operation_id, at, record, emit)
    with transaction.atomic():
        user, profile, roles, credentials = _owner_anchors(actor, at)
        case = _case(profile, verification_uuid)
        targets = _targets(case)
        target = next((t for t in targets if t.id == target_uuid), None)
        if target is None:
            raise ProfileNotFound("Verification unavailable")
        digest = request_hash(
            "verification.withdraw_target",
            {
                "case": case.id,
                "target": target.id,
                "expected_version": expected_version,
            },
        )
        if receipt(user, operation_id, "verification.withdraw_target", digest, case.id):
            return _owner_dto(case)
        if case.version != expected_version or target.state not in {
            "submitted",
            "under_review",
        }:
            raise ProfileConflict("Verification version conflict")
        prior = target.version
        target.state, target.version = "withdrawn", target.version + 1
        target.save(update_fields=["state", "version", "updated_at"])
        seq = (
            VerificationDecision.objects.filter(
                profile=profile, target_kind=target.target
            ).aggregate(value=Max("decision_sequence"))["value"]
            or 0
        ) + 1
        VerificationDecision.objects.create(
            target=target,
            profile=profile,
            target_kind=target.target,
            actor=user,
            decision="withdraw",
            reason_code="owner_withdrawn",
            target_snapshot_hash=target.target_snapshot_hash,
            bound_evidence_revision=target.bound_evidence_revision,
            decision_sequence=seq,
            decided_at=at,
            created_at=at,
            updated_at=at,
        )
        _history(case, user, "target_withdraw", "owner_withdrawn", prior, at, target)
        case.version += 1
        if all(
            t.state in {"approved", "rejected", "stale", "withdrawn"} for t in targets
        ):
            case.state = (
                "withdrawn"
                if all(t.state == "withdrawn" for t in targets)
                else "decided"
            )
            case.decided_at = at
        case.save(update_fields=["state", "version", "decided_at", "updated_at"])
        remember(
            user,
            operation_id,
            "verification.withdraw_target",
            digest,
            case.id,
            case.id,
            case.version,
            at,
        )
        record(
            SecurityOutcome(
                "verification.withdrawn",
                "succeeded",
                target.id,
                operation_id,
                ("state", "version"),
                "owner_withdrawn",
            )
        )
        emit(case)
        return _owner_dto(case)


def _staff_anchors(
    actor,
    verification_uuid,
    step_up_id,
    reason_code,
    at,
    *,
    assignee_uuid=None,
    assigned=True,
):
    from django.conf import settings
    from django.core.exceptions import PermissionDenied

    from apps.accounts.policies import require_account_action
    from apps.accounts.sessions import locked_actor
    from apps.assets.models import Asset
    from apps.governance.staff import require_staff

    from .contracts import ProfileNotFound
    from .models import Credential, VerificationAssignment
    from .policies import validate_context
    from .setup import locked_roles

    validate_context(actor, at)
    if settings.SETTINGS_ENV not in {"test", "development"}:
        raise PermissionDenied("Verification unavailable")
    if not isinstance(verification_uuid, UUID):
        raise ProfileNotFound("Verification unavailable")
    locator = (
        Verification.objects.filter(pk=verification_uuid)
        .values("profile_id", "profile__user_id")
        .first()
    )
    if locator is None:
        raise ProfileNotFound("Verification unavailable")
    participants = {locator["profile__user_id"]}
    identifiers = [actor.user_uuid]
    if assignee_uuid is not None:
        if not isinstance(assignee_uuid, UUID):
            raise ProfileNotFound("Verification unavailable")
        identifiers.append(assignee_uuid)
    participants.update(
        User.objects.filter(public_id__in=identifiers).values_list("pk", flat=True)
    )
    users = {
        u.pk: u
        for u in User.objects.select_for_update()
        .filter(pk__in=participants)
        .order_by("pk")
    }
    user = locked_actor(actor, "staff.command", at)
    owner = users[locator["profile__user_id"]]
    if owner.pk == user.pk:
        raise PermissionDenied("Staff authority denied")
    require_account_action(owner, "professional.verify_submit", "normal")
    profile = (
        ProfessionalProfile.objects.select_for_update()
        .filter(pk=locator["profile_id"], user=owner)
        .exclude(state="archived")
        .first()
    )
    if profile is None:
        raise ProfileNotFound("Verification unavailable")
    roles = locked_roles(profile)
    credentials = list(
        Credential.objects.select_for_update().filter(profile=profile).order_by("id")
    )
    case = _case(profile, verification_uuid)
    if case.state == "draft":
        raise ProfileNotFound("Verification unavailable")
    targets = _targets(case)
    assignments = list(
        VerificationAssignment.objects.select_for_update()
        .filter(verification=case, ended_at__isnull=True)
        .order_by("id")
    )
    from .models import ProfessionalRoleRestriction

    list(
        ProfessionalRoleRestriction.objects.select_for_update()
        .filter(role__in=roles)
        .order_by("id")
    )
    # Evidence and assets precede governance authority locks. Source rows are
    # locked for binding checks, but their bytes are never read here.
    from .models import VerificationEvidence

    evidence = list(
        VerificationEvidence.objects.select_for_update()
        .filter(target__in=targets)
        .order_by("id")
    )
    list(
        Asset.objects.select_for_update()
        .filter(credential_revisions__verification_evidence__in=evidence)
        .order_by("id")
    )
    require_staff(
        user, "professional_verification", case.id, step_up_id, reason_code, at
    )
    if assigned and (len(assignments) != 1 or assignments[0].assignee_id != user.pk):
        raise PermissionDenied("Staff authority denied")
    receiver = next((u for u in users.values() if u.public_id == assignee_uuid), None)
    return (
        user,
        owner,
        profile,
        roles,
        credentials,
        case,
        targets,
        assignments,
        receiver,
    )


def _staff_dto(case, targets, assignments, *, include_evidence=True):
    from .contracts import (
        VerificationEvidenceDTO,
        VerificationStaffDTO,
        VerificationTargetDTO,
    )
    from .models import VerificationEvidence

    evidence = (
        (
            VerificationEvidence.objects.filter(target__in=targets)
            .select_related("credential_revision")
            .order_by("target__target", "id")
        )
        if include_evidence
        else ()
    )
    return VerificationStaffDTO(
        case.id,
        case.state,
        case.version,
        case.submitted_at,
        tuple(
            VerificationTargetDTO(t.id, t.target, t.state, t.version)
            for t in sorted(targets, key=lambda row: row.target)
        ),
        next((t.identity_name for t in targets if t.target == "identity"), "")
        if include_evidence
        else "",
        tuple(
            VerificationEvidenceDTO(
                e.credential_revision_id,
                e.credential_revision.source_asset_id,
                e.category,
                e.credential_revision.type_code,
                e.credential_revision.issuer,
                e.credential_revision.title,
                e.credential_revision.issued_on,
                e.credential_revision.expires_on,
            )
            for e in evidence
        ),
        assignments[0].id if assignments else None,
    )


def assign_verification(
    actor,
    verification_uuid,
    assignee_uuid,
    expected_version,
    step_up_id,
    reason_code,
    at,
    *,
    record,
    emit,
):
    from django.core.exceptions import PermissionDenied
    from django.db import transaction

    from apps.accounts.policies import require_account_action
    from apps.governance.staff_models import StaffCapabilityGrant

    from .contracts import ProfileConflict
    from .models import VerificationAssignment

    _context(actor, expected_version, step_up_id, at, record, emit)
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
        ) = _staff_anchors(
            actor,
            verification_uuid,
            step_up_id,
            reason_code,
            at,
            assignee_uuid=assignee_uuid,
            assigned=False,
        )
        if receiver is None or receiver.pk == owner.pk:
            raise PermissionDenied("Staff authority denied")
        require_account_action(receiver, "staff.command", "normal")
        grant = (
            StaffCapabilityGrant.objects.select_for_update()
            .filter(
                user=receiver,
                capability="professional_verification",
                revoked_at__isnull=True,
                valid_from__lte=at,
                valid_until__gt=at,
            )
            .first()
        )
        if grant is None or grant.granted_by_id == receiver.pk:
            raise PermissionDenied("Staff authority denied")
        if case.version != expected_version:
            raise ProfileConflict("Verification version conflict")
        prior = case.version
        for old in assignments:
            old.ended_at, old.version = at, old.version + 1
            old.save(update_fields=["ended_at", "version", "updated_at"])
        assignment = VerificationAssignment.objects.create(
            verification=case,
            assignee=receiver,
            assigned_by=user,
            assigned_at=at,
            created_at=at,
        )
        case.version += 1
        case.save(update_fields=["version", "updated_at"])
        _history(
            case, user, "reassign" if assignments else "assign", reason_code, prior, at
        )
        record(
            SecurityOutcome(
                "verification.assigned",
                "succeeded",
                case.id,
                step_up_id,
                ("assigned_staff", "version"),
                reason_code,
            )
        )
        emit(case)
        return _staff_dto(
            case, targets, [assignment], include_evidence=receiver.pk == user.pk
        )


def start_verification_review(
    actor,
    verification_uuid,
    expected_version,
    step_up_id,
    reason_code,
    at,
    *,
    record,
    emit,
):
    from django.db import transaction

    from .contracts import ProfileConflict

    _context(actor, expected_version, step_up_id, at, record, emit)
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
        if case.version != expected_version or case.state != "submitted":
            raise ProfileConflict("Verification version conflict")
        prior = case.version
        for target in targets:
            if target.state == "submitted":
                target.state, target.version = "under_review", target.version + 1
                target.save(update_fields=["state", "version", "updated_at"])
        case.state, case.version = "under_review", case.version + 1
        case.save(update_fields=["state", "version", "updated_at"])
        _history(case, user, "start_review", reason_code, prior, at)
        record(
            SecurityOutcome(
                "verification.review_started",
                "succeeded",
                case.id,
                step_up_id,
                ("state", "version"),
                reason_code,
            )
        )
        emit(case)
        return _staff_dto(case, targets, assignments)


def effective_decision(profile, kind):
    return (
        VerificationDecision.objects.filter(
            profile=profile,
            target_kind=kind,
            decision__in=["approve", "reject", "revoke"],
        )
        .order_by("-decision_sequence")
        .first()
    )


def _terminal_command(
    actor,
    verification_uuid,
    target_uuid,
    value,
    expected_case_version,
    expected_target_version,
    expected_binding,
    step_up_id,
    reason_code,
    explanation,
    operation_id,
    at,
    *,
    record,
    emit,
    asset_validator,
    approval_uuid=None,
):
    from dataclasses import asdict

    from django.db import transaction

    from .contracts import ProfileConflict, ProfileNotFound
    from .setup import receipt, remember, request_hash
    from .verification_selectors import TargetReviewBinding, target_review_binding

    _context(actor, expected_case_version, operation_id, at, record, emit)
    if (
        type(expected_target_version) is not int
        or expected_target_version < 1
        or not isinstance(expected_binding, TargetReviewBinding)
        or value not in {"approve", "reject", "revoke"}
        or reason_code
        not in {
            "identity_verified",
            "credentials_approved",
            "evidence_incomplete",
            "credentials_invalid",
            "evidence_expired",
            "evidence_revoked",
        }
        or type(explanation) is not str
        or len(explanation) > 1000
        or any(ord(c) < 32 and c not in "\n\t" for c in explanation)
        or (value == "revoke" and not isinstance(approval_uuid, UUID))
    ):
        raise ValueError("Invalid verification decision")
    command = (
        "verification.revoke_target"
        if value == "revoke"
        else "verification.decide_target"
    )
    with transaction.atomic():
        user, owner, profile, roles, credentials, case, targets, assignments, _ = (
            _staff_anchors(actor, verification_uuid, step_up_id, reason_code, at)
        )
        target = next((t for t in targets if t.id == target_uuid), None)
        if target is None:
            raise ProfileNotFound("Verification unavailable")
        role = next((r for r in roles if r.id == target.role_id), None)
        digest = request_hash(
            command,
            {
                "case": case.id,
                "target": target.id,
                "decision": value,
                "case_version": expected_case_version,
                "target_version": expected_target_version,
                "binding": asdict(expected_binding),
                "reason": reason_code,
                "explanation": explanation,
                "approval": approval_uuid,
            },
        )
        if receipt(user, operation_id, command, digest, case.id):
            return _staff_dto(case, targets, assignments)
        binding = target_review_binding(profile, role, target)
        if (
            case.version != expected_case_version
            or target.version != expected_target_version
            or binding != expected_binding
        ):
            raise ProfileConflict("Verification version conflict")
        previous = effective_decision(profile, target.target)
        if value == "revoke":
            if (
                target.state != "approved"
                or previous is None
                or previous.decision != "approve"
                or previous.id != approval_uuid
                or previous.target_id != target.id
            ):
                raise ProfileConflict("Approval unavailable")
        else:
            if (
                case.state != "under_review"
                or target.state != "under_review"
                or target.bound_evidence_revision != binding.evidence_revision
                or target.bound_decision_version != binding.decision_version
                or target.bound_declaration_version != binding.declaration_version
                or (role is not None and not role.declared_active)
            ):
                raise ProfileConflict("Verification binding conflict")
            revisions = _current_revisions(credentials, target.target)
            if _hash_target(
                profile, role, revisions
            ) != target.target_snapshot_hash or set(
                target.evidence.values_list("credential_revision_id", flat=True)
            ) != {r.id for r in revisions}:
                raise ProfileConflict("Verification evidence conflict")
            try:
                _validate_revisions(owner, profile, revisions, at, asset_validator)
            except (ValueError, LookupError):
                raise ProfileConflict("Verification evidence unavailable") from None
        sequence = (
            VerificationDecision.objects.filter(
                profile=profile, target_kind=target.target
            ).aggregate(value=Max("decision_sequence"))["value"]
            or 0
        ) + 1
        VerificationDecision.objects.create(
            target=target,
            profile=profile,
            target_kind=target.target,
            actor=user,
            decision=value,
            reason_code=reason_code,
            explanation=explanation,
            target_snapshot_hash=target.target_snapshot_hash,
            bound_evidence_revision=target.bound_evidence_revision,
            decision_sequence=sequence,
            supersedes_decision=previous,
            revoked_approval=previous if value == "revoke" else None,
            decided_at=at,
            created_at=at,
            updated_at=at,
        )
        prior = target.version
        target.version += 1
        if value != "revoke":
            target.state = "approved" if value == "approve" else "rejected"
        target.save(update_fields=["state", "version", "updated_at"])
        if role is None:
            profile.identity_decision_version += 1
            profile.save(update_fields=["identity_decision_version", "updated_at"])
        else:
            role.decision_version += 1
            role.version += 1
            role.save(update_fields=["decision_version", "version", "updated_at"])
        _history(case, user, "decision", reason_code, prior, at, target)
        case.version += 1
        if case.state in {"submitted", "under_review"} and all(
            t.state in {"approved", "rejected", "stale", "withdrawn"} for t in targets
        ):
            case.state, case.decided_at = "decided", at
        case.save(update_fields=["state", "version", "decided_at", "updated_at"])
        # A historical approval can be revoked while a new review is pending.
        # Close only older pending targets for this kind, preserving all others.
        _stale_pending(profile, target.target, user, operation_id, at, record, emit)
        remember(
            user, operation_id, command, digest, case.id, target.id, case.version, at
        )
        record(
            SecurityOutcome(
                {
                    "approve": "verification.approved",
                    "reject": "verification.rejected",
                    "revoke": "verification.revoked",
                }[value],
                "succeeded",
                target.id,
                operation_id,
                ("state", "version", "decision_version"),
                reason_code,
            )
        )
        emit(case)
        return _staff_dto(case, targets, assignments)


def decide_verification_target(*args, record, emit, asset_validator):
    return _terminal_command(
        *args, record=record, emit=emit, asset_validator=asset_validator
    )


def revoke_verification_target(
    actor,
    verification_uuid,
    target_uuid,
    effective_approval_uuid,
    expected_case_version,
    expected_target_version,
    expected_binding,
    step_up_id,
    reason_code,
    explanation,
    operation_id,
    at,
    *,
    record,
    emit,
    asset_validator,
):
    return _terminal_command(
        actor,
        verification_uuid,
        target_uuid,
        "revoke",
        expected_case_version,
        expected_target_version,
        expected_binding,
        step_up_id,
        reason_code,
        explanation,
        operation_id,
        at,
        record=record,
        emit=emit,
        asset_validator=asset_validator,
        approval_uuid=effective_approval_uuid,
    )
