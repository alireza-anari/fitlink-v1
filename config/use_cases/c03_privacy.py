"""Server-only bridge for one self-storage subject; no registry or sharing API."""

from datetime import datetime, timedelta
from uuid import UUID, uuid4

from django.conf import settings
from django.db import DatabaseError, transaction

from apps.accounts.models import User
from apps.accounts.sessions import AccountActor, locked_actor
from apps.athletes import baseline
from apps.athletes.baseline_models import BaselineAssessment
from apps.athletes.consent import (
    DISCLOSURE_HASH,
    DISCLOSURE_SCHEMA,
    DISCLOSURE_VERSION,
    STORAGE_KIND,
    STORAGE_PURPOSE,
)
from apps.athletes.contracts import ProfileConflict
from apps.governance import consents
from apps.governance.consent_models import Consent
from config.use_cases import consent as consent_commands


def validate_baseline_scope(
    scope: consents.ValidatedConsentScope, subject: User
) -> bool:
    if (
        scope.kind != STORAGE_KIND
        or scope.purpose != STORAGE_PURPOSE
        or scope.grantee_uuid != subject.public_id
        or scope.subject_uuid != subject.public_id
        or scope.object_version != DISCLOSURE_SCHEMA
    ):
        return False
    try:
        with transaction.atomic():
            profile = baseline.locked_profile(subject)
            row = baseline.locked_baseline(profile, scope.object_uuid)
            return row.schema_version == DISCLOSURE_SCHEMA
    except (DatabaseError, LookupError):
        return False


def scope_for(
    user: User, row: BaselineAssessment, expires_at: datetime
) -> consents.ValidatedConsentScope:
    return consents.ValidatedConsentScope(
        user.public_id,
        user.public_id,
        STORAGE_PURPOSE,
        STORAGE_KIND,
        row.id,
        DISCLOSURE_SCHEMA,
        expires_at,
    )


def baseline_storage_current(user: User, row: BaselineAssessment, at: datetime) -> bool:
    # Scope's expiry is a query predicate only; the grant's own expiry is authority.
    current = consents.has_current_grant(
        user.public_id,
        user.public_id,
        STORAGE_PURPOSE,
        scope_for(user, row, at + timedelta(microseconds=1)),
        at,
        scope_validator=validate_baseline_scope,
    )
    return current and bool(
        list(
            Consent.objects.select_for_update(of=("self",))
            .filter(
                subject=user,
                grantee=user,
                purpose=STORAGE_PURPOSE,
                text_version=DISCLOSURE_VERSION,
                content_hash=DISCLOSURE_HASH,
                granted_at__lte=at,
                expires_at__gt=at,
                revoked_at__isnull=True,
                scopes__kind=STORAGE_KIND,
                scopes__object_uuid=row.id,
                scopes__object_version=DISCLOSURE_SCHEMA,
            )
            .order_by("id")
            .values_list("id", flat=True)
        )
    )


