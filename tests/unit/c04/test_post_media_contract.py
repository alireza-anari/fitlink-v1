"""Educational media has a distinct ingress and private preview purpose."""

from uuid import uuid4

from apps.assets.publication_contracts import AuthorizedEducationalMediaRelease
from apps.assets.validation import PURPOSES


def test_educational_ingress_has_explicit_purpose():
    assert "educational_image" in PURPOSES


def test_educational_copy_has_explicit_server_binding():
    release = AuthorizedEducationalMediaRelease(
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        "educational_image",
        1,
        1,
        1,
        1,
    )
    assert release.purpose == "educational_image"
