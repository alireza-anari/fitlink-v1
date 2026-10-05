import re
from typing import Protocol

from botocore.config import Config  # type: ignore[import-untyped]
from django.conf import settings
from django.core.files.base import ContentFile
from storages.backends.s3 import S3Storage  # type: ignore[import-untyped]


def validate_key(key: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_./-]{1,512}", key) or any(
        part in {"", ".", ".."} for part in key.split("/")
    ):
        raise ValueError("Invalid private object key")


def validate_expiry(expiry: int) -> None:
    if not 1 <= expiry <= 60:
        raise ValueError("Private URL expiry must be 1..60 seconds")


class PrivateObjectStore(Protocol):
    def put(self, key: str, data: bytes, content_type: str) -> None: ...
    def read(self, key: str) -> bytes: ...
    def delete(self, key: str) -> None: ...
    def signed_read_url(self, key: str, expires_seconds: int = 60) -> str: ...


class FakePrivateStore:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def put(self, key: str, data: bytes, content_type: str) -> None:
        validate_key(key)
        self.objects[key] = data

    def read(self, key: str) -> bytes:
        validate_key(key)
        try:
            return self.objects[key]
        except KeyError:
            raise FileNotFoundError("Private object absent") from None

    def delete(self, key: str) -> None:
        validate_key(key)
        self.objects.pop(key, None)

    def signed_read_url(self, key: str, expires_seconds: int = 60) -> str:
        validate_key(key)
        validate_expiry(expires_seconds)
        return f"fake://private/{key}?expires={expires_seconds}"


class TypedContentFile(ContentFile):
    content_type: str


class S3PrivateStore:
    def __init__(self) -> None:
        self.backend = S3Storage(
            endpoint_url=settings.S3_ENDPOINT_URL,
            bucket_name=settings.S3_BUCKET_NAME,
            region_name=settings.S3_REGION,
            access_key=settings.S3_ACCESS_KEY_ID,
            secret_key=settings.S3_SECRET_ACCESS_KEY,
            addressing_style=settings.S3_ADDRESSING_STYLE,
            signature_version="s3v4",
            default_acl=None,
            querystring_auth=True,
            querystring_expire=60,
            file_overwrite=True,
            client_config=Config(
                signature_version="s3v4",
                s3={"addressing_style": settings.S3_ADDRESSING_STYLE},
                connect_timeout=2,
                read_timeout=3,
                retries={"max_attempts": 1},
            ),
        )

    def put(self, key: str, data: bytes, content_type: str) -> None:
        validate_key(key)
        content = TypedContentFile(data)
        content.content_type = content_type
        self.backend.save(key, content)

    def read(self, key: str) -> bytes:
        validate_key(key)
        with self.backend.open(key, "rb") as content:
            return bytes(content.read())

    def delete(self, key: str) -> None:
        validate_key(key)
        self.backend.delete(key)

    def signed_read_url(self, key: str, expires_seconds: int = 60) -> str:
        validate_key(key)
        validate_expiry(expires_seconds)
        return str(self.backend.url(key, expire=expires_seconds))


def get_private_store() -> PrivateObjectStore:
    if settings.STORAGE_BACKEND == "fake":
        return FakePrivateStore()
    if settings.STORAGE_BACKEND == "s3":
        return S3PrivateStore()
    raise ValueError("Invalid storage backend")
