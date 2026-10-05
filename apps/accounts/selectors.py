"""Owned account visibility; generic model CRUD is intentionally absent."""

from uuid import UUID

from django.db.models import QuerySet
from django.utils import timezone

from .models import User
from .sessions import AccountActor, actor_user


def visible_accounts(actor: AccountActor) -> QuerySet[User]:
    user = actor_user(actor, "account.self", timezone.now())
    return User.objects.filter(pk=user.pk)


def visible_account(actor: AccountActor, public_id: UUID) -> User | None:
    return visible_accounts(actor).filter(public_id=public_id).first()
