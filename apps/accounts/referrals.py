"""Digest-only acquisition attribution; never permissions or lead conversion."""

import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from django.conf import settings
from django.db import transaction
from django.db.models import Q

from .contracts import OutcomeRecorder, SecurityOutcome
from .models import User
from .policies import require_account_action
from .referral_models import InviteReferralLink, ReferralAttribution
from .security_keys import security_digest
from .sessions import AccountActor, locked_actor

REFERRAL_SECONDS = 30 * 86400


@dataclass(frozen=True)
class ReferralDescriptor:
    link_uuid: UUID


def _link(token: str, at: datetime) -> InviteReferralLink | None:
    if not isinstance(token, str) or re.fullmatch(r"[A-Za-z0-9_-]{43}", token) is None:
        return None
    ring = settings.ACCOUNT_SECURITY.keys
    matches = Q(pk__in=[])
    for key_id in ring.key_ids:
        matches |= Q(
            key_id=key_id, token_digest=security_digest("referral", token, key_id)
        )
    return InviteReferralLink.objects.filter(
        matches, created_at__lte=at, expires_at__gt=at, revoked_at__isnull=True
    ).first()


def resolve_referral(token: str, at: datetime) -> ReferralDescriptor | None:
    link = _link(token, at)
    if (
        not link
        or not User.objects.filter(
            pk=link.issuer_id, state="active", is_active=True
        ).exists()
    ):
        return None
    return ReferralDescriptor(link.id)


def issue_referral(actor: AccountActor, at: datetime, record: OutcomeRecorder) -> str:
    if not callable(record):
        raise ValueError("Referral recorder required")
    with transaction.atomic():
        issuer = locked_actor(actor, "referral.create", at)
        token = secrets.token_urlsafe(32)
        key_id = settings.ACCOUNT_SECURITY.keys.active_id
        link = InviteReferralLink.objects.create(
            issuer=issuer,
            token_digest=security_digest("referral", token, key_id),
            key_id=key_id,
            created_at=at,
            expires_at=at + timedelta(seconds=REFERRAL_SECONDS),
        )
        record(
            SecurityOutcome(
                "referral.created",
                "succeeded",
                link.id,
                uuid4(),
                reason_code="user_requested",
            )
        )
        return token


def revoke_referral(actor: AccountActor, link_uuid: UUID, at: datetime) -> None:
    with transaction.atomic():
        issuer = locked_actor(actor, "referral.create", at)
        link = (
            InviteReferralLink.objects.select_for_update()
            .filter(pk=link_uuid, issuer=issuer)
            .first()
        )
        if not link or at < link.created_at:
            raise PermissionError("Referral action denied")
        if link.revoked_at is None:
            link.revoked_at = at
            link.save(update_fields=["revoked_at"])


def bind_descriptor(
    user: User, descriptor: ReferralDescriptor, at: datetime, record: OutcomeRecorder
) -> UUID:
    if not callable(record) or not isinstance(descriptor, ReferralDescriptor):
        raise ValueError("Invalid referral contract")
    with transaction.atomic():
        initial = InviteReferralLink.objects.filter(pk=descriptor.link_uuid).first()
        if not initial:
            raise PermissionError("Referral action denied")
        identities = {
            row.pk: row
            for row in User.objects.select_for_update()
            .filter(pk__in=[user.pk, initial.issuer_id])
            .order_by("pk")
        }
        recipient = identities.get(user.pk)
        issuer = identities.get(initial.issuer_id)
        if not recipient or not issuer or recipient.pk == issuer.pk:
            raise PermissionError("Referral action denied")
        require_account_action(recipient, "referral.attribute", "normal")
        require_account_action(issuer, "referral.create", "normal")
        link = (
            InviteReferralLink.objects.select_for_update()
            .filter(
                pk=initial.pk,
                issuer=issuer,
                created_at__lte=at,
                expires_at__gt=at,
                revoked_at__isnull=True,
            )
            .first()
        )
        if not link:
            raise PermissionError("Referral action denied")
        previous = ReferralAttribution.objects.filter(recipient=recipient).first()
        if previous:
            return previous.id
        attribution = ReferralAttribution.objects.create(
            recipient=recipient, link=link, attributed_at=at
        )
        record(
            SecurityOutcome(
                "referral.attributed",
                "succeeded",
                attribution.id,
                uuid4(),
                reason_code="user_requested",
            )
        )
        return attribution.id


def bind_attribution(
    user: User, token: str, at: datetime, record: OutcomeRecorder
) -> UUID:
    descriptor = resolve_referral(token, at)
    if not descriptor:
        raise PermissionError("Referral action denied")
    return bind_descriptor(user, descriptor, at, record)
