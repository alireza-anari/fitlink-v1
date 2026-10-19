"""Explicit public facts; neither private setup nor a model serializer."""

import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from .contracts import ProfessionalStepInput
from .validation import STEP_FIELDS, locations, normalize_step, plain

PUBLIC_FIELDS = frozenset(
    {
        "display_name",
        "biography",
        "specialties",
        "experience_years",
        "service_modes",
        "languages",
        "locations",
        "accent_color",
        "welcome_message",
    }
)
PUBLIC_ROLES = frozenset({"coach", "nutritionist"})
PUBLIC_MEDIA = frozenset({"avatar", "cover", "logo"})
SUMMARY_FIELDS = frozenset(
    {"role", "title", "issuer", "type_label", "issued_on", "expires_on"}
)
MAX_PUBLIC_BYTES = 16 * 1024
RESERVED_SLUGS = frozenset(
    {
        "admin", "api", "assets", "athletes", "comparison", "favorites",
        "health", "login", "logout", "marketplace", "media", "owner", "posts",
        "professionals", "publication", "search", "sitemap", "staff", "static",
    }
)


def canonical_slug(profile_uuid: UUID, requested: str | None) -> str:
    if not isinstance(profile_uuid, UUID):
        raise ValueError("Invalid public profile identifier")
    if requested is None:
        return "p-" + profile_uuid.hex
    if (
        not isinstance(requested, str)
        or not re.fullmatch(r"[a-z0-9-]{1,80}", requested)
        or requested in RESERVED_SLUGS
    ):
        raise ValueError("Invalid public profile slug")
    return requested


def bounded_json(value) -> bytes:
    try:
        body = json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
            allow_nan=False,
        ).encode()
    except (TypeError, ValueError, UnicodeError):
        raise ValueError("Invalid publication data") from None
    if len(body) > MAX_PUBLIC_BYTES:
        raise ValueError("Publication data exceeds bound")
    return body


@dataclass(frozen=True)
class PublicationMediaSelection:
    purpose: str
    asset_uuid: UUID

    def __post_init__(self):
        if self.purpose not in PUBLIC_MEDIA or not isinstance(self.asset_uuid, UUID):
            raise ValueError("Invalid selected public media")


@dataclass(frozen=True)
class PublicationSelection:
    fields: tuple[str, ...]
    roles: tuple[str, ...]
    qualification_revision_ids: tuple[UUID, ...] = ()
    media: tuple[PublicationMediaSelection, ...] = ()
    slug: str | None = None
    valid_until: datetime | None = None

    def __post_init__(self):
        for value, allowed, required in (
            (self.fields, PUBLIC_FIELDS, True),
            (self.roles, PUBLIC_ROLES, True),
        ):
            if (
                not isinstance(value, tuple)
                or (required and not value)
                or any(not isinstance(v, str) for v in value)
                or len(set(value)) != len(value)
                or not set(value) <= allowed
            ):
                raise ValueError("Invalid publication selection")
        if "display_name" not in self.fields:
            raise ValueError("Public display name must be deliberately selected")
        revisions = self.qualification_revision_ids
        if (
            not isinstance(revisions, tuple)
            or any(not isinstance(v, UUID) for v in revisions)
            or len(set(revisions)) != len(revisions)
            or not isinstance(self.media, tuple)
            or any(not isinstance(v, PublicationMediaSelection) for v in self.media)
            or len({v.purpose for v in self.media}) != len(self.media)
            or len({v.asset_uuid for v in self.media}) != len(self.media)
        ):
            raise ValueError("Invalid publication source selection")
        if self.slug is not None:
            canonical_slug(UUID(int=0), self.slug)
        if self.valid_until is not None and (
            not isinstance(self.valid_until, datetime)
            or self.valid_until.utcoffset() is None
        ):
            raise ValueError("Publication expiry requires an aware time")
        bounded_json(
            {
                "fields": self.fields,
                "roles": self.roles,
                "qualifications": [str(v) for v in revisions],
                "media": [(v.purpose, str(v.asset_uuid)) for v in self.media],
                "slug": self.slug,
                "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            }
        )


@dataclass(frozen=True)
class PublicCredentialSummary:
    role: str
    title: str
    issuer: str
    type_label: str
    issued_on: date | None
    expires_on: date | None

    def __post_init__(self):
        if self.role not in PUBLIC_ROLES:
            raise ValueError("Invalid public qualification role")
        for value, limit in ((self.title, 160), (self.issuer, 160), (self.type_label, 64)):
            plain(value, limit, required=True)
        if any(type(v) is not date for v in (self.issued_on, self.expires_on) if v is not None):
            raise ValueError("Invalid public qualification date")
        if self.issued_on and self.expires_on and self.expires_on < self.issued_on:
            raise ValueError("Invalid public qualification dates")

    def as_public_dict(self) -> dict:
        return {
            "role": self.role,
            "title": self.title,
            "issuer": self.issuer,
            "type_label": self.type_label,
            "issued_on": self.issued_on.isoformat() if self.issued_on else None,
            "expires_on": self.expires_on.isoformat() if self.expires_on else None,
        }


def _summary(value, roles):
    if not isinstance(value, dict) or set(value) != SUMMARY_FIELDS:
        raise ValueError("Invalid public qualification fields")
    dates = []
    for key in ("issued_on", "expires_on"):
        raw = value[key]
        if raw is None:
            dates.append(None)
        else:
            try:
                parsed = date.fromisoformat(raw)
                if parsed.isoformat() != raw:
                    raise ValueError
                dates.append(parsed)
            except (ValueError, TypeError):
                raise ValueError("Invalid public qualification date") from None
    summary = PublicCredentialSummary(
        value["role"], value["title"], value["issuer"], value["type_label"], *dates
    )
    if summary.role not in roles:
        raise ValueError("Qualification role is not selected")


def validate_public_snapshot(snapshot: dict) -> None:
    extra = {"verified_roles", "qualification_summaries", "media_purposes"}
    if (
        not isinstance(snapshot, dict)
        or not {"display_name", "verified_roles"} <= set(snapshot)
        or not set(snapshot) <= PUBLIC_FIELDS | extra
    ):
        raise ValueError("Invalid public snapshot fields")
    bounded_json(snapshot)
    roles = snapshot["verified_roles"]
    if (
        not isinstance(roles, list)
        or not roles
        or any(not isinstance(r, str) for r in roles)
        or len(set(roles)) != len(roles)
        or not set(roles) <= PUBLIC_ROLES
    ):
        raise ValueError("Invalid public capabilities")
    # Reuse the existing C03 plain-text, broad-location and typed field bounds.
    # Identity fields are excluded before those validators are entered.
    for step, fields in STEP_FIELDS.items():
        selected = {k: snapshot[k] for k in fields & PUBLIC_FIELDS if k in snapshot}
        for key in ("languages", "service_modes"):
            if selected.get(key) == []:
                selected.pop(key)
        if selected:
            normalize_step(step, ProfessionalStepInput(selected))
    if "locations" in snapshot:
        locations(snapshot["locations"])
    summaries = snapshot.get("qualification_summaries", [])
    if not isinstance(summaries, list):
        raise ValueError("Invalid public qualification summaries")
    for value in summaries:
        _summary(value, roles)
    media = snapshot.get("media_purposes", [])
    if (
        not isinstance(media, list)
        or any(not isinstance(v, str) for v in media)
        or len(set(media)) != len(media)
        or not set(media) <= PUBLIC_MEDIA
    ):
        raise ValueError("Invalid public media purposes")
