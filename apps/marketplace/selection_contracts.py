"""Private selection scopes and finite current-output command contracts."""

import re
from dataclasses import dataclass, field
from uuid import UUID

from apps.accounts.sessions import AccountActor


class SelectionConflict(ValueError):
    pass


@dataclass(frozen=True)
class ComparisonScope:
    actor: AccountActor | None = field(default=None, repr=False)
    session_key: str | None = field(default=None, repr=False)
    session_digest: str | None = field(default=None, repr=False)
    key_id: str | None = field(default=None, repr=False)

    def __post_init__(self):
        if self.actor is not None:
            if not isinstance(self.actor, AccountActor) or any(
                v is not None
                for v in (self.session_key, self.session_digest, self.key_id)
            ):
                raise ValueError("Invalid comparison scope")
        elif (
            not isinstance(self.session_key, str)
            or not re.fullmatch(r"[a-z0-9]{32}", self.session_key)
            or not isinstance(self.session_digest, str)
            or not re.fullmatch(r"[0-9a-f]{64}", self.session_digest)
            or not isinstance(self.key_id, str)
            or not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", self.key_id)
        ):
            raise ValueError("Invalid comparison scope")


@dataclass(frozen=True)
class FavoriteDTO:
    selected: bool


@dataclass(frozen=True)
class ComparisonDTO:
    version: int
    items: tuple


def validate_favorite(identifier, selected, operation):
    if (
        not isinstance(identifier, UUID)
        or type(selected) is not bool
        or not isinstance(operation, UUID)
    ):
        raise ValueError("Invalid favorite command")


def validate_comparison_command(command, identifier, version, operation):
    if (
        command not in ("add", "remove", "clear")
        or (command == "clear" and identifier is not None)
        or (command != "clear" and not isinstance(identifier, UUID))
        or type(version) is not int
        or not 1 <= version <= 9223372036854775807
        or not isinstance(operation, UUID)
    ):
        raise ValueError("Invalid comparison command")
