"""Only implemented factual search criteria and finite input are admitted."""

import importlib

import pytest

pytestmark = pytest.mark.unit


def criteria(**values):
    contracts = importlib.import_module("apps.marketplace.contracts")
    assert hasattr(contracts, "SearchCriteria"), "Missing bounded search criteria"
    return contracts.SearchCriteria(**values)


@pytest.mark.parametrize(
    "values",
    [
        {"rating": 5},
        {"capacity": True},
        {"packages": "x"},
        {"q": "x" * 121},
        {"q": " ".join(["x"] * 13)},
        {"q": "ـَ"},
        {"role": "assistant"},
        {"page_size": True},
        {"page_size": 21},
        {"sort": "price"},
        {"specialties": ("a",) * 2},
        {"languages": ("fa",) * 6},
        {"min_experience": 81},
        {"min_experience": 8, "max_experience": 2},
        {"city": "تهران"},
        {"region": "تهران"},
        {"q": "'); DROP TABLE x; --"},
    ],
)
def test_invalid_unsupported_and_unbounded_criteria_rejected(values):
    with pytest.raises(ValueError):
        criteria(**values)


def test_equivalent_criteria_share_cursor_binding():
    a = criteria(
        q="كيان ۱۲", specialties=("قدرت",), country="IR", region="تهران", city="تهران"
    )
    b = criteria(
        q="کیان 12", specialties=("قدرت",), country="IR", region="تهران", city="تهران"
    )
    assert a.binding() == b.binding()


def test_query_adapter_rejects_duplicate_unknown_and_byte_bounds():
    contracts = importlib.import_module("apps.marketplace.contracts")
    assert hasattr(contracts, "SearchCriteria"), "Missing bounded search criteria"
    parse = contracts.SearchCriteria.from_query_string
    for raw in ["q=a&q=b", "rating=5", "q=" + "ی" * 2100, "cursor=" + "x" * 2049]:
        with pytest.raises(ValueError):
            parse(raw)
