"""Educational posts are finite text and selected image identifiers, never HTML."""

import importlib
import importlib.util
from uuid import uuid4

import pytest


def contracts():
    name = "apps.professionals.post_contracts"
    assert importlib.util.find_spec(name), "Missing safe educational post contract"
    return importlib.import_module(name)


def test_plain_text_draft_is_private_and_does_not_require_an_image():
    value = contracts().PostInput.from_dict({"text": "آموزش حرکت", "images": []})
    assert value.text == "آموزش حرکت"
    assert value.images == ()
    with pytest.raises(ValueError):
        value.validate_publication()


@pytest.mark.parametrize(
    "text",
    [
        "<script>alert(1)</script>",
        "<svg/>",
        "<style>x</style>",
        "javascript:alert(1)",
        "https://remote.test/image.png",
        "x\x00y",
        "x" * 2001,
        "",
    ],
)
def test_unsafe_or_unbounded_post_text_rejected(text):
    with pytest.raises(ValueError):
        contracts().PostInput.from_dict({"text": text, "images": []})


@pytest.mark.parametrize(
    "extra", ["html", "markdown", "title", "url", "owner", "profile_uuid"]
)
def test_unknown_post_fields_rejected(extra):
    with pytest.raises(ValueError):
        contracts().PostInput.from_dict({"text": "آموزش", "images": [], extra: "x"})


@pytest.mark.parametrize("count", [1, 2, 3, 4])
def test_one_to_four_ordered_images_admitted(count):
    images = [{"asset_uuid": str(uuid4()), "alt": "شرح حرکت"} for _ in range(count)]
    value = contracts().PostInput.from_dict({"text": "آموزش", "images": images})
    value.validate_publication()
    assert [str(i.asset_uuid) for i in value.images] == [
        i["asset_uuid"] for i in images
    ]


@pytest.mark.parametrize(
    "images",
    [
        [{"asset_uuid": str(uuid4()), "alt": ""}],
        [{"asset_uuid": str(uuid4()), "alt": "x" * 201}],
        [{"asset_uuid": str(uuid4()), "alt": "x", "url": "https://remote.test"}],
        [{"asset_uuid": "forged", "alt": "x"}],
        [{"asset_uuid": str(uuid4()), "alt": "x"} for _ in range(5)],
    ],
)
def test_malformed_or_unbounded_image_selection_rejected(images):
    with pytest.raises(ValueError):
        contracts().PostInput.from_dict({"text": "آموزش", "images": images})


def test_duplicate_images_rejected():
    image = {"asset_uuid": str(uuid4()), "alt": "شرح"}
    with pytest.raises(ValueError):
        contracts().PostInput.from_dict({"text": "آموزش", "images": [image, image]})


def test_quotes_are_text_and_export_has_only_explicit_fields():
    value = contracts().PostInput.from_dict(
        {"text": "حرکت \"الف\" و 'ب'", "images": []}
    )
    assert value.as_dict() == {"text": "حرکت \"الف\" و 'ب'", "images": []}
