"""Bounded reports and assigned public-content decisions; no evidence payloads."""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class ModerationCase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target_kind = models.CharField(max_length=8)
    target_uuid = models.UUIDField()
    revision_uuid = models.UUIDField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="public_moderation_cases",
    )
    assigned_staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_public_moderation_cases",
        null=True,
    )
    version = models.PositiveBigIntegerField(default=1)
    state = models.CharField(max_length=12, default="open")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["created_at", "id"], name="public_moderation_queue")
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["target_kind", "target_uuid", "revision_uuid"],
                name="public_moderation_target_revision",
            ),
            models.CheckConstraint(
                condition=models.Q(target_kind__in=["profile", "post"]),
                name="public_moderation_target_kind",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="public_moderation_version"
            ),
            models.CheckConstraint(
                condition=models.Q(
                    state__in=["open", "hidden", "dismissed", "restored"]
                ),
                name="public_moderation_state",
            ),
            models.CheckConstraint(
                condition=~models.Q(assigned_staff=models.F("owner")),
                name="public_moderation_nonself",
            ),
        ]


class PublicContentReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(
        ModerationCase, on_delete=models.PROTECT, related_name="reports"
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="public_content_reports",
    )
    reason = models.CharField(max_length=12)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["case", "reporter"], name="public_report_dedup"
            ),
            models.CheckConstraint(
                condition=models.Q(
                    reason__in=["privacy", "unsafe", "misleading", "other"]
                ),
                name="public_report_reason",
            ),
        ]


class PublicContentOperation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    operation_id = models.UUIDField()
    command = models.CharField(max_length=16)
    request_hash = models.CharField(max_length=64)
    result_uuid = models.UUIDField()
    resulting_version = models.PositiveBigIntegerField(default=1)
    resulting_state = models.CharField(max_length=12)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["actor", "operation_id"], name="public_content_operation"
            ),
            models.CheckConstraint(
                condition=models.Q(
                    command__in=["report", "claim", "hide", "dismiss", "restore"]
                ),
                name="public_content_command",
            ),
            models.CheckConstraint(
                condition=models.Q(request_hash__regex=r"^[0-9a-f]{64}$"),
                name="public_content_hash",
            ),
            models.CheckConstraint(
                condition=models.Q(resulting_version__gte=1),
                name="public_content_result_version",
            ),
        ]


class ModerationHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(
        ModerationCase, on_delete=models.PROTECT, related_name="history"
    )
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    operation_id = models.UUIDField()
    action = models.CharField(max_length=12)
    resulting_version = models.PositiveBigIntegerField()
    reason_code = models.CharField(max_length=32)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["actor", "operation_id"],
                name="public_moderation_history_operation",
            ),
            models.CheckConstraint(
                condition=models.Q(action__in=["claim", "hide", "dismiss", "restore"]),
                name="public_moderation_history_action",
            ),
            models.CheckConstraint(
                condition=models.Q(resulting_version__gte=2),
                name="public_moderation_history_version",
            ),
        ]
