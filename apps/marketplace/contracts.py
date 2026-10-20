"""Finite public payloads; restricted source metadata never joins a public DTO."""

import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID

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
        "verified_roles",
        "qualification_summaries",
        "media_purposes",
    }
)
SUMMARY_FIELDS = frozenset(
    {"role", "title", "issuer", "type_label", "issued_on", "expires_on"}
)


class MarketplaceUnavailable(RuntimeError):
    pass


def context(identifier, at):
    if (
        not isinstance(identifier, UUID)
        or not isinstance(at, datetime)
        or at.utcoffset() is None
    ):
        raise ValueError("Invalid public read context")


def _text(value, limit, *, required=False):
    if (
        not isinstance(value, str)
        or len(value) > limit
        or (required and not value.strip())
        or re.search(r"[<>\x00-\x08\x0b-\x1f\x7f]", value)
    ):
        raise ValueError("Invalid public text")


def _tokens(value, maximum, allowed=None):
    if not isinstance(value, list) or len(value) > maximum:
        raise ValueError("Invalid public selections")
    for item in value:
        _text(item, 64, required=True)
    if len(set(value)) != len(value) or (
        allowed is not None and not set(value) <= allowed
    ):
        raise ValueError("Invalid public selections")


def _validate_fields(value):
    for name, limit in [
        ("display_name", 120),
        ("biography", 2000),
        ("welcome_message", 500),
    ]:
        if name in value:
            _text(value[name], limit, required=name == "display_name")
    if "experience_years" in value:
        years = value["experience_years"]
        if years is not None and (type(years) is not int or not 0 <= years <= 80):
            raise ValueError("Invalid declared experience")
    for name, maximum, allowed in [
        ("specialties", 10, None),
        ("languages", 5, None),
        ("service_modes", 2, {"online", "in_person"}),
    ]:
        if name in value:
            _tokens(value[name], maximum, allowed)
    if "languages" in value and any(
        not re.fullmatch(r"[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*", tag) or len(tag) > 35
        for tag in value["languages"]
    ):
        raise ValueError("Invalid public language")
    if "accent_color" in value and (
        not isinstance(value["accent_color"], str)
        or not re.fullmatch(r"(?:#[a-fA-F0-9]{6})?", value["accent_color"])
    ):
        raise ValueError("Invalid public accent")
    locations = value.get("locations", [])
    if not isinstance(locations, list) or len(locations) > 10:
        raise ValueError("Invalid broad locations")
    seen = set()
    for row in locations:
        if not isinstance(row, dict) or not {"region", "city"} <= row.keys() <= {
            "country_code",
            "region",
            "city",
            "modes",
        }:
            raise ValueError("Invalid broad location fields")
        _text(row["region"], 100, required=True)
        _text(row["city"], 100, required=True)
        country = row.get("country_code", "IR")
        if not isinstance(country, str) or not re.fullmatch("[A-Z]{2}", country):
            raise ValueError("Invalid broad country")
        _tokens(row.get("modes", ["in_person"]), 2, {"online", "in_person"})
        key = (country, row["region"], row["city"])
        if key in seen:
            raise ValueError("Duplicate broad location")
        seen.add(key)
    summaries = value.get("qualification_summaries", [])
    if len(summaries) > 16 * 1024 // 36:
        raise ValueError("Public qualifications exceed bound")
    for row in summaries:
        for name, limit in [("title", 160), ("issuer", 160), ("type_label", 64)]:
            _text(row[name], limit, required=True)
        dates = []
        for name in ["issued_on", "expires_on"]:
            raw = row[name]
            if raw is None:
                dates.append(None)
                continue
            if not isinstance(raw, str):
                raise ValueError("Invalid public qualification date")
            parsed = date.fromisoformat(raw)
            if parsed.isoformat() != raw:
                raise ValueError("Invalid public qualification date")
            dates.append(parsed)
        if all(dates) and dates[1] < dates[0]:
            raise ValueError("Invalid public qualification dates")


