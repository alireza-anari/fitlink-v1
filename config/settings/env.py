import os

from django.core.exceptions import ImproperlyConfigured


def invalid(name: str) -> None:
    raise ImproperlyConfigured(f"Invalid or missing configuration: {name}")


def str_value(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.environ.get(name, default)
    if value is None or not value.strip():
        if required:
            invalid(name)
        return ""
    return value.strip()


def bool_value(name: str, default: bool = False) -> bool:
    value = str_value(name, str(default)).lower()
    if value not in {"true", "false", "1", "0"}:
        invalid(name)
    return value in {"true", "1"}


def int_value(name: str, default: int | None = None, minimum: int | None = None) -> int:
    try:
        value = int(
            str_value(
                name,
                str(default) if default is not None else None,
                required=default is None,
            )
        )
    except (ValueError, TypeError):
        invalid(name)
        raise AssertionError("unreachable") from None
    if minimum is not None and value < minimum:
        invalid(name)
    return value


def csv_value(
    name: str, default: str | None = None, required: bool = False
) -> tuple[str, ...]:
    value = str_value(name, default, required)
    result = tuple(item.strip() for item in value.split(",") if item.strip())
    if required and not result:
        invalid(name)
    return result


def require_local_redis(values: tuple[str, ...]) -> None:
    from urllib.parse import urlsplit

    for value in values:
        parsed = urlsplit(value)
        if parsed.scheme != "redis" or parsed.hostname not in {
            "redis",
            "127.0.0.1",
            "localhost",
        }:
            invalid("REDIS_URLS")
