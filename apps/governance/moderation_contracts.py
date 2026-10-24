"""C04 public content metadata only; no evidence or dispute payloads."""

import json
from dataclasses import dataclass, field
from uuid import UUID

REPORT_REASONS = frozenset({"privacy", "unsafe", "misleading", "other"})
MODERATION_ACTIONS = frozenset({"hide", "dismiss", "restore"})


@dataclass(frozen=True)
class PublicReportTarget:
    kind: str
    object_uuid: UUID

    def __post_init__(self):
        if (
            not isinstance(self.kind, str)
            or self.kind not in {"profile", "post"}
            or not isinstance(self.object_uuid, UUID)
        ):
            raise ValueError("Invalid public report target")


@dataclass(frozen=True)
class ReportReceipt:
    receipt_id: UUID


@dataclass(frozen=True)
class ModerationDTO:
    id: UUID
    version: int
    state: str


@dataclass(frozen=True)
class ModerationPage:
    cases: tuple[ModerationDTO, ...]
    cursor: str | None


@dataclass(frozen=True)
class ModerationView:
    id: UUID
    version: int
    state: str
    target: PublicReportTarget
    revision_uuid: UUID
    reasons: tuple[str, ...]
    content_json: str | None = field(repr=False)

    @property
    def content(self):
        return json.loads(self.content_json) if self.content_json is not None else None


def validate_report_command(target, reason, operation_id):
    if not isinstance(target, PublicReportTarget):
        raise ValueError("Invalid report command")
    target.__post_init__()
    if (
        not isinstance(reason, str)
        or reason not in REPORT_REASONS
        or not isinstance(operation_id, UUID)
    ):
        raise ValueError("Invalid report command")


def validate_decision_command(
    case_uuid, expected_version, action, step_up_id, operation_id
):
    if (
        not all(isinstance(v, UUID) for v in (case_uuid, step_up_id, operation_id))
        or type(expected_version) is not int
        or not 1 <= expected_version <= 9_223_372_036_854_775_807
        or not isinstance(action, str)
        or action not in MODERATION_ACTIONS
    ):
        raise ValueError("Invalid moderation command")
