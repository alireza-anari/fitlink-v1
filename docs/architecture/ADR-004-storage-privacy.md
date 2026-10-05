# ADR-004: Private assets, purpose-limited consent and controlled public copies

Date: 2026-10-03. Status: Accepted; amended by locked Stage 2 archive/deletion policies. Numeric retention periods remain an operational release gate.

## Context

Health declarations, photos, credentials, chat attachments and dispute evidence must remain private while professional public profiles/case studies need deliberate publication. Sharing with a professional, external AI processing and public publication have different purposes. Disconnection and revocation must affect reports, links, workers and derived views.

## Decision

Use S3-compatible storage behind Django storage/asset services; MinIO may support local development. PostgreSQL Asset metadata and domain consent/policies are authoritative. Uploads start private in quarantine; verify size/type/checksum, scan and sanitize derivatives before use. Restrict types/sizes and isolate untrusted download origin. Owner/purpose/subject validation prevents binding another person's file.

Private delivery requires current object authorization; authenticated streaming or at most 60-second signed URLs, never permanent public URLs. High-risk immediate revocation uses proxy delivery. Signed URLs may remain usable until expiry; do not assert otherwise. Private responses are no-store. Public media are separate sanitized copies explicitly released by public-profile or case-study workflows, never a source-file/bucket-wide public toggle.

Athlete Consent specifies grantee, purpose, data objects/categories, version/content hash, time and revocation/expiry. Separate storing health, private professional sharing, external AI processing, Mirror summary sharing and case-study publication. Relationship membership alone cannot read sensitive data; assistants get no sensitive grant under the V1 limited role. Case-study changes require new explicit approval. Revocation removes controlled public copies and future access; downloaded public copies cannot be recalled.

End operational access immediately; permit only read-only ArchiveManifest records for services actually delivered by that professional: their delivered plan revisions/final summaries/notes/completed appointments and finalized reports. No future data, live athlete profile/timeline, new report generation or automatic chat archive. Athlete-derived/sensitive parts require current archive consent; revoke/redact normal visibility without destroying restricted integrity evidence. Held evidence remains staff-only, separate from ordinary archive.

Deletion is a verified request → immediate normal-access restriction → pending deletion → hold/retention evaluation → deletion/anonymization → completion workflow, with partially held records resumed on release. Central configurable RetentionPolicy replaces scattered durations. RecordHold temporarily isolates affected dispute/fraud/security/required-audit records; no global blanket hold or ordinary access. Inventory all derivatives/provider outputs and audit completion/exceptions. Backups age out under infrastructure policy; retain erasure markers beyond restorable backup lifetime, replay them offline on restore and verify before traffic. Actual periods/legal basis need release sign-off, not redesign of this locked workflow.

## Alternatives rejected

- Public S3 keys for all files: bypasses relationship/consent and exposes irreversible copies.
- One boolean `is_private`: cannot distinguish storage, named sharing, public publication and provider processing.
- Permanent cached exports: carry revoked sensitive material beyond source rights.
- Deleting all relationships on Pro expiry: explicitly forbidden; entitlements and ownership are separate.
- Unsafe cascade deletion or unlimited retention: replaced by configurable durations, affected-record holds, anonymization and completion evidence.

## Consequences and validation

Erasure/revocation touches projections, jobs, sockets and derivatives; maintain access-context version and inventories. Test unrelated UUID downloads, scan quarantine, revoked photos in old reports, public-copy withdrawal and restore-safe erasure. Offline workout records are minimal account-scoped browser data with logout clearing; no offline photo/health cache. Upload guidance: [Django security documentation](https://docs.djangoproject.com/en/5.2/topics/security/).
