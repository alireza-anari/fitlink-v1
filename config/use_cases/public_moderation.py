"""Explicit profile/post callbacks; governance cannot import feature domains."""

from django.db import transaction

from apps.accounts.models import User
from apps.governance.moderation_models import ModerationCase
from apps.professionals.models import ProfessionalProfile, ProfessionalPublication
from apps.professionals.post_models import EducationalPost


def lock_target(actor, target):
    owners = (
        ProfessionalProfile.objects.filter(pk=target.object_uuid).values_list(
            "user_id", flat=True
        )
        if target.kind == "profile"
        else EducationalPost.objects.filter(pk=target.object_uuid).values_list(
            "profile__user_id", flat=True
        )
    )
    ids = list(owners) + list(
        User.objects.filter(public_id=actor.user_uuid).values_list("pk", flat=True)
    )
    list(User.objects.select_for_update().filter(pk__in=ids).order_by("pk"))


def lock_case(actor, identifier):
    owner = (
        ModerationCase.objects.filter(pk=identifier)
        .values_list("owner_id", flat=True)
        .first()
    )
    ids = list(
        User.objects.filter(public_id=actor.user_uuid).values_list("pk", flat=True)
    )
    if owner is not None:
        ids.append(owner)
    list(User.objects.select_for_update().filter(pk__in=ids).order_by("pk"))


def target_source(target, at):
    if target.kind == "profile":
        from config.use_cases.marketplace import current_source

        value = current_source(target.object_uuid, at)
        owner = (
            ProfessionalProfile.objects.filter(pk=target.object_uuid)
            .values_list("user_id", flat=True)
            .first()
        )
    else:
        from config.use_cases.public_content import public_post

        value = public_post(target.object_uuid, at)
        owner = (
            EducationalPost.objects.filter(pk=target.object_uuid)
            .values_list("profile__user_id", flat=True)
            .first()
        )
    return (
        (owner, value.revision_uuid)
        if value is not None and owner is not None
        else None
    )


def apply_decision(case, action, at):
    if not transaction.get_connection().in_atomic_block:
        raise PermissionError("Moderation transaction required")
    if action == "dismiss":
        return
    query = (
        ProfessionalPublication.objects
        if case.target_kind == "profile"
        else EducationalPost.objects
    )
    where = (
        {"profile_id": case.target_uuid}
        if case.target_kind == "profile"
        else {"pk": case.target_uuid}
    )
    row = query.select_for_update().filter(**where).first()
    if row is None:
        raise LookupError("Content unavailable")
    if action == "hide":
        if row.current_revision_id != case.revision_uuid or row.hidden_at is not None:
            raise ValueError("Content version changed")
        row.hidden_at, row.hidden_case_uuid = at, case.id
        if case.target_kind == "post":
            row.state = "hidden"
    else:
        if row.hidden_case_uuid != case.id:
            raise ValueError("Moderation latch changed")
        row.hidden_at = row.hidden_case_uuid = None
        if case.target_kind == "post":
            row.state = (
                "published"
                if row.current_revision_id and row.withdrawn_at is None
                else "draft"
            )
    row.version += 1
    row.updated_at = at
    row.save()
