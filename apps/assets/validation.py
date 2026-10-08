"""Raster admission coherence only; Task 5 establishes content safety."""

MAX_BYTES = 10_000_000
MEDIA_TYPES = frozenset({"image/jpeg", "image/png"})
PURPOSES = frozenset(
    {"identity_evidence", "credential_evidence", "avatar", "cover", "logo"}
)


def validate_declaration(size: int, media_type: str) -> None:
    if (
        type(size) is not int
        or not 1 <= size <= MAX_BYTES
        or media_type not in MEDIA_TYPES
    ):
        raise ValueError("Invalid upload declaration")


def raster_signature(prefix: bytes, declared_type: str) -> str:
    if declared_type not in MEDIA_TYPES:
        raise ValueError("Invalid raster declaration")
    detected = (
        "image/png"
        if prefix.startswith(b"\x89PNG\r\n\x1a\n")
        else "image/jpeg"
        if prefix.startswith(b"\xff\xd8\xff")
        else ""
    )
    if detected != declared_type:
        raise ValueError("Invalid raster signature")
    return detected


def validate_filename(name: str, declared_type: str) -> None:
    suffix = name.rsplit(".", 1)[-1].lower()
    allowed = (
        {"png"}
        if declared_type == "image/png"
        else {"jpg", "jpeg"}
        if declared_type == "image/jpeg"
        else set()
    )
    if suffix not in allowed:
        raise ValueError("Invalid raster extension")
