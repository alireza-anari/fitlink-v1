"""Versioned token normalization; presentation text is never overwritten."""

import unicodedata

NORMALIZATION_VERSION = "fa-search-v1"
TRANSLATION = str.maketrans("يك٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "یک01234567890123456789")


def normalize_persian(value: str) -> str:
    if not isinstance(value, str) or any(
        unicodedata.category(char) in {"Cc", "Cf"} and char not in "\t\r\n\u200c\u200d"
        for char in value
    ):
        raise ValueError("Invalid search text")
    result = []
    for char in unicodedata.normalize("NFKC", value).translate(TRANSLATION).casefold():
        if char == "ـ" or (
            unicodedata.category(char).startswith("M")
            and "ARABIC" in unicodedata.name(char, "")
        ):
            continue
        result.append(char if char.isalnum() else " ")
    return " ".join("".join(result).split())
