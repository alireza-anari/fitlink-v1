# FitLink C03 Profiles and Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for sequential execution after separate authorization. Steps use checkbox syntax. This document authorizes no execution, subagents, merge, deployment or C04 work.

**Goal:** Provide resumable private athlete baseline and professional setup, safe private evidence/media, and bounded staff verification that establishes future publication eligibility without publishing anything.

**Architecture:** Add athletes and professionals to the existing modular Django monolith. Reuse current AccountActor/session authorization, governance evidence/outbox/consent/retention and C01 private storage; composition under config wires validated cross-domain subjects and effects. Profiles, declarations, verification, publication eligibility and later relationship authority remain separate facts.

**Tech Stack:** Existing Python 3.13/Django 5.2 LTS/DRF/PostgreSQL/Redis/Celery/Beat/Channels/S3-compatible storage; Django Templates/Tailwind/Vanilla ES Modules, Persian RTL. Pillow image processing and a private ClamAV scanner are proposed bounded additions, reviewed and pinned only during authorized execution.

**Spec:** Current planning mandate supplied in Pasted text(2).txt; docs/product/V1_PRODUCT_SPEC.md; docs/architecture/DOMAIN_MODEL.md; docs/architecture/PERMISSIONS_MATRIX.md; the architecture, five ADRs, roadmap and C02 handoff listed below.

## Global Constraints

- Planning only on profiles/c03-plan; no production code, tests, models, migrations, dependencies or routes are created by this planning commit.
- Do not modify main, foundation/c01-cloud or accounts/c02-cloud; do not merge, deploy or begin C04.
- One permanent accounts.User, browser Session + CSRF, current account state/auth_version; no JWT or browser bearer credentials.
- Athlete profiles remain private; professional preview remains authenticated and owner-only, including after verification in C03.
- Verification controls publication eligibility only. Actual publication, public copies, search, indexes, SEO and Marketplace belong to C04.
- Credentials and identity evidence remain private even after approval; no external AI transfer, public document URL, raw content or signed URL in logs/audit/outbox.
- No generic authorization/ACL/workflow framework, file manager, account directory or generic model CRUD.
- No future-domain imports, fabricated UI/data, forced ref updates, destructive migrations or weakened C02 gates.
- Every implementation task requires observed behavioral RED, minimal implementation, observed GREEN and regression evidence; collection and source inspection are not execution evidence.

## Review Focus

1. Optional answers omitted or consent declined must remain unknown/declined, never empty health history or failed onboarding; pin in Task 3.
2. A user switching between athlete/professional contexts must never blend permissions or preview another workspace; pin in Tasks 2, 10 and 12.
3. A file arriving after abandon/replacement/expiry must never become usable or delete a held predecessor; pin in Tasks 4, 5 and 9.
4. Credential expiry or a bound edit during staff review must prevent a stale approval even when an old snapshot is readable; pin in Tasks 6–8.
5. A restarted worker or interrupted wizard must preserve committed work, resume safely and expose bounded failure states; pin in Tasks 3, 5, 11 and 13.

---

## 1. Baseline, source authority and inspection record

| Fact | Immutable evidence |
|---|---|
| Repository | alireza-anari/fitlink-v1 |
| Completed C02 branch | accounts/c02-cloud |
| C02 final head | 0905be6c6ca608d469fe33e87f514b22591132d1 |
| C02 final tree | ed788191bb6f5011e6b35a63823ae8183af7b53d |
| Verified implementation parent | 935494eda888cdcfd7dffaac4c519f083cda9595 |
| Implementation tree | a3b8aa9b01ad09e38049c445b8e9697818b92ed5 |
| Verified implementation CI | 37486370317, completed success on 935494e; final 0905be6 is the handoff documentation commit |
| Protected main | 8ede9a451db6103f4e3ebf65784ee9f16b96feb2 |
| Protected Foundation | 75c551e5b9bbbfb7777ee52b09a1993b681e921a |
| Planning branch starting point | profiles/c03-plan from exactly 0905be6, not the implementation parent or current main |

Remote branch, Git commit/tree, recursive tree and CI run were inspected through authenticated GitHub API on 2026-10-06. This planning workspace has no existing Git checkout; the inspected files are a read-only source snapshot at the exact SHA, not a recovered C02 implementation workspace. Publishing uses the authenticated API. No synthetic local ancestry is to be pushed.

Read completely: docs/product/V1_PRODUCT_SPEC.md and OPEN_QUESTIONS_AND_RISKS.md; docs/architecture/V1_ARCHITECTURE.md, DOMAIN_MODEL.md, PERMISSIONS_MATRIX.md and ADR-001 through ADR-005; docs/implementation/V1_IMPLEMENTATION_ROADMAP.md, C02_HANDOFF.md, C02_EXECUTION_LEDGER.md and C02_SETUP.md. The ledger's final verified exit supersedes historical incomplete states; Tasks 1–16 are complete. Its daily recovery-quota reconciliation, metadata-only holds, confirmation default-deny and production provider limitations remain binding.

Precedence: (1) this user's current locked C03 scope/security rulings; (2) locked Stage 2 product/permissions/ADR decisions; (3) domain/architecture and roadmap stage allocation; (4) verified C02 handoff/ledger contracts; (5) implementation evidence and explicitly labeled engineering decisions here. Conceptual names are not existing schemas. Earlier prose allowing deliberately public credential copies does not authorize any in C03; current source-evidence privacy rules prevail. Product-wide baseline fields are allocated across C03 setup and C09 completion, not silently removed from V1.

## 2. Goal, non-goals and domain boundaries

C03 completes independent private setup, optional dual profiles, declared roles, baseline branding, broad locations, private credentials/media, owner preview, staff assignment/review/history, an inert assistant role primitive and a publication-eligibility reader for C04. Existing private-workspace support is a profile foundation; no coaching services exist yet.

Athletes owns AthleteProfile and dated BaselineAssessment setup snapshots. Professionals owns ProfessionalProfile, ProfessionalRole, Credential revisions, Verification bundles/decisions, locations and AssistantMembership metadata. Assets owns private metadata, quarantine, derivative processing and authorized delivery. Governance owns consent/audit/outbox/retention/hold infrastructure, not professional decisions. Config composition supplies explicit domain validators and effects; governance/assets never import athletes/professionals.

Deferred: C04 public pages/projections/copies/search/FTS/trigram/ranking/SEO/cards/favorites/comparison/posts; C05+ packages/prices/intake/CRM/relationships/capacity/subscriptions/workouts/nutrition/messaging/appointments/reviews/AI; C09 HealthLimitationsProfile/HealthDeclaration, health documents, medications/allergies/injuries, body/daily tracking, goals/milestones, photo gallery/progress photographs and sharing UX. No professional athlete-data reader or consent-grant-to-professional endpoint exists in C03. No public athlete slug/route/index/media class exists.

## 3. Existing surfaces to reuse and bounded gaps

| Existing files/surface | Reuse and required bounded extension |
|---|---|
| apps/accounts/models.py, managers.py, migrations/0001_initial.py | Permanent User/public_id/phone/adult fields; no alteration or replacement; optional profiles use protected one-to-one FKs |
| apps/accounts/sessions.py | AccountActor, actor_user(actor, action, at), locked_actor; current session-control expiry/revocation/auth_version on every command/read |
| apps/accounts/policies.py | Current active/adult/normal scope; NORMAL_ACTIONS is a closed C02 allowlist. Add explicit C03 action names in Task 2, never wildcard acceptance or role-derived account authority |
| apps/accounts/state.py, config/account_middleware.py | Existing state/auth invalidation remains authoritative. New selectors deny immediately from User state; no accounts-to-profile imports |
| config/authentication.py, permissions.py, api_security.py | AccountSessionAuthentication/AccountActionPermission, CSRF ordering, generic 403/404/409/503 and no-store; no stock is_staff permissions |
| apps/governance/staff.py, staff_models.py | require_staff, StaffCapabilityGrant and case/auth-version-bound StaffStepUpGrant; add professional_verification capability via additive constraint migration; explicit profile-owned assignment checks still required |
| apps/accounts/recovery.py, config/use_cases/recovery.py | Evidence for non-self assigned case authorization, current-participant locking and required read audits; reuse pattern, not recovery tables or receipt credentials |
| apps/governance/audit.py, audit_models.py | SecurityOutcome and append_event in same transaction; extend bounded actions/subject types/reasons/changed-field names and PostgreSQL metadata functions/checks |
| apps/governance/outbox.py, outbox_models.py, tasks.py; config/event_handlers.py | Durable dispatcher, leases, receipts, eight attempts, 100-row batches, 60s leases, 300s backoff. Add explicit UUID-only event contracts/handlers; no dynamic import or new event engine |
| apps/governance/consents.py, consent_models.py; config/use_cases/consent.py | Existing immutable scopes/current-grant/terminal-revoke semantics. Only account_metadata validator exists; add optional server-supplied validation callback, rechecked on grant/read, and baseline_storage purpose through composition |
| apps/governance/privacy.py, privacy_models.py, retention.py; config/use_cases/privacy.py | Verified deletion restricts account/revokes auth and consent. Holds currently validate privacy_request only; add domain-validation callback and enumerated C03 subject kinds with audited case validation; no general arbitrary typed reference |
| apps/governance/flags.py, flag_models.py | professional_entry_enabled and professional_registration data; authoritative registration switch, not authorization. Marketplace has no C03 publication effect |
| apps/assets/storage.py | PrivateObjectStore, FakePrivateStore and S3PrivateStore/get_private_store; opaque keys, expiry 1..60s. Add bounded read/write support needed for upload processing, not public bucket behavior |
| config/settings/base.py, env.py, test.py, production.py, config/celery.py | Existing environment validation and one Beat scheduler; add validated upload/scanner settings, closed production verification/processing until configured |
| templates/accounts/base.html, templates/base.html, static/src/styles.css, accounts.js | Native Persian RTL/server forms, explicit ES modules and no browser credential storage; no SPA or offline private cache |
| tests/unit/c02, tests/integration/c02, tests/e2e/c02, tests/conftest.py | Keep all suites, skip-as-failure and async Playwright/ORM thread boundaries; add parallel c03 directories without rewriting C02 assertions |
| tests/integration/test_minio_storage.py; docker/verify_c02.sh, c02_baseline.py, c02_upgrade_probe.py | Existing private MinIO and exact-source same-database patterns; preserve independent immutable C01/C02 tests and add exact C02→C03 probe |
| .github/workflows/ci.yml, pyproject.toml, package.json, compose.yaml | Existing frozen/build/type/real-service/browser/restart gates. Execution later adds C03 branch gates and scan service, never changes protected branches |

Explicit reuse points cover User, Session/CSRF, current state, auth_version, AccountActor, Consent, AuditEvent, outbox, privacy/retention/hold metadata, professional_registration, staff capability/assignment/step-up and private storage. No existing profile or Asset model, upload service, image dependency, professional-verification capability or professional-assignment record is present.

## 4. Proposed models and exact field contracts

All new entities use UUID primary keys (User remains unchanged), UTC created/updated timestamps, positive optimistic version on mutable records, protected FKs and finite enum/check constraints. User public_id is the API identity. Within-domain references are relational. Cross-domain Asset/Consent/Hold subject references are validated by composition and rechecked server-side, never trusted from JSON. A mutation's actor/owner is derived from AccountActor.

