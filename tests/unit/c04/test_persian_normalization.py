"""fa-search-v1 equivalence is behavioral, not a source-string contract."""

import importlib
import importlib.util

import pytest

pytestmark = pytest.mark.unit


def normalize(value):
    path = "apps.marketplace.normalization"
    assert importlib.util.find_spec(path) is not None, "Missing Persian normalization"
    return importlib.import_module(path).normalize_persian(value)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("كيان", "کیان"),
        ("کِیـان", "کیان"),
        ("۱۲ ١٢ 12", "12 12 12"),
        ("نیم\u200cفاصله", "نیم فاصله"),
        ("نیم\u200dفاصله", "نیم فاصله"),
        ("  FITNESS\tCoach  ", "fitness coach"),
        ("", ""),
        ("کیان، تهران!", "کیان تهران"),
    ],
)
def test_normalization_equivalence(raw, expected):
    assert normalize(raw) == expected


@pytest.mark.parametrize("raw", [None, 12, "name\x00hidden", "a\u202eb"])
def test_normalization_rejects_mistyped_and_control_input(raw):
    with pytest.raises(ValueError):
        normalize(raw)
