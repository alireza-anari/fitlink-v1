"""Strict labeled dates and Tehran adult declaration boundary.

Borkowski year-start algorithm adapted from jalaali-js (MIT), source blob
14309485f93dd8eff2e30d7ba20ba38115457a74; see dates.LICENSE.
Only the reviewed UI range 1200..1500 is accepted; no calendar guessing.
"""

import re
from bisect import bisect_right
from datetime import date, datetime, timedelta
from functools import lru_cache
from typing import Literal
from zoneinfo import ZoneInfo

from .phone import DIGITS

_BREAKS = (
    -61,
    9,
    38,
    199,
    426,
    686,
    756,
    818,
    1111,
    1181,
    1210,
    1635,
    2060,
    2097,
    2192,
    2262,
    2324,
    2394,
    2456,
    3178,
)


@lru_cache(maxsize=302)
def _year_start(year: int) -> date:
    # This deliberately supports 1501 internally to measure the final UI year.
    if not 1200 <= year <= 1501:
        raise ValueError("unsupported calendar date")
    leap_j = -14
    previous = _BREAKS[0]
    jump = 0
    for boundary in _BREAKS[1:]:
        jump = boundary - previous
        if year < boundary:
            break
        leap_j += (jump // 33) * 8 + (jump % 33) // 4
        previous = boundary
    n = year - previous
    leap_j += (n // 33) * 8 + ((n % 33) + 3) // 4
    if jump % 33 == 4 and jump - n == 4:
        leap_j += 1
    gregorian = year + 621
    leap_g = gregorian // 4 - ((gregorian // 100 + 1) * 3) // 4 - 150
    return date(gregorian, 3, 20 + leap_j - leap_g)


def parse_birth_date(raw: str, calendar: Literal["gregorian", "jalali"]) -> date:
    if not isinstance(raw, str) or len(raw) != 10:
        raise ValueError("invalid birth date")
    value = raw.translate(DIGITS)
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("invalid birth date")
    year, month, day = map(int, value.split("-"))
    if calendar == "gregorian":
        try:
            return date(year, month, day)
        except ValueError:
            raise ValueError("invalid birth date") from None
    if calendar != "jalali" or not 1200 <= year <= 1500 or not 1 <= month <= 12:
        raise ValueError("invalid birth date")
    length = 31 if month <= 6 else 30
    if month == 12:
        length = (_year_start(year + 1) - _year_start(year)).days - 336
    if not 1 <= day <= length:
        raise ValueError("invalid birth date")
    offset = (month - 1) * 31 if month <= 6 else 186 + (month - 7) * 30
    return _year_start(year) + timedelta(days=offset + day - 1)


def gregorian_to_jalali(value: date) -> tuple[int, int, int]:
    starts = tuple(_year_start(year) for year in range(1200, 1502))
    if not starts[0] <= value < starts[-1]:
        raise ValueError("unsupported calendar date")
    index = bisect_right(starts, value) - 1
    offset = (value - starts[index]).days
    if offset < 186:
        month, day = divmod(offset, 31)
        return 1200 + index, month + 1, day + 1
    month, day = divmod(offset - 186, 30)
    return 1200 + index, month + 7, day + 1


def require_adult(birth_date: date, attested: bool, at: datetime) -> None:
    if (
        not isinstance(birth_date, date)
        or isinstance(birth_date, datetime)
        or attested is not True
        or at.tzinfo is None
        or at.utcoffset() is None
    ):
        raise ValueError("adult declaration required")
    today = at.astimezone(ZoneInfo("Asia/Tehran")).date()
    # Tuple ordering gives February 29 a March 1 anniversary in common years.
    age = (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )
    if birth_date > today or age < 18:
        raise ValueError("adult declaration required")