def grant_baseline_storage(
    actor: AccountActor,
    baseline_uuid: UUID,
    expected_version: int,
    confirmed: bool = False,
    operation_id: UUID | None = None,
    at: datetime | None = None,
) -> UUID:
    if at is None or operation_id is None:
        raise ValueError("Invalid baseline consent command")
    baseline.context(actor, expected_version, operation_id, at)
    with transaction.atomic():
        user = locked_actor(actor, "athlete.baseline_write", at)
        profile = baseline.locked_profile(user)
        row = baseline.locked_baseline(profile, baseline_uuid)
        if confirmed is not True:
            raise PermissionError(
                "Explicit baseline self-storage confirmation required"
            )
        digest = baseline.request_hash(
            "baseline.grant_storage",
            {
                "baseline_uuid": row.id,
                "expected_version": expected_version,
                "confirmed": True,
                "disclosure": DISCLOSURE_HASH,
            },
        )
        old = baseline.receipt(
            user, operation_id, "baseline.grant_storage", digest, row.id
        )
        if old:
            if old.result_uuid is None:
                raise PermissionError("Consent receipt unavailable")
            consent = (
                Consent.objects.select_for_update()
                .filter(
                    pk=old.result_uuid,
                    subject=user,
                    grantee=user,
                    purpose=STORAGE_PURPOSE,
                    text_version=DISCLOSURE_VERSION,
                    content_hash=DISCLOSURE_HASH,
                    granted_at__lte=at,
                    expires_at__gt=at,
                    revoked_at__isnull=True,
                    scopes__kind=STORAGE_KIND,
                    scopes__object_uuid=row.id,
                    scopes__object_version=DISCLOSURE_SCHEMA,
                )
                .first()
            )
            if consent is None or not baseline_storage_current(user, row, at):
                raise PermissionError("Consent receipt is no longer current")
            return consent.id
        if row.version != expected_version or row.state != "draft":
            raise ProfileConflict("Consent requires the current owned draft")
        duration = getattr(settings, "BASELINE_STORAGE_CONSENT_SECONDS", None)
        if type(duration) is not int or not 1 <= duration <= 31536000:
            raise ValueError("Baseline storage duration is not configured")
        scope = consents.validate_scope(
            actor,
            user.public_id,
            STORAGE_PURPOSE,
            STORAGE_KIND,
            row.id,
            DISCLOSURE_SCHEMA,
            at + timedelta(seconds=duration),
            at,
            scope_validator=validate_baseline_scope,
        )
        identifier = consent_commands.grant_consent(
            actor,
            scope,
            DISCLOSURE_VERSION,
            DISCLOSURE_HASH,
            at,
            scope_validator=validate_baseline_scope,
        )
        baseline.remember(
            user,
            operation_id,
            "baseline.grant_storage",
            digest,
            row.id,
            row,
            at,
            identifier,
        )
        return identifier


def revoke_baseline_storage(
    actor: AccountActor,
    baseline_uuid: UUID,
    consent_uuid: UUID,
    expected_consent_version: int,
    operation_id: UUID,
    at: datetime,
) -> None:
    baseline.context(actor, expected_consent_version, operation_id, at)
    if not isinstance(consent_uuid, UUID):
        raise ValueError("Invalid consent UUID")
    with transaction.atomic():
        user = locked_actor(actor, "athlete.baseline_write", at)
        profile = baseline.locked_profile(user)
        row = baseline.locked_baseline(profile, baseline_uuid)
        target = (
            Consent.objects.select_for_update()
            .filter(
                pk=consent_uuid,
                subject=user,
                grantee=user,
                purpose=STORAGE_PURPOSE,
                scopes__kind=STORAGE_KIND,
                scopes__object_uuid=row.id,
                scopes__object_version=DISCLOSURE_SCHEMA,
            )
            .first()
        )
        if target is None:
            raise PermissionError("Consent action denied")
        digest = baseline.request_hash(
            "baseline.revoke_storage",
            {
                "baseline_uuid": row.id,
                "consent_uuid": consent_uuid,
                "expected_version": expected_consent_version,
            },
        )
        old = baseline.receipt(
            user, operation_id, "baseline.revoke_storage", digest, row.id
        )
        if old:
            if old.result_uuid != target.id or target.revoked_at is None:
                raise PermissionError("Consent receipt unavailable")
            return
        consent_commands.revoke_consent(actor, target.id, expected_consent_version, at)
        baseline.remember(
            user,
            operation_id,
            "baseline.revoke_storage",
            digest,
            row.id,
            row,
            at,
            target.id,
        )


# Task 9: a closed, server-only composition of installed C03 lifetime subjects.
from contextvars import ContextVar  # noqa: E402
from functools import partial  # noqa: E402

from django.core.exceptions import PermissionDenied  # noqa: E402
from django.utils import timezone  # noqa: E402