| Model / proposed file | Key fields and invariant |
|---|---|
| AthleteProfile / apps/athletes/models.py | user OneToOne(PROTECT), status onboarding/active/archived, version, timezone from User preference, current_baseline nullable FK(PROTECT), onboarding_step enum. Private only; no automatic row for legacy users |
| BaselineAssessment / apps/athletes/baseline_models.py | athlete FK, sequence unique per athlete, parent nullable, state draft/submitted/superseded, schema_version=1, version, observed_at, submitted_at; typed setup fields in §5; correction clones into one draft, submitted answers immutable; current pointer advances atomically |
| ProfessionalProfile / apps/professionals/models.py | user OneToOne(PROTECT), state setup/private_ready/archived, version, verification_revision positive, display_name, identity_name private, biography, specialties, experience_years, service_modes, languages, setup_step, avatar/cover/logo Asset FKs nullable, accent_color, welcome_message; no slug/publication route/state in C03 |
| ProfessionalRole / apps/professionals/profile_models.py | profile FK, role coach/nutritionist, declared_active boolean, restricted_at nullable, version. Unique(profile,role); Both means two active rows, never a third role or User flag |
| ProfessionalLocation / profile_models.py | profile FK, country_code IR default, region and city normalized bounded text, modes, archived_at, version. Multiple locations; no street/address/venue/coordinates/geospatial columns/search index in C03 |
| Credential / apps/professionals/credential_models.py | profile FK, role nullable for identity evidence, category identity/qualification, type_code, issuer, title, issued_on/expires_on nullable, current_revision FK, version, withdrawn_at; private metadata, no public summary/document switch |
| CredentialRevision / credential_models.py | credential FK, sequence, copied bounded evidence metadata, source_asset FK(PROTECT), created_at, owner revision hash. Immutable after submission, including asset checksum reference; changing source/issuer/title/type/dates creates a revision |
| Verification / apps/professionals/verification_models.py | profile FK, sequence, state draft/submitted/under_review/approved/rejected/stale/withdrawn/revoked, version, bound_verification_revision, submitted_at/decided_at, snapshot schema/hash, private identity_name, requested_roles, identity_asset and immutable credential_revision references through VerificationEvidence; no inline document bytes |
| VerificationEvidence / verification_models.py | verification FK, CredentialRevision FK, role/category snapshot; unique(verification,credential_revision). Snapshot immutable after submit; referenced assets cannot be replaced |
| VerificationAssignment / verification_models.py | verification FK, assignee User FK, assigned_by User FK, assigned_at, ended_at, version; one live assignment per bundle, no self-case assignment; history retained |
| VerificationDecision / verification_models.py | verification FK, actor User FK, decision approve/reject/revoke/stale/withdraw, reason_code, bounded private explanation, approved_roles, identity_approved, snapshot_hash, bound revision, decided_at; append-only. One approve/reject terminal decision per submission; later revocation is another row |
| VerificationHistory / verification_models.py | bundle FK, event submit/assign/start_review/reassign/decision, actor reference, at, versions, reason_code; immutable transition evidence, no document payload |
| AssistantMembership / apps/professionals/assistant_models.py | profile FK, assistant User FK, role client_support only, state defined/revoked, version, defined_at/revoked_at. C03 defines metadata only; no invitation/activation/client assignment/API/operational grants. C06 expands reviewed lifecycle/entitlements |
| Asset / apps/assets/models.py | owner User FK, subject_kind/profile UUID, purpose identity_evidence/credential_evidence/avatar/cover/logo, source UUID key, classification private_source/private_derivative only, state, version, declared_size/type, actual_size/detected_type/SHA256, processing_version, created_at/upload_expires_at, accepted_at/finalized_at/revoked_at, rejection_code; key/checksum/private scanner details never public DTO |
| AssetDerivative / apps/assets/derivative_models.py | asset FK, purpose owner_preview/evidence_preview, unique(asset,processing_version,purpose), opaque key, SHA256, dimensions, MIME image/jpeg or image/png, state/version; private always |
| AssetProcessingAttempt / derivative_models.py | asset FK, processing_version/lease UUID/expiry, attempt, state pending/running/ready/failed, scanner engine/signature IDs, bounded failure code; no filenames/scan body in operational logs |
| ProfileCommandReceipt / each profile domain's receipt_models.py | owner User FK, operation_id UUID, command enum, normalized request hash, object/result UUIDs, resulting version, created_at; unique(owner,operation_id). API result reconstructed through current selector; no saved private response body |

SQL-enforced constraints: one profile of each type per User, one live baseline draft, one live verification among draft/submitted/under_review per profile, positive versions/sequences, unique role/location normalized facts, non-self membership, enum/size/type/hash validity, timestamp and state-null consistency (explicit non-NULL tests to avoid SQL three-valued holes), one live assignment and one terminal approve/reject per bundle, derivative/processing-effect uniqueness. FK ownership consistency checked under locks; immutable snapshot/decision/history guards reject ORM/bulk/direct SQL UPDATE/DELETE by ordinary principals. Privileged retention is separate, audited and policy-controlled, not an application bypass flag.

Indexes: baseline(athlete,sequence), verification(profile,sequence), verification(state,submitted_at,id) for bounded staff queue, live assignment(assignee,verification), credentials(profile,role), assets(owner,state,created_at) and (state,upload_expires_at), attempts(state,lease_until). Only these operational/ownership indexes; no public location/specialty/text/trigram indexes.

## 5. Athlete baseline field and workflow contract

PRODUCT_SPEC §4.1 and DOMAIN_MODEL §3 justify a dated baseline, not a medical record or longitudinal tracker. C03 schema v1 accepts these explicitly bounded fields; values below are engineering validation bounds, not medical guidance. Decimal units and unknown/declined are explicit. Persian/Arabic digits normalize at adapters; canonical values use ASCII decimals. Do not ask for age again: derive age_at_assessment from C02 birth_date and observed_at using existing date rules, mark declared rather than verified.

| Step / field | Representation, limits and completion |
|---|---|
| basics: height_cm, weight_kg | Decimal(5,1), height 50..250, weight 20..400; optional, dated self_reported and baseline_storage consent required before storing. Bounds reject unit mistakes, not diagnosis |
| goals | 1..5 selections from general_fitness/strength/endurance/muscle_gain/weight_management; mandatory nonempty, no Goal model/target prescription |
| experience | level beginner/intermediate/advanced mandatory; training_experience_months optional integer 0..1200, self-reported |
| availability | available_days distinct ISO weekdays 1..7, 1..7 entries mandatory; no calendar/appointment objects |
| facilities | equipment bounded list of bodyweight/dumbbells/barbell/machines/bands/other, optional other description ≤200; facilities home/gym/outdoors/other; at least one selection mandatory |
| context | lifestyle sedentary/mixed/active optional; sleep_hours Decimal(3,1) 0..24, energy integer 1..10 optional; baseline facts only, not daily metrics |
| habits | meals_per_day integer 0..12, hydration_habit low/regular/unknown, nutrition_habits plain text ≤500 optional; no food logs/macros/plans |
| optional measures | waist_cm Decimal(5,1) 20..250 optional; approximate_records ≤5 entries, label ≤80, value Decimal(8,2)>0, unit kg/reps/seconds/metres, observed_at, provenance self_reported; no progress/performance timeline |

No injury/limitation/allergy/medication/supplement/health-document/photo fields, including free-form health prompts or attachment affordances. Reject unknown input keys rather than storing arbitrary JSON that could admit C09 fields. Personal logging remains a later workout flow, never gated by this baseline in C03. Baseline completion only means required non-sensitive setup steps are present; C05 will separately decide/request current intake completeness without forcing optional sensitive values.

Owner explicitly creates profile; resume reads own draft and server-derived completion. Each step save carries expected_version and operation_id; missing fields in a step mean unchanged, explicit null means clear optional field. Native forms express clear explicitly. UI saves one server step at a time, returns the committed version and shows saved timestamp. Partial draft is valid; submit validates mandatory selections and required consent for values actually present, freezes snapshot and sets profile active/current_baseline. Corrections create one next-sequence draft with parent submitted snapshot; submit supersedes predecessor without rewriting answers. Profile height/current context is derived from current baseline, not an independently drifting copy.

Optional baseline_storage consent is a self-grantee purpose under existing Consent. The scope names the draft assessment UUID and schema_version=1, and its immutable disclosure/text hash covers the fixed optional field set; object_version is the disclosure schema, not each mutable draft version. Composition checks actual owner/schema/field set again. New correction assessment needs its own explicit consent before copied optional data is retained; copy only non-sensitive fields until consent. Decline leaves required setup available. Revoke/expiry immediately denies optional-value reads/writes and marks them inaccessible in selectors; retained snapshots/held evidence do not disappear from integrity history or grant normal access. C03 provides a clear-fields command and domain erasure inventory, not the full C18 export/deletion pipeline. C09 adds separate health-storage and professional-share grants, never reuses baseline_storage to share.

## 6. Professional setup, roles and completion

Create requires current active adult normal AccountActor plus professional_registration enabled, atomically rechecked; one-to-one duplicate/replay returns the current owned row. Flag false/outage prevents new profile creation, not owner management/read of an existing profile. Registration flag cannot authorize assets/review/athlete access. No Pro dependency exists for baseline branding; advanced tier choices are deferred without silently paywalling core setup.

Profile fields: display_name 1..120 required; private identity_name 1..120 required for submission; biography plain text ≤2000; specialties ≤10 plain bounded tokens each ≤64; experience_years integer 0..80; service_modes nonempty online/in_person; languages ≤5 validated BCP47-like bounded tags (fa default); optional welcome ≤500; accent strict #RRGGBB, no CSS/HTML; nullable ready own avatar/cover/logo. Role UI Coach/Nutritionist/Both maps to exactly one/two declared-active rows. Switching roles deactivates rows, never deletes history. Broad region/city each 1..100; in_person requires ≥1 active broad location, online-only need not invent one. No precise address/location lookup service or discoverability.

Steps: identity/roles → description/specialties/experience → modes/languages/locations → optional private branding → credentials → owner preview/submission. Each step is resumable/optimistic/idempotent. private_ready requires required profile fields and roles/mode/location consistency; verification submission additionally requires ready identity and applicable credential evidence. Optional media are never required. Wizard has no package/calendar/template/payment/intake/AI links or active placeholders.

Declared capabilities are data for later private-management policy; C03 offers no prescribing or relationship API. verified_roles are derived from the current approved bundle, never mass-assigned profile fields. Both submission is all-or-nothing for requested roles: incomplete or rejected evidence does not manufacture partial Both verification. Owner may explicitly submit a narrower role set in a new bundle. Expired/withdrawn/restricted role evidence denies that verified capability immediately, independent of worker schedules. Publication eligibility requires identity and credentials for all currently declared-active roles; profile existence/declaration never grants athlete authority.

## 7. Verification binding and state machines

Verification-bound set: private identity_name; requested/declared-active role set; credential category/type/role/issuer/title/issued_on/expires_on and immutable source Asset UUID/SHA256; staff-imposed capability restrictions. Changing any bound value increments ProfessionalProfile.verification_revision, atomically makes an in-flight bundle stale with immutable history, and makes earlier approval ineligible. Editing while approved leaves the historical decision intact and requires a new draft/submission. No automatic reapproval or silent snapshot replacement.

Cosmetic/non-bound set: display_name (deliberate public presentation name), biography, specialties, experience_years (declared, not credential-attested), service_modes, languages, broad locations, avatar/cover/logo, accent_color, welcome. These retain verification but must remain valid private setup/asset facts. UI labels experience/specialties self-declared, not verified claims. Changing account phone/auth_version does not change identity evidence approval; it revokes old actors and rechecks current state. A later verified legal-identity feature must explicitly extend this binding before claiming it is verified.

| From | Command / authorized actor | To and effects |
|---|---|---|
| absent | owner prepares bundle | draft at next sequence; captures current bound revision, not publication |
| draft | owner submit with complete ready evidence | submitted, immutable snapshot/schema/hash/evidence links, timestamp/history/audit/outbox |
| submitted | capable non-self staff assigns case with step-up | submitted with live assignment; bounded minimal metadata, no evidence read on queue |
| submitted | assigned staff start_review | under_review; audited history, fresh case step-up |
| under_review | assigned staff approve with identity check and all requested credential checks | approved; append immutable decision/history, approved_roles exactly requested_roles, conditional eligibility |
| under_review | assigned staff reject with reason | rejected; immutable decision/private bounded feedback; source retains private classification and approved policy retention |
| submitted/under_review | bound edit, owner withdraw, or supported security invalidation | stale/withdrawn; immutable reasoned history, close assignment, no decision based on superseded facts |
| approved | named assigned staff revoke with fresh step-up/reason | revoked; separate immutable revocation decision; eligibility false synchronously |
| rejected/stale/withdrawn/revoked | owner prepares/resubmits corrected evidence | new draft and new sequence/bundle; predecessor never edited/reopened; fresh submission/assignment required |

Only draft has mutable snapshot/evidence; other state columns/versions may transition by services but submitted snapshot hash/identity/evidence never change. Rejection remains history; no delete/reuse of its UUID. Owner coarse status exposes own feedback but no staff-private operational notes. No unevidenced approval, owner/self review, superuser exception or unaudited reassignment.

Account restriction/suspension/deletion: immediately deny owner normal access and publication eligibility from current account state. In-flight decisions against inactive/non-active owners are denied; registered composition handler may record stale bundles afterward, but delayed outbox cannot make eligibility true. Historical approval need not be destroyed merely by temporary suspension. Restoration, if later authorized in accounts, still rechecks current bound revision/evidence/expiry/restrictions; never changes a decision. Credential withdrawal/revocation/expiry denies capability at query/decision time; scanner quarantine/revocation after approval denies eligibility. No C03 account-reactivation command exists.

