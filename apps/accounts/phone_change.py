"""Owned dual-purpose proof application, never a recovery or staff shortcut."""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta
from uuid import UUID

from django.conf import settings
from django.db import models, transaction

from .contracts import IdentityChangeResult, OutcomeRecorder, SecurityOutcome
from .models import User
from .otp import OtpBinding
from .phone import normalize_iranian_mobile
from .recovery_models import PhoneChangeHistory, PhoneChangeIntent
from .security_models import OTPChallenge, OTPPhoneState
from .sessions import AccountActor, actor_user, locked_actor
from .state import invalidate_auth_locked


class PhoneChangeConflict(PermissionError):
    pass


def _time(at: datetime) -> None:
    if at.tzinfo is None or at.utcoffset() is None:
        raise ValueError("Required phone change time")


@contextmanager
def locked_change(
    actor: AccountActor, change_uuid: UUID, at: datetime
) -> Iterator[tuple[User, PhoneChangeIntent]]:
    _time(at)
    candidate = PhoneChangeIntent.objects.filter(
        pk=change_uuid, user__public_id=actor.user_uuid
    ).first()
    if not candidate:
        raise PermissionError("Phone change denied")
    candidates = list(
        User.objects.filter(
            models.Q(public_id=actor.user_uuid) | models.Q(phone=candidate.new_phone)
        ).order_by("pk")
    )
    phones = sorted(
        {candidate.old_phone, candidate.new_phone, *(u.phone for u in candidates)}
    )
    with transaction.atomic():
        for phone in phones:
            anchor, _ = OTPPhoneState.objects.get_or_create(phone=phone)
            OTPPhoneState.objects.select_for_update().get(pk=anchor.pk)
        current = list(
            User.objects.select_for_update()
            .filter(pk__in=[u.pk for u in candidates])
            .order_by("pk")
        )
        if [(u.pk, u.phone) for u in current] != [(u.pk, u.phone) for u in candidates]:
            raise PhoneChangeConflict("Phone change conflict")
        user = locked_actor(actor, "phone_change.apply", at)
        intent = PhoneChangeIntent.objects.select_for_update().get(pk=candidate.pk)
        if intent.user_id != user.pk or (intent.old_phone, intent.new_phone) != (
            candidate.old_phone,
            candidate.new_phone,
        ):
            raise PermissionError("Phone change denied")
        yield user, intent


def _live(intent: PhoneChangeIntent, user: User, at: datetime) -> None:
    if (
        intent.applied_at
        or intent.retired_at
        or not intent.created_at <= at < intent.expires_at
        or intent.issued_auth_version != user.auth_version
        or intent.old_phone != user.phone
    ):
        raise PhoneChangeConflict("Phone change unavailable")


def begin_phone_change(
    actor: AccountActor, new_phone: str, at: datetime, record: OutcomeRecorder
) -> UUID:
    _time(at)
    if not callable(record):
        raise ValueError("Required phone change recorder")
    new = normalize_iranian_mobile(new_phone)
    candidate = actor_user(actor, "phone_change.begin", at)
    if candidate.phone == new:
        raise ValueError("Distinct phone required")
    with transaction.atomic():
        for phone in sorted({candidate.phone, new}):
            anchor, _ = OTPPhoneState.objects.get_or_create(phone=phone)
            OTPPhoneState.objects.select_for_update().get(pk=anchor.pk)
        user = locked_actor(actor, "phone_change.begin", at)
        if user.phone != candidate.phone:
            raise PhoneChangeConflict("Phone change conflict")
        previous = list(
            PhoneChangeIntent.objects.select_for_update()
            .filter(user=user, applied_at__isnull=True, retired_at__isnull=True)
            .order_by("id")
        )
        for intent in previous:
            intent.retired_at, intent.version = at, intent.version + 1
            intent.save(update_fields=["retired_at", "version"])
            OTPChallenge.objects.filter(
                context_uuid=intent.id, target_user=user, retired_at__isnull=True
            ).update(retired_at=at)
        intent = PhoneChangeIntent.objects.create(
            user=user,
            old_phone=user.phone,
            new_phone=new,
            issued_auth_version=user.auth_version,
            created_at=at,
            expires_at=at
            + timedelta(seconds=settings.ACCOUNT_SECURITY.policy.recent_auth_seconds),
        )
        record(
            SecurityOutcome(
                "phone_change.requested", "accepted", user.public_id, intent.id
            )
        )
        return intent.id


def change_binding(
    actor: AccountActor,
    change_uuid: UUID,
    kind: str,
    at: datetime,
    *,
    lock: bool = False,
) -> OtpBinding:
    if kind not in {"old", "new"}:
        raise ValueError("Invalid phone proof purpose")
    user = actor_user(actor, "phone_change.apply", at, lock=lock)
    query = (
        PhoneChangeIntent.objects.select_for_update()
        if lock
        else PhoneChangeIntent.objects.all()
    )
    intent = query.filter(pk=change_uuid, user=user).first()
    if not intent:
        raise PermissionError("Phone change denied")
    _live(intent, user, at)
    return OtpBinding(
        "phone_change_" + kind,
        intent.id,
        user.public_id,
        intent.issued_auth_version,
        intent.old_phone if kind == "old" else intent.new_phone,
    )


