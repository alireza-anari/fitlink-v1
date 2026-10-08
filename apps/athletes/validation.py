"""Engineering input bounds for one dated snapshot, never medical advice."""

import re
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

from .contracts import BaselineStepInput

STEP_FIELDS = {
    "basics": ("height_cm", "weight_kg"),
    "goals": ("goals",),
    "experience": ("experience", "training_experience_months"),
    "availability": ("available_days",),
    "facilities": ("equipment", "equipment_other", "facilities"),
    "context": ("lifestyle", "sleep_hours", "energy"),
    "habits": ("meals_per_day", "hydration_habit", "nutrition_habits"),
    "measures": ("waist_cm", "approximate_records"),
}
OPTIONAL_DEFAULTS: dict[str, object] = {
    "height_cm": None,
    "weight_kg": None,
    "training_experience_months": None,
    "lifestyle": "",
    "sleep_hours": None,
    "energy": None,
    "meals_per_day": None,
    "hydration_habit": "",
    "nutrition_habits": "",
    "waist_cm": None,
    "approximate_records": [],
}
NON_SENSITIVE_FIELDS = (
    "goals",
    "experience",
    "available_days",
    "equipment",
    "equipment_other",
    "facilities",
)
TOKENS = {
    "goals": {
        "general_fitness",
        "strength",
        "endurance",
        "muscle_gain",
        "weight_management",
    },
    "experience": {"beginner", "intermediate", "advanced"},
    "equipment": {"bodyweight", "dumbbells", "barbell", "machines", "bands", "other"},
    "facilities": {"home", "gym", "outdoors", "other"},
    "lifestyle": {"sedentary", "mixed", "active"},
    "hydration_habit": {"low", "regular", "unknown"},
}
DECIMALS = {
    "height_cm": (50, 250, 1),
    "weight_kg": (20, 400, 1),
    "waist_cm": (20, 250, 1),
    "sleep_hours": (0, 24, 1),
}
INTEGERS = {
    "training_experience_months": (0, 1200),
    "energy": (1, 10),
    "meals_per_day": (0, 12),
}
TEXT = {"equipment_other": 200, "nutrition_habits": 500}


def _decimal(value: object, low: int, high: int, places: int) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal)):
        raise ValueError("Invalid decimal value")
    try:
        result = Decimal(value)
    except InvalidOperation:
        raise ValueError("Invalid decimal value") from None
    if (
        not result.is_finite()
        or not low <= result <= high
        or result.quantize(Decimal(1).scaleb(-places)) != result
    ):
        raise ValueError("Decimal outside snapshot bounds")
    return result.quantize(Decimal(1).scaleb(-places))


def _text(value: object, limit: int) -> str:
    if (
        not isinstance(value, str)
        or len(value) > limit
        or re.search(r"[<>\x00-\x08\x0b-\x1f\x7f]", value)
    ):
        raise ValueError("Invalid plain snapshot text")
    return value.strip()


def _records(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list) or len(value) > 5:
        raise ValueError("Invalid approximate records")
    result = []
    keys = {"label", "value", "unit", "observed_at", "provenance"}
    for entry in value:
        if not isinstance(entry, dict) or set(entry) != keys:
            raise ValueError("Invalid approximate record fields")
        label = _text(entry["label"], 80)
        if (
            not label
            or not isinstance(entry["unit"], str)
            or entry["unit"] not in {"kg", "reps", "seconds", "metres"}
            or entry["provenance"] != "self_reported"
        ):
            raise ValueError("Invalid approximate record")
        number = _decimal(entry["value"], 0, 999999, 2)
        if number <= 0:
            raise ValueError("Invalid approximate record value")
        if not isinstance(entry["observed_at"], str):
            raise ValueError("Invalid approximate record date")
        try:
            observed = datetime.fromisoformat(entry["observed_at"])
        except ValueError:
            raise ValueError("Invalid approximate record date") from None
        if observed.tzinfo is None or observed.utcoffset() is None:
            raise ValueError("Invalid approximate record date")
        result.append(
            {
                "label": label,
                "value": str(number),
                "unit": entry["unit"],
                "observed_at": observed.astimezone(UTC).isoformat(),
                "provenance": "self_reported",
            }
        )
    return result


def normalize_step(step: str, payload: BaselineStepInput) -> dict[str, object]:
    if (
        not isinstance(step, str)
        or step not in STEP_FIELDS
        or not isinstance(payload, BaselineStepInput)
        or not isinstance(payload.values, dict)
        or not set(payload.values) <= set(STEP_FIELDS[step])
    ):
        raise ValueError("Unknown baseline step or fields")
    result: dict[str, object] = {}
    for name, value in payload.values.items():
        if value is None:
            if name not in OPTIONAL_DEFAULTS:
                raise ValueError("Only optional fields may be cleared")
            default = OPTIONAL_DEFAULTS[name]
            result[name] = default.copy() if isinstance(default, list) else default
        elif name in DECIMALS:
            result[name] = _decimal(value, *DECIMALS[name])
        elif name in INTEGERS:
            low, high = INTEGERS[name]
            if type(value) is not int or not low <= value <= high:
                raise ValueError("Invalid snapshot integer")
            result[name] = value
        elif name in TEXT:
            result[name] = _text(value, TEXT[name])
        elif name == "approximate_records":
            result[name] = _records(value)
        elif name in {"goals", "available_days", "equipment", "facilities"}:
            if not isinstance(value, list) or len(value) > (
                7 if name == "available_days" else len(TOKENS[name])
            ):
                raise ValueError("Invalid snapshot selection")
            if name == "available_days":
                if any(
                    type(token) is not int or not 1 <= token <= 7 for token in value
                ):
                    raise ValueError("Invalid weekday selection")
            elif any(
                not isinstance(token, str) or token not in TOKENS[name]
                for token in value
            ):
                raise ValueError("Invalid snapshot token")
            if len(set(value)) != len(value):
                raise ValueError("Duplicate snapshot selection")
            result[name] = sorted(value)
        else:
            if not isinstance(value, str) or value not in TOKENS[name]:
                raise ValueError("Invalid snapshot token")
            result[name] = value
    return result


def completed_steps(row) -> tuple[str, ...]:
    return tuple(
        step
        for step, field in (
            ("goals", "goals"),
            ("experience", "experience"),
            ("availability", "available_days"),
            ("facilities", "facilities"),
        )
        if getattr(row, field)
    )


def optional_present(row) -> bool:
    return any(
        getattr(row, name) != default for name, default in OPTIONAL_DEFAULTS.items()
    )