Owner preview selector requires current active adult normal actor and exact user ownership regardless of verification, role, flag, referral, consent or assistant membership. It returns a dedicated DTO of presentation fields, setup/verification coarse status and private derivative references resolved through authenticated endpoints; no identity/evidence/internal keys/staff notes. No public preview tokens/slugs/share links. Responses no-store, X-Robots-Tag noindex,nofollow and no public metadata; no source URL in HTML.

publication_eligibility(profile_uuid, at) is an internal reader returning eligible:boolean, verified_roles tuple, reason_codes tuple, bound_revision integer. It rechecks User active/is_active/adult, private_ready, active declarations/no restrictions, current approved identity/requested roles, matching verification_revision/snapshot, unexpired current credential revisions and ready nonrevoked evidence. Invalid/missing DB state fails closed. It grants no public route, copies or relationship authority and does not use Marketplace as object permission. C04 will combine this with explicit publication choices and its flag. No stored is_verified/is_public boolean is authoritative.

## 8. Staff capability, assignment and step-up workflow

Add professional_verification to existing CAPABILITIES (fits length 24) and both grant/step-up CHECK allowlists. Authority continues through require_staff(user, capability, case_uuid, step_up_id, reason_code, at) inside transaction after locked_actor(actor,'staff.command',at). Grant must be current, issued by another trusted user; step-up must match capability/case/current auth_version, freshness ≤ existing 600s, not self-issued, supported method only. Production verified MFA provider/evidence standards remain release gates; C03 must not treat mock/disabled as live verification.

Assignment is professional-domain metadata. Trusted capability holders receive only a bounded submitted queue (maximum page 25, stable time/UUID cursor, UUID/state/time/requested roles; no phone/name/credential/athlete fields). Queue read is capability+queue-bound step-up+reason+audit. assign_verification chooses validated current capable staff through an internal trusted operation, using submitted case-bound authority; no User directory or client-submitted arbitrary staff grant. Non-self staff may claim an unassigned case; reassignment requires case-bound step-up, explicit reason, expected version, closes predecessor and appends history. Starting review, metadata/detail/evidence reads and decisions require live assignment to actor, current case step-up and conflict-of-interest separation from owner. Changing assignee invalidates prior review commands even if step-up remains unexpired. Staff read outage/audit failure returns no evidence derivative.

Revocation uses the same named capability and an explicit assigned approved case; immutable prior approval preserved. Account restriction remains its existing capability/contract, not a verification override. Retention/hold staff requires privacy_operations in its validated case and cannot use verification capability to erase or browse other evidence.

## 9. Asset/upload, sanitization and private delivery

Bounded C03 upload contract chooses JPEG/PNG raster scans for identity/credentials and JPEG/PNG avatar/cover/logo. PDF/Office/archive/video/SVG/HTML/GIF/WebP and executable files are rejected in C03; credential documents can be supplied as legible raster scans. This is an engineering allowlist, not a new public document feature. Architecture's document ceiling remains 20 MB for later reviewed formats; C03 raster uploads all use ≤10,000,000 bytes (decimal MB), ≤20,000,000 decoded pixels, maximum dimension 10,000, one frame. No new generic file preview/PDF interpreter is needed. Scanner success is necessary but never sufficient to trust content.

Proposed C03 strategy uses authenticated same-origin multipart proxy uploads; no direct S3 upload credentials/presigned PUT, arbitrary key, remote URL import or cross-origin upload policy. Existing PrivateObjectStore lacks bounded streaming; add put_stream/read_limited (maximum size enforced even without trustworthy Content-Length), preserving put/read/delete/signed_read_url for C01 tests. Fake store shared through injected per-workflow instance; get_private_store's new Fake instance per call is not a persistence service.

1. begin_upload(actor,purpose,validated subject,operation_id,at) checks active account, exact owner/profile/credential purpose and quota before an Asset row. Opaque random key never incorporates filename/phone/name; client supplies no owner/key/classification. Limits: ≤10 live uploads/user, ≤100 MB accepted source bytes/day, configurable engineering abuse bounds under owner/User lock; scanner tasks get IDs only. upload_expires_at is 1h operational admission expiry, not data-retention duration.
2. receive_upload(asset_uuid,expected_version,stream,at) reauthorizes own pending asset, rejects second body, caps streaming memory/disk/bytes, writes only private quarantine. Never holds PostgreSQL locks across storage I/O: reserve transition with version/attempt, use random immutable object key, then lock/recheck. Storage failure/stale account/revoke leaves quarantined failure, not usable data; orphan reconciliation tracks keys in Asset row.
3. finalize_upload verifies stored bytes/size/SHA256 and allowed JPEG/PNG signature/extension/detected decode type, not caller MIME. It commits quarantined plus asset.processing_requested outbox; accepted 202 is not ready. Asset source becomes immutable once accepted; no repeat overwrite, finalization accepts same operation receipt only.
4. worker claims processing lease/version, private malware scan through bounded ClamAV INSTREAM; unknown/error/timeout/stale signatures/limit-exceeded fail closed. Isolated image subprocess (no network, nonroot, read-only runtime, bounded CPU/memory/output, 30s timeout) fully decodes allowed formats, treats decompression warnings as errors, rejects truncation/multiple frames and mismatch, strips all EXIF/GPS/comments/text/ICC metadata and re-encodes clean pixels. Preview max edge 1600, avatar/logo 512, cover 1600; output MIME and extension server-selected. No inline source serving, arbitrary Image.open formats or external AI.
5. Before ready commit, recheck owner state, purpose/binding/version/revocation/lease and hold/consent where applicable. Write derivative to new private key before commit; compare checksum and deterministic processing_version, unique derivative/effect prevents duplicates. Crash/retry adopts an identical expected derivative or queues cleanup; it cannot release stale content. Store scan engine/signature and processing algorithm versions in restricted metadata.
6. attach_ready_asset(owner command) checks both source/destination current ownership, purpose and ready derivative; evidence association freezes source revision at submit, profile branding replacements never mutate verification evidence.
7. abandon/revoke denies new access immediately, cancels lease and unbinds only authorized mutable references; source/derivatives follow central retention and record-specific holds. Pending expiry becomes abandoned even if worker delayed; cleanup erases eligible object inventories under explicit effective policy, retries delete idempotently and preserves held evidence. No hardcoded destroy-on-hour-expiry retention.

Asset states: pending_upload → receiving → quarantined → processing → ready or rejected; pending/receiving/quarantined/processing → abandoned; ready → revoked; rejected/abandoned/revoked → deletion_pending → deleted only after policy/holds. Scanner outage remains quarantined/retryable with bounded code; exhaustion cannot convert failure to ready. Derivatives have pending/ready/revoked/deleted; source and child visibility remain private. Visibility is separate from processing state; verified approval never changes either storage ACL/classification.

Credential/identity sources have no consumer or staff download endpoint in C03 and no signed-source URLs. Only the isolated processor can read source bytes for scanning/sanitization. Owner and assigned staff see the ready sanitized evidence derivative through authenticated proxy delivery with current object/case authority and synchronous audit. Retaining originals for verification integrity does not permit raw delivery. Quarantined/rejected sources or derivatives never download. Later source-download support would require a separately reviewed isolated-origin authentication/delivery design; do not add shared cross-subdomain session cookies or bearer tokens to resolve it. Branding preview also uses same-origin authenticated sanitized derivative proxy in C03; a later signed-derivative caller must obtain object authorization before S3 signing, expiry ≤60s, with residual window disclosed. Test unauthorized signing by spy: storage signer call count zero. Every private response no-store, nosniff, safe content-disposition and generic server filename; never leak original filename or private key. No public bucket/ACL/CORS changes.

Dependency review (planning research, no installation): existing stdlib/Django/django-storages cannot safely decode/re-encode images, remove metadata or detect decompression bombs. Pillow is justified solely for allowed JPEG/PNG decoding/sanitization. Official documentation reviewed on 2026-10-06 lists 12.3.0 stable, MIT-CMU license, maintained releases and security fixes; candidate floor Pillow>=12.3.0,<13, exact patched version/hashes must be rechecked against official security advisories at Task 5 before lock. Primary references: https://pillow.readthedocs.io/en/stable/about.html, /handbook/security.html and /releasenotes/12.3.0.html. This is not a claim that the candidate is free of vulnerabilities.

ClamAV is a separate private scanner runtime, not a Python dependency or external document-transfer service. Official GPLv2/license and bounded INSTREAM protocol reviewed: https://docs.clamav.net/ and https://docs.clamav.net/manual/Usage/ClamdProtocol.html. Task 5 records supported patched engine version, container digest, signature policy, redistribution/license review and maintenance owner in DEPENDENCIES/C03_SETUP. No libclamav linking, generic cloud scanner, Python MIME package or image AI dependency. Deterministic fake scanner/decode fixtures plus real private scanner/MinIO gates exercise clean/malicious/timeout/limits; signatures and scanner network isolation are production release prerequisites. Adding dependencies is execution work, not part of this commit.

## 10. Consent, privacy, holds and deletion boundaries

baseline_storage is the only new consumer consent purpose in C03; self-grantee with owner/assessment/schema checks. Credentials are deliberately supplied for private verification; they are not athlete sharing, external-AI or publication consents. Explicit upload-purpose disclosure covers storage/review/retention; no consent alone authorizes a staff read or public use. Privacy/legal review approves exact production wording/durations before live collection. Credential/publication and health/photo sharing are not conflated.

Retained classes: athlete_profile, athlete_baseline, professional_profile, credential_source, credential_revision, verification_evidence, verification_history, profile_media, asset_quarantine, command_receipt. Map source plus derivatives, owner, subject/version, classification, policy reference and deletion behavior in per-domain privacy modules. Only server-resolved subjects may be held. New RecordHold kinds enumerate athlete_baseline, professional_credential, professional_verification and profile_asset in addition to privacy_request. Composition validates real owner/version and case association; profile-owned credential/verification cases use assigned staff authority where required, privacy_operations step-up and explicit reason. A credential hold covers its snapshotted source/derivative inventory, not all owner media. Overdue review never silently releases; expiry or authorized release follows existing rule. No retention policy duration seeded for production; missing effective policy prevents destructive cleanup, raises an operator signal and blocks live release, not permission to retain forever.

Extend existing governance validation with server-supplied subject/case callbacks: governance retains no reverse domain imports; domain helpers return ValidatedRecordSubject only after real-row validation and mutation rechecks. Plain dataclass construction is insufficient. Additive SQL enum/metadata checks retain all C02 protections. No global arbitrary validator registration from requests.

Deletion request/current restriction immediately denies profiles/assets/preview/staff decisions against the owner/public eligibility from current User state. C03 composition handlers enumerate its assets, invalidate active upload leases and inert assistant memberships, make stale processing results unreleasable and mark ready items revoked using current owner predicates. These effects may reconcile through existing outbox, but HTTP/task release deny synchronously even before cleanup. C18 owns full exports, deletion processing, erasure markers, provider/backup restore and resumable policy execution; C03 exposes validated inventories and bounded cleanup/hold integration for its objects, never a new deletion account state machine. No cascade erases User or C02 audit/consent/history.

## 11. Interfaces, authorization and API contract

New profile actions added to NORMAL_ACTIONS: athlete.profile_read, athlete.profile_write, athlete.baseline_read, athlete.baseline_write, professional.profile_read, professional.profile_write, professional.verify_submit, asset.owner_read, asset.owner_write. Staff continues staff.command. Account action allowlisting is only the account-state predicate; feature policies still require exact ownership/state/binding. Unknown actions remain denied.

Proposed typed inputs/results live in apps/athletes/contracts.py, apps/professionals/contracts.py and apps/assets/contracts.py. At means aware datetime; IDs UUID; expected_version positive int excluding bool; operation_id UUID. Private DTOs expose allowlisted values and current versions, no model serializer. Domain services accept current AccountActor plus required record/emitter callbacks where composition owns events. Exact public composition interfaces below are targets for later execution, not existing functions:

| File / interface | Signature contract and return |
|---|---|
| config/use_cases/athlete_profile.py | create_athlete_profile(actor, operation_id, at) → AthleteProfileDTO; begin_baseline(actor, expected_profile_version, operation_id, at) → BaselineDTO; save_baseline_step(actor, baseline_uuid, step, input: BaselineStepInput, expected_version, operation_id, at) → BaselineDTO; submit_baseline(actor, baseline_uuid, expected_version, operation_id, at) → BaselineDTO; correct_baseline(actor, baseline_uuid, expected_version, operation_id, at) → BaselineDTO |
| apps/athletes/selectors.py | own_athlete_profile(actor, at) → AthleteProfileDTO; own_baseline(actor, baseline_uuid, at) → BaselineDTO; optional values filtered by current self-storage grant |
| config/use_cases/professional_profile.py | create_professional_profile(actor, operation_id, at) → ProfessionalProfileDTO; save_professional_step(actor, step, input: ProfessionalStepInput, expected_version, operation_id, at) → ProfessionalProfileDTO |
| apps/professionals/selectors.py | own_professional_profile(actor, at) → ProfessionalProfileDTO; owner_preview(actor, at) → OwnerPreviewDTO; publication_eligibility(profile_uuid, at) → PublicationEligibility |
| config/use_cases/profile_assets.py | begin_profile_upload(actor, purpose, subject_uuid, operation_id, at) → UploadDTO; receive_profile_upload(actor, asset_uuid, expected_version, stream, at) → UploadDTO; finalize_profile_upload(actor, asset_uuid, expected_version, operation_id, at) → UploadDTO; abandon_profile_upload(actor, asset_uuid, expected_version, operation_id, at) → UploadDTO; authorized_profile_download(actor, asset_uuid, purpose, at, staff_context=None) → AuthorizedAssetRead |
| config/use_cases/professional_verification.py | prepare_verification(actor, expected_profile_version, operation_id, at) → VerificationOwnerDTO; submit_verification(actor, verification_uuid, expected_version, operation_id, at) → VerificationOwnerDTO; withdraw_verification(same args) → VerificationOwnerDTO; assign_verification(actor, verification_uuid, assignee_uuid, expected_version, step_up_id, reason_code, at) → VerificationStaffDTO; start_verification_review(actor, verification_uuid, expected_version, step_up_id, reason_code, at) → VerificationStaffDTO; decide_verification(actor, verification_uuid, decision: approve/reject, expected_version, expected_bound_revision, step_up_id, reason_code, explanation, operation_id, at) → VerificationStaffDTO; revoke_verification(same authority/version fields, no client-selected decision) → VerificationStaffDTO |
| apps/professionals/verification_selectors.py | assigned_verification_detail(actor, verification_uuid, step_up_id, reason_code, at) → VerificationStaffDTO; assigned_verification_evidence(same authority plus asset_uuid) → AuthorizedAssetRead; submitted_verification_queue(actor, step_up_id, reason_code, cursor, at) → bounded minimal queue DTO |
| config/use_cases/c03_privacy.py | validate_c03_consent_scope / validate_c03_hold_subject / validate_c03_hold_case: explicit composition callbacks to existing governance services; inventory_c03_owner(owner_uuid, at) → private typed record/asset inventory, no public endpoint |

Domain implementation functions with the same command names live in apps/athletes/services.py/baseline.py, apps/professionals/services.py/credentials.py/verification.py, apps/assets/uploads.py/delivery.py and accept required governance callbacks; config merely supplies validators/providers/recorders, no business logic. Do not call downstream selectors via ORM shortcuts in adapters.

API prefix remains /api/v1/. Use explicit own resources/commands, no owner UUID in create/update payload and no profile directory. Proposed route inventory:

| Route | Contract |
|---|---|
| POST /athlete/profile/; GET /athlete/profile/ | explicit own create/read; create 201, replay 200 current DTO |
| POST /athlete/baseline/draft/; GET /athlete/baseline/<uuid>/ | create/resume next owned draft, own detail only |
| POST /athlete/baseline/<uuid>/steps/<step>/ | save one allowlisted step; expected_version+operation_id |
| POST /athlete/baseline/<uuid>/submit/ or correct/ or clear-optional/ | frozen submit, new correction draft, consent-aware clearing |
| POST /athlete/baseline/<uuid>/storage-consent/; POST .../storage-consent/revoke/ | explicit current disclosure confirmation, existing grant/revoke with validated self-scope, no general arbitrary consent endpoint |
| POST /professional/profile/; GET /professional/profile/ | owned creation/read; flag only on creation |
| POST /professional/profile/steps/<step>/; GET /professional/preview/ | owned setup command/preview, no route by slug or someone else's UUID |
| POST /professional/credentials/; POST /professional/credentials/<uuid>/revise/ or withdraw/ | owned bounded metadata/evidence commands; no public credentials endpoint |
| POST /professional/verification/draft/; POST /professional/verification/<uuid>/submit/ or withdraw/; GET .../<uuid>/ | owned bundle commands/coarse history/feedback |
| POST /profile-assets/begin/; POST /profile-assets/<uuid>/body/ or finalize/ or abandon/; GET .../<uuid>/status/ or content/ | proxy multipart body only at body; status safe DTO, content current authorization |
| GET /staff/professional-verification/queue/; GET .../<uuid>/ | named capability/step-up minimal queue or assigned case |
| POST /staff/professional-verification/<uuid>/assign/ or start/ or decide/ or revoke/; GET .../<uuid>/evidence/<uuid>/ | explicit audited case operations; assignee selection internal trusted operation, no staff/User grant CRUD |

All paths under /api/v1; no routes for assistant activation, eligibility public lookup or public search. Serializers reject unknown fields, supplied owner/state/approved_roles/asset keys, HTML and malformed UUIDs. Normal JSON/form body cap 4096 bytes using existing pattern; multipart ≤10MB plus bounded overhead, max one file and explicitly capped form fields; larger baseline snapshots cannot bypass step limits. Response 400 validation, generic 403 absent/stale/non-normal actor (C02 convention), 404 inaccessible object uniform with absent UUID, 409 accessible version/state or changed receipt payload, 429 upload quota, 503 DB/storage/scanner unavailable, 202 queued processing, 200 completed commands. Authorization precedes conflict details. CSRF precedes command side effects, including multipart; no CORS or exempt browser endpoint. Private no-store everywhere. No signed URL/source filename/internal hash in DTOs.

## 12. Persian RTL UI and browser contract

Native HTML routes: /athlete/setup/, /athlete/baseline/<uuid>/; /professional/setup/, /professional/preview/, /professional/verification/; /staff/professional-verification/queue/ and /staff/professional-verification/<uuid>/. Forms call same composition commands. Successful POST redirects to authorized GET; never repeat a decision/upload on reload. UUID references and operation_id may be form hidden fields, never authority. Staff receives assigned case references and fresh step-up through trusted operations; no secret/MFA proof in query parameters or browser storage.

Use lang=fa/dir=rtl, semantic headings/fieldset/labels, Persian validation and save/status text, keyboard focus/error summary, unit suffixes, responsive layouts at 1280×900 and 390×844, no horizontal overflow. Dates use existing Gregorian/Jalali conversion and Tehran display; UTC storage, no copied age gate. Label optional facts as اختیاری and self-reports as اظهارشده توسط شما; owner preview says پیش‌نمایش خصوصی and pending verification says قابل انتشار عمومی نیست. Approval text says eligibility for later publication, not a live public page. Progress counts only installed steps, no fake percentages/empty later features. Credential forms clearly state private review and accepted JPEG/PNG scans/limits. Declined optional baseline displays ثبت نشده, not no injury/normal health.

ES modules enhance step autosave/status and upload progress only; native forms work with JS disabled. No localStorage/sessionStorage/IndexedDB/Service Worker cache of baseline/evidence/credentials/step-up/session tokens; reconnect resumes from server draft. Templates autoescape plain text; accent cannot inject CSS, media URLs resolved by authorized derivative views. Strict console/pageerror and CSRF/account-switch/logout/expired step-up tests use actual Playwright. Follow existing async fixtures and thread_sensitive sync_to_async ORM helpers; never DJANGO_ALLOW_ASYNC_UNSAFE or suppressed errors. Test-only mock assertions/fixture data remain memory-only; no screenshots/traces of credentials or authority secrets.

## 13. Background jobs, event inventory and recovery

Only genuinely needed C03 jobs: private scan/derivative processing, expired/abandoned upload reconciliation and policy/hold-eligible asset cleanup. No async verification decisions, baseline saves, publication or provider AI. Reuse existing durable dispatcher and effect receipts; job arguments event/lease/asset UUIDs and processing version only, no image/body/identity/name/URL.

New audit inventory (action names <32 chars): athlete.profile_created, baseline.saved, baseline.submitted, baseline.corrected, baseline.cleared, professional.profile_created, professional.profile_saved, professional.roles_changed, credential.created, credential.revised, credential.withdrawn, asset.begun, asset.uploaded, asset.finalized, asset.read, asset.rejected, asset.revoked, asset.deleted, verification.submitted, verification.assigned, verification.review_started, verification.read, verification.approved, verification.rejected, verification.stale, verification.withdrawn, verification.revoked, assistant.defined, assistant.revoked. Reuse consent.granted/revoked, privacy.hold/policy, account.state_changed and outbox.retry. Subject types athlete/baseline/professional/credential/asset/verification/assistant; allowed reasons add verification_submitted, verification_review, credentials_approved, evidence_incomplete, credentials_invalid, evidence_expired, material_changed, owner_withdrawn, upload_invalid, scan_failed, retention_due. Private staff explanation stays in decision domain, never general reason/audit. Extend changed-field names only; no copied field values.

| Outbox event | Exact UUID-only payload / effect |
|---|---|
| athlete.baseline_changed | baseline_uuid,user_uuid; aggregate baseline, aggregate_version=current version; registered metadata receipt only |
| professional.profile_changed | profile_uuid,user_uuid; profile version; metadata receipt only, no public projection |
| verification.changed | verification_uuid,user_uuid; bundle version; metadata receipt, current eligibility remains query-time |
| asset.processing_requested | asset_uuid,user_uuid; asset version; bounded scan/derivative workflow under processing lease |
| asset.cleanup_requested | asset_uuid,user_uuid; asset version; current state/policy/hold inventory cleanup |
| assistant.membership_changed | membership_uuid,user_uuid; membership version; inert metadata receipt |

Event types must fit existing outbox column limits; extend aggregate UUID key mapping, payload UUID fields, event/receipt CHECKs and PostgreSQL payload function in a new migration. Dedup event:type:UUID:version; existing consent/security events retain their schemas. Reads get audit but no outbox; routine step saves emit only installed metadata effects, not notifications. New handlers live in config/c03_event_handlers.py imported explicitly by existing HANDLERS, no feature imports in governance/accounts.

Avoid long image work in dispatch_event's PostgreSQL transaction. asset.processing_requested handler inserts a unique durable AssetProcessingAttempt and returns; a bounded worker reconciler claims attempt rows, commits lease, does scan/I/O outside transaction, then rechecks and commits effect. A broker prompt is optional, never sole durability. One Beat adds installed scans with validated intervals (30s processing, 300s upload/cleanup scan engineering defaults, max100); no worker selects arbitrary IDs/paths from payload. Test restart between handler receipt and worker prompt: durable pending attempt is discovered. Queue identity state/hold/consent is revalidated at claim and release. Repeated scan/finalize/delete has one observable effect; attempts/backoff/exhaustion explicit, no unknown-error detail logged.

## 14. Concurrency, transactions and idempotency

Stable lock protocol: existing accounts commands keep phone anchors → sorted User PKs → account controls/domain rows. C03 commands never mutate phone and never acquire phone anchors after a User lock. Pre-read only to locate owner/participants; lock involved Users (owner, acting staff, assignee/self-grantee) in PK order and revalidate mapping/current AccountActor before feature rows. Then profile → baseline/credential IDs sorted → verification → assignment/evidence → assets/attempts sorted → staff capability/step-up → consent/hold rows → receipts/audit/outbox. Already-locked User rechecks by locked_actor/require_staff must not introduce a new participant. Profile creates serialize on User; first-upload quotas serialize on owner. Asset workers lock owner before asset/attempt; hold commands through composition lock same subject anchor before hold mutation. Audit/outbox share the mutation connection.

Existing consent grant locks sorted participants first; C03 self-consent has one User, then callback locks baseline/profile before Consent. Current-grant reads inside writes lock relevant Consent rows so revocation serializes; one-way terminal revoke remains intact. New privacy callbacks follow same owner/subject/hold ordering; no feature waits for an earlier governance lock while holding an opposite anchor. Test the concrete wait graph against C02 logout/recovery/phone/state/consent/hold/outbox paths rather than relying on this description alone. Any discovered cycle must be corrected before task gate, not retried indefinitely.

Receipt lookup after current authorization, under owner lock: unique(owner,operation_id), command+normalized input hash equality; same retry returns safe current owned result, differing command/payload 409. Never resurrect revoked profile/asset from an old receipt. Receipts include no document bytes; storage body is exactly-once accepted by source Asset/version reservation, and finalization has separate receipt. expected_version required for edits/submission/assignment/decision; no last-write-wins. Creation duplicate protection is SQL plus User lock; do not leak which other owner has a UUID.