from apps.assets import cleanup as asset_cleanup  # noqa: E402
from apps.assets.models import (  # noqa: E402
    Asset,
    AssetDerivative,
    AssetProcessingAttempt,
)
from apps.assets.privacy import (  # noqa: E402
    MAX_INVENTORY,
    OwnerInventory,
    bounded_rows,
    enumerate_asset_inventory,
)
from apps.athletes.models import AthleteProfile  # noqa: E402
from apps.athletes.privacy import enumerate_athlete_inventory  # noqa: E402
from apps.governance import retention  # noqa: E402
from apps.governance.privacy_models import PrivacyRequest, RecordHold  # noqa: E402
from apps.professionals.models import (  # noqa: E402
    Credential,
    CredentialRevision,
    ProfessionalProfile,
    ProfessionalRole,
    Verification,
    VerificationAssignment,
    VerificationEvidence,
    VerificationTarget,
)
from apps.professionals.privacy import (  # noqa: E402
    case_asset_inventory,
    enumerate_professional_inventory,
)

_hold_owner_context: ContextVar[UUID | None] = ContextVar(
    "c03_hold_owner", default=None
)

HOLD_KINDS = frozenset(
    {
        "athlete_baseline",
        "professional_credential",
        "professional_verification",
        "profile_asset",
    }
)


def _valid_reference(subject):
    return (
        isinstance(subject, retention.ValidatedRecordSubject)
        and isinstance(subject.kind, str)
        and subject.kind in HOLD_KINDS
        and isinstance(subject.record_uuid, UUID)
        and isinstance(subject.owner_uuid, UUID)
        and type(subject.version) is int
        and subject.version > 0
    )


def _subject_row(subject):
    if subject.kind == "athlete_baseline":
        return BaselineAssessment.objects.filter(
            pk=subject.record_uuid, athlete__user__public_id=subject.owner_uuid
        ).first()
    if subject.kind == "professional_credential":
        return Credential.objects.filter(
            pk=subject.record_uuid, profile__user__public_id=subject.owner_uuid
        ).first()
    if subject.kind == "professional_verification":
        return Verification.objects.filter(
            pk=subject.record_uuid, profile__user__public_id=subject.owner_uuid
        ).first()
    if subject.kind == "profile_asset":
        return Asset.objects.filter(
            pk=subject.record_uuid, owner__public_id=subject.owner_uuid
        ).first()
    return None


def _asset_binding_valid(asset):
    if asset.classification != "private_source":
        return False
    if asset.subject_kind == "professional_profile":
        return ProfessionalProfile.objects.filter(
            pk=asset.subject_uuid, user_id=asset.owner_id
        ).exists()
    if asset.subject_kind == "professional_credential":
        return Credential.objects.filter(
            pk=asset.subject_uuid, profile__user_id=asset.owner_id
        ).exists()
    return False


def validate_c03_hold_subject(subject):
    if not _valid_reference(subject):
        return False
    row = _subject_row(subject)
    if isinstance(row, Credential):
        if (
            row.role_id is not None
            and row.role.profile_id != row.profile_id
            or row.current_revision_id is not None
            and row.current_revision.credential_id != row.id
        ):
            return False
    if isinstance(row, BaselineAssessment) and row.parent_id is not None:
        if row.parent.athlete_id != row.athlete_id:
            return False
    return bool(
        row
        and row.version == subject.version
        and (not isinstance(row, Asset) or _asset_binding_valid(row))
    )


def _case_assets(case_uuid, owner_uuid, credential_uuid=None):
    return case_asset_inventory(case_uuid, owner_uuid, credential_uuid)


def _subject_assets(subject, case_uuid):
    if subject.kind == "profile_asset":
        return (subject.record_uuid,)
    if subject.kind == "professional_verification":
        return _case_assets(subject.record_uuid, subject.owner_uuid)
    if subject.kind == "professional_credential":
        return _case_assets(case_uuid, subject.owner_uuid, subject.record_uuid)
    return ()