def validate_change_binding(
    actor: AccountActor, binding: OtpBinding, at: datetime
) -> None:
    if binding.purpose not in {"phone_change_old", "phone_change_new"}:
        raise PermissionError("Phone change denied")
    current = change_binding(
        actor,
        binding.context_uuid,
        binding.purpose.removeprefix("phone_change_"),
        at,
        lock=True,
    )
    if current != binding:
        raise PhoneChangeConflict("Phone change conflict")


def record_change_proof(
    actor: AccountActor, binding: OtpBinding, challenge_id: UUID, at: datetime
) -> None:
    validate_change_binding(actor, binding, at)
    intent = PhoneChangeIntent.objects.select_for_update().get(pk=binding.context_uuid)
    kind = binding.purpose.removeprefix("phone_change_")
    setattr(intent, kind + "_phone_challenge_id", challenge_id)
    setattr(intent, kind + "_phone_verified_at", at)
    intent.version += 1
    intent.save(
        update_fields=[
            kind + "_phone_challenge",
            kind + "_phone_verified_at",
            "version",
        ]
    )


def apply_phone_change(
    actor: AccountActor,
    change_uuid: UUID,
    at: datetime,
    record: OutcomeRecorder,
    *,
    emit: Callable[[IdentityChangeResult], None],
) -> IdentityChangeResult:
    if not callable(record) or not callable(emit):
        raise ValueError("Required identity effect recorders")
    with locked_change(actor, change_uuid, at) as (user, intent):
        if intent.applied_at is not None:
            assert intent.effect_auth_version is not None
            return IdentityChangeResult(
                user.public_id, intent.effect_auth_version, intent.id
            )
        _live(intent, user, at)
        if (
            not intent.old_phone_challenge_id
            or not intent.new_phone_challenge_id
            or intent.old_phone_challenge_id == intent.new_phone_challenge_id
        ):
            raise PhoneChangeConflict("Both proofs required")
        proofs = {
            row.id: row
            for row in OTPChallenge.objects.select_for_update()
            .filter(
                pk__in=[intent.old_phone_challenge_id, intent.new_phone_challenge_id]
            )
            .order_by("id")
        }
        for kind, proof_id, phone in [
            ("old", intent.old_phone_challenge_id, intent.old_phone),
            ("new", intent.new_phone_challenge_id, intent.new_phone),
        ]:
            proof = proofs.get(proof_id)
            anchor = OTPPhoneState.objects.get(phone=phone)
            if (
                not proof
                or proof.phone_state_id != anchor.pk
                or proof.generation != anchor.generation
                or proof.context_uuid != intent.id
                or proof.purpose != "phone_change_" + kind
                or proof.target_user_id != user.pk
                or proof.target_auth_version != user.auth_version
                or proof.delivery_state != "sent"
                or proof.consumed_at is None
                or proof.proof_applied_at is not None
                or proof.locked_at
                or proof.retired_at
                or not proof.consumed_at <= at < proof.expires_at
                or (at - proof.consumed_at).total_seconds() > 300
            ):
                raise PhoneChangeConflict("Phone proof unavailable")
        if User.objects.filter(phone=intent.new_phone).exclude(pk=user.pk).exists():
            raise PhoneChangeConflict("Phone unavailable")
        old_version = user.auth_version
        invalidate_auth_locked(user, at)
        user.phone = intent.new_phone
        user.save(update_fields=["phone"])
        OTPChallenge.objects.filter(
            phone_state__phone=user.phone, retired_at__isnull=True
        ).update(retired_at=at)
        OTPPhoneState.objects.filter(phone=user.phone).update(
            generation=models.F("generation") + 1
        )
        for proof in proofs.values():
            proof.proof_applied_at = at
            proof.save(update_fields=["proof_applied_at"])
        PhoneChangeHistory.objects.create(
            user=user,
            old_phone=intent.old_phone,
            new_phone=intent.new_phone,
            change_context=intent.id,
            actor_uuid=actor.user_uuid,
            at=at,
            old_auth_version=old_version,
            new_auth_version=user.auth_version,
        )
        intent.applied_at, intent.effect_auth_version, intent.version = (
            at,
            user.auth_version,
            intent.version + 1,
        )
        intent.save(update_fields=["applied_at", "effect_auth_version", "version"])
        result = IdentityChangeResult(user.public_id, user.auth_version, intent.id)
        record(
            SecurityOutcome(
                "account.phone_changed",
                "succeeded",
                user.public_id,
                intent.id,
                ("phone", "auth_version", "revoked_at", "proof_applied_at"),
                "user_requested",
            )
        )
        emit(result)
        return result