Staff decision rechecks live assignment, fresh step-up, case version, expected_bound_revision, profile verification_revision, requested role set, snapshot hash, ready source/derivatives and credential expiry inside transaction. Bound edit and decide take same profile/case lock: if edit first decision fails stale; if decision first later edit makes eligibility false and preserves decision. Two approve/reject commands yield one decision, other current replay or 409, never two conflicting histories. New resubmission must acquire profile lock and allocate next sequence; terminal predecessor stays immutable. Same operation key returns same bundle; differing key cannot create another live bundle. Reassignment concurrent with decision has one serialized valid outcome. Worker lease token/processing_version fences stale processes; no storage read of an unbounded client key.

## 15. Additive migration and exact upgrade rehearsal

No User columns, accounts migrations, original governance migrations or auth tables are rewritten. New assets/athletes/professionals tables and new governance migrations extend finite CHECKs/functions while retaining old accepted values and immutability privileges. Initial new-domain migrations depend on swappable User plus existing governance0010 and assets where needed; AthleteProfile/Baseline current pointer and Credential current_revision circular references are split into later AddField migrations after their tables exist. Only after tables exist register settings/apps/callbacks/routes. No blanket profile creation/data backfill for C02 users, no fake verification/capability/consent seed, no public indexes. SQL reviewed before apply; nullable-to-required fields must not use destructive default updates on legacy users. Downgrade preserves feature data by disabling routes/roll-forward rather than casually dropping snapshots. Reversibility of each CHECK widening documented; fail if reverting would orphan accepted C03 records.

Exact fixture: authenticated checkout of 0905be6c6ca608d469fe33e87f514b22591132d1 into ignored .runtime/c02; independent Git blob/mode manifest reconstructs ed788191bb6f5011e6b35a63823ae8183af7b53d. Test missing/modified/unexpected/symlink sources, permit only enumerated generated outputs. Do not substitute main/current code/historical models for original C02 runtime. Preserve separate C01 fixture and verify_c02.sh unchanged.

Rehearsal procedure (Task 14):

1. New isolated Compose project/volumes; reject existing volume names; never remove user data. Build/run exact C02 code/frozen dependencies, apply its migrations and full C02 regression including immutable C01 rehearsal.
2. Populate a separate fresh C02 PostgreSQL database using C02 APIs/services: active adult dual-context candidate (no profiles yet), active legacy null-DOB row, restricted and suspended users; normal/account_control current/revoked/expired sessions; normalized phones/UUIDs/unusable passwords; OTP/proof metadata; recovery/PhoneChangeHistory; consent/scope/revocation; flags; AuditEvent/outbox/receipt; privacy requests/draft+effective synthetic policies/record-specific holds. Synthetic step-up/grants only through existing test/trusted helpers. No production evidence or live identity data.
3. Restrict ignored manifest to 0600; snapshot all C02 table OIDs, row PKs/UUIDs/counts, phones/password/adult/state/auth versions, session bytes and auth/control mappings, governance fields/history and checksums. Session keys/phones never in CI logs/artifacts.
4. Switch only code image to C03 in the same DB/service/network/volume/password; migrate forward once and again (idempotent), inspect every new sqlmigrate, makemigrations --check --dry-run, showmigrations; schema retains auth_user absence and original User table OID.
5. Assert all C02 rows/identifiers/counts/security/governance data preserved exactly before exercising new flows, no profile/role/verification/Asset created for legacy users. Valid preexisting normal sessions still resolve under unchanged C02 authority; restricted account_control remains controls-only; stale/revoked/expired/legacy unsupported cookies still denied. Only deliberate subsequently tested commands may append audit/session state; separate those assertions from migration preservation.
6. Use valid preserved owner session to explicitly create profiles/baseline, upload/process private media, submit/review; old unauthorized controls cannot acquire C03 access. Recheck C02 phone/recovery/consent/privacy services and all regression suites on upgraded runtime. Keep same-database evidence distinct from pytest-created test DB evidence.
7. Independently new zero-state C03 database migrates cleanly, no auth_user, correct constraints and no drift, complete backend/browser/storage/concurrency gates. Immutable C02/C01 source proofs and full regression remain mandatory. Cleanup only task containers/networks, retain volumes and sensitive manifest locally per existing practice.

## 16. Test matrix, security checklist and CI gates

| Gate / tests | Assertions and owning tasks |
|---|---|
| Unit/schema/contracts | field bounds, unknown keys/C09 fields denied, declared≠verified≠publication≠relationship, flag≠authorization, no future import/public route/index (1–3,6,10,12) |
| Cross-owner profile/UUID | cross-athlete/professional read/write/detail/list/count denied, guessed/absent UUID same 404, owner derived from actor, dual-context isolation, unrelated professional no athlete access (2,3,10,12) |
| Baseline privacy | optional decline/unknown/completion, consent expiry/revoke/storage-only/self-grantee, submitted correction immutable, no C09 photos/health payload accepted (3,9,11,12) |
| PostgreSQL integrity | actual unique/check/FK/null constraints, SQL/bulk immutability and runtime UPDATE/DELETE/TRUNCATE denied; duplicate profile/live draft/live submission (1,2,3,6,7,14) |
| PostgreSQL races | independent connections/barriers: create/create, save/save, submit/resubmit, approve/reject, decision/edit, reassignment/decision, expired credential/decision, logout/restriction/deletion/receipt/upload/release and hold/cleanup (2–9,13,14) |
| Staff | no capability/no assignment/stale case step-up/current auth mismatch/expired grant/self-case/bare superuser denial, assigned minimal audited reads, audit failure no content, reason/decision immutable (7,8,12) |
| Private storage | source stays private after approval, other owner/purpose rejected before signer/read, no anonymous URLs/public copies, bounded signing helper expiry, derivative-only no-store proxy/audit, source inventory links (4,5,8,9,13) |
| Hostile uploads | spoofed MIME/extension/magic, unknown content, ≤10MB boundary+over limit/missing Content-Length, quota, truncation, huge dimensions/pixel bomb/multiple frames, EXIF/GPS/ICC removal, HTML/SVG/PDF/archive rejected, scanner unknown/malicious/outage/timeout fail closed (4,5) |
| Upload lifecycle | wrong owner/subject/role binding, receive replay/mutable source denial, finalize/abandon races, worker crash/stale lease, duplicate derivative, abandoned cleanup and hold-specific no erase, delete retry and no unrelated hold freeze (4,5,9,13) |
| Account/consent/flags | restriction/suspension/deletion immediately deny new writes/download/preview/eligibility; grant/flag/referral/profile existence never object authority; registration flag disables only new registration; existing owner setup remains available (2,8–10,12) |
| Audit/outbox | transactions roll back domain changes on evidence failure; raw/signed URL/name/document/baseline sentinel rejected through ORM+bulk+SQL; UUID-only payloads, bounded event fields, duplicate effect/unknown event/stale handler/restart recovery (1,5,7,9,13) |
| Native Persian RTL | actual Playwright owner/dual-profile/baseline resume/optional consent/upload/preview/submission/staff review/rejection/resubmission/revoke; JS disabled, CSRF, reload one effect, current/logout/expired authority, desktop/mobile accessibility/no overflow/strict console (11,12) |
| Scope absence | no public unverified or verified C03 page/search/index/sitemap/card, no public athlete/credential copy, no assistant operational routes, no C04/C05+/C09 app/import/data leakage; no AI network egress (10,12,14) |
| Upgrade/fresh/regression | exact populated C02→C03 same-DB and original source verification; users/UUID/phone/session/auth/governance/table identities preserved, no automatic profiles/auth_user; clean independent chain and full C01/C02 suites (14) |

Security review checklist: verify every read/list/count/attachment/task uses scoped selector; both destination/source ownership; auth_version/state checked under mutation locks; staff capability+assignment+case freshness/non-self; no superuser bypass; C03 declarations confer no relationship authority; metadata-only evidence/outbox direct insertion protected; no source→public ACL toggle; source/derivative sanitization cannot be bypassed by ready flag; SQL immutability/null/uniqueness guards; upload resource/malware limits; lock-order graph and stale worker fencing; held record isolated; deletion/current consent deny before asynchronous cleanup; no C04/C09 routes/indexes/fields; no secrets/private data in browser caches/logs/CI artifacts; no destructive migration, generic directory or future module dependency.

CI execution gates (not run during planning): frozen uv lock/sync/npm; build:css, check:js, hashed collectstatic; Ruff lint/format; existing mypy target set plus new domain/assets/config C03 modules; Django test/production checks, git diff --check; makemigrations --check --dry-run and emitted SQL; all tests/unit + actual PostgreSQL integration (no SQLite substitution/skips); real Redis/Celery/outbox, private MinIO+scanner; actual Playwright C01/C02/C03 flows; existing real broker/storage/quota restart probes plus C03 worker crash/restart; exact C02→C03 populated upgrade and fresh zero-state migration. Preserve docker/verify_c02.sh and all original checks, not just sampled C02 tests. Do not relax stage-specific old C02 scope tests: immutable fixture checks retain old expectations; current-source absence tests may be narrowly expanded to enumerated C03 paths/models after new RED assertions pin privacy/scope, never blanket allowlists.

Planning branch changes only documentation, so the existing workflow (push only accounts/c02-cloud) does not run on profiles/c03-plan. Lack of a plan CI run is expected and not an implementation PASS. Execution later creates a separately authorized implementation branch and its explicit CI trigger; this plan never enables one now.

## 17. Sequential task-by-task TDD execution order

Common bounded recovery discipline: read ledger/task/current git state, preserve all unpublished work, verify baseline/remote before starting; do not recreate completed tasks. Each task first adds its named tests and observes behavior RED (missing import/fixture failure alone is not RED), then implements only its interfaces, runs named GREEN and previous gates, reviews security/migrations, commits coherently and records exact head/tree/CI/evidence. Do not advance a task with unresolved required service/browser/SQL gates. No per-task delegation authorized by this plan. An execution ledger will be created only in execution.

### Task 1: Add domain schemas and bounded governance evidence contracts

**Objective:** Establish additive metadata with exact constraints and evidence allowlists; no routes.

**Files:** Create apps/athletes/__init__.py, apps.py, models.py, baseline_models.py, receipt_models.py, migrations/__init__.py, migrations/0001_initial.py, migrations/0002_current_baseline.py; apps/professionals/__init__.py, apps.py, models.py, profile_models.py, credential_models.py, verification_models.py, assistant_models.py, receipt_models.py, migrations/__init__.py, migrations/0001_initial.py, migrations/0002_current_credential_revision.py, migrations/0003_immutable_evidence.py; apps/assets/models.py, derivative_models.py, migrations/__init__.py, migrations/0001_initial.py; apps/governance/migrations/0011_c03_contracts.py. Modify apps/governance/audit_models.py, outbox_models.py, outbox.py, staff_models.py, consent_models.py, privacy_models.py; config/settings/base.py. Create tests/unit/c03/test_schema_contract.py, tests/integration/c03/conftest.py, test_c03_migrations.py, test_evidence_guards.py. Narrowly update existing current-source model allowlists only with new guarded scope assertions.

**Interfaces:** Produces §4 models/enums, §13 audit/event payload validation and professional_verification grant/step-up CHECK support; no authority from new fields.

- [ ] RED: test_optional_profiles_not_created asserts zero new profile rows after migrating populated C02; test_c03_unique_profiles/roles/live_drafts/live_verification/assignment asserts actual SQL rejects duplicates; test_c03_evidence_append_only rejects ORM/bulk/direct SQL and restricted-role mutation; test_c03_metadata_payload_denies_private_values rejects document/URL/value sentinels and invalid NULL combinations. Existing C02 constraints still reject their invalid fixtures.
- [ ] Run real PostgreSQL tests/integration/c03/test_c03_migrations.py and test_evidence_guards.py; inspect behavioral failures and sqlmigrate output before implementation.
- [ ] Implement only schema/registration and additive allowlist functions/CHECKs, split current-pointer circular FKs as listed. Do not seed profiles/approvals/production policies.
- [ ] GREEN: focused schema+SQL tests; full current unit and C02 PostgreSQL migration/evidence suites, makemigrations --check --dry-run, Ruff/mypy/Django/production checks. No skipped service gate.
- [ ] Review FK/NULL/append-only/runtime-role/privacy metadata guards; commit feat(c03): add private profile and verification metadata. Record migrations and exact SQL evidence.

**Migration impact:** New tables plus governance0011; existing migrations/User untouched. **Security focus:** no public fields/evidence payload bypass. **Commit boundary:** schema+required schema tests only.

### Task 2: Own-profile authorization, creation, receipts and registration flag

**Objective:** Explicit optional dual profiles with current owner authority and retry safety.

