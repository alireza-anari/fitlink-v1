"""Consent is only an additional predicate; it never authorizes object access."""

import re
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from uuid import UUID, uuid4

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from apps.accounts.contracts import OutcomeRecorder, SecurityOutcome
from apps.accounts.models import User
from apps.accounts.sessions import AccountActor, actor_user, locked_actor

from .consent_models import PURPOSES, Consent, ConsentScope


@dataclass(frozen=True)
class ValidatedConsentScope:
    subject_uuid: UUID
    grantee_uuid: UUID
    purpose: str
    kind: str
    object_uuid: UUID
    object_version: int
    expires_at: datetime


def _account_metadata(scope: ValidatedConsentScope, subject: User) -> bool:
    return (
        scope.purpose == "account_metadata"
        and scope.object_uuid == subject.public_id
        and scope.object_version == subject.state_version
    )


# Only this already-installed, nonsensitive, account-owned subject is supported.
# Future domains must supply reviewed server validators; unknown kinds deny.
SCOPE_VALIDATORS = MappingProxyType({"account_metadata": _account_metadata})


def _valid_scope(scope: ValidatedConsentScope, subject: User, at: datetime) -> bool:
    if not isinstance(scope, ValidatedConsentScope):
        return False
    validator = SCOPE_VALIDATORS.get(scope.kind)
    return bool(
        validator
        and scope.subject_uuid == subject.public_id
        and isinstance(scope.grantee_uuid, UUID)
        and isinstance(scope.object_uuid, UUID)
        and type(scope.object_version) is int
        and scope.object_version >= 1
        and scope.purpose in PURPOSES
        and isinstance(scope.expires_at, datetime)
        and timezone.is_aware(scope.expires_at)
        and scope.expires_at > at
        and validator(scope, subject)
    )


def validate_scope(
    actor: AccountActor,
    grantee_uuid: UUID,
    purpose: str,
    kind: str,
    object_uuid: UUID,
    object_version: int,
    expires_at: datetime,
    at: datetime,
) -> ValidatedConsentScope:
    subject = actor_user(actor, "consent.grant", at)
    scope = ValidatedConsentScope(
        subject.public_id,
        grantee_uuid,
        purpose,
        kind,
        object_uuid,
        object_version,
        expires_at,
    )
    if not _valid_scope(scope, subject, at):
        raise PermissionError("Consent scope denied")
    return scope


def grant_consent(
    actor: AccountActor,
    scope: ValidatedConsentScope,
    text_version: str,
    content_hash: str,
    at: datetime,
    record: OutcomeRecorder,
) -> UUID:
    if (
        not callable(record)
        or not isinstance(text_version, str)
        or re.fullmatch(r"[a-zA-Z0-9_.:-]{1,64}", text_version) is None
        or not isinstance(content_hash, str)
        or re.fullmatch(r"[0-9a-f]{64}", content_hash) is None
    ):
        raise ValueError("Invalid consent contract")
    with transaction.atomic():
        if not isinstance(scope, ValidatedConsentScope):
            raise PermissionError("Consent scope denied")
        participants = list(
            User.objects.select_for_update()
            .filter(public_id__in=[actor.user_uuid, scope.grantee_uuid])
            .order_by("id")
        )
        subject = locked_actor(actor, "consent.grant", at)
        if not _valid_scope(scope, subject, at):
            raise PermissionError("Consent scope denied")
        grantee = next(
            (
                user
                for user in participants
                if user.public_id == scope.grantee_uuid
                and user.state == "active"
                and user.is_active
            ),
            None,
        )
        if not grantee:
            raise PermissionError("Consent scope denied")
        consent = Consent.objects.create(
            subject=subject,
            grantee=grantee,
            purpose=scope.purpose,
            text_version=text_version,
            content_hash=content_hash,
            granted_at=at,
            expires_at=scope.expires_at,
        )
        ConsentScope.objects.create(
            consent=consent,
            kind=scope.kind,
            object_uuid=scope.object_uuid,
            object_version=scope.object_version,
        )
        record(
            SecurityOutcome(
                "consent.granted",
                "succeeded",
                consent.id,
                uuid4(),
                reason_code="user_requested",
            )
        )
        return consent.id


def revoke_consent(
    actor: AccountActor,
    consent_uuid: UUID,
    expected_version: int,
    at: datetime,
    record: OutcomeRecorder,
) -> None:
    if (
        not callable(record)
        or type(expected_version) is not int
        or expected_version < 1
    ):
        raise ValueError("Invalid consent contract")
    with transaction.atomic():
        subject = locked_actor(actor, "consent.revoke", at)
        consent = (
            Consent.objects.select_for_update()
            .filter(
                id=consent_uuid,
                subject=subject,
                version=expected_version,
                revoked_at__isnull=True,
            )
            .first()
        )
        if not consent or at < consent.granted_at:
            raise PermissionError("Consent action denied")
        consent.revoked_at = at
        consent.version += 1
        consent.save(update_fields=["revoked_at", "version"])
        record(
            SecurityOutcome(
                "consent.revoked",
                "succeeded",
                consent.id,
                uuid4(),
                ("revoked_at", "version"),
                "user_requested",
            )
        )


def visible_consents(actor: AccountActor, at: datetime) -> QuerySet[Consent]:
    subject = actor_user(actor, "consent.status", at)
    return Consent.objects.filter(subject=subject)


def has_current_grant(
    subject_uuid: UUID,
    grantee_uuid: UUID,
    purpose: str,
    scope: ValidatedConsentScope,
    at: datetime,
) -> bool:
    subject = User.objects.filter(
        public_id=subject_uuid, state="active", is_active=True
    ).first()
    if not subject or not _valid_scope(scope, subject, at):
        return False
    if scope.grantee_uuid != grantee_uuid or scope.purpose != purpose:
        return False
    # No object permission is inferred here; the caller must check its own policy.
    return Consent.objects.filter(
        subject=subject,
        grantee__public_id=grantee_uuid,
        grantee__state="active",
        grantee__is_active=True,
        purpose=purpose,
        revoked_at__isnull=True,
        granted_at__lte=at,
        expires_at__gt=at,
        scopes__kind=scope.kind,
        scopes__object_uuid=scope.object_uuid,
        scopes__object_version=scope.object_version,
    ).exists()
