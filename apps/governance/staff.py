import secrets
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction

from apps.accounts.models import User

from .audit_models import REASONS
from .staff_models import CAPABILITIES, StaffCapabilityGrant, StaffStepUpGrant


@dataclass(frozen=True)
class MockAssertion:
    raw_assertion: str = field(repr=False)


@dataclass(frozen=True)
class VerifiedStepUp:
    user_uuid: UUID
    capability: str
    case_uuid: UUID | None
    provider_reference: UUID
    verified_at: datetime
    expires_at: datetime


class MockStepUpProvider:
    """Private memory-only test adapter; never a web assertion-reading route."""

    def __init__(self):
        if settings.SETTINGS_ENV not in {"test", "development"}:
            raise ValueError("Step-up adapter unavailable")
        self._pending: dict[str, VerifiedStepUp] = {}
        self._lock = threading.Lock()

    def prepare(self, user_uuid, capability, case_uuid, at) -> MockAssertion:
        if settings.SETTINGS_ENV not in {"test", "development"}:
            raise ValueError("Step-up adapter unavailable")
        if capability not in CAPABILITIES:
            raise ValueError("Step-up adapter unavailable")
        raw = secrets.token_urlsafe(48)
        with self._lock:
            self._pending = {
                key: value
                for key, value in self._pending.items()
                if value.expires_at > at
            }
            if len(self._pending) >= 1000:
                raise ValueError("Step-up adapter unavailable")
            self._pending[raw] = VerifiedStepUp(
                user_uuid,
                capability,
                case_uuid,
                uuid4(),
                at,
                at
                + timedelta(
                    seconds=settings.ACCOUNT_SECURITY.policy.recent_auth_seconds
                ),
            )
        return MockAssertion(raw)

    def verify(self, user_uuid, capability, case_uuid, raw_assertion, at):
        if settings.SETTINGS_ENV not in {"test", "development"}:
            return None
        with self._lock:
            proof = self._pending.get(raw_assertion)
            if not proof or not proof.verified_at <= at < proof.expires_at:
                self._pending.pop(raw_assertion, None)
                return None
            if (proof.user_uuid, proof.capability, proof.case_uuid) != (
                user_uuid,
                capability,
                case_uuid,
            ):
                return None
            del self._pending[raw_assertion]
            return proof


def issue_mock_step_up(
    actor: User,
    capability: str,
    case_uuid: UUID | None,
    raw_assertion: str,
    issuer: User,
    at: datetime,
    provider: MockStepUpProvider,
) -> UUID:
    """Composition supplies the verifier, never a client-submitted evidence ID."""
    if (
        settings.SETTINGS_ENV not in {"test", "development"}
        or settings.ACCOUNT_SECURITY.step_up_provider != "mock"
        or not transaction.get_connection().in_atomic_block
        or issuer.pk == actor.pk
    ):
        raise PermissionDenied("Staff authority denied")
    identities = {
        row.pk: row
        for row in User.objects.select_for_update()
        .filter(pk__in=[actor.pk, issuer.pk])
        .order_by("pk")
    }
    current = identities[actor.pk]
    if any(not row.is_active or row.state != "active" for row in identities.values()):
        raise PermissionDenied("Staff authority denied")
    proof = provider.verify(current.public_id, capability, case_uuid, raw_assertion, at)
    if proof is None:
        raise PermissionDenied("Staff authority denied")
    grant = StaffStepUpGrant.objects.create(
        user=current,
        auth_version=current.auth_version,
        capability=capability,
        case_uuid=case_uuid,
        method="mock",
        provider_reference=proof.provider_reference,
        verified_at=proof.verified_at,
        expires_at=proof.expires_at,
        trusted_issuer=issuer,
    )
    from apps.accounts.contracts import SecurityOutcome

    from .audit import append_event

    append_event(
        SecurityOutcome("staff.step_up", "succeeded", current.public_id, grant.id),
        actor_uuid=issuer.public_id,
        subject_type="staff",
    )
    return grant.id


def require_staff(
    actor: User,
    capability: str,
    case_uuid: UUID | None,
    step_up_id: UUID,
    reason_code: str,
    at: datetime,
) -> None:
    if not transaction.get_connection().in_atomic_block:
        raise RuntimeError("Staff authority requires the domain transaction")
    if capability not in CAPABILITIES or not reason_code or reason_code not in REASONS:
        raise PermissionDenied("Staff authority denied")
    # Identity rows precede authority rows in the global lock ordering.
    current = User.objects.select_for_update().get(pk=actor.pk)
    grant = (
        StaffCapabilityGrant.objects.select_for_update()
        .filter(
            user=current,
            capability=capability,
            revoked_at__isnull=True,
            valid_from__lte=at,
            valid_until__gt=at,
        )
        .first()
    )
    step = (
        StaffStepUpGrant.objects.select_for_update()
        .filter(
            pk=step_up_id,
            user=current,
            capability=capability,
            case_uuid=case_uuid,
            auth_version=current.auth_version,
            revoked_at__isnull=True,
            verified_at__lte=at,
            expires_at__gt=at,
        )
        .first()
    )
    valid = (
        current.is_active
        and current.state == "active"
        and grant
        and step
        and grant.granted_by_id != current.pk
        and step.trusted_issuer_id != current.pk
        and (at - step.verified_at).total_seconds()
        <= settings.ACCOUNT_SECURITY.policy.recent_auth_seconds
        and (
            step.method == "verified_mfa"
            or (
                step.method == "mock"
                and settings.SETTINGS_ENV in {"test", "development"}
            )
        )
    )
    if not valid:
        raise PermissionDenied("Staff authority denied")