**Files:** Create apps/athletes/contracts.py, policies.py, selectors.py, services.py; apps/professionals/contracts.py, policies.py, selectors.py, services.py; config/use_cases/athlete_profile.py, professional_profile.py; tests/unit/c03/test_profile_policy.py, tests/integration/c03/test_owned_profiles.py, test_profile_races.py. Modify apps/accounts/policies.py (finite names only); config/event_handlers.py; create config/c03_event_handlers.py with metadata-only handlers implemented here.

**Interfaces:** create_athlete_profile/create_professional_profile and own_* selectors from §11, receipt reuse; profile commands produce DTO id/version/state with derived owner.

- [ ] RED: test_dual_profiles_one_user asserts independent one-to-ones; test_cross_owner_profile_read_write_count_and_uuid denies all foreign projections; test_profile_create_race yields one row; test_receipt_payload_conflict returns 409 only after authorization; test_profile_flag_is_not_authority denies unrelated access; flag false/outage denies creation but not existing owned setup; old/control/underage/suspended actors denied.
- [ ] Run focused unit policy plus PostgreSQL owned/race tests and observe denial/duplicate failures before code.
- [ ] Implement active current locked_actor, explicit owner selectors/receipts, authoritative create-only flag check and same-transaction audit/outbox. Add action names without changing existing action behavior.
- [ ] GREEN: Task 1 + profile tests and entire C02 state/session/flag/referral suites; PostgreSQL independent-connection state/create/logout races.
- [ ] Review dual-context/non-authority/error ordering; commit feat(c03): authorize explicit owner profile creation.

**Migration impact:** none beyond Task 1. **Security focus:** flags/roles/consent/referral/superuser confer no ownership. **Commit boundary:** creation/read contracts and finite account-action extension.

### Task 3: Dated baseline drafts, self-storage consent and correction

**Objective:** Resumable minimal setup with optional facts protected and immutable submitted history.

**Files:** Create apps/athletes/baseline.py, validation.py, consent.py, privacy.py; config/use_cases/c03_privacy.py; tests/unit/c03/test_baseline_fields.py, test_consent_callback_contract.py; tests/integration/c03/test_baseline_workflow.py, test_baseline_consent.py, test_baseline_races.py. Modify apps/athletes/contracts.py, selectors.py; config/use_cases/athlete_profile.py; apps/governance/consents.py and config/use_cases/consent.py to accept bounded server scope callback (unknown default denied); use Task 1 baseline_storage SQL purpose.

**Interfaces:** save_baseline_step, submit_baseline, correct_baseline plus clear_optional_baseline(actor,baseline_uuid,expected_version,operation_id,at); baseline-storage validation and current filtering from §5. begin_baseline creates/resumes the single owned draft under the profile lock; correct_baseline creates the next draft after a submitted predecessor. grant_baseline_storage(actor, baseline_uuid, expected_version, confirmed, operation_id, at) and revoke_baseline_storage(actor, baseline_uuid, consent_uuid, expected_consent_version, operation_id, at) expose only the server-produced self-scope/disclosure; confirmed defaults false.

- [ ] RED: test_resume_partial_steps retains committed answers/version; test_optional_decline_is_unknown_and_completes_setup; test_storage_grant_cannot_share rejects other grantee/purpose/owner/schema; test_health_photo_unknown_fields_rejected; test_submit_freezes_answers and test_correction_new_snapshot preserve predecessor; test_concurrent_save_submit/revoke has serialized safe outcome; test_new_correction_does_not_copy_optional_without_consent.
- [ ] Run unit field/consent tests and real PostgreSQL workflow/consent/races, observe actual missing snapshot/permission behavior.
- [ ] Implement typed schema/step limits, existing C02 age/date authority, self-consent through composition callbacks revalidated under locks, current optional filtering, receipt/version freeze/correction. No health/photo model/UI.
- [ ] GREEN: Tasks 1–2, all named baseline cases, C02 consent terminal SQL and revocation/state races, full unit suite. Verify expired consent and missing values never produce a diagnosis or mandatory sensitive gate.
- [ ] Review optional storage/consent/immutable revision/unknown-field exclusion; commit feat(c03): add private resumable baseline snapshots.

**Migration impact:** none; schema already installed. **Security focus:** no invented medical/photo/longitudinal collection. **Commit boundary:** baseline command/consent contracts only.

### Task 4: Owned bounded quarantine upload and finalization

**Objective:** Accept one private immutable source safely without releasing it before processing.

**Files:** Create apps/assets/contracts.py, policies.py, uploads.py, delivery.py, validation.py; config/use_cases/profile_assets.py; tests/unit/c03/test_upload_contract.py, test_asset_validation.py; tests/integration/c03/test_upload_lifecycle.py, test_upload_races.py, test_private_assets.py. Modify apps/assets/storage.py; config/settings/env.py, base.py, test.py, production.py; apps/professionals/policies.py for purpose/binding validators.

**Interfaces:** begin/receive/finalize/abandon upload and AuthorizedAssetRead (§11); new bounded store read_limited(key,max_bytes)/put_stream(key,stream,content_type,max_bytes) with existing methods preserved.

- [ ] RED: test_foreign_upload_binding_and_download_denied asserts zero storage read/sign calls; test_size_limit_without_content_length; test_spoofed_type_extension_signature; test_receive_source_once; test_finalize_quarantines_not_ready; test_finalize_abandon_and_logout_races; test_daily_and_pending_upload_quota; test_late_body_after_expiry_denied.
- [ ] Observe real PostgreSQL/FakePrivateStore failures then real private MinIO roundtrip/anonymous-403 using existing infrastructure, not mocked S3 permissions.
- [ ] Implement proxy upload reservation/version/I/O boundary, opaque immutable key/size/hash, current owner/purpose validation, metadata audit+asset processing outbox. No decoder/scanner-ready shortcut or public storage changes.
- [ ] GREEN: previous tasks + focused lifecycle/races, existing test_storage/test_minio_storage and C02 current-state gates; bounded streaming verifies cap with absent/lying header.
- [ ] Review CSRF adapter prerequisites, resource cap/ownership/I/O races; commit feat(assets): add private quarantined profile uploads.

**Migration impact:** none. **Security focus:** never ready on client metadata or storage timeout. **Commit boundary:** quarantine lifecycle/storage extension.

### Task 5: Isolated scan/sanitization and durable processing recovery

**Objective:** Release only safe private derivatives after resource-bounded processing.

**Files:** Create apps/assets/processing.py, scanner.py, images.py, tasks.py, processing_worker.py; tests/unit/c03/test_image_sanitization.py, test_scanner_contract.py; tests/integration/c03/test_asset_processing.py, test_processing_worker.py, test_scanner_service.py; tests/fixtures/c03/asset_manifest.json and deterministic synthetic JPEG/PNG fixtures; docker/Clamav.Dockerfile. Modify config/c03_event_handlers.py, config/celery.py, config/settings/base.py/env.py/test.py/production.py, compose.yaml, Dockerfile, pyproject.toml, uv.lock, docs/development/DEPENDENCIES.md. Create docs/implementation/C03_SETUP.md with dependency review/source/version/license/digest/limits and production closure.

**Interfaces:** process_asset(asset_uuid,processing_version,lease_uuid,at) → bounded result; scan_due_assets(at,batch_size≤100) → count; scanner.clean result never substitutes for successful sanitize; outbox handler creates unique durable attempt only.

- [ ] RED: test_clean_pixels_strip_all_metadata, test_bomb_truncated_multiframe_invalid_format, test_scanner_malicious_unknown_timeout_and_stale_signature_closed, test_duplicate_derivative_effect, test_processing_stale_lease_or_deleted_owner_cannot_release, test_crash_after_outbox_receipt_before_prompt_recovers. Assert task/log sentinels contain no bytes/private paths/URL.
- [ ] Record official Pillow/ClamAV patched release/license/maintenance/advisory review before dependency changes. Observe deterministic behavioral RED with fake scanner and isolated processor, and service RED on real worker/MinIO/scanner; fixture setup failures do not satisfy RED.
- [ ] Pin reviewed Pillow version/hashes and private scanner image digest during execution only; implement permitted-format full decode/resource isolation, scan/versioned derivatives and durable attempt reconciler. Fail closed production if scanner/isolated delivery absent; no external AI or sensitive telemetry.
- [ ] GREEN: deterministic decode/metadata/output checks and real scanner clean/malicious INSTREAM/timeout/limits, non-eager Celery/process-crash recovery, all storage+C02 outbox/worker/restart suites; frozen locks/static/quality gates.
- [ ] Review native decoder CVEs/resource limits, scanner no content egress and long-I/O transaction separation; commit feat(assets): sanitize private media with durable scan recovery.

**Migration impact:** no new schema unless reviewed findings require a separately named additive migration, recorded before proceeding. **Security focus:** unknown/exhausted scans stay unusable. **Commit boundary:** processor plus justified dependency/config/review record.

### Task 6: Professional steps, declared roles, locations and credential revisions

**Objective:** Resumable private setup and evidence changes with exact binding semantics.

**Files:** Create apps/professionals/validation.py, credentials.py, setup.py, verification.py (bound_revision_changed helper only); tests/unit/c03/test_professional_fields.py, test_verification_binding.py; tests/integration/c03/test_professional_setup.py, test_credential_revisions.py, test_bound_edit_races.py. Modify apps/professionals/contracts.py, services.py, selectors.py; config/use_cases/professional_profile.py; create config/use_cases/professional_verification.py for shared orchestration wiring as functionality arrives.

**Interfaces:** save_professional_step; create_credential(actor,input,expected_profile_version,operation_id,at), revise_credential(actor,credential_uuid,input,expected_version,operation_id,at), withdraw_credential(same authority/version); bound_revision_changed callback/transition owned by professionals.

- [ ] RED: test_coach_nutritionist_both_are_rows_not_auth; test_resume_and_in_person_location_gate; test_cosmetic_change_retains_binding; parameterized test_each_bound_field_increments_revision for exact §7 set; test_foreign_or_unready_asset_cannot_attach; test_submitted_source_immutable; test_assistant_role_has_no_setup_access. Bound edits must never leave matching eligibility or an in-flight snapshot silently changed.
- [ ] Run focused field/binding and actual PostgreSQL setup/credential/race suites, inspect missing expected binding behavior.
- [ ] Implement bounded step/state completion, role deactivation/history, private metadata revisions and typed owner asset validation, uniform version/receipt command contracts. No billing, packages/address/slug/public credentials.
- [ ] GREEN: Tasks 1–5 plus credential ownership/history/current-state/role race tests and C02 authorization suites; all fields roundtrip Persian safely.
- [ ] Review declaration/verification distinction and identity evidence minimization; commit feat(professionals): add resumable setup and private credential revisions.

**Migration impact:** none. **Security focus:** no verified capability from declaration/source attachment. **Commit boundary:** setup/role/location/credentials.

### Task 7: Immutable submission, assignment and bounded staff reads

**Objective:** Real case authority before evidence review, including fresh assignment and read audit.

**Files:** Modify apps/professionals/verification.py; create apps/professionals/verification_selectors.py; tests/unit/c03/test_verification_contract.py; tests/integration/c03/test_verification_submission.py, test_verification_staff.py, test_verification_assignment_races.py. Modify config/use_cases/professional_verification.py; config/c03_event_handlers.py; apps/professionals/selectors.py; apps/assets/delivery.py for authorized staff derivative-only policy; raw source delivery remains denied.

**Interfaces:** prepare/submit/withdraw/assign/start review and assigned detail/evidence/queue from §11; required governance callbacks, current version/snapshot hash/evidence links.

- [ ] RED: test_submit_freezes_bound_snapshot, test_duplicate_submission_and_new_resubmission_bundle, test_staff_without_capability_assignment_fresh_stepup_or_nonself_denied, test_bare_superuser_no_shortcut, test_reassignment_invalidates_old_reviewer, test_queue_minimal_and_bounded, test_audit_failure_prevents_evidence_read. Queue access must not confer case evidence access.
- [ ] Observe PostgreSQL real grant/step/assignment/SQL immutability and read-audit failures; repeat concurrency with independent connections for submit/edit/reassign.
- [ ] Implement finite state machine and live assignment through existing require_staff; audit before evidence release, owner coarse history, case-specific version/freshness; no generic staff directory/override.
- [ ] GREEN: Task 6 plus all submission/staff/assignment tests and complete C02 staff/recovery/audit rollback suites; verify source privacy remains unchanged by submission.
- [ ] Review privacy/conflict separation/step-up handling and live-assignment races; commit feat(professionals): submit immutable verification cases for assigned review.

**Migration impact:** none. **Security focus:** current actor/capability/assignment/reason/step-up on reads as well as writes. **Commit boundary:** submission and review intake.