def validate_c03_hold_case(subject, case_uuid, acting_user, *, at=None):
    at = at or timezone.now()
    if _hold_owner_context.get() != getattr(subject, "owner_uuid", None):
        return False
    if (
        not validate_c03_hold_subject(subject)
        or not isinstance(case_uuid, UUID)
        or acting_user.public_id == subject.owner_uuid
        or not acting_user.is_active
        or acting_user.state != "active"
    ):
        return False
    intake = PrivacyRequest.objects.filter(
        pk=case_uuid, user__public_id=subject.owner_uuid, created_at__lte=at
    ).exists()
    if intake:
        # A credential hold must pin submitted case evidence, never later uploads.
        if subject.kind not in {"profile_asset", "athlete_baseline"}:
            return False
    else:
        case = Verification.objects.filter(
            pk=case_uuid,
            profile__user__public_id=subject.owner_uuid,
            submitted_at__isnull=False,
            submitted_at__lte=at,
        ).first()
        if (
            not case
            or not VerificationAssignment.objects.filter(
                verification=case,
                assignee=acting_user,
                ended_at__isnull=True,
                assigned_at__lte=at,
            ).exists()
        ):
            return False
        from apps.governance.staff_models import StaffCapabilityGrant

        if (
            not StaffCapabilityGrant.objects.filter(
                user=acting_user,
                capability="professional_verification",
                revoked_at__isnull=True,
                valid_from__lte=at,
                valid_until__gt=at,
            )
            .exclude(granted_by=acting_user)
            .exists()
        ):
            return False
        if (
            subject.kind == "professional_verification"
            and subject.record_uuid != case_uuid
        ):
            return False
        if subject.kind == "athlete_baseline":
            return False
        case_assets = _case_assets(
            case_uuid,
            subject.owner_uuid,
            subject.record_uuid if subject.kind == "professional_credential" else None,
        )
        if (
            subject.kind == "professional_credential"
            and not case_assets
            or subject.kind == "profile_asset"
            and subject.record_uuid not in case_assets
        ):
            return False
    asset_ids = _subject_assets(subject, case_uuid)
    return (
        not Asset.objects.filter(pk__in=asset_ids)
        .filter(state__in=["deletion_pending", "deleted"])
        .exists()
    )


def _lock_owner_records(owner):
    """Identity is already locked; take installed domain anchors before assets."""
    for query in (
        AthleteProfile.objects.filter(user=owner),
        BaselineAssessment.objects.filter(athlete__user=owner),
        ProfessionalProfile.objects.filter(user=owner),
        ProfessionalRole.objects.filter(profile__user=owner),
        Credential.objects.filter(profile__user=owner),
        CredentialRevision.objects.filter(credential__profile__user=owner),
        Verification.objects.filter(profile__user=owner),
        VerificationTarget.objects.filter(verification__profile__user=owner),
        VerificationAssignment.objects.filter(verification__profile__user=owner),
        VerificationEvidence.objects.filter(target__verification__profile__user=owner),
        Asset.objects.filter(owner=owner),
        AssetProcessingAttempt.objects.filter(asset__owner=owner),
        AssetDerivative.objects.filter(asset__owner=owner),
    ):
        bounded_rows(query.select_for_update())


