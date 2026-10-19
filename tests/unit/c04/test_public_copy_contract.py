"""Publication-copy authority is exact, immutable and cannot name evidence."""

import importlib
import importlib.util
from dataclasses import FrozenInstanceError, fields, replace
from uuid import uuid4

import pytest

pytestmark = pytest.mark.unit


def module(name):
    path = "apps.assets." + name
    assert importlib.util.find_spec(path), "Missing isolated publication copy boundary"
    return importlib.import_module(path)


def release():
    return module("publication_contracts").AuthorizedPublicMediaRelease(
        owner_uuid=uuid4(),
        profile_uuid=uuid4(),
        publication_uuid=uuid4(),
        revision_uuid=uuid4(),
        source_asset_uuid=uuid4(),
        purpose="avatar",
        source_version=1,
        processing_version=1,
        publication_version=3,
        generation=1,
    )


def test_release_is_frozen_and_exact():
    value = release()
    with pytest.raises(FrozenInstanceError):
        value.purpose = "identity_evidence"
    assert value.source_asset_uuid != value.revision_uuid


@pytest.mark.parametrize(
    "purpose",
    [
        "identity_evidence",
        "credential_evidence",
        "owner_preview",
        "evidence_preview",
        "educational_image",
        "avatar/../../credential",
    ],
)
def test_private_source_and_evidence_never_public_copy(purpose):
    with pytest.raises(ValueError):
        replace(release(), purpose=purpose)


@pytest.mark.parametrize("value", [0, -1, True, 1.5, "1", None])
def test_release_versions_are_positive_exact_integers(value):
    for name in (
        "source_version",
        "processing_version",
        "publication_version",
        "generation",
    ):
        with pytest.raises(ValueError):
            replace(release(), **{name: value})


def test_public_copy_dto_exposes_no_private_source_or_storage_metadata():
    dto = module("publication_contracts").PublicCopyDTO
    assert {f.name for f in fields(dto)} == {"id", "generation", "state"}


def test_publication_key_cannot_alias_private_storage():
    storage = module("public_storage")
    identifier = uuid4()
    key = storage.publication_key(identifier, 2)
    assert key == f"publication/{identifier.hex}/g2.png"
    for value in (
        "source/secret",
        "derivative/secret",
        "publication/../source",
        "https://synthetic.invalid/image.png",
    ):
        with pytest.raises(ValueError):
            storage.validate_publication_key(value)