### Task 8: Staff decisions, stale review, revocation and eligibility primitive

**Objective:** Synchronous immutable decisions with query-time publication denial under changing facts.

**Files:** Modify apps/professionals/verification.py, verification_selectors.py, selectors.py, credentials.py; config/use_cases/professional_verification.py. Create tests/unit/c03/test_publication_eligibility.py; tests/integration/c03/test_verification_decisions.py, test_verification_decision_races.py, test_verification_revocation.py.

**Interfaces:** decide/revoke and publication_eligibility (§11/§7); read result never public projection or relationship permission.

- [ ] RED: test_one_concurrent_approve_reject_terminal_decision; test_edit_while_decide_two_orders; test_decision_replay_vs_changed_payload; test_identity_plus_all_requested_credentials_required; test_expired_withdrawn_or_quarantined_evidence_denies; test_rejection_history_retained_resubmit_new_bundle; test_revocation_immediate_eligibility_false; parameterized test_account_state_and_auth_change; cosmetic fields retain eligibility but no public route exists.
- [ ] Run actual PostgreSQL barriers/constraints and C02 state/logout/deletion interleavings; observe behavioral race/eligibility RED.
- [ ] Implement profile-first locking, expected bound revision/snapshot/assignment/state rechecks, immutable decision/history plus transactional audit/outbox, expiry-current eligibility. No public status toggle or role-granted authority.
- [ ] GREEN: Tasks 1–7 + decisions/races/revoke/eligibility matrix; full C02 audit/session/privacy/consent suites; direct SQL history mutation denied.
- [ ] Review stale decision and temporary restriction semantics; commit feat(professionals): enforce revision-bound verification and eligibility.

**Migration impact:** none. **Security focus:** no stale approvals/automatic republishing/superuser bypass. **Commit boundary:** decisions/revocation/eligibility.

### Task 9: Domain privacy inventory, holds and bounded private cleanup

**Objective:** Erase only eligible abandoned/revoked assets and isolate retained evidence without access.

**Files:** Create apps/assets/privacy.py, cleanup.py; apps/professionals/privacy.py; tests/unit/c03/test_privacy_inventory.py; tests/integration/c03/test_asset_holds.py, test_c03_deletion_effects.py, test_asset_cleanup_races.py. Modify apps/athletes/privacy.py; config/use_cases/c03_privacy.py, config/c03_event_handlers.py, config/event_handlers.py; apps/governance/retention.py (reviewed callback only), apps/assets/tasks.py/processing_worker.py; config/settings/base.py for installed bounded cleanup schedule.

**Interfaces:** inventory_c03_owner; enumerate_asset_inventory; cleanup_asset(asset_uuid,expected_version,policy_uuid,at) → bounded status; validate_c03_hold_subject/case; existing security/consent/hold events compose registered current-state effects.

- [ ] RED: test_hold_specific_source_derivatives_not_other_media; test_forged_subject_or_case_or_version_denied; test_cleanup_without_effective_policy_denied; test_overdue_review_not_silent_release; test_released_expired_hold_allows_eligible_retry; test_hold_vs_cleanup_race; test_deletion_owner_denies_release_preview_and_stale_task; test_retained_evidence_not_normal_access; test_orphan_late_upload_reconciled.
- [ ] Observe real PostgreSQL+MinIO cleanup/hold interleavings and existing C02 hold behavior before code; no actual production retention period.
- [ ] Implement exact inventory/callback revalidation and versioned policy-controlled deletion across source/derivative keys; registered account/consent effects deny/revoke without reopening accounts or full C18 deletion.
- [ ] GREEN: all previous tasks + hold/cleanup/deletion tests, C02 privacy/retention/outbox restart regression, idempotent storage delete failure/recovery with held objects intact.
- [ ] Review lifetime/hold/access separation and deletion inventory completeness; commit feat(c03): integrate private asset retention and record-specific holds.

**Migration impact:** none beyond Task 1 enumerated subject CHECKs. **Security focus:** no blanket hold or privilege from retention. **Commit boundary:** C03 privacy/cleanup only.

### Task 10: Owner-only preview, inert assistant primitive and C04 scope guard

**Objective:** Safe private presentation and future eligibility facts without operational/public features.

**Files:** Create apps/professionals/preview.py, assistants.py; tests/unit/c03/test_scope_boundary.py; tests/integration/c03/test_owner_preview.py, test_assistant_primitive.py, test_c03_dependency_direction.py. Modify apps/professionals/selectors.py/contracts.py; config/use_cases/professional_profile.py.

**Interfaces:** owner_preview; define_assistant_role(actor,assistant_uuid,operation_id,at) and revoke_assistant_role(actor,membership_uuid,expected_version,operation_id,at) are internal trusted primitives only, no public API/UI/activation. All C03 selectors reject membership authority.

- [ ] RED: test_unverified_verified_preview_owner_only_and_noindex; test_preview_dto_no_evidence_keys_or_staff_notes; test_assistant_fixed_role_never_grants_access to health/inbox/profile/evidence/plans; test_no_c04_route_index_projection_or_c09_fields; test_eligibility_input_only_no_public_copy; dependency tests deny upstream imports.
- [ ] Run focused DTO/scope and PostgreSQL context/assistant tests before implementation, with all denied future names explicit.
- [ ] Implement allowlisted preview and inert role validation/non-self membership; no client IDs/operational grants/entitlement assumption/max-two activation rule until C06 catalog.
- [ ] GREEN: previous tasks + cross-owner/assistant/scope absence/dependency tests and existing scope suites retained on immutable C02 fixture.
- [ ] Review no public/assistant/relationship authority leakage; commit feat(c03): expose private owner preview and bounded role primitives.

**Migration impact:** none. **Security focus:** private preview for all verification states, no active assistant access. **Commit boundary:** presentation DTO and role primitive.

### Task 11: Session/CSRF API adapters and native owner Persian RTL setup

**Objective:** Expose only approved owner commands through consistent API/native forms.

**Files:** Create apps/athletes/api.py, serializers.py, forms.py, views.py, urls.py; apps/professionals/api.py, serializers.py, forms.py, views.py, urls.py; apps/assets/api.py, serializers.py, views.py, urls.py; templates/athletes/setup.html, baseline.html; templates/professionals/setup.html, preview.html, verification.html; static/src/profiles.js; tests/unit/c03/test_api_schema.py, test_forms.py, test_native_adapters.py; tests/integration/c03/test_owner_api.py; tests/e2e/c03/conftest.py, helpers.py, test_owner_setup.py, test_private_uploads.py. Modify config/urls.py, templates/accounts/me.html, static/src/app.js, package.json (module syntax check only), config/api_security.py only for bounded multipart parser/error integration if required.

**Interfaces:** exact owner route inventory §11; same DTO/input/composition services, native redirect after command. No new consumer authentication.

- [ ] RED: test_csrf_before_profile_and_upload_side_effect; test_unknown_owner_state_fields_denied; test_api_no_store_uniform_403_404_409_503; Playwright test_owner_dual_context_resume_optional_consent, test_upload_quarantine_status_and_private_preview, test_js_disabled_setup, test_logout_or_switch_account_denied, test_private_data_not_browser_cached. Verify schema/HTML excludes later features.
- [ ] Observe actual HTTP/PostgreSQL and Playwright behavioral RED at both viewports; fixture/event-loop failures must be diagnosed before claiming RED.
- [ ] Implement explicit routes/serializers/native Persian forms and minimal ES enhancements. Keep 4096-byte step payloads/proxy limit, existing CSRF/session adapters, validated safe redirects, no evidence in preview DTOs.
- [ ] GREEN: full previous backend+C02 HTTP/browser suites and all new owner browser cases, strict console/pageerrors/layout/static checks; JS disabled flows work.
- [ ] Review adapters never perform ORM authorization/role checks independently of services; commit feat(c03): add private Persian profile and baseline flows.

**Migration impact:** none. **Security focus:** enumerated routes only, CSRF before storage writes, no browser secrets/cache. **Commit boundary:** owner presentation/adapters/browser evidence.

### Task 12: Bounded staff Persian RTL case review adapters

**Objective:** Staff review/read/decision UI preserves full capability/assignment/freshness contract.

**Files:** Create apps/professionals/staff_api.py, staff_forms.py, staff_views.py; templates/professionals/staff_verification_queue.html, staff_verification.html; tests/unit/c03/test_staff_adapters.py; tests/integration/c03/test_verification_api.py; tests/e2e/c03/test_staff_verification.py. Modify apps/professionals/urls.py/serializers.py and apps/assets/views.py only for assigned evidence proxy.

**Interfaces:** exact staff routes §11; trusted assignment and step-up references, case-bound reason/expected versions, successful POST→redirect→GET with fresh authority recheck.

- [ ] RED: Playwright test_assigned_staff_approve_reject_resubmit_revoke and parameterized deny_capability_assignment_expired_stepup_crosscase_self_superuser; test_decision_reload_single_effect; test_evidence_read_audited_and_no_source_url; test_public_search_and_profile_paths_absent; test_case_revoked_between_post_and_get_denied.
- [ ] Observe real PostgreSQL/browser RED using existing memory-only mock authority pattern; screenshots/traces/log secrets remain disabled, no auth bypass.
- [ ] Implement reasoned minimal case context, authorized private evidence delivery and redirect; no staff User directory, grant editor, unaudited notes/export or exception override.
- [ ] GREEN: previous tasks + all actual staff desktop/mobile cases, C02 staff recovery/reload/step-up suites, strict diagnostics and native CSRF tests.
- [ ] Review staff field minimization/nonself/purpose/download isolation; commit feat(c03): add assigned Persian staff verification review.

**Migration impact:** none. **Security focus:** read and write authority rechecked, no superuser or public route. **Commit boundary:** staff adapters/browser evidence.

### Task 13: Full worker/storage/concurrency failure rehearsal and CI wiring

**Objective:** Prove current permissions and idempotent processing across crashes/restarts, then run all gates on execution branch.

**Files:** Create docker/c03_asset_restart_probe.py; tests/integration/c03/test_c03_failure_recovery.py; tests/unit/c03/test_ci_contract.py. Modify .github/workflows/ci.yml (explicit separately authorized execution branch only), docker/verify_foundation.sh to run installed c03 suites/browser in separate process with C02 preserved, config/celery.py/compose.yaml only if proven missing limits; docs/implementation/C03_SETUP.md. No planning-branch CI trigger.

**Interfaces:** prepare/verify processing-restart probe on task-only database/private storage; existing durable outbox/celery leases/effects remain authoritative.

- [ ] RED: test_processor_crash_before_after_derivative_write_before_commit, test_scanner_storage_broker_failure_recovered, test_current_state_consent_hold_during_job, test_bounded_exhaustion_never_ready and test_existing_c02_gates_not_removed; actual probe leaves pending work, restart recovers one effect.
- [ ] Observe service failure injections and missing CI gate assertions before wiring/fixes; never count inaccessible service as safe behavior PASS.
- [ ] Add deterministic fixtures/real service probes and bounded recovery correction only where a test demonstrates a gap; CI keeps existing jobs plus c03 backend/storage/browser/SQL gates. Record engine/signature fixture/digest/retry evidence without raw content.
- [ ] GREEN: real PostgreSQL, Redis/non-eager Celery, private MinIO/scanner restart, all concurrency/upload cases, every C01/C02/C03 suite; no selected skip. Quality/frozen/type/static gates green.
- [ ] Review lock graph/wake-up durability/leases/stale release; commit test(c03): verify private processing recovery and full regression gates.

**Migration impact:** none expected; any new fix migration explicitly reviewed/tested before synchronization. **Security focus:** retries cannot release unauthorized material or delete held evidence. **Commit boundary:** proven resilience and execution CI.

### Task 14: Exact populated C02 upgrade, clean migration and final handoff

**Objective:** Establish compatibility evidence and completed C03 exit without merger/publication.

**Files:** Create docker/c03_source_manifest.json, c03_baseline.py, c03_upgrade_probe.py, verify_c03.sh; tests/unit/c03/test_exact_baseline.py, test_final_rehearsal.py; tests/integration/c03/test_upgrade_from_c02.py; docs/implementation/C03_HANDOFF.md, C03_EXECUTION_LEDGER.md (ledger exists from execution start and is finalized here). Modify .github/workflows/ci.yml for exact fixture/gates; C03_SETUP.md. Preserve existing docker/verify_c02.sh and immutable C01/C02 fixtures.

**Interfaces:** §15 immutable verifier/source tree and prepare/verify same-database probe, independent fresh C03 run; no new business command.

