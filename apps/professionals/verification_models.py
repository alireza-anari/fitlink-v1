import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.governance.audit_models import AppendOnlyQuerySet


class Verification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.PROTECT,
        related_name="verifications",
    )
    sequence = models.PositiveIntegerField()
    state = models.CharField(max_length=16, default="draft")
    version = models.PositiveBigIntegerField(default=1)
    submitted_at = models.DateTimeField(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    snapshot_schema = models.PositiveSmallIntegerField(default=1)
    snapshot_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["profile", "sequence"], name="verification_profile_seq"),
            models.Index(
                fields=["state", "submitted_at", "id"], name="verification_staff_queue"
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "sequence"], name="verification_sequence_unique"
            ),
            models.UniqueConstraint(
                fields=["profile"],
                condition=models.Q(state__in=["draft", "submitted", "under_review"]),
                name="verification_one_live_bundle",
            ),
            models.CheckConstraint(
                condition=models.Q(sequence__gte=1), name="verification_sequence_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="verification_version_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(snapshot_schema=1), name="verification_snapshot_schema"
            ),
            models.CheckConstraint(
                condition=models.Q(
                    state__in=[
                        "draft",
                        "submitted",
                        "under_review",
                        "decided",
                        "withdrawn",
                    ]
                ),
                name="verification_state",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(state="draft", submitted_at__isnull=True)
                    | models.Q(
                        state__in=["submitted", "under_review", "decided", "withdrawn"],
                        submitted_at__isnull=False,
                    )
                ),
                name="verification_submit_timestamp",
            ),
        ]


class VerificationTarget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    verification = models.ForeignKey(
        "professionals.Verification",
        on_delete=models.PROTECT,
        related_name="targets",
    )
    target = models.CharField(max_length=16)
    role = models.ForeignKey(
        "professionals.ProfessionalRole",
        on_delete=models.PROTECT,
        related_name="verification_targets",
        null=True,
        blank=True,
    )
    state = models.CharField(max_length=16, default="draft")
    version = models.PositiveBigIntegerField(default=1)
    bound_evidence_revision = models.PositiveBigIntegerField(default=1)
    bound_decision_version = models.PositiveBigIntegerField(default=1)
    bound_declaration_version = models.PositiveBigIntegerField(null=True, blank=True)
    target_snapshot_hash = models.CharField(max_length=64)
    identity_name = models.CharField(max_length=120, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["verification", "target"], name="verification_target_idx")
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["verification", "target"], name="verification_target_unique"
            ),
            models.CheckConstraint(
                condition=models.Q(target__in=["identity", "coach", "nutritionist"]),
                name="verification_target_kind",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    state__in=[
                        "draft",
                        "submitted",
                        "under_review",
                        "approved",
                        "rejected",
                        "stale",
                        "withdrawn",
                    ]
                ),
                name="verification_target_state",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="verification_target_version"
            ),
            models.CheckConstraint(
                condition=models.Q(bound_evidence_revision__gte=1),
                name="target_evidence_version",
            ),
            models.CheckConstraint(
                condition=models.Q(bound_decision_version__gte=1),
                name="target_decision_version",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        target="identity",
                        role__isnull=True,
                        bound_declaration_version__isnull=True,
                    )
                    | (
                        models.Q(
                            target__in=["coach", "nutritionist"],
                            role__isnull=False,
                            bound_declaration_version__isnull=False,
                        )
                        & models.Q(bound_declaration_version__gte=1)
                    )
                ),
                name="target_role_declaration_pair",
            ),
        ]


class VerificationEvidence(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target = models.ForeignKey(
        "professionals.VerificationTarget",
        on_delete=models.PROTECT,
        related_name="evidence",
    )
    credential_revision = models.ForeignKey(
        "professionals.CredentialRevision",
        on_delete=models.PROTECT,
        related_name="verification_evidence",
    )
    category = models.CharField(max_length=16)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["target", "credential_revision"],
                name="verification_evidence_unique",
            ),
            models.CheckConstraint(
                condition=models.Q(category__in=["identity", "qualification"]),
                name="verification_evidence_category",
            ),
        ]


class VerificationAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    verification = models.ForeignKey(
        "professionals.Verification",
        on_delete=models.PROTECT,
        related_name="assignments",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="professional_verification_assignments",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="issued_professional_verification_assignments",
    )
    assigned_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    version = models.PositiveBigIntegerField(default=1)

    class Meta:
        indexes = [
            models.Index(
                fields=["assignee", "verification"], name="verification_assignee_idx"
            )
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["verification"],
                condition=models.Q(ended_at__isnull=True),
                name="verification_one_live_assignment",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="verification_assignment_version"
            ),
        ]


class VerificationDecision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target = models.ForeignKey(
        "professionals.VerificationTarget",
        on_delete=models.PROTECT,
        related_name="decisions",
    )
    profile = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.PROTECT,
        related_name="verification_decisions",
    )
    target_kind = models.CharField(max_length=16)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="professional_verification_decisions",
    )
    decision = models.CharField(max_length=12)
    reason_code = models.CharField(max_length=32)
    explanation = models.CharField(max_length=1000, blank=True)
    target_snapshot_hash = models.CharField(max_length=64)
    bound_evidence_revision = models.PositiveBigIntegerField()
    decision_sequence = models.PositiveIntegerField()
    supersedes_decision = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="superseded_by",
        null=True,
        blank=True,
    )
    revoked_approval = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="revocations",
        null=True,
        blank=True,
    )
    decided_at = models.DateTimeField()
    objects = AppendOnlyQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Verification decisions are append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Verification decisions are append-only")

    class Meta:
        indexes = [
            models.Index(fields=["target", "decision_sequence"], name="decision_target_seq")
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "target_kind", "decision_sequence"],
                name="decision_profile_target_sequence",
            ),
            models.UniqueConstraint(
                fields=["target"],
                condition=models.Q(decision__in=["approve", "reject", "stale", "withdraw"]),
                name="decision_one_terminal_target",
            ),
            models.UniqueConstraint(
                fields=["revoked_approval"],
                condition=models.Q(decision="revoke"),
                name="decision_one_revoke_per_approval",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    target_kind__in=["identity", "coach", "nutritionist"]
                ),
                name="decision_target_kind",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    decision__in=["approve", "reject", "revoke", "stale", "withdraw"]
                ),
                name="verification_decision_kind",
            ),
            models.CheckConstraint(
                condition=models.Q(bound_evidence_revision__gte=1),
                name="decision_evidence_version",
            ),
            models.CheckConstraint(
                condition=models.Q(decision_sequence__gte=1),
                name="decision_sequence_positive",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(decision="revoke", revoked_approval__isnull=False)
                    | (
                        ~models.Q(decision="revoke")
                        & models.Q(revoked_approval__isnull=True)
                    )
                ),
                name="decision_revoke_approval_pair",
            ),
        ]


class VerificationHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    verification = models.ForeignKey(
        "professionals.Verification",
        on_delete=models.PROTECT,
        related_name="history",
    )
    target = models.ForeignKey(
        "professionals.VerificationTarget",
        on_delete=models.PROTECT,
        related_name="history",
        null=True,
        blank=True,
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="professional_verification_history",
    )
    event = models.CharField(max_length=24)
    reason_code = models.CharField(max_length=32)
    prior_version = models.PositiveBigIntegerField()
    new_version = models.PositiveBigIntegerField()
    at = models.DateTimeField()
    objects = AppendOnlyQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Verification history is append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Verification history is append-only")

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    event__in=[
                        "submit",
                        "assign",
                        "start_review",
                        "reassign",
                        "decision",
                        "target_stale",
                        "target_withdraw",
                    ]
                ),
                name="verification_history_event",
            ),
            models.CheckConstraint(
                condition=models.Q(prior_version__gte=1),
                name="verification_history_prior",
            ),
            models.CheckConstraint(
                condition=models.Q(new_version__gte=1),
                name="verification_history_new",
            ),
        ]
