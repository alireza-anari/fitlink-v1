"""Separate publication namespace on the existing nonanonymous private origin."""

import re
from uuid import UUID

from .publication_contracts import MAX_PUBLIC_IMAGE_BYTES, positive_version
from .storage import get_private_store, validate_limit


def publication_key(identifier: UUID, generation: int) -> str:
    if not isinstance(identifier, UUID):
        raise ValueError("Invalid publication object identity")
    positive_version(generation)
    return f"publication/{identifier.hex}/g{generation}.png"


def validate_publication_key(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"publication/[0-9a-f]{32}/g[1-9][0-9]{0,18}\.png", value
    ):
        raise ValueError("Invalid publication object namespace")
    positive_version(int(value.rsplit("/g", 1)[1][:-4]))


class PublicationObjectStore:
    """No URL signer, public ACL method or arbitrary private-key access."""

    def __init__(self, backend):
        self._backend = backend

    def put(self, key, data, content_type):
        validate_publication_key(key)
        if (
            not isinstance(data, bytes)
            or not 0 < len(data) <= MAX_PUBLIC_IMAGE_BYTES
            or content_type not in {"image/png", "image/jpeg"}
        ):
            raise ValueError("Invalid publication object")
        self._backend.put(key, data, content_type)

    def read_limited(self, key, max_bytes):
        validate_publication_key(key)
        validate_limit(max_bytes)
        return self._backend.read_limited(key, max_bytes)

    def head(self, key):
        validate_publication_key(key)
        return self._backend.head(key)

    def delete(self, key):
        validate_publication_key(key)
        self._backend.delete(key)


def get_publication_store():
    return PublicationObjectStore(get_private_store())