- [ ] RED: test_exact_c02_source_tamper_missing_extra_symlink; test_upgrade_probe_preserves_all_c02_rows_sessions_governance_oid_and_no_profiles; test_final_gates_include_all_c02_and_real_c03_services_browser; actual same-database probe assertions must fail without planned rehearsal.
- [ ] Implement only verifier/probes/CI/docs from §15, then run exact original C02 source suites/population, same-DB upgrade and independent clean C03 chain. Never replace this with migration historical-model fixture tests alone.
- [ ] GREEN: all §16 gates with actual Actions job logs/head/tree, full previous suites, no migration drift/default auth_user/automatic profiles, all live-service/browser/restart/upgrade checks. Verify protected refs unchanged and current local/remote source tree equality.
- [ ] Conduct fresh self-review against §16 security checklist and task/source requirements; independently review whole branch when execution authorization permits reviewer delegation, otherwise explicitly record review method. Critical/Important findings require reproduced RED→GREEN and final corrected-head full gates before PASS.
- [ ] Commit docs(c03): record verified private profiles and verification handoff; final ledger records exact heads/trees/tests/CI/review/deferred release dependencies. Stop; no C04/publication/merge/deploy.

**Migration impact:** rehearsal proves cumulative additive chain only. **Security focus:** backward auth/privacy invariants, scope absence and review findings. **Commit boundary:** compatibility evidence and final docs, not new functionality.

### Exact task verification commands

These commands are instructions for later authorized execution, not planning actions. Run from the implementation checkout with the same validated PostgreSQL/Redis/private MinIO environment as C02_SETUP; scanner-specific tests additionally use the private Compose scanner. For every row, run the focused command before implementation and require behavioral FAIL, then rerun after implementation and require exit 0/PASS with no selected skips. Unit tests run without service substitution for integration tests. The inherited `--ds=config.settings.test` applies.

| Task | Focused RED→GREEN command |
|---|---|
| 1 | `uv run --frozen pytest tests/unit/c03/test_schema_contract.py tests/integration/c03/test_c03_migrations.py tests/integration/c03/test_evidence_guards.py -q --strict-markers` |
| 2 | `uv run --frozen pytest tests/unit/c03/test_profile_policy.py tests/integration/c03/test_owned_profiles.py tests/integration/c03/test_profile_races.py -q --strict-markers` |
| 3 | `uv run --frozen pytest tests/unit/c03/test_baseline_fields.py tests/unit/c03/test_consent_callback_contract.py tests/integration/c03/test_baseline_workflow.py tests/integration/c03/test_baseline_consent.py tests/integration/c03/test_baseline_races.py -q --strict-markers` |
| 4 | `uv run --frozen pytest tests/unit/c03/test_upload_contract.py tests/unit/c03/test_asset_validation.py tests/integration/c03/test_upload_lifecycle.py tests/integration/c03/test_upload_races.py tests/integration/c03/test_private_assets.py tests/integration/test_minio_storage.py -q --strict-markers` |
| 5 | `uv run --frozen pytest tests/unit/c03/test_image_sanitization.py tests/unit/c03/test_scanner_contract.py tests/integration/c03/test_asset_processing.py tests/integration/c03/test_processing_worker.py tests/integration/c03/test_scanner_service.py -q --strict-markers` |
| 6 | `uv run --frozen pytest tests/unit/c03/test_professional_fields.py tests/unit/c03/test_verification_binding.py tests/integration/c03/test_professional_setup.py tests/integration/c03/test_credential_revisions.py tests/integration/c03/test_bound_edit_races.py -q --strict-markers` |
| 7 | `uv run --frozen pytest tests/unit/c03/test_verification_contract.py tests/integration/c03/test_verification_submission.py tests/integration/c03/test_verification_staff.py tests/integration/c03/test_verification_assignment_races.py -q --strict-markers` |
| 8 | `uv run --frozen pytest tests/unit/c03/test_publication_eligibility.py tests/integration/c03/test_verification_decisions.py tests/integration/c03/test_verification_decision_races.py tests/integration/c03/test_verification_revocation.py -q --strict-markers` |
| 9 | `uv run --frozen pytest tests/unit/c03/test_privacy_inventory.py tests/integration/c03/test_asset_holds.py tests/integration/c03/test_c03_deletion_effects.py tests/integration/c03/test_asset_cleanup_races.py -q --strict-markers` |
| 10 | `uv run --frozen pytest tests/unit/c03/test_scope_boundary.py tests/integration/c03/test_owner_preview.py tests/integration/c03/test_assistant_primitive.py tests/integration/c03/test_c03_dependency_direction.py -q --strict-markers` |
| 11 | `uv run --frozen pytest tests/unit/c03/test_api_schema.py tests/unit/c03/test_forms.py tests/unit/c03/test_native_adapters.py tests/integration/c03/test_owner_api.py -q --strict-markers`; separately `uv run --frozen pytest tests/e2e/c03/test_owner_setup.py tests/e2e/c03/test_private_uploads.py -q --strict-markers --tracing=off --screenshot=off --video=off` |
| 12 | `uv run --frozen pytest tests/unit/c03/test_staff_adapters.py tests/integration/c03/test_verification_api.py -q --strict-markers`; separately `uv run --frozen pytest tests/e2e/c03/test_staff_verification.py -q --strict-markers --tracing=off --screenshot=off --video=off` |
| 13 | `uv run --frozen pytest tests/unit/c03/test_ci_contract.py tests/integration/c03/test_c03_failure_recovery.py -q --strict-markers`; real isolated Compose prepare/restart/verify probe is wired in this task and must execute in required CI |
| 14 | `uv run --frozen pytest tests/unit/c03/test_exact_baseline.py tests/unit/c03/test_final_rehearsal.py tests/integration/c03/test_upgrade_from_c02.py -q --strict-markers`; `sh docker/verify_c03.sh` for the exact-source/populated upgrade, clean state and full service/browser/restart rehearsal |

After each focused GREEN, require `uv run --frozen pytest tests/unit -q --strict-markers`, the complete installed `tests/integration/c03` plus C02 integration directory and initial migration tests against real PostgreSQL, and existing C02_SETUP quality/static/production commands. Tasks introducing browser behavior require all installed C03 and all C02 browser files in separate supported async processes; immutable C01 smoke remains its own process. Final full gate is `sh docker/verify_c03.sh`, which explicitly invokes original `docker/verify_c02.sh` within the exact C02 fixture and the current complete rehearsal. The execution ledger records actual commands, exit codes, counts and job logs, not this command table as evidence.

### Bounded governance callback interfaces

Task 3 extends existing consent functions with optional keyword `scope_validator: Callable[[ValidatedConsentScope, User], bool] | None = None`. Existing account_metadata validation remains the default. A C03 callback is server code supplied by config/use_cases/c03_privacy.py, recognizes only baseline_storage/athlete_baseline schema 1/self-grantee, resolves the owner row and acquires/revalidates the profile/baseline anchor during grant. validate_scope, grant_consent and has_current_grant all reapply the same callback; no consumer can provide a callable or a kind-registration endpoint. Existing `_valid_scope` common checks still run. Do not add health/share/AI/publication validators.

Task 9 extends retention functions with optional server keyword `subject_validator: Callable[[ValidatedRecordSubject], bool] | None = None` and, for apply_hold, `case_validator: Callable[[ValidatedRecordSubject, UUID, User], bool] | None = None`. Existing privacy_request validation remains the default. C03 composition first locks the owner/subject anchors, supplies exact installed-domain validators and calls existing require_staff/privacy_operations; validation occurs again before hold read/write/cleanup. Arbitrary constructed dataclasses, unknown kinds, wrong owner/version or unrelated case return false. This changes only the demonstrated installed-subject gap, not staff permission semantics or a new authorization framework.

## 18. Commit/checkpoint strategy and recovery

Planning branch: one coherent docs-only commit adding this file, parent exactly 0905be6. Do not update risk register absent a genuinely new unresolved product question. Authenticated create_file/commit API may be used if shell authentication unavailable; verify target branch expected head immediately before write, parent afterward, exact file/blob and one-file compare, then recheck protected refs. Never force-update an existing ref or publish synthetic local ancestry. If branch exists with unexpected work, inspect and preserve it; do not recreate/reset.

Later execution requires separately authorized branch/method; do not execute this planning branch by implication. At execution start create C03_EXECUTION_LEDGER with fixed C02 baseline, plan blob/hash, environment, protected refs and Task 1 pending. Each task records start/RED/implementation/GREEN/security/migration/checkpoint/status with exact local and remote commit/tree and CI run link. Use separate test-spec RED and implementation GREEN commits where required for real CI; ledger-only status commits never substitute for source CI. Preserve unfinished staged/unstaged/untracked files and original evidence after interruption; inspect local vs remote before resume. PENDING_CI/BLOCKED are real states, not PASS. No repeated completed tasks or clean/reset/stash over user work. Keep private rehearsal manifests/logs ignored and restricted.

## 19. Exit criteria, blocking questions and operational dependencies

Implementation exit: all 14 tasks complete in order; both profiles optional/unique; baseline/setups resume and correct immutably; current owner/CSRF/session checks on every surface; declared roles never confer verified/public/athlete authority; assigned reasoned step-up staff review/immutable decisions/stale races/revocation verified; source evidence has no download route and private derivatives remain private; safe scan/quarantine/finalize/abandon/holds/restart proven; inert assistant role no operational authority; query-time eligibility implemented with zero C04 routes/copies/indexes; exact C02→C03 and fresh zero-state migrations plus all C01/C02 regression green; no unresolved Critical/Important review finding. Passing these engineering gates is not permission for live rollout.

## Blocking Product Questions

None for this bounded C03 plan. Both profiles and role rows are explicit in the sources; current mandate resolves C04/C09 allocation and evidence privacy. Baseline completeness is C03 setup only, not a fabricated future coaching-request gate. Technical decisions (revision binding, all-or-nothing requested roles, raster allowlist, stale decision rules, lock order, internal membership primitive and proxy delivery) are stated here. Existing operational evidence/retention/catalog choices stay release dependencies, not invented product answers.

Release dependencies: approved identity and role-specific credential evidence checklists (identity/qualification naming above are metadata categories, not fabricated proof standards); authorized verifier assignment/conflict procedures and real verified MFA integration (C02 has only mock/disabled installed); production verification switch remains closed until provider/config tests; approved privacy/consent wording, retention durations/hold review and backup policies; authenticated sanitized derivative proxy and malware scanner engine/signature freshness/isolation; isolated original-download design remains deferred; reviewed pinned Pillow/ClamAV artifacts/security/license notices and maintenance owner; object storage ACL/network/secrets and scan/queue/backlog/retry/operator alerts. Core Free branding remains available; advanced branding/assistant activation catalog remains C06/C13. No SMS/payment/AI vendor is selected. Full privacy exports/erasure/backup restore are C18/C20 integration, not claimed complete here.

## 20. Planning self-review findings

Reviewed the completed draft against authoritative requirements, the 32 required output areas, every named negative test and existing C02 implementation surfaces. Corrected bounded design hazards before finalization:

- Closed account actions and governance DB allowlists require explicit additive extensions; a new profile service cannot silently call unknown actions or persist unsafe metadata.
- Governance consent/hold validators currently accept only C02 subjects; composition callbacks are revalidated and preserve dependency direction/default-deny rather than importing profiles upstream.
- Long scan I/O must not run inside existing dispatch_event transaction; durable AssetProcessingAttempt plus reconciler preserves crash recovery after receipt.
- Current-pointer FK cycles require split additive migrations; User/C02 rows receive no profile backfill.
- Baseline product mentions injuries/photos, but current C03 mandate allocates those to C09. C03 rejects their inputs and preserves optional/unknown/self-storage boundaries.
- Credential evidence cannot be reused as preview/public media; approval changes no ACL/classification. Raster sources are bounded and isolated; public copies and PDF/active-format support are not silently added.
- Bound edits make old approval ineligible without revoking for cosmetic presentation changes; explicit snapshot/version locks pin decision races and immutable rejection/resubmission history.
- Assistant membership remains defined metadata, no active client/workspace authority or guessed entitlement policy. Both means two role rows, no mixed privilege context.
- Account restriction/consent/credential expiry deny at query/release time even if events/Beat delayed; retention and holds never restore ordinary access.
- Exact populated original C02 runtime is required in the same database, separately from historical-model and clean migration tests; C01/C02 suites and secret-safe browser harness remain mandatory.

No C04/C05+/C09 implementation, public discovery/file manager, broad assistant authority, generic CRUD/account enumeration, JWT architecture, new unreviewed production evidence standard or destructive migration is planned. Review was performed by the planning author using a separate requirement/security/contract pass, not represented as an independent subagent review. No implementation test PASS is claimed by this document. Stop after the planning commit is synchronized and verified.