def _lock_subject_anchors(owner, subject, case_uuid=None):
    # A lifetime command for one record must not lock all accumulated history.
    bounded_rows(AthleteProfile.objects.filter(user=owner).select_for_update())
    bounded_rows(ProfessionalProfile.objects.filter(user=owner).select_for_update())
    if subject.kind == "athlete_baseline":
        bounded_rows(
            BaselineAssessment.objects.filter(
                pk=subject.record_uuid, athlete__user=owner
            ).select_for_update()
        )
    if subject.kind == "professional_verification":
        case_uuid = subject.record_uuid
    credential_ids = (
        {subject.record_uuid} if subject.kind == "professional_credential" else set()
    )
    if subject.kind == "profile_asset":
        binding = Asset.objects.filter(
            pk=subject.record_uuid, owner=owner, subject_kind="professional_credential"
        ).first()
        if binding is not None:
            credential_ids.add(binding.subject_uuid)
    if case_uuid is not None:
        for evidence in bounded_rows(
            VerificationEvidence.objects.filter(
                target__verification_id=case_uuid,
                target__verification__profile__user=owner,
            )
        ):
            credential_ids.add(evidence.credential_revision.credential_id)
    roles = Credential.objects.filter(
        pk__in=credential_ids, profile__user=owner
    ).values_list("role_id", flat=True)
    bounded_rows(ProfessionalRole.objects.filter(pk__in=roles).select_for_update())
    bounded_rows(
        Credential.objects.filter(
            pk__in=credential_ids, profile__user=owner
        ).select_for_update()
    )
    if case_uuid is not None:
        bounded_rows(
            Verification.objects.filter(
                pk=case_uuid, profile__user=owner
            ).select_for_update()
        )
        bounded_rows(
            VerificationTarget.objects.filter(
                verification_id=case_uuid, verification__profile__user=owner
            ).select_for_update()
        )
        bounded_rows(
            VerificationAssignment.objects.filter(
                verification_id=case_uuid, verification__profile__user=owner
            ).select_for_update()
        )
        bounded_rows(
            VerificationEvidence.objects.filter(
                target__verification_id=case_uuid,
                target__verification__profile__user=owner,
            ).select_for_update()
        )
    asset_ids = _subject_assets(subject, case_uuid)
    bounded_rows(
        Asset.objects.filter(pk__in=asset_ids, owner=owner).select_for_update()
    )


def inventory_c03_owner(owner_uuid, at):
    retention._time(at)
    if not isinstance(owner_uuid, UUID):
        raise PermissionError("Inventory owner denied")
    with transaction.atomic():
        owner = User.objects.select_for_update().filter(public_id=owner_uuid).first()
        if owner is None:
            raise PermissionError("Inventory owner denied")
        _lock_owner_records(owner)
        for asset in bounded_rows(Asset.objects.filter(owner=owner)):
            if not _asset_binding_valid(asset):
                raise PermissionError("Inventory subject denied")
        records = (
            enumerate_athlete_inventory(owner_uuid)
            + enumerate_professional_inventory(owner_uuid)
            + enumerate_asset_inventory(owner_uuid, at)
        )
        if len(records) > MAX_INVENTORY:
            raise PermissionError("Inventory bound exceeded")
        return OwnerInventory(owner_uuid, records)


def apply_c03_hold(
    actor,
    subject,
    case_uuid,
    purpose,
    reason_code,
    review_at,
    expires_at,
    step_up_id,
    at,
):
    if not _valid_reference(subject):
        raise PermissionDenied("Hold subject denied")
    with transaction.atomic():
        participants = list(
            User.objects.select_for_update()
            .filter(public_id__in=[subject.owner_uuid, actor.user_uuid])
            .order_by("pk")
        )
        owner = next(
            (u for u in participants if u.public_id == subject.owner_uuid), None
        )
        if owner is None or not any(
            u.public_id == actor.user_uuid for u in participants
        ):
            raise PermissionDenied("Hold subject denied")
        _lock_subject_anchors(owner, subject, case_uuid)
        token = _hold_owner_context.set(owner.public_id)
        try:
            return retention.apply_hold(
                actor,
                subject,
                case_uuid,
                purpose,
                reason_code,
                review_at,
                expires_at,
                step_up_id,
                at,
                subject_validator=validate_c03_hold_subject,
                case_validator=partial(validate_c03_hold_case, at=at),
            )
        finally:
            _hold_owner_context.reset(token)


