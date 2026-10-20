"""Filters match released facts and one broad-location tuple."""

import pytest

from tests.integration.c04.search_helpers import names, search

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_country_region_city_mode_are_one_tuple(corpus):
    corpus(
        locations=(
            {
                "country_code": "IR",
                "region": "تهران",
                "city": "تهران",
                "modes": ["in_person"],
            },
            {
                "country_code": "IR",
                "region": "فارس",
                "city": "شیراز",
                "modes": ["online"],
            },
        ),
        modes=("online", "in_person"),
    )
    assert names(
        search(country="IR", region="تهران", city="تهران", mode="in_person")
    ) == ["کیان"]
    assert search(country="IR", region="تهران", city="تهران", mode="online").items == ()
    assert search(country="IR", region="فارس", city="تهران").items == ()


def test_filters_are_or_within_and_across_and_unknown_experience_excluded(corpus):
    corpus("کیان", specialties=("قدرت",), languages=("fa",), experience=None)
    corpus("سارا", specialties=("دویدن",), languages=("en",), experience=12)
    assert names(search(specialties=("قدرت", "دویدن"), languages=("en",))) == ["سارا"]
    assert names(search(min_experience=0)) == ["سارا"]
    assert search(max_experience=10).items == ()
