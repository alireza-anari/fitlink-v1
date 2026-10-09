"""Private setup bounds; declarations never confer verified authority."""

import re
import unicodedata
from datetime import date
from uuid import UUID

from .contracts import CredentialInput, ProfessionalStepInput

IDENTITY_FIELDS = {"identity_name"}
CREDENTIAL_FIELDS = {
    "category",
    "role",
    "type_code",
    "issuer",
    "title",
    "issued_on",
    "expires_on",
    "source_asset",
}
STEP_FIELDS = {
    "identity": {"display_name", "identity_name", "roles"},
    "description": {"biography", "specialties", "experience_years"},
    "locations": {"service_modes", "languages", "locations"},
    "branding": {"avatar", "cover", "logo", "accent_color", "welcome_message"},
    "credentials": set(),
    "preview": set(),
}
TEXT_LIMITS = {
    "display_name": 120,
    "identity_name": 120,
    "biography": 2000,
    "welcome_message": 500,
    "type_code": 64,
    "issuer": 160,
    "title": 160,
}
PROFILE_FIELDS = tuple(
    name
    for fields in STEP_FIELDS.values()
    for name in sorted(fields)
    if name not in {"roles", "locations"}
)


def plain(value: object, limit: int, *, required: bool = False) -> str:
    if not isinstance(value, str) or re.search(r"[<>\x00-\x08\x0b-\x1f\x7f]", value):
        raise ValueError("Invalid private text")
    result = unicodedata.normalize("NFC", value.strip())
    if len(result) > limit or (required and not result):
        raise ValueError("Invalid private text")
    return result


def tokens(value: object, maximum: int, allowed: set[str] | None = None) -> list[str]:
    if not isinstance(value, list) or not 1 <= len(value) <= maximum:
        raise ValueError("Invalid private selections")
    result = [plain(v, 64, required=True) for v in value]
    if len(set(result)) != len(result) or (
        allowed is not None and not set(result) <= allowed
    ):
        raise ValueError("Invalid private selections")
    return result


def locations(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list) or len(value) > 10:
        raise ValueError("Invalid broad locations")
    result: list[dict[str, object]] = []
    for entry in value:
        if not isinstance(entry, dict) or not {"region", "city"} <= set(entry) <= {
            "country_code",
            "region",
            "city",
            "modes",
        }:
            raise ValueError("Invalid broad location")
        country = entry.get("country_code", "IR")
        if not isinstance(country, str) or not re.fullmatch(r"[A-Z]{2}", country):
            raise ValueError("Invalid country")
        row: dict[str, object] = {
            "country_code": country,
            "region": plain(entry["region"], 100, required=True),
            "city": plain(entry["city"], 100, required=True),
            "modes": tokens(
                entry.get("modes", ["in_person"]), 2, {"online", "in_person"}
            ),
        }
        if any(
            all(old[k] == row[k] for k in ("country_code", "region", "city"))
            for old in result
        ):
            raise ValueError("Duplicate broad location")
        result.append(row)
    return result


def normalize_step(step: str, payload: ProfessionalStepInput) -> dict[str, object]:
    if (
        not isinstance(step, str)
        or step not in STEP_FIELDS
        or not isinstance(payload, ProfessionalStepInput)
        or not isinstance(payload.values, dict)
        or not set(payload.values) <= STEP_FIELDS[step]
    ):
        raise ValueError("Invalid professional step")
    result: dict[str, object] = {}
    for name, value in payload.values.items():
        if name in TEXT_LIMITS:
            result[name] = plain(
                value,
                TEXT_LIMITS[name],
                required=name in {"display_name", "identity_name"},
            )
        elif name == "roles":
            result[name] = sorted(tokens(value, 2, {"coach", "nutritionist"}))
        elif name == "experience_years":
            if value is not None and (type(value) is not int or not 0 <= value <= 80):
                raise ValueError("Invalid declared experience")
            result[name] = value
        elif name == "specialties":
            result[name] = tokens(value, 10) if value != [] else []
        elif name == "service_modes":
            result[name] = sorted(tokens(value, 2, {"online", "in_person"}))
        elif name == "languages":
            langs = tokens(value, 5)
            if any(
                len(tag) > 35
                or not re.fullmatch(r"[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*", tag)
                for tag in langs
            ):
                raise ValueError("Invalid language tags")
            result[name] = langs
        elif name == "locations":
            result[name] = locations(value)
        elif name == "accent_color":
            if not isinstance(value, str) or (
                value != "" and not re.fullmatch(r"#[0-9A-Fa-f]{6}", value)
            ):
                raise ValueError("Invalid accent")
            result[name] = value.lower()
        elif name in {"avatar", "cover", "logo"}:
            if value is not None and not isinstance(value, UUID):
                raise ValueError("Invalid private asset")
            result[name] = value
    return result


def normalize_credential(payload: CredentialInput) -> dict[str, object]:
    if (
        not isinstance(payload, CredentialInput)
        or not isinstance(payload.values, dict)
        or not set(payload.values) <= CREDENTIAL_FIELDS
        or not {"category", "type_code", "title", "issuer"} <= set(payload.values)
    ):
        raise ValueError("Invalid credential input")
    values = payload.values
    category, role = values["category"], values.get("role")
    if (
        category not in ("identity", "qualification")
        or (category == "identity" and role is not None)
        or (category == "qualification" and role not in ("coach", "nutritionist"))
    ):
        raise ValueError("Invalid credential target")
    result: dict[str, object] = {"category": category, "role": role}
    for name in ("type_code", "issuer", "title"):
        result[name] = plain(values[name], TEXT_LIMITS[name], required=True)
    for name in ("issued_on", "expires_on"):
        value = values.get(name)
        if value is not None and type(value) is not date:
            raise ValueError("Invalid credential date")
        result[name] = value
    issued, expires = result["issued_on"], result["expires_on"]
    if isinstance(issued, date) and isinstance(expires, date) and expires < issued:
        raise ValueError("Invalid credential dates")
    source = values.get("source_asset")
    if source is not None and not isinstance(source, UUID):
        raise ValueError("Invalid private asset")
    result["source_asset"] = source
    return result