def release_c03_hold(actor, hold_uuid, expected_version, reason_code, step_up_id, at):
    with transaction.atomic():
        candidate = RecordHold.objects.filter(pk=hold_uuid).first()
        if candidate is None or candidate.subject_kind not in HOLD_KINDS:
            raise PermissionDenied("Hold action denied")
        participants = list(
            User.objects.select_for_update()
            .filter(public_id__in=[candidate.owner_uuid, actor.user_uuid])
            .order_by("pk")
        )
        owner = next(
            (u for u in participants if u.public_id == candidate.owner_uuid), None
        )
        if owner is None or actor.user_uuid == owner.public_id:
            raise PermissionDenied("Hold action denied")
        _lock_subject_anchors(
            owner,
            retention.ValidatedRecordSubject(
                candidate.subject_kind,
                candidate.subject_uuid,
                candidate.owner_uuid,
                candidate.subject_version,
            ),
            candidate.case_uuid,
        )

        def validate_stored(subject):
            row = _subject_row(subject) if _valid_reference(subject) else None
            # The stored hold is authoritative for its original version. Revocation
            # can advance the retained record without preventing authorized release.
            return bool(row and row.version >= subject.version)

        return retention.release_hold(
            actor,
            hold_uuid,
            expected_version,
            reason_code,
            step_up_id,
            at,
            subject_validator=validate_stored,
        )


def _asset_held(asset, at):
    for hold in bounded_rows(
        RecordHold.objects.filter(
            owner_uuid=asset.owner.public_id,
            released_at__isnull=True,
            created_at__lte=at,
            expires_at__gt=at,
        )
    ):
        subject = retention.ValidatedRecordSubject(
            hold.subject_kind, hold.subject_uuid, hold.owner_uuid, hold.subject_version
        )
        if hold.subject_kind in HOLD_KINDS and asset.id in _subject_assets(
            subject, hold.case_uuid
        ):
            # Never reinterpret a pre-revocation version as an absent hold.
            return True
    return False


def _asset_in_use(asset):
    profile = ProfessionalProfile.objects.filter(user_id=asset.owner_id).first()
    return bool(
        profile
        and asset.id in {profile.avatar_id, profile.cover_id, profile.logo_id}
        and asset.owner.state == "active"
        and asset.owner.is_active
    )


def _cleanup_subject(asset):
    if not _asset_binding_valid(asset):
        return False
    subject = retention.ValidatedRecordSubject(
        "profile_asset", asset.id, asset.owner.public_id, asset.version
    )
    _lock_subject_anchors(asset.owner, subject)
    return _asset_binding_valid(asset)


def cleanup_asset(asset_uuid, expected_version, policy_uuid, at, *, store=None):
    return asset_cleanup.cleanup_asset(
        asset_uuid,
        expected_version,
        policy_uuid,
        at,
        subject_validator=_cleanup_subject,
        hold_validator=_asset_held,
        in_use_validator=_asset_in_use,
        store=store,
    )


