import uuid

from django.db import models
from django.utils import timezone

EVENT_TYPES = (
    "account.security_changed",
    "consent.granted",
    "consent.revoked",
    "privacy.intake_recorded",
    "feature_flag.changed",
    "athlete.baseline_changed",
    "professional.profile_changed",
    "verification.changed",
    "asset.processing_requested",
    "asset.cleanup_requested",
    "assistant.membership_changed",
)


class OutboxPayloadAllowed(models.Func):
    function = "fitlink_valid_outbox_payload"
    output_field = models.BooleanField()


class OutboxEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=32)
    schema_version = models.PositiveSmallIntegerField(default=1)
    aggregate_uuid = models.UUIDField()
    aggregate_version = models.PositiveBigIntegerField()
    payload = models.JSONField(default=dict)
    dedup_key = models.CharField(max_length=160, unique=True)
    state = models.CharField(max_length=9, default="pending")
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    available_at = models.DateTimeField(default=timezone.now)
    lease_until = models.DateTimeField(null=True)
    lease_uuid = models.UUIDField(null=True)
    dispatched_at = models.DateTimeField(null=True)
    exhausted_at = models.DateTimeField(null=True)
    last_error_code = models.CharField(max_length=32, blank=True)

    def save(self, *args, **kwargs):
        from .outbox import validate_event

        validate_event(
            self.event_type,
            self.aggregate_uuid,
            self.aggregate_version,
            self.payload,
            self.dedup_key,
        )
        return super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(
                fields=["state", "available_at", "lease_until"], name="outbox_due_lease"
            )
        ]
        constraints = [
            models.CheckConstraint(
                condition=OutboxPayloadAllowed("event_type", "payload"),
                name="outbox_payload_id_only",
            ),
            models.CheckConstraint(
                condition=models.Q(event_type__in=EVENT_TYPES), name="outbox_type"
            ),
            models.CheckConstraint(
                condition=models.Q(schema_version=1), name="outbox_schema_version"
            ),
            models.CheckConstraint(
                condition=models.Q(aggregate_version__gte=1),
                name="outbox_aggregate_version",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    state__in=["pending", "leased", "sent", "exhausted"]
                ),
                name="outbox_state",
            ),
            models.CheckConstraint(
                condition=models.Q(attempts__lte=8), name="outbox_attempt_bound"
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(lease_uuid__isnull=True, lease_until__isnull=True)
                    | models.Q(lease_uuid__isnull=False, lease_until__isnull=False)
                ),
                name="outbox_lease_pair",
            ),
        ]


class OutboxDeliveryReceipt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        OutboxEvent, on_delete=models.PROTECT, related_name="receipts"
    )
    handler = models.CharField(max_length=32)
    effect_key = models.CharField(max_length=120)
    result = models.CharField(max_length=7)
    completed_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["handler", "effect_key"], name="outbox_durable_effect"
            ),
            models.UniqueConstraint(
                fields=["event", "handler"], name="outbox_event_handler"
            ),
            models.CheckConstraint(
                condition=models.Q(result__in=["applied", "skipped"]),
                name="outbox_receipt_result",
            ),
        ]