def snapshot_json(value):
    if (
        not isinstance(value, dict)
        or not {"display_name", "verified_roles"} <= value.keys()
        or not value.keys() <= PUBLIC_FIELDS
    ):
        raise ValueError("Invalid public fields")
    if not isinstance(value["display_name"], str) or not value["display_name"]:
        raise ValueError("Invalid public display name")
    roles = value["verified_roles"]
    if (
        not isinstance(roles, list)
        or not roles
        or any(type(r) is not str or r not in {"coach", "nutritionist"} for r in roles)
        or len(set(roles)) != len(roles)
    ):
        raise ValueError("Invalid public roles")
    summaries = value.get("qualification_summaries", [])
    if not isinstance(summaries, list) or any(
        not isinstance(r, dict) or r.keys() != SUMMARY_FIELDS or r["role"] not in roles
        for r in summaries
    ):
        raise ValueError("Invalid public qualifications")
    purposes = value.get("media_purposes", [])
    if (
        not isinstance(purposes, list)
        or any(
            type(p) is not str or p not in {"avatar", "cover", "logo"} for p in purposes
        )
        or len(set(purposes)) != len(purposes)
    ):
        raise ValueError("Invalid public media selection")
    _validate_fields(value)
    try:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)
    except (TypeError, ValueError, UnicodeError):
        raise ValueError("Invalid public data") from None
    if len(text.encode()) > 1024 * 1024:
        raise ValueError("Public data exceeds bound")
    return text


@dataclass(frozen=True)
class PublicMedia:
    purpose: str
    copy_uuid: UUID

    def __post_init__(self):
        if self.purpose not in {"avatar", "cover", "logo"} or not isinstance(
            self.copy_uuid, UUID
        ):
            raise ValueError("Invalid public media")

    def as_public_dict(self):
        return {"purpose": self.purpose, "delivery_id": str(self.copy_uuid)}


@dataclass(frozen=True, init=False)
class PublicProfessionalDTO:
    profile_uuid: UUID
    slug: str
    _json: str = field(repr=False)

    def __init__(self, profile_uuid, slug, snapshot, media):
        if (
            not isinstance(profile_uuid, UUID)
            or not isinstance(slug, str)
            or not re.fullmatch(r"[a-z0-9-]{1,80}", slug)
        ):
            raise ValueError("Invalid public identity")
        snapshot = json.loads(snapshot_json(snapshot))
        if (
            not isinstance(media, tuple)
            or any(not isinstance(m, PublicMedia) for m in media)
            or len({m.purpose for m in media}) != len(media)
            or set(snapshot.get("media_purposes", [])) != {m.purpose for m in media}
        ):
            raise ValueError("Invalid public media")
        snapshot.pop("media_purposes", None)
        snapshot.update(
            profile_uuid=str(profile_uuid),
            slug=slug,
            media=[m.as_public_dict() for m in media],
        )
        object.__setattr__(self, "profile_uuid", profile_uuid)
        object.__setattr__(self, "slug", slug)
        object.__setattr__(
            self,
            "_json",
            json.dumps(snapshot, ensure_ascii=False, sort_keys=True, allow_nan=False),
        )

    def as_public_dict(self):
        return json.loads(self._json)


@dataclass(frozen=True)
class ProjectionSource:
    profile_uuid: UUID
    publication_uuid: UUID
    revision_uuid: UUID
    publication_version: int
    source_version: int
    slug: str
    snapshot_json: str = field(repr=False)
    authority_hash: str = field(repr=False)
    next_expiry: datetime | None
    media: tuple[PublicMedia, ...]

    def dto(self):
        return PublicProfessionalDTO(
            self.profile_uuid, self.slug, json.loads(self.snapshot_json), self.media
        )


@dataclass(frozen=True)
class RefreshResult:
    profile_uuid: UUID
    generation: int
    state: str


@dataclass(frozen=True)
class ReconcileResult:
    processed: int
    tombstones: int
    failures: int
