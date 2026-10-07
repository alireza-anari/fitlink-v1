import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("assets", "0001_private_asset_metadata"),
    ]
    operations = [
        migrations.CreateModel(
            name="ProfessionalProfile",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("state", models.CharField(default="setup", max_length=16)),
                ("version", models.PositiveBigIntegerField(default=1)),
                ("identity_evidence_revision", models.PositiveBigIntegerField(default=1)),
                ("identity_decision_version", models.PositiveBigIntegerField(default=1)),
                ("display_name", models.CharField(blank=True, max_length=120)),
                ("identity_name", models.CharField(blank=True, max_length=120)),
                ("biography", models.CharField(blank=True, max_length=2000)),
                ("specialties", models.JSONField(blank=True, default=list)),
                ("experience_years", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("service_modes", models.JSONField(blank=True, default=list)),
                ("languages", models.JSONField(blank=True, default=list)),
                ("setup_step", models.CharField(default="identity", max_length=32)),
                ("accent_color", models.CharField(blank=True, max_length=7)),
                ("welcome_message", models.CharField(blank=True, max_length=500)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("avatar", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="professional_avatar_profiles", to="assets.asset")),
                ("cover", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="professional_cover_profiles", to="assets.asset")),
                ("logo", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="professional_logo_profiles", to="assets.asset")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="professional_profile", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "constraints": [
                    models.CheckConstraint(condition=models.Q(("state__in", ["setup", "private_ready", "archived"])), name="professional_profile_state"),
                    models.CheckConstraint(condition=models.Q(("version__gte", 1)), name="professional_profile_version"),
                    models.CheckConstraint(condition=models.Q(("identity_evidence_revision__gte", 1)), name="profile_identity_evidence_version"),
                    models.CheckConstraint(condition=models.Q(("identity_decision_version__gte", 1)), name="profile_identity_decision_version"),
                ],
            },
        ),
        migrations.CreateModel(
            name="ProfessionalRole",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("role", models.CharField(max_length=16)),
                ("declared_active", models.BooleanField(default=True)),
                ("version", models.PositiveBigIntegerField(default=1)),
                ("declaration_version", models.PositiveBigIntegerField(default=1)),
                ("evidence_revision", models.PositiveBigIntegerField(default=1)),
                ("decision_version", models.PositiveBigIntegerField(default=1)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="roles", to="professionals.professionalprofile")),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(fields=("profile", "role"), name="profile_role_unique"),
                    models.CheckConstraint(condition=models.Q(("role__in", ["coach", "nutritionist"])), name="professional_role_kind"),
                    models.CheckConstraint(condition=models.Q(("version__gte", 1)), name="professional_role_version"),
                    models.CheckConstraint(condition=models.Q(("declaration_version__gte", 1)), name="role_declaration_version"),
                    models.CheckConstraint(condition=models.Q(("evidence_revision__gte", 1)), name="role_evidence_revision"),
                    models.CheckConstraint(condition=models.Q(("decision_version__gte", 1)), name="role_decision_version"),
                ],
            },
        ),
        migrations.CreateModel(
            name="ProfessionalLocation",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("country_code", models.CharField(default="IR", max_length=2)),
                ("region", models.CharField(max_length=100)),
                ("city", models.CharField(max_length=100)),
                ("modes", models.JSONField(default=list)),
                ("archived_at", models.DateTimeField(blank=True, null=True)),
                ("version", models.PositiveBigIntegerField(default=1)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="locations", to="professionals.professionalprofile")),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(condition=models.Q(("archived_at__isnull", True)), fields=("profile", "country_code", "region", "city"), name="professional_location_fact"),
                    models.CheckConstraint(condition=models.Q(("version__gte", 1)), name="professional_location_version"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Credential",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("category", models.CharField(max_length=16)),
                ("type_code", models.CharField(max_length=64)),
                ("issuer", models.CharField(max_length=160)),
                ("title", models.CharField(max_length=160)),
                ("issued_on", models.DateField(blank=True, null=True)),
                ("expires_on", models.DateField(blank=True, null=True)),
                ("version", models.PositiveBigIntegerField(default=1)),
                ("withdrawn_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="credentials", to="professionals.professionalprofile")),
                ("role", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="credentials", to="professionals.professionalrole")),
            ],
            options={
                "indexes": [models.Index(fields=["profile", "role"], name="credential_profile_role")],
                "constraints": [
                    models.CheckConstraint(condition=models.Q(("version__gte", 1)), name="credential_version"),
                    models.CheckConstraint(condition=models.Q(("category__in", ["identity", "qualification"])), name="credential_category"),
                    models.CheckConstraint(condition=models.Q(models.Q(("category", "identity"), ("role__isnull", True)), models.Q(("category", "qualification"), ("role__isnull", False)), _connector="OR"), name="credential_role_pair"),
                ],
            },
        ),
        migrations.CreateModel(
            name="CredentialRevision",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("sequence", models.PositiveIntegerField()),
                ("category", models.CharField(max_length=16)),
                ("type_code", models.CharField(max_length=64)),
                ("issuer", models.CharField(max_length=160)),
                ("title", models.CharField(max_length=160)),
                ("issued_on", models.DateField(blank=True, null=True)),
                ("expires_on", models.DateField(blank=True, null=True)),
                ("source_sha256", models.CharField(max_length=64)),
                ("revision_hash", models.CharField(max_length=64)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("credential", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="revisions", to="professionals.credential")),
                ("source_asset", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="credential_revisions", to="assets.asset")),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(fields=("credential", "sequence"), name="credential_revision_sequence"),
                    models.CheckConstraint(condition=models.Q(("sequence__gte", 1)), name="credential_revision_positive"),
                    models.CheckConstraint(condition=models.Q(("category__in", ["identity", "qualification"])), name="credential_revision_category"),
                ],
            },
        ),
        migrations.AddField(
            model_name="credential",
            name="current_revision",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="professionals.credentialrevision"),
        ),
        migrations.CreateModel(
            name="Verification",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("sequence", models.PositiveIntegerField()),
                ("state", models.CharField(default="draft", max_length=16)),
                ("version", models.PositiveBigIntegerField(default=1)),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("decided_at", models.DateTimeField(blank=True, null=True)),
                ("snapshot_schema", models.PositiveSmallIntegerField(default=1)),
                ("snapshot_hash", models.CharField(blank=True, max_length=64)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="verifications", to="professionals.professionalprofile")),
            ],
            options={
                "indexes": [
                    models.Index(fields=["profile", "sequence"], name="verification_profile_seq"),
                    models.Index(fields=["state", "submitted_at", "id"], name="verification_staff_queue"),
                ],
                "constraints": [
                    models.UniqueConstraint(fields=("profile", "sequence"), name="verification_sequence_unique"),
                    models.UniqueConstraint(condition=models.Q(("state__in", ["draft", "submitted", "under_review"])), fields=("profile",), name="verification_one_live_bundle"),
                    models.CheckConstraint(condition=models.Q(("sequence__gte", 1)), name="verification_sequence_positive"),
                    models.CheckConstraint(condition=models.Q(("version__gte", 1)), name="verification_version_positive"),
                    models.CheckConstraint(condition=models.Q(("snapshot_schema", 1)), name="verification_snapshot_schema"),
                    models.CheckConstraint(condition=models.Q(("state__in", ["draft", "submitted", "under_review", "decided", "withdrawn"])), name="verification_state"),
                    models.CheckConstraint(condition=models.Q(models.Q(("state", "draft"), ("submitted_at__isnull", True)), models.Q(("state__in", ["submitted", "under_review", "decided", "withdrawn"]), ("submitted_at__isnull", False)), _connector="OR"), name="verification_submit_timestamp"),
                ],
            },
        ),
        migrations.CreateModel(
            name="VerificationTarget",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("target", models.CharField(max_length=16)),
                ("state", models.CharField(default="draft", max_length=16)),
                ("version", models.PositiveBigIntegerField(default=1)),
                ("bound_evidence_revision", models.PositiveBigIntegerField(default=1)),
                ("bound_decision_version", models.PositiveBigIntegerField(default=1)),
                ("bound_declaration_version", models.PositiveBigIntegerField(blank=True, null=True)),
                ("target_snapshot_hash", models.CharField(max_length=64)),
                ("identity_name", models.CharField(blank=True, max_length=120)),
                ("role", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="verification_targets", to="professionals.professionalrole")),
                ("verification", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="targets", to="professionals.verification")),
            ],
            options={
                "indexes": [models.Index(fields=["verification", "target"], name="verification_target_idx")],
                "constraints": [
                    models.UniqueConstraint(fields=("verification", "target"), name="verification_target_unique"),
                    models.CheckConstraint(condition=models.Q(("target__in", ["identity", "coach", "nutritionist"])), name="verification_target_kind"),
                    models.CheckConstraint(condition=models.Q(("state__in", ["draft", "submitted", "under_review", "approved", "rejected", "stale", "withdrawn"])), name="verification_target_state"),
                    models.CheckConstraint(condition=models.Q(("version__gte", 1)), name="verification_target_version"),
                    models.CheckConstraint(condition=models.Q(("bound_evidence_revision__gte", 1)), name="target_evidence_version"),
                    models.CheckConstraint(condition=models.Q(("bound_decision_version__gte", 1)), name="target_decision_version"),
                    models.CheckConstraint(condition=models.Q(models.Q(("bound_declaration_version__isnull", True), ("role__isnull", True), ("target", "identity")), models.Q(models.Q(("bound_declaration_version__isnull", False), ("role__isnull", False), ("target__in", ["coach", "nutritionist"])), ("bound_declaration_version__gte", 1)), _connector="OR"), name="target_role_declaration_pair"),
                ],
            },
        ),
        migrations.CreateModel(
            name="VerificationEvidence",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("category", models.CharField(max_length=16)),
                ("credential_revision", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="verification_evidence", to="professionals.credentialrevision")),
                ("target", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="evidence", to="professionals.verificationtarget")),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(fields=("target", "credential_revision"), name="verification_evidence_unique"),
                    models.CheckConstraint(condition=models.Q(("category__in", ["identity", "qualification"])), name="verification_evidence_category"),
                ],
            },
        ),
        migrations.CreateModel(
            name="VerificationAssignment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("assigned_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("ended_at", models.DateTimeField(blank=True, null=True)),
                ("version", models.PositiveBigIntegerField(default=1)),
                ("assigned_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="issued_professional_verification_assignments", to=settings.AUTH_USER_MODEL)),
                ("assignee", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="professional_verification_assignments", to=settings.AUTH_USER_MODEL)),
                ("verification", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="assignments", to="professionals.verification")),
            ],
            options={
                "indexes": [models.Index(fields=["assignee", "verification"], name="verification_assignee_idx")],
                "constraints": [
                    models.UniqueConstraint(condition=models.Q(("ended_at__isnull", True)), fields=("verification",), name="verification_one_live_assignment"),
                    models.CheckConstraint(condition=models.Q(("version__gte", 1)), name="verification_assignment_version"),
                ],
            },
        ),
        migrations.CreateModel(
            name="VerificationDecision",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("target_kind", models.CharField(max_length=16)),
                ("decision", models.CharField(max_length=12)),
                ("reason_code", models.CharField(max_length=32)),
                ("explanation", models.CharField(blank=True, max_length=1000)),
                ("target_snapshot_hash", models.CharField(max_length=64)),
                ("bound_evidence_revision", models.PositiveBigIntegerField()),
                ("decision_sequence", models.PositiveIntegerField()),
                ("decided_at", models.DateTimeField()),
                ("actor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="professional_verification_decisions", to=settings.AUTH_USER_MODEL)),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="verification_decisions", to="professionals.professionalprofile")),
                ("revoked_approval", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="revocations", to="professionals.verificationdecision")),
                ("supersedes_decision", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="superseded_by", to="professionals.verificationdecision")),
                ("target", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="decisions", to="professionals.verificationtarget")),
            ],
            options={
                "indexes": [models.Index(fields=["target", "decision_sequence"], name="decision_target_seq")],
                "constraints": [
                    models.UniqueConstraint(fields=("profile", "target_kind", "decision_sequence"), name="decision_profile_target_sequence"),
                    models.UniqueConstraint(condition=models.Q(("decision__in", ["approve", "reject", "stale", "withdraw"])), fields=("target",), name="decision_one_terminal_target"),
                    models.UniqueConstraint(condition=models.Q(("decision", "revoke")), fields=("revoked_approval",), name="decision_one_revoke_per_approval"),
                    models.CheckConstraint(condition=models.Q(("target_kind__in", ["identity", "coach", "nutritionist"])), name="decision_target_kind"),
                    models.CheckConstraint(condition=models.Q(("decision__in", ["approve", "reject", "revoke", "stale", "withdraw"])), name="verification_decision_kind"),
                    models.CheckConstraint(condition=models.Q(("bound_evidence_revision__gte", 1)), name="decision_evidence_version"),
                    models.CheckConstraint(condition=models.Q(("decision_sequence__gte", 1)), name="decision_sequence_positive"),
                    models.CheckConstraint(condition=models.Q(models.Q(("decision", "revoke"), ("revoked_approval__isnull", False)), models.Q(models.Q(("decision", "revoke"), _negated=True), ("revoked_approval__isnull", True)), _connector="OR"), name="decision_revoke_approval_pair"),
                ],
            },
        ),
        migrations.CreateModel(
            name="VerificationHistory",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("event", models.CharField(max_length=24)),
                ("reason_code", models.CharField(max_length=32)),
                ("prior_version", models.PositiveBigIntegerField()),
                ("new_version", models.PositiveBigIntegerField()),
                ("at", models.DateTimeField()),
                ("actor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="professional_verification_history", to=settings.AUTH_USER_MODEL)),
                ("target", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="history", to="professionals.verificationtarget")),
                ("verification", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="history", to="professionals.verification")),
            ],
            options={
                "constraints": [
                    models.CheckConstraint(condition=models.Q(("event__in", ["submit", "assign", "start_review", "reassign", "decision", "target_stale", "target_withdraw"])), name="verification_history_event"),
                    models.CheckConstraint(condition=models.Q(("prior_version__gte", 1)), name="verification_history_prior"),
                    models.CheckConstraint(condition=models.Q(("new_version__gte", 1)), name="verification_history_new"),
                ],
            },
        ),
        migrations.CreateModel(
            name="ProfessionalRoleRestriction",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("reason_code", models.CharField(max_length=32)),
                ("applied_at", models.DateTimeField()),
                ("released_at", models.DateTimeField(blank=True, null=True)),
                ("version", models.PositiveBigIntegerField(default=1)),
                ("applied_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="applied_role_restrictions", to=settings.AUTH_USER_MODEL)),
                ("released_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="released_role_restrictions", to=settings.AUTH_USER_MODEL)),
                ("role", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="restrictions", to="professionals.professionalrole")),
                ("verification", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="role_restrictions", to="professionals.verification")),
            ],
            options={
                "indexes": [models.Index(fields=["role", "released_at"], name="role_restriction_current")],
                "constraints": [
                    models.UniqueConstraint(condition=models.Q(("released_at__isnull", True)), fields=("role",), name="role_one_live_restriction"),
                    models.CheckConstraint(condition=models.Q(("version__gte", 1)), name="role_restriction_version"),
                    models.CheckConstraint(condition=models.Q(models.Q(("released_at__isnull", True), ("released_by__isnull", True)), models.Q(("released_at__isnull", False), ("released_by__isnull", False)), _connector="OR"), name="role_restriction_release_pair"),
                ],
            },
        ),
        migrations.CreateModel(
            name="RoleRestrictionHistory",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("event", models.CharField(max_length=12)),
                ("reason_code", models.CharField(max_length=32)),
                ("prior_version", models.PositiveBigIntegerField()),
                ("new_version", models.PositiveBigIntegerField()),
                ("at", models.DateTimeField()),
                ("actor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="role_restriction_history", to=settings.AUTH_USER_MODEL)),
                ("restriction", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="history", to="professionals.professionalrolerestriction")),
            ],
            options={
                "constraints": [
                    models.CheckConstraint(condition=models.Q(("event__in", ["applied", "released"])), name="role_restriction_history_event"),
                    models.CheckConstraint(condition=models.Q(("prior_version__gte", 1)), name="role_restriction_history_prior"),
                    models.CheckConstraint(condition=models.Q(("new_version__gte", 1)), name="role_restriction_history_new"),
                ],
            },
        ),
        migrations.CreateModel(
            name="AssistantMembership",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("role", models.CharField(default="client_support", max_length=20)),
                ("state", models.CharField(default="defined", max_length=12)),
                ("version", models.PositiveBigIntegerField(default=1)),
                ("defined_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("assistant", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="assistant_definitions", to=settings.AUTH_USER_MODEL)),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="assistant_definitions", to="professionals.professionalprofile")),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(condition=models.Q(("state", "defined")), fields=("profile", "assistant"), name="assistant_membership_live"),
                    models.CheckConstraint(condition=models.Q(("role", "client_support")), name="assistant_fixed_role"),
                    models.CheckConstraint(condition=models.Q(("state__in", ["defined", "revoked"])), name="assistant_membership_state"),
                    models.CheckConstraint(condition=models.Q(("version__gte", 1)), name="assistant_membership_version"),
                ],
            },
        ),
        migrations.CreateModel(
            name="ProfileCommandReceipt",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("operation_id", models.UUIDField()),
                ("command", models.CharField(max_length=64)),
                ("request_hash", models.CharField(max_length=64)),
                ("object_uuid", models.UUIDField(blank=True, null=True)),
                ("result_uuid", models.UUIDField(blank=True, null=True)),
                ("resulting_version", models.PositiveBigIntegerField(default=1)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="professional_profile_receipts", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(fields=("owner", "operation_id"), name="professional_receipt_operation"),
                    models.CheckConstraint(condition=models.Q(("resulting_version__gte", 1)), name="professional_receipt_version"),
                ],
            },
        ),
    ]