def revoke_owner_lifetime(owner, at, *, asset_ids=None):
    """Current-state metadata only. Retention never re-enables a read or a job."""
    from django.db.models import F

    from apps.accounts.contracts import SecurityOutcome
    from apps.governance.audit import append_event
    from apps.governance.outbox import append_outbox
    from apps.professionals.models import AssistantMembership

    if not transaction.get_connection().in_atomic_block:
        raise RuntimeError("Lifetime effects require the domain transaction")
    if owner.is_active and owner.state == "active":
        return
    bounded_rows(ProfessionalProfile.objects.filter(user=owner).select_for_update())
    query = Asset.objects.select_for_update().filter(owner=owner)
    if asset_ids is not None:
        query = query.filter(pk__in=asset_ids)
    assets = list(
        query.filter(owner=owner)
        .exclude(state__in=["revoked", "abandoned", "deletion_pending", "deleted"])
        .order_by("pk")[:100]
    )
    for asset in assets:
        asset.state = "abandoned" if asset.accepted_at is None else "revoked"
        asset.revoked_at = at
        asset.version += 1
        asset.save(update_fields=["state", "revoked_at", "version", "updated_at"])
    AssetProcessingAttempt.objects.filter(
        asset_id__in=[a.id for a in assets], state__in=["pending", "running"]
    ).update(
        state="failed",
        lease_uuid=None,
        lease_until=None,
        failure_code="owner_unavailable",
        updated_at=at,
    )
    AssetDerivative.objects.filter(
        asset_id__in=[a.id for a in assets], state__in=["pending", "ready"]
    ).update(state="revoked", version=F("version") + 1, updated_at=at)
    AssistantMembership.objects.filter(profile__user=owner).exclude(
        state="revoked"
    ).update(state="revoked", revoked_at=at, version=F("version") + 1, updated_at=at)

    for asset in assets:
        append_event(
            SecurityOutcome(
                "asset.revoked",
                "succeeded",
                asset.id,
                uuid4(),
                ("state", "version", "revoked_at"),
                "security_restriction",
            ),
            subject_type="asset",
        )
        append_outbox(
            "asset.cleanup_requested",
            asset.id,
            asset.version,
            {"asset_uuid": str(asset.id), "user_uuid": str(owner.public_id)},
            f"asset.cleanup_requested:{asset.id}:{asset.version}",
        )


def apply_c03_consent_effect(consent, at):
    """Only installed self-baseline consent; no invented media consent scope."""
    if consent.purpose != STORAGE_PURPOSE or consent.grantee_id != consent.subject_id:
        return
    for row in bounded_rows(consent.scopes.filter(kind=STORAGE_KIND)):
        scope = consents.ValidatedConsentScope(
            consent.subject.public_id,
            consent.grantee.public_id,
            consent.purpose,
            row.kind,
            row.object_uuid,
            row.object_version,
            consent.expires_at,
        )
        if not validate_baseline_scope(scope, consent.subject):
            raise PermissionDenied("Consent lifetime subject denied")


def is_c03_record_held(subject, at):
    return retention.is_record_held(
        subject, at, subject_validator=validate_c03_hold_subject
    )


def reconcile_asset_lifetime(asset_uuid, at):
    from django.db.models import F

    from apps.accounts.contracts import SecurityOutcome
    from apps.governance.audit import append_event
    from apps.governance.outbox import append_outbox

    locator = Asset.objects.filter(pk=asset_uuid).values("owner_id").first()
    if locator is None:
        return
    with transaction.atomic():
        owner = User.objects.select_for_update().get(pk=locator["owner_id"])
        if not owner.is_active or owner.state != "active":
            revoke_owner_lifetime(owner, at, asset_ids=[asset_uuid])
        candidate = Asset.objects.get(pk=asset_uuid)
        candidate.owner = owner
        if not _cleanup_subject(candidate):
            return
        row = Asset.objects.select_for_update().get(pk=asset_uuid)
        if row.state in {"pending_upload", "receiving"} and row.upload_expires_at <= at:
            row.state, row.revoked_at, row.version = "abandoned", at, row.version + 1
            row.save(update_fields=["state", "revoked_at", "version", "updated_at"])
            AssetProcessingAttempt.objects.filter(
                asset=row, state__in=["pending", "running"]
            ).update(
                state="failed",
                lease_uuid=None,
                lease_until=None,
                failure_code="retention_due",
                updated_at=at,
            )
            AssetDerivative.objects.filter(
                asset=row, state__in=["pending", "ready"]
            ).update(state="revoked", version=F("version") + 1, updated_at=at)
            append_event(
                SecurityOutcome(
                    "asset.revoked",
                    "succeeded",
                    row.id,
                    uuid4(),
                    ("state", "version", "revoked_at"),
                    "retention_due",
                ),
                subject_type="asset",
            )
            append_outbox(
                "asset.cleanup_requested",
                row.id,
                row.version,
                {"asset_uuid": str(row.id), "user_uuid": str(owner.public_id)},
                f"asset.cleanup_requested:{row.id}:{row.version}",
            )
