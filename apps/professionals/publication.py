"""Owner-serialized explicit publication; verification never calls these commands."""

from collections.abc import Callable
from uuid import UUID

from django.db import IntegrityError, transaction
from django.db.models import Max

from apps.accounts.contracts import SecurityOutcome
from apps.accounts.sessions import locked_actor

from .contracts import ProfileConflict, ProfileNotFound
from .policies import owned_profile
from .publication_contracts import (
    PublicationDisclosure,
    PublicationDraftDTO,
    PublicationDTO,
    PublicationSelection,
    PublicationUnavailable,
    bounded_json,
    canonical_slug,
)
from .publication_models import (
    ProfessionalPublication,
    PublicationMediaBinding,
    PublicationQualification,
    PublicationRevision,
)
from .publication_selectors import (
    selected_sources,
    source_is_current,
    source_snapshot,
    stored_selection,
)
from .selectors import publication_eligibility
from .setup import context, locked_profile, receipt, remember, request_hash


def _callbacks(record, emit):
    if not callable(record) or not callable(emit):
        raise RuntimeError("Publication requires trusted transaction hooks")


def _disclosure(disclose):
    if not callable(disclose):
        raise RuntimeError("Publication disclosure provider unavailable")
    result = disclose()
    if not isinstance(result, PublicationDisclosure):
        raise PublicationUnavailable("Publication disclosure unavailable")
    return result


def _enabled(enabled):
    if not callable(enabled):
        raise RuntimeError("Publication requires current feature authority")
    if enabled() is not True:
        raise PublicationUnavailable("Marketplace publication disabled")


def _eligible(profile, selection, at):
    facts = publication_eligibility(profile.id, at)
    if (
        not facts.eligible
        or not facts.identity_verified
        or not set(selection.roles) <= set(facts.verified_roles)
    ):
        raise ProfileConflict("Publication eligibility changed")
    approved = {
        binding.kind: set(binding.evidence_revision_ids)
        for binding in facts.evidence_binding.roles
        if binding.kind in selection.roles
    }
    qualifications, media = selected_sources(profile, selection)
    if any(
        row.id not in approved.get(row.credential.role.role, set())
        for row in qualifications
    ):
        raise ValueError("Qualification is not part of current approved evidence")
    return qualifications, media


def project_publication(row):
    return PublicationDTO(
        row.id,
        row.profile_id,
        row.slug,
        row.version,
        row.state,
        row.current_revision_id,
        row.requested_revision_id,
    )


def _draft(publication, revision, version, disclosure):
    if (revision.disclosure_version, revision.disclosure_hash) != (
        disclosure.version,
        disclosure.digest,
    ):
        raise PublicationUnavailable("Publication disclosure changed")
    return PublicationDraftDTO(
        publication.id,
        revision.id,
        version,
        revision.source_profile_version,
        publication.slug,
        revision.disclosure_version,
        revision.disclosure_hash,
        disclosure.text,
        revision.valid_until,
        bounded_json(revision.snapshot).decode(),
    )


def _record(actor, publication, operation, action, record, emit):
    record(
        SecurityOutcome(
            action,
            "succeeded",
            publication.id,
            operation,
            ("version", "state", "current_revision"),
            "user_requested",
        )
    )
    emit(publication)


def _owned_publication(user, identifier):
    if not isinstance(identifier, UUID):
        raise ProfileNotFound("Publication unavailable")
    profile_id = (
        ProfessionalPublication.objects.filter(pk=identifier, profile__user=user)
        .values_list("profile_id", flat=True)
        .first()
    )
    if profile_id is None:
        raise ProfileNotFound("Publication unavailable")
    profile = owned_profile(user, profile_id, lock=True)
    row = ProfessionalPublication.objects.select_for_update().get(
        pk=identifier, profile=profile
    )
    return profile, row


