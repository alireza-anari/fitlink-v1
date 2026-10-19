"""Trusted publication flag, disclosure, audit and UUID-only outbox wiring."""

from django.conf import settings

from apps.governance.audit import append_event
from apps.governance.flags import feature_enabled
from apps.governance.outbox import append_outbox
from apps.professionals import publication
from apps.professionals.publication_contracts import (
    PublicationDisclosure,
    PublicationUnavailable,
)


def _disclosure():
    value = getattr(settings, "C04_PUBLICATION_DISCLOSURE", None)
    if not isinstance(value, dict) or set(value) != {"version", "text"}:
        raise PublicationUnavailable("Approved publication disclosure unavailable")
    try:
        return PublicationDisclosure(value["version"], value["text"])
    except ValueError:
        raise PublicationUnavailable(
            "Approved publication disclosure unavailable"
        ) from None


def _hooks(actor):
    def record(outcome):
        append_event(outcome, actor_uuid=actor.user_uuid, subject_type="professional")

    def emit(row):
        append_outbox(
            "professional.publication_changed",
            row.id,
            row.version,
            {"publication_uuid": str(row.id), "user_uuid": str(actor.user_uuid)},
            f"professional.publication_changed:{row.id}:{row.version}",
        )

    return {"record": record, "emit": emit}


def prepare_publication(
    actor,
    selection,
    expected_profile_version,
    expected_publication_version,
    operation_id,
    at,
):
    return publication.prepare_publication(
        actor,
        selection,
        expected_profile_version,
        expected_publication_version,
        operation_id,
        at,
        **_hooks(actor),
        enabled=lambda: feature_enabled("marketplace"),
        disclose=_disclosure,
    )


def confirm_publication(
    actor,
    publication_uuid,
    revision_uuid,
    confirmed,
    expected_version,
    operation_id,
    at,
):
    return publication.confirm_publication(
        actor,
        publication_uuid,
        revision_uuid,
        confirmed,
        expected_version,
        operation_id,
        at,
        **_hooks(actor),
        enabled=lambda: feature_enabled("marketplace"),
        disclose=_disclosure,
    )


def unpublish_profile(actor, publication_uuid, expected_version, operation_id, at):
    # Withdrawal never depends on discovery being enabled or disclosure text.
    return publication.unpublish_profile(
        actor,
        publication_uuid,
        expected_version,
        operation_id,
        at,
        **_hooks(actor),
    )
