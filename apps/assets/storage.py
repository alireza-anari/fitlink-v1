import re
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from tempfile import SpooledTemporaryFile
from typing import Protocol

from botocore.config import Config  # type: ignore[import-untyped]
from botocore.exceptions import (  # type: ignore[import-untyped]
    BotoCoreError,
    ClientError,
)
from django.conf import settings
from django.core.files.base import ContentFile
from storages.backends.s3 import S3Storage  # type: ignore[import-untyped]

from .contracts import UploadUnavailable


class ByteStream(Protocol):
    def read(self, size: int = -1) -> bytes: ...


@dataclass(frozen=True)
class ObjectMetadata:
    size: int
    content_type: str


def validate_limit(max_bytes: int) -> None:
    if type(max_bytes) is not int or not 1 <= max_bytes <= 10_000_000:
        raise ValueError("Invalid bounded object limit")


@contextmanager
def limited_spool(
    stream: ByteStream, max_bytes: int
) -> Iterator[SpooledTemporaryFile[bytes]]:
    validate_limit(max_bytes)
    total = 0
    with SpooledTemporaryFile(max_size=1_048_576, mode="w+b") as content:
        while True:
            chunk = stream.read(min(65536, max_bytes + 1 - total))
            if not isinstance(chunk, bytes):
                raise ValueError("Invalid upload stream")
            total += len(chunk)
            if total > max_bytes:
                raise ValueError("Private object too large")
            if not chunk:
                break
            content.write(chunk)
        if total == 0:
            raise ValueError("Empty private object")
        content.seek(0)
        yield content


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
    def put_stream(
        self, key: str, stream: ByteStream, content_type: str, max_bytes: int
    ) -> None: ...
    def read_limited(self, key: str, max_bytes: int) -> bytes: ...
    def head(self, key: str) -> ObjectMetadata: ...


class FakePrivateStore:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.content_types: dict[str, str] = {}

    def put(self, key: str, data: bytes, content_type: str) -> None:
        validate_key(key)
        self.objects[key] = data
        self.content_types[key] = content_type

    def read(self, key: str) -> bytes:
        validate_key(key)
        try:
            return self.objects[key]
        except KeyError:
            raise FileNotFoundError("Private object absent") from None

    def delete(self, key: str) -> None:
        validate_key(key)
        self.objects.pop(key, None)
        self.content_types.pop(key, None)

    def put_stream(
        self, key: str, stream: ByteStream, content_type: str, max_bytes: int
    ) -> None:
        validate_key(key)
        if key in self.objects:
            raise ValueError("Private source already exists")
        with limited_spool(stream, max_bytes) as content:
            self.put(key, content.read(), content_type)

    def head(self, key: str) -> ObjectMetadata:
        return ObjectMetadata(len(self.read(key)), self.content_types.get(key, ""))

    def read_limited(self, key: str, max_bytes: int) -> bytes:
        validate_limit(max_bytes)
        data = self.read(key)
        if len(data) > max_bytes:
            raise ValueError("Private object too large")
        return data

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

    def put_stream(
        self, key: str, stream: ByteStream, content_type: str, max_bytes: int
    ) -> None:
        validate_key(key)
        with limited_spool(stream, max_bytes) as content:
            try:
                self.backend.connection.meta.client.put_object(
                    Bucket=self.backend.bucket_name,
                    Key=key,
                    Body=content,
                    ContentType=content_type,
                    IfNoneMatch="*",
                )
            except ClientError as error:
                if error.response.get("Error", {}).get("Code") in {
                    "PreconditionFailed",
                    "ConditionalRequestConflict",
                    "412",
                    "409",
                }:
                    raise ValueError("Private source already exists") from None
                raise UploadUnavailable("Private store unavailable") from None
            except BotoCoreError:
                raise UploadUnavailable("Private store unavailable") from None

    def head(self, key: str) -> ObjectMetadata:
        validate_key(key)
        try:
            result = self.backend.connection.meta.client.head_object(
                Bucket=self.backend.bucket_name, Key=key
            )
            return ObjectMetadata(
                result["ContentLength"], result.get("ContentType", "")
            )
        except ClientError as error:
            if error.response.get("Error", {}).get("Code") in {
                "NoSuchKey",
                "404",
                "NotFound",
            }:
                raise FileNotFoundError("Private object absent") from None
            raise UploadUnavailable("Private store unavailable") from None
        except BotoCoreError:
            raise UploadUnavailable("Private store unavailable") from None

    def read_limited(self, key: str, max_bytes: int) -> bytes:
        validate_key(key)
        validate_limit(max_bytes)
        try:
            result = self.backend.connection.meta.client.get_object(
                Bucket=self.backend.bucket_name, Key=key
            )
        except ClientError as error:
            if error.response.get("Error", {}).get("Code") in {
                "NoSuchKey",
                "404",
                "NotFound",
            }:
                raise FileNotFoundError("Private object absent") from None
            raise UploadUnavailable("Private store unavailable") from None
        except BotoCoreError:
            raise UploadUnavailable("Private store unavailable") from None
        body = result["Body"]
        try:
            if result["ContentLength"] > max_bytes:
                raise ValueError("Private object too large")
            data = bytes(body.read(max_bytes + 1))
            if len(data) > max_bytes:
                raise ValueError("Private object too large")
            return data
        except BotoCoreError:
            raise UploadUnavailable("Private store unavailable") from None
        finally:
            body.close()


def get_private_store() -> PrivateObjectStore:
    if settings.STORAGE_BACKEND == "fake":
        return FakePrivateStore()
    if settings.STORAGE_BACKEND == "s3":
        return S3PrivateStore()
    raise ValueError("Invalid storage backend")
