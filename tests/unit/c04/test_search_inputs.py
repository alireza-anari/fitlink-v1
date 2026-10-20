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


@pytest.mark.parametrize(
    "values",
    [
        {"q": []},
        {"role": []},
        {"mode": {}},
        {"sort": []},
        {"specialties": ("a\x00b",)},
        {"languages": ("fa\u202eb",)},
        {"page_size": 0},
        {"min_experience": True},
    ],
)
def test_malformed_types_are_uniform_validation_errors(values):
    with pytest.raises(ValueError):
        criteria(**values)


def test_cursor_is_signed_bound_finite_and_expires_at_fifteen_minutes():
    from datetime import timedelta
    from uuid import uuid4

    from django.utils import timezone

    from apps.marketplace import search_contracts

    assert callable(getattr(search_contracts, "encode_cursor", None)), (
        "Missing visible-only cursor"
    )
    now = timezone.now()
    selected = criteria(q="كيان", page_size=2)
    key = (2, 123, 456, uuid4())
    token = search_contracts.encode_cursor(selected, key, now)
    assert len(token.encode()) <= 2048
    assert search_contracts.decode_cursor(selected, token, now) == key
    for supplied, at, value in [
        (criteria(q="other", page_size=2), now, token),
        (criteria(q="کیان", page_size=3), now, token),
        (selected, now + timedelta(minutes=15), token),
        (selected, now - timedelta(seconds=1), token),
        (selected, now, token + "x"),
        (selected, now, "x" * 2049),
    ]:
        with pytest.raises(ValueError):
            search_contracts.decode_cursor(supplied, value, at)


def test_candidate_query_compiles_without_global_postgres_lookup_registration():
    from django.utils import timezone

    from apps.marketplace.search import candidate_query

    value = criteria(
        q="کیان", country="IR", region="تهران", city="تهران", mode="in_person"
    )
    sql, parameters = candidate_query(value, None, timezone.now())[
        :100
    ].query.sql_with_params()
    assert "کیان" not in sql and "کیان" in parameters
