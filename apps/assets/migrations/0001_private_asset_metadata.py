import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Asset",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("subject_kind", models.CharField(max_length=32)),
                ("subject_uuid", models.UUIDField()),
                ("purpose", models.CharField(max_length=32)),
                ("source_key", models.CharField(blank=True, max_length=255)),
                ("classification", models.CharField(default="private_source", max_length=24)),
                ("state", models.CharField(default="pending_upload", max_length=20)),
                ("version", models.PositiveBigIntegerField(default=1)),
                ("declared_size", models.PositiveBigIntegerField(default=0)),
                ("declared_type", models.CharField(blank=True, max_length=64)),
                ("actual_size", models.PositiveBigIntegerField(blank=True, null=True)),
                ("detected_type", models.CharField(blank=True, max_length=64)),
                ("sha256", models.CharField(blank=True, max_length=64)),
                ("processing_version", models.PositiveBigIntegerField(default=1)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("upload_expires_at", models.DateTimeField()),
                ("accepted_at", models.DateTimeField(blank=True, null=True)),
                ("finalized_at", models.DateTimeField(blank=True, null=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("rejection_code", models.CharField(blank=True, max_length=32)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="private_assets", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "indexes": [
                    models.Index(fields=["owner", "state", "created_at"], name="asset_owner_state"),
                    models.Index(fields=["state", "upload_expires_at"], name="asset_state_expiry"),
                ],
                "constraints": [
                    models.CheckConstraint(condition=models.Q(("version__gte", 1)), name="asset_version"),
                    models.CheckConstraint(condition=models.Q(("processing_version__gte", 1)), name="asset_processing_version"),
                    models.CheckConstraint(condition=models.Q(("purpose__in", ["identity_evidence", "credential_evidence", "avatar", "cover", "logo"])), name="asset_c03_purpose"),
                    models.CheckConstraint(condition=models.Q(("classification__in", ["private_source", "private_derivative"])), name="asset_private_class"),
                    models.CheckConstraint(condition=models.Q(("state__in", ["pending_upload", "receiving", "quarantined", "processing", "ready", "rejected", "abandoned", "revoked", "deletion_pending", "deleted"])), name="asset_state"),
                ],
            },
        ),
        migrations.CreateModel(
            name="AssetDerivative",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("processing_version", models.PositiveBigIntegerField()),
                ("purpose", models.CharField(max_length=24)),
                ("key", models.CharField(max_length=255)),
                ("sha256", models.CharField(max_length=64)),
                ("width", models.PositiveIntegerField()),
                ("height", models.PositiveIntegerField()),
                ("mime_type", models.CharField(max_length=16)),
                ("state", models.CharField(default="pending", max_length=12)),
                ("version", models.PositiveBigIntegerField(default=1)),
                ("asset", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="derivatives", to="assets.asset")),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(fields=("asset", "processing_version", "purpose"), name="asset_derivative_effect"),
                    models.CheckConstraint(condition=models.Q(("processing_version__gte", 1)), name="derivative_processing_version"),
                    models.CheckConstraint(condition=models.Q(("version__gte", 1)), name="derivative_version"),
                    models.CheckConstraint(condition=models.Q(("purpose__in", ["owner_preview", "evidence_preview"])), name="derivative_purpose"),
                    models.CheckConstraint(condition=models.Q(("mime_type__in", ["image/jpeg", "image/png"])), name="derivative_mime"),
                    models.CheckConstraint(condition=models.Q(("state__in", ["pending", "ready", "revoked", "deleted"])), name="derivative_state"),
                ],
            },
        ),
        migrations.CreateModel(
            name="AssetProcessingAttempt",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("processing_version", models.PositiveBigIntegerField()),
                ("lease_uuid", models.UUIDField(blank=True, null=True)),
                ("lease_until", models.DateTimeField(blank=True, null=True)),
                ("attempt", models.PositiveSmallIntegerField(default=1)),
                ("state", models.CharField(default="pending", max_length=12)),
                ("scanner_engine", models.CharField(blank=True, max_length=64)),
                ("scanner_signature", models.CharField(blank=True, max_length=128)),
                ("failure_code", models.CharField(blank=True, max_length=32)),
                ("asset", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="processing_attempts", to="assets.asset")),
            ],
            options={
                "indexes": [models.Index(fields=["state", "lease_until"], name="asset_attempt_lease")],
                "constraints": [
                    models.UniqueConstraint(fields=("asset", "processing_version", "attempt"), name="asset_processing_attempt_unique"),
                    models.CheckConstraint(condition=models.Q(("processing_version__gte", 1)), name="attempt_processing_version"),
                    models.CheckConstraint(condition=models.Q(("attempt__gte", 1)), name="attempt_positive"),
                    models.CheckConstraint(condition=models.Q(("state__in", ["pending", "running", "ready", "failed"])), name="attempt_state"),
                    models.CheckConstraint(condition=models.Q(models.Q(("lease_uuid__isnull", True), ("lease_until__isnull", True)), models.Q(("lease_uuid__isnull", False), ("lease_until__isnull", False)), _connector="OR"), name="attempt_lease_pair"),
                ],
            },
        ),
    ]
