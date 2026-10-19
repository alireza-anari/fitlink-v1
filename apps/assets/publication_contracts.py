"""Server-validated publication release metadata; possession grants no authority."""

from dataclasses import dataclass
from uuid import UUID

PUBLIC_MEDIA_PURPOSES = frozenset({"avatar", "cover", "logo"})
MAX_PUBLIC_IMAGE_BYTES = 10_000_000


def positive_version(value):
    if type(value) is not int or not 1 <= value <= 9_223_372_036_854_775_807:
        raise ValueError("Invalid publication generation")


@dataclass(frozen=True)
class AuthorizedPublicMediaRelease:
    owner_uuid: UUID
    profile_uuid: UUID
    publication_uuid: UUID
    revision_uuid: UUID
    source_asset_uuid: UUID
    purpose: str
    source_version: int
    processing_version: int
    publication_version: int
    generation: int

    def __post_init__(self):
        for value in (
            self.owner_uuid,
            self.profile_uuid,
            self.publication_uuid,
            self.revision_uuid,
            self.source_asset_uuid,
        ):
            if not isinstance(value, UUID):
                raise ValueError("Invalid publication binding")
        if (
            not isinstance(self.purpose, str)
            or self.purpose not in PUBLIC_MEDIA_PURPOSES
        ):
            raise ValueError("Invalid publication media purpose")
        for value in (
            self.source_version,
            self.processing_version,
            self.publication_version,
            self.generation,
        ):
            positive_version(value)


@dataclass(frozen=True)
class PublicCopyDTO:
    id: UUID
    generation: int
    state: str


@dataclass(frozen=True)
class CopyResult:
    copy_uuid: UUID
    generation: int
    status: str
