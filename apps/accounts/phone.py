"""Normalize presentation inputs; persistence remains canonical-only."""

import re

DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def normalize_iranian_mobile(raw: str) -> str:
    if not isinstance(raw, str) or len(raw) > 64:
        raise ValueError("invalid phone")
    value = raw.translate(DIGITS)
    if not re.fullmatch(r"[0-9+ ()-]+", value):
        raise ValueError("invalid phone")
    value = value.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if value.startswith("+98"):
        value = value[3:]
    elif value.startswith("0098"):
        value = value[4:]
    elif value.startswith("98"):
        value = value[2:]
    elif value.startswith("0"):
        value = value[1:]
    if not re.fullmatch(r"9[0-9]{9}", value):
        raise ValueError("invalid phone")
    return "+98" + value