def prepare_publication(
    actor,
    selection: PublicationSelection,
    expected_profile_version: int,
    expected_publication_version: int | None,
    operation_id: UUID,
    at,
    *,
    record: Callable,
    emit: Callable,
    enabled: Callable,
    disclose: Callable,
) -> PublicationDraftDTO:
    context(actor, expected_profile_version, operation_id, at)
    _callbacks(record, emit)
    if not isinstance(selection, PublicationSelection) or (
        expected_publication_version is not None
        and (
            type(expected_publication_version) is not int
            or expected_publication_version < 1
        )
    ):
        raise ValueError("Invalid publication prepare command")
    # Revalidate even an in-process value object; do not trust arbitrary mappings.
    selection = stored_selection(selection.as_selection_dict())
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_write", at)
        profile = locked_profile(user)
        _enabled(enabled)
        disclosure = _disclosure(disclose)
        row = (
            ProfessionalPublication.objects.select_for_update()
            .filter(profile=profile)
            .first()
        )
        digest = request_hash(
            "publication.prepare",
            {
                "selection": selection.as_selection_dict(),
                "profile_version": expected_profile_version,
                "publication_version": expected_publication_version,
            },
        )
        old = receipt(user, operation_id, "publication.prepare", digest, profile.id)
        if old:
            if row is None or old.result_uuid is None:
                raise ProfileConflict("Publication receipt unavailable")
            revision = row.revisions.filter(pk=old.result_uuid).first()
            if revision is None:
                raise ProfileConflict("Publication receipt unavailable")
            return _draft(row, revision, old.resulting_version, disclosure)
        if profile.version != expected_profile_version or (
            row is None
            and expected_publication_version is not None
            or row is not None
            and row.version != expected_publication_version
        ):
            raise ProfileConflict("Publication version changed")
        if selection.valid_until is not None and selection.valid_until <= at:
            raise ValueError("Publication expiry must be in the future")
        qualifications, media = _eligible(profile, selection, at)
        snapshot = source_snapshot(profile, selection, qualifications)
        slug = canonical_slug(profile.id, selection.slug)
        if row is not None:
            if selection.slug is not None and slug != row.slug:
                raise ProfileConflict("Publication slug is permanent")
        else:
            try:
                with transaction.atomic():
                    row = ProfessionalPublication.objects.create(
                        profile=profile, slug=slug, created_at=at, updated_at=at
                    )
            except IntegrityError:
                raise ProfileConflict("Publication slug unavailable") from None
        sequence = (row.revisions.aggregate(value=Max("sequence"))["value"] or 0) + 1
        revision = PublicationRevision.objects.create(
            publication=row,
            sequence=sequence,
            source_profile_version=profile.version,
            snapshot=snapshot,
            selection=selection.as_selection_dict(),
            disclosure_version=disclosure.version,
            disclosure_hash=disclosure.digest,
            valid_until=selection.valid_until,
            created_at=at,
            updated_at=at,
        )
        PublicationQualification.objects.bulk_create(
            [
                PublicationQualification(
                    revision=revision,
                    credential_revision=qualification,
                    position=index,
                    role=qualification.credential.role.role,
                    created_at=at,
                    updated_at=at,
                )
                for index, qualification in enumerate(qualifications)
            ]
        )
        PublicationMediaBinding.objects.bulk_create(
            [
                PublicationMediaBinding(
                    revision=revision,
                    asset=asset,
                    purpose=purpose,
                    asset_version=asset.version,
                    processing_version=asset.processing_version,
                    created_at=at,
                    updated_at=at,
                )
                for purpose, asset in media
            ]
        )
        row.current_revision = None
        row.requested_revision = revision
        row.state = "publication_requested"
        row.withdrawn_at = None
        row.version += 1
        row.updated_at = at
        row.save(
            update_fields=[
                "current_revision",
                "requested_revision",
                "state",
                "withdrawn_at",
                "version",
                "updated_at",
            ]
        )
        remember(
            user,
            operation_id,
            "publication.prepare",
            digest,
            profile.id,
            revision.id,
            row.version,
            at,
        )
        _record(actor, row, operation_id, "publication.prepared", record, emit)
        return _draft(row, revision, row.version, disclosure)


