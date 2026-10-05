from datetime import UTC, date, datetime, timedelta
from importlib import import_module

import pytest

pytestmark = pytest.mark.unit


def function(module, name):
    try:
        loaded = import_module("apps.accounts." + module)
    except ModuleNotFoundError:
        pytest.fail(f"missing C02 contract: {module}.{name}")
    assert hasattr(loaded, name), f"missing C02 contract: {module}.{name}"
    return getattr(loaded, name)


@pytest.mark.parametrize(
    "raw",
    [
        "۰۹۱۲۳۴۵۶۷۸۹",
        "٠٩١٢٣٤٥٦٧٨٩",
        "09123456789",
        "9123456789",
        "989123456789",
        "+989123456789",
        "00989123456789",
        "(0912) 345-6789",
    ],
)
def test_canonical_mobile(raw):
    assert function("phone", "normalize_iranian_mobile")(raw) == "+989123456789"


@pytest.mark.parametrize(
    "raw",
    [
        "0912\u200b3456789",
        "0912\u202e3456789",
        "०9123456789",
        "09123456789x123",
        "++989123456789",
        "+449123456789",
        "02123456789",
        "0912345678",
        "\t09123456789",
        " " * 65,
        "",
        "09９23456789",
    ],
)
def test_invalid_mobile(raw):
    with pytest.raises(ValueError):
        function("phone", "normalize_iranian_mobile")(raw)


def test_calendar_reference_vectors():
    parse = function("dates", "parse_birth_date")
    assert parse("1395-01-23", "jalali") == date(2016, 4, 11)
    assert parse("۱۳۹۵-۰۱-۲۳", "jalali") == date(2016, 4, 11)
    assert parse("1395-12-30", "jalali") == date(2017, 3, 20)
    assert parse("2000-02-29", "gregorian") == date(2000, 2, 29)
    for raw, calendar in [
        ("1394-12-30", "jalali"),
        ("1199-01-01", "jalali"),
        ("1501-01-01", "jalali"),
        ("2001-02-29", "gregorian"),
        ("2000-02-29", "unknown"),
        ("2000-2-29", "gregorian"),
    ]:
        with pytest.raises(ValueError):
            parse(raw, calendar)


def test_exhaustive_supported_calendar_roundtrip():
    parse = function("dates", "parse_birth_date")
    reverse = function("dates", "gregorian_to_jalali")
    current = parse("1200-01-01", "jalali")
    final = parse("1500-12-29", "jalali")
    while current <= final:
        year, month, day = reverse(current)
        assert parse(f"{year:04}-{month:02}-{day:02}", "jalali") == current
        current += timedelta(days=1)


def test_adult_birthdays_and_tehran_boundary():
    adult = function("dates", "require_adult")
    with pytest.raises(ValueError):
        adult(date(2008, 10, 6), True, datetime(2026, 10, 5, 12, tzinfo=UTC))
    adult(date(2008, 10, 6), True, datetime(2026, 10, 5, 21, tzinfo=UTC))
    with pytest.raises(ValueError):
        adult(date(2008, 2, 29), True, datetime(2026, 2, 28, 12, tzinfo=UTC))
    adult(date(2008, 2, 29), True, datetime(2026, 3, 1, 12, tzinfo=UTC))
    for born, attested in [(date(2000, 1, 1), False), (date(2027, 1, 1), True)]:
        with pytest.raises(ValueError):
            adult(born, attested, datetime(2026, 10, 5, tzinfo=UTC))
    with pytest.raises(ValueError):
        adult(date(2000, 1, 1), True, datetime(2026, 10, 5))


def test_client_ip_trust_boundary():
    extract = function("client_ip", "client_ip")
    assert extract("198.51.100.1", "1.2.3.4", ()) == "198.51.100.1"
    assert extract("::ffff:198.51.100.1", None, ()) == "198.51.100.1"
    assert (
        extract("10.0.0.1", "198.51.100.1, 10.0.0.2", ("10.0.0.0/8",)) == "198.51.100.1"
    )
    for header in ["garbage", "1.2.3.4,", ",".join(["1.2.3.4"] * 11)]:
        with pytest.raises(ValueError):
            extract("10.0.0.1", header, ("10.0.0.0/8",))
    with pytest.raises(ValueError):
        extract("10.0.0.1", "1.2.3.4", ("0.0.0.0/0",))
