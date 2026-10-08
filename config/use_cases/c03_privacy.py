"""Server-only bridge for one self-storage subject; no registry or sharing API."""

from datetime import datetime, timedelta
from uuid import UUID

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
