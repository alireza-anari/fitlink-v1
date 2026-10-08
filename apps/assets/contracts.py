"""Private ingress exposes workflow metadata, never keys, hashes or URLs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


class AssetNotFound(LookupError):
    pass


class UploadConflict(ValueError):
    pass


class UploadQuota(ValueError):
    pass


class UploadUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class AssetSubject:
    kind: str
    id: UUID


@dataclass(frozen=True)
class UploadDTO:
    id: UUID
    version: int
    state: str
    purpose: str
    upload_expires_at: datetime


@dataclass(frozen=True)
class AuthorizedAssetRead:
    asset_uuid: UUID
    derivative_uuid: UUID
    content_type: str
