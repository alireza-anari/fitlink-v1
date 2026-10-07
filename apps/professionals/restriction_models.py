import uuid

from django.conf import settings
from django.db import models

from apps.governance.audit_models import AppendOnlyQuerySet


class ProfessionalRoleRestriction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        "professionals.ProfessionalRole",
        on_delete=models.PROTECT,
        related_name="restrictions",
    )
    verification = models.ForeignKey(
        "professionals.Verification",
        on_delete=models.PROTECT,
        related_name="role_restrictions",
    )
    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="applied_role_restrictions",
    )
    released_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="released_role_restrictions",
        null=True,
        blank=True,
    )
    reason_code = models.CharField(max_length=32)
    applied_at = models.DateTimeField()
    released_at = models.DateTimeField(null=True, blank=True)
    version = models.PositiveBigIntegerField(default=1)

    class Meta:
        indexes = [
            models.Index(
                fields=["role", "released_at"], name="role_restriction_current"
            )
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(reason_code="role_restricted"),
                name="role_restriction_reason",
            ),
            models.CheckConstraint(
                condition=models.Q(released_at__isnull=True)
                | models.Q(released_at__gte=models.F("applied_at")),
                name="role_restriction_time",
            ),
            models.UniqueConstraint(
                fields=["role"],
                condition=models.Q(released_at__isnull=True),
                name="role_one_live_restriction",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="role_restriction_version"
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(released_at__isnull=True, released_by__isnull=True)
                    | models.Q(released_at__isnull=False, released_by__isnull=False)
                ),
                name="role_restriction_release_pair",
            ),
        ]


class RoleRestrictionHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restriction = models.ForeignKey(
        "professionals.ProfessionalRoleRestriction",
        on_delete=models.PROTECT,
        related_name="history",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="role_restriction_history",
    )
    event = models.CharField(max_length=12)
    reason_code = models.CharField(max_length=32)
    prior_version = models.PositiveBigIntegerField()
    new_version = models.PositiveBigIntegerField()
    at = models.DateTimeField()
    objects = AppendOnlyQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Restriction history is append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Restriction history is append-only")

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    reason_code__in=["role_restricted", "restriction_removed"]
                ),
                name="restriction_history_reason",
            ),
            models.CheckConstraint(
                condition=models.Q(new_version__gt=models.F("prior_version")),
                name="restriction_history_forward",
            ),
            models.CheckConstraint(
                condition=models.Q(event__in=["applied", "released"]),
                name="role_restriction_history_event",
            ),
            models.CheckConstraint(
                condition=models.Q(prior_version__gte=1),
                name="role_restriction_history_prior",
            ),
            models.CheckConstraint(
                condition=models.Q(new_version__gte=1),
                name="role_restriction_history_new",
            ),
        ]
