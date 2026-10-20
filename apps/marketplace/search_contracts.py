"""Immutable factual criteria; signed paging binds their canonical meaning."""

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import parse_qsl
from uuid import UUID

from django.core import signing

from .normalization import NORMALIZATION_VERSION, normalize_persian

FIELDS = frozenset(
    {
        "q",
        "role",
        "mode",
        "country",
        "region",
        "city",
        "specialties",
        "languages",
        "min_experience",
        "max_experience",
        "sort",
        "page_size",
    }
)


@dataclass(frozen=True, init=False)
class SearchCriteria:
    q: str
    role: str | None
    mode: str | None
    country: str | None
    region: str | None
    city: str | None
    specialties: tuple[str, ...]
    languages: tuple[str, ...]
    min_experience: int | None
    max_experience: int | None
    sort: str
    page_size: int

    def __init__(self, **values):
        if not values.keys() <= FIELDS:
            raise ValueError("Unsupported search criteria")
        data = dict(
            q="",
            role=None,
            mode=None,
            country=None,
            region=None,
            city=None,
            specialties=(),
            languages=(),
            min_experience=None,
            max_experience=None,
            sort="relevance",
            page_size=20,
        )
        data.update(values)
        raw = data["q"]
        if (
            not isinstance(raw, str)
            or len(raw) > 120
            or re.search(r"[<>;:'\"&|!*()\\]", raw)
        ):
            raise ValueError("Invalid search query")
        data["q"] = normalize_persian(raw)
        if (raw and not data["q"]) or len(data["q"].split()) > 12:
            raise ValueError("Invalid search query")
        if (
            data["role"] not in (None, "coach", "nutritionist")
            or data["mode"] not in (None, "online", "in_person")
            or data["sort"] != "relevance"
        ):
            raise ValueError("Unsupported search criteria")
        if type(data["page_size"]) is not int or not 1 <= data["page_size"] <= 20:
            raise ValueError("Invalid search bound")
        location = [data[k] is not None for k in ("country", "region", "city")]
        if any(location):
            if (
                not all(location)
                or not isinstance(data["country"], str)
                or not re.fullmatch("[A-Z]{2}", data["country"])
            ):
                raise ValueError("Invalid location criteria")
            for key in ("region", "city"):
                text = data[key]
                if not isinstance(text, str) or not 1 <= len(text) <= 100:
                    raise ValueError("Invalid location criteria")
                data[key] = normalize_persian(text)
                if not data[key]:
                    raise ValueError("Invalid location criteria")
        for key in ("specialties", "languages"):
            items = data[key]
            if (
                not isinstance(items, tuple)
                or len(items) > 5
                or any(not isinstance(x, str) or not 1 <= len(x) <= 64 for x in items)
            ):
                raise ValueError("Invalid search filters")
            if key == "languages" and any(
                not re.fullmatch(r"[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*", x)
                or len(x) > 35
                for x in items
            ):
                raise ValueError("Invalid language criteria")
            normalized = tuple(normalize_persian(x) for x in items)
            if any(not x for x in normalized) or len(set(normalized)) != len(
                normalized
            ):
                raise ValueError("Invalid search filters")
            data[key] = tuple(sorted(normalized))
        for key in ("min_experience", "max_experience"):
            number = data[key]
            if number is not None and (
                type(number) is not int or not 0 <= number <= 80
            ):
                raise ValueError("Invalid declared experience criteria")
        if (
            data["min_experience"] is not None
            and data["max_experience"] is not None
            and data["min_experience"] > data["max_experience"]
        ):
            raise ValueError("Invalid declared experience criteria")
        for key, value in data.items():
            object.__setattr__(self, key, value)

    def binding(self):
        return json.dumps(
            {
                "normalization": NORMALIZATION_VERSION,
                **{k: getattr(self, k) for k in sorted(FIELDS)},
            },
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    @classmethod
    def from_query_string(cls, raw):
        if (
            not isinstance(raw, str)
            or len(raw.encode()) > 4096
            or re.search(r"%(?![0-9A-Fa-f]{2})", raw)
        ):
            raise ValueError("Invalid search input")
        try:
            pairs = parse_qsl(
                raw,
                keep_blank_values=True,
                strict_parsing=True,
                encoding="utf-8",
                errors="strict",
                max_num_fields=14,
            )
        except (ValueError, UnicodeError):
            raise ValueError("Invalid search input") from None
        values = {}
        cursor = None
        for key, value in pairs:
            if (
                key not in FIELDS | {"cursor"}
                or key in values
                or (key == "cursor" and cursor is not None)
            ):
                raise ValueError("Invalid search input")
            if key == "cursor":
                if not value or len(value.encode()) > 2048:
                    raise ValueError("Invalid search cursor")
                cursor = value
                continue
            if key in {"specialties", "languages"}:
                value = tuple(value.split(","))
            elif key in {"min_experience", "max_experience", "page_size"}:
                if not re.fullmatch(r"[0-9]{1,2}", value):
                    raise ValueError("Invalid search integer")
                value = int(value)
            values[key] = value
        return cls(**values), cursor


@dataclass(frozen=True)
class PublicPage:
    items: tuple
    next_cursor: str | None


def _time(at):
    if not isinstance(at, datetime) or at.utcoffset() is None:
        raise ValueError("Invalid search time")
    return at.timestamp()


def _cursor_key(key):
    if (
        not isinstance(key, tuple)
        or len(key) != 4
        or type(key[0]) is not int
        or key[0] not in (0, 1, 2)
        or any(type(v) is not int or not 0 <= v <= 2**63 - 1 for v in key[1:3])
        or not isinstance(key[3], UUID)
    ):
        raise ValueError("Invalid search cursor")
    return key


def encode_cursor(criteria, key, at):
    if not isinstance(criteria, SearchCriteria):
        raise ValueError("Invalid search criteria")
    _cursor_key(key)
    return signing.Signer(salt="fitlink:c04:public-search:v1").sign_object(
        {
            "v": NORMALIZATION_VERSION,
            "criteria": hashlib.sha256(criteria.binding().encode()).hexdigest(),
            "key": [*key[:3], str(key[3])],
            "issued": _time(at),
        },
        compress=False,
    )


def decode_cursor(criteria, token, at):
    if (
        not isinstance(criteria, SearchCriteria)
        or not isinstance(token, str)
        or len(token.encode()) > 2048
    ):
        raise ValueError("Invalid search cursor")
    now = _time(at)
    try:
        value = signing.Signer(salt="fitlink:c04:public-search:v1").unsign_object(token)
        if (
            not isinstance(value, dict)
            or set(value) != {"v", "criteria", "key", "issued"}
            or value["v"] != NORMALIZATION_VERSION
            or value["criteria"]
            != hashlib.sha256(criteria.binding().encode()).hexdigest()
            or type(value["issued"]) not in (int, float)
            or not 0 <= now - value["issued"] < 900
            or not isinstance(value["key"], list)
            or len(value["key"]) != 4
        ):
            raise ValueError
        return _cursor_key((*value["key"][:3], UUID(value["key"][3])))
    except (ValueError, TypeError, KeyError, AttributeError, signing.BadSignature):
        raise ValueError("Invalid search cursor") from None