def confirm_publication(
    actor,
    publication_uuid,
    revision_uuid,
    confirmed: bool,
    expected_version,
    operation_id,
    at,
    *,
    record,
    emit,
    enabled,
    disclose,
) -> PublicationDTO:
    context(actor, expected_version, operation_id, at)
    _callbacks(record, emit)
    if (
        type(confirmed) is not bool
        or not confirmed
        or not isinstance(revision_uuid, UUID)
    ):
        raise ValueError("Explicit exact publication confirmation required")
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_write", at)
        profile, row = _owned_publication(user, publication_uuid)
        _enabled(enabled)
        digest = request_hash(
            "publication.confirm",
            {
                "publication": publication_uuid,
                "revision": revision_uuid,
                "confirmed": confirmed,
                "version": expected_version,
            },
        )
        old = receipt(user, operation_id, "publication.confirm", digest, row.id)
        if old:
            return project_publication(row)
        if (
            row.version != expected_version
            or row.state != "publication_requested"
            or row.requested_revision_id != revision_uuid
            or row.hidden_at is not None
            or row.hidden_case_uuid is not None
        ):
            raise ProfileConflict("Publication revision changed")
        revision = row.revisions.select_for_update().get(pk=revision_uuid)
        if revision.confirmed_at is not None or revision.confirmed_by_id is not None:
            raise ProfileConflict("Publication already confirmed")
        disclosure = _disclosure(disclose)
        if (revision.disclosure_version, revision.disclosure_hash) != (
            disclosure.version,
            disclosure.digest,
        ):
            raise ProfileConflict("Publication disclosure changed")
        if revision.valid_until is not None and revision.valid_until <= at:
            raise ProfileConflict("Publication revision expired")
        selection = stored_selection(revision.selection)
        _eligible(profile, selection, at)
        if not source_is_current(profile, revision):
            raise ProfileConflict("Publication source changed")
        revision.confirmed_by = user
        revision.confirmed_at = at
        revision.save(update_fields=["confirmed_by", "confirmed_at"])
        if not selection.media:
            row.current_revision = revision
            row.requested_revision = None
            row.state = "published"
        # Selected private media cannot become public without separate copies.
        # Task3 owns promotion only after every selected copy is actually ready.
        row.version += 1
        row.updated_at = at
        row.save(
            update_fields=[
                "current_revision",
                "requested_revision",
                "state",
                "version",
                "updated_at",
            ]
        )
        remember(
            user,
            operation_id,
            "publication.confirm",
            digest,
            row.id,
            revision.id,
            row.version,
            at,
        )
        _record(actor, row, operation_id, "publication.confirmed", record, emit)
        return project_publication(row)


def unpublish_profile(
    actor,
    publication_uuid,
    expected_version,
    operation_id,
    at,
    *,
    record,
    emit,
) -> PublicationDTO:
    context(actor, expected_version, operation_id, at)
    _callbacks(record, emit)
    with transaction.atomic():
        user = locked_actor(actor, "professional.profile_write", at)
        _, row = _owned_publication(user, publication_uuid)
        digest = request_hash(
            "publication.unpublish",
            {
                "publication": publication_uuid,
                "version": expected_version,
            },
        )
        old = receipt(user, operation_id, "publication.unpublish", digest, row.id)
        if old:
            return project_publication(row)
        if row.version != expected_version:
            raise ProfileConflict("Publication version changed")
        row.current_revision = row.requested_revision = None
        row.state = "unpublished"
        row.withdrawn_at = row.updated_at = at
        row.version += 1
        row.save(
            update_fields=[
                "current_revision",
                "requested_revision",
                "state",
                "withdrawn_at",
                "version",
                "updated_at",
            ]
        )
        remember(
            user,
            operation_id,
            "publication.unpublish",
            digest,
            row.id,
            row.id,
            row.version,
            at,
        )
        _record(actor, row, operation_id, "publication.withdrawn", record, emit)
        return project_publication(row)
