"""Finite educational text and source selections; never executable markup."""

import re
from dataclasses import dataclass, field
from uuid import UUID

from .publication_contracts import bounded_json
from .validation import plain


@dataclass(frozen=True)
class PostDTO:
    id: UUID
    revision_id: UUID | None
    version: int
    state: str


@dataclass(frozen=True)
class PublicPostImage:
    copy_uuid: UUID
    alt: str


@dataclass(frozen=True)
class PublicPostDTO:
    id: UUID
    profile_uuid: UUID
    revision_uuid: UUID
    text: str
    images: tuple[PublicPostImage, ...]


def _text(value, limit):
    value = plain(value, limit, required=True)
    if re.search(r"(?:javascript|data|https?|file|vbscript)\s*:", value, re.I):
        raise ValueError("External or executable content is not supported")
    return value


@dataclass(frozen=True)
class PostImageInput:
    asset_uuid: UUID
    alt: str = field(repr=False)

    def __post_init__(self):
        if not isinstance(self.asset_uuid, UUID):
            raise ValueError("Invalid post image")
        object.__setattr__(self, "alt", _text(self.alt, 200))


@dataclass(frozen=True)
class PostInput:
    text: str = field(repr=False)
    images: tuple[PostImageInput, ...] = field(default=(), repr=False)

    def __post_init__(self):
        object.__setattr__(self, "text", _text(self.text, 2000))
        if (
            not isinstance(self.images, tuple)
            or len(self.images) > 4
            or any(not isinstance(i, PostImageInput) for i in self.images)
            or len({i.asset_uuid for i in self.images}) != len(self.images)
        ):
            raise ValueError("Invalid post images")
        bounded_json(self.as_dict(), limit=16 * 1024)

    @classmethod
    def from_dict(cls, value):
        if (
            not isinstance(value, dict)
            or set(value) != {"text", "images"}
            or not isinstance(value["images"], list)
            or len(value["images"]) > 4
        ):
            raise ValueError("Invalid post fields")
        images = []
        for image in value["images"]:
            if not isinstance(image, dict) or set(image) != {"asset_uuid", "alt"}:
                raise ValueError("Invalid post image fields")
            try:
                identifier = UUID(image["asset_uuid"])
                if str(identifier) != image["asset_uuid"]:
                    raise ValueError
            except (ValueError, TypeError, AttributeError):
                raise ValueError("Invalid post image identifier") from None
            images.append(PostImageInput(identifier, image["alt"]))
        return cls(value["text"], tuple(images))

    def validate_publication(self):
        if not self.images:
            raise ValueError("Publication requires one to four images")

    def as_dict(self):
        return {
            "text": self.text,
            "images": [
                {"asset_uuid": str(i.asset_uuid), "alt": i.alt} for i in self.images
            ],
        }
