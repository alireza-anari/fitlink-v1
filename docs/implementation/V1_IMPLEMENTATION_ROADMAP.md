# FitLink V1 implementation roadmap

Stage 2 planning, 2026-10-03. **Do not execute this roadmap in Stage 2.** C01–C20 are coding milestones, distinct from the conversation's Stage 1/Stage 2 design work. The next authorized coding stage would be C01 only. Authority: [product specification](../product/V1_PRODUCT_SPEC.md), [architecture](../architecture/V1_ARCHITECTURE.md), [domain model](../architecture/DOMAIN_MODEL.md), [permissions](../architecture/PERMISSIONS_MATRIX.md) and [remaining risks](../product/OPEN_QUESTIONS_AND_RISKS.md).

Only C01 has a detailed execution plan: [2026-10-03-project-foundation.md](../superpowers/plans/2026-10-03-project-foundation.md). Later milestones require their own bounded plan/review before execution, not speculation about exact source files here. None may silently change locked V1 scope.

## Ordering and shared exit discipline

The twenty-stage progression is retained with three dependency refinements: minimal Custom User is in C01 before all auth migrations; audit/account restriction and consent primitives precede private records; entitlement admission is in C06 before paid gateway integration in C13. Health/media/consent UX completion is C09, but no earlier domain gets to defer permission checks until then. Staff/admin actions arrive with their domain and C18 completes cross-domain workflows. Marketplace C04 is verified-profile discovery; package cards/details appear only when C05 offers exist, with no fabricated prices/reviews or actionable request CTA before its prerequisites.

Each milestone must leave boot, migration consistency and the previously completed suites passing. Use PostgreSQL for constraint/concurrency tests, fake providers for deterministic tests, service boundaries for composition and current permissions for derived outputs. No stage relies on unimplemented future modules at import time. Additive migrations preserve history and `AUTH_USER_MODEL`; publish no incomplete workflow to beta users. Live rollout occurs only after C19/C20 gates. Every stage updates relevant docs and has reviewable small commits.

## C01 — Project Foundation

- **Goal:** reproducible stack skeleton only, with minimal Custom User for migration safety.
- **Domains:** config/runtime, accounts identity minimum, assets storage interface only.
- **Prerequisites:** approved Foundation plan and explicit execution authorization; Python/Docker/Node tooling access.
- **Deliverables:** locked dependencies, split settings/env validation, PostgreSQL/Redis, Celery/Beat/ASGI/Channels/DRF, local Compose/MinIO, Tailwind/RTL base, logging/health, pytest/Playwright/CI/docs.
- **Migrations:** only accounts/0001_initial for minimal User plus Django built-ins using the swapped user; no profiles/OTP/domain tables.
- **Jobs:** bootstrap worker/Beat with no business schedules; harmless infrastructure probe for integration validation.
- **API/UI:** `/health/live/`, `/health/ready/`, public `/api/v1/status/`, one neutral Persian RTL baseline page; no registration/admin/login/client screens.
- **Security/privacy:** required production config fails closed; unusable consumer passwords; no public storage/default auth_user/secrets.
- **Tests:** empty-DB migration identity, Django boot, environment failure, DB/Redis/Channels/Celery/storage integration, RTL/static smoke.
- **Exit:** all Foundation plan gates pass on clean local/CI environment, lockfiles reproducible, no business-domain implementation beyond minimal User.

C01 execution status: **PASS**, 2026-10-05. Cloud checks and actual private
GitHub Actions run37295879078 passed; final Foundation review has no unresolved
Critical/Important finding. See execution ledger and Foundation handoff.
C02 remains unstarted and requires new explicit authorization.

## C02 — Accounts, OTP, authentication and base authorization

- **Goal:** adult phone entry, sessions and policy primitives safe for subsequent private domains.
- **Domains:** accounts, governance initial audit/consent/account restriction/privacy-request intake.
- **Prerequisites:** C01; operational identity evidence procedure drafted for recovery development, fakes allowed.
- **Deliverables:** OTP adapter/mock, normalization/throttles, adult attestation, context authorization/session revocation/referrals, manual RecoveryRequest/PhoneChangeHistory and staff controls; core Consent/AuditEvent/outbox and coarse FeatureFlag services for Marketplace, professional registration, Insights and Mirror.
- **Migrations:** additive account fields/challenges/recovery/session controls; governance consent/audit/outbox/privacy request/retention-policy/hold metadata/FeatureFlag base. No swapped-user replacement or experimentation assignments.
- **Jobs:** SMS delivery/reconciliation if needed without optimistic login; outbox dispatcher/retry scan; no general notification SMS.
- **API/UI:** OTP request/verify/logout, account/preferences, recovery request/status, staff decision, export/deletion request intake (execution completed C18).
- **Security/privacy:** uniform errors, attempt/IP/phone limits, old-auth invalidation, reasoned staff evidence access, no questions/bypass; pending deletion restricts account immediately.
- **Tests:** challenge expiry/resend/replay/races/limiter outage, under-18 rejection, CSRF/session rotation, manual recovery authorization/unique-phone conflicts and base cross-user denials.
- **Exit:** registration/login works with mock SMS; recovery records audit/history and revokes old sessions; consumer password route absent; no sensitive-record view yet.

## C03 — Athlete/professional profiles and verification

- **Goal:** resumable baseline/setup and verified capability/private-public separation.
- **Domains:** athletes, professionals, assets, governance.
- **Prerequisites:** C02 authorization/consent/audit; settings/storage baseline C01.
- **Deliverables:** profiles, baseline wizard, declared Coach/Nutritionist roles, setup/branding, private credentials/images, broad locations, assistant membership role definition, staff verification. Wizard steps for packages/calendar/templates link to later domains only when available.
- **Migrations:** profile/baseline/role/location/credential/verification/assistant models and Asset metadata; private upload state/derivatives.
- **Jobs:** scans/image sanitization and expired upload cleanup.
- **API/UI:** profile/setup/baseline drafts, authenticated owner preview, verification submit/staff review, safe upload/finalization; no public unverified route.
- **Security/privacy:** owner-only preview, private credential source, explicit storage/sharing consents, quarantine/type/size validation, assistant membership grants no health/inbox access.
- **Tests:** cross-profile/UUID access, draft resume, capability versus verification, public route/index/search denial before approval, asset spoofing/quarantine and staff audit.
- **Exit:** independent athletes and unverified private professionals onboard; approval controls publication eligibility; credential source cannot become public.

## C04 — Marketplace, search and public profiles

- **Goal:** discover verified professionals through truthful server-rendered public data.
- **Domains:** marketplace, professionals, assets, governance.
- **Prerequisites:** C03 approved/public projection fields; Marketplace flag.
- **Deliverables:** PostgreSQL Persian full-text/trigram search, capabilities/modes/city/region and available criterion filters, relevance labels, favorites/compare max three, SEO/structured metadata, simple educational text/image posts.
- **Migrations:** public projection/search indexes, favorites/comparison, educational posts; no review/case-study facts fabricated before C14.
- **Jobs:** public projection refresh/purge and reconciliation.
- **API/UI:** public professional pages/search/cards/comparison/posts; package/consultation sections rendered only for actual enabled offers in C05/C11.
- **Security/privacy:** no athlete indexing or private credential fields; public/index/discovery denied on verification revocation; no card prices/precise map/fake match percentage/social feed.
- **Tests:** Persian normalization/filter ordering, fourth comparison rejection, no unverified/stale public leaks, safe branding/text, SEO facts match actual records.
- **Exit:** verified discovery works; all public data allowlisted; future unavailable sections are omitted rather than invented.

## C05 — Packages, intake, submitted requests and CRM

- **Goal:** capture explicit client demand and professional offers without premature acceptance.
- **Domains:** coaching, marketplace/professionals, governance.
- **Prerequisites:** C03 profiles, C04 profile presentation; standard baseline/consent available.
- **Deliverables:** versioned packages/discounts/terms, custom intake, standard intake snapshots, draft/submitted/rejected/withdrawn requests, lead sources/pipeline/notes/reminders and waitlist enrollment. Accept/convert actions remain disabled until C06.
- **Migrations:** package/intake/answers/request/lead/CRMNote/discount/waitlist, terms snapshots; no gateway package Payment.
- **Jobs:** safe CRM follow-up reminders through initial in-app notification records; expire discounts/requests using date-derived checks.
- **API/UI:** package profile details with prices, request intake/submission, CRM pipeline and waitlist; no platform package checkout.
- **Security/privacy:** only submitted purpose-limited intake review, private lead notes, no longitudinal data grant from lead/request; authenticated athlete claim for manual leads.
- **Tests:** form/price snapshot immutability, discount boundaries, baseline/custom completion, source attribution, cross-workspace denials, full/waitlist display without fake seat allocation.
- **Exit:** valid requests/leads can be submitted and reviewed; no acceptance, client conversion or revenue verification bypass exists.

## C06 — Relationships, capacity and central entitlements

- **Goal:** make every admission/offboarding path atomic and role-safe.
- **Domains:** coaching, billing entitlement configuration/service, professionals assistants, governance, notifications minimum.
- **Prerequisites:** C05 requests/terms; C02 consent/audit/outbox; operational archive design locked.
- **Deliverables:** accept/convert/private invite/restart, active episodes/scopes/seats, end/disconnect, narrow ArchiveManifest/read selector, tags/groups, designated private notes, fixed assigned-client support role; central Free five/Pro beta 100 config and staff control. Paid state comes later; Pro test fixtures are not production grants.
- **Migrations:** relationship/scope/seat/group/note/archive, EntitlementConfiguration and minimal Subscription period/state interface required by resolver, durable Notification rows.
- **Jobs:** waitlist opening notices, access revocation/output invalidation, source event dispatch.
- **API/UI:** acceptance/rejection, client list, end/restart, read-only archive, groups/tags/notes, admin entitlement controls.
- **Security/privacy:** transaction locks/uniqueness, distinct-client cap, no overlapping authority; archive cannot read new athlete data, sensitive grants purpose-specific; assistant cannot accept/prescribe/read sensitive data.
- **Tests:** concurrent acceptance/free cap/seat allocation, dual-role distinct counts, entitlement config change without deploy, overlimit nondeletion, grant withdrawal, archive cutoff/new-data denial and assistant revocation.
- **Exit:** all activation paths share atomic checks; end immediately blocks operational access; cap defaults/config and narrow archive demonstrably work.

## C07 — Workouts, program builder and versioning

- **Goal:** professional training programming plus independent athlete workout logging.
- **Domains:** workouts, coaching, assets/governance.
- **Prerequisites:** C06 training scopes, history/audit, validated custom media; basic athlete context C03.
- **Deliverables:** platform/custom exercises/media, workout/day/full-program templates, structured advanced prescriptions/blocks/mesocycles/progression/deloads, immutable revisions/rollback, assignments/bulk per-recipient checks, athlete overrides/change requests, online sessions/sets.
- **Migrations:** exercises/templates/program/revision/block/day/prescription/assignment/override/change request/session/set models; explicit uniqueness/version constraints.
- **Jobs:** assignment notifications/media processing/report source events; no AI auto-publish.
- **API/UI:** plan editor/diff/history/template assignment, athlete schedule/session logging and approved substitutions.
- **Security/privacy:** Coach authority, exact revision attribution, no athlete major edits or professional rewrites of actual logs; isolated custom videos.
- **Tests:** every listed prescription feature survives roundtrip, revisions immutability/rollback, concurrent/stale edits, dual-role/scope negatives and group authorization.
- **Exit:** real multi-week programs and online logs retain exact history; no shared template mutation changes assigned plans.

## C08 — Nutrition, food, recipes and plan versioning

- **Goal:** reproducible nutrition prescriptions and confirmed actual intake.
- **Domains:** nutrition, coaching, assets/governance.
- **Prerequisites:** C06 explicit nutrition authority/consent; C03 uploads; C07 revision pattern understood (no generic merged engine required).
- **Deliverables:** common Iranian foods with provenance, workspace custom foods, recipe ingredients/yield/totals, meals/alternatives/free text, immutable plans/assignments/rollback, adherence and quantities, optional private food images; unconfirmed AI draft interface only until C15.
- **Migrations:** Food/Recipe/ingredients/plan revisions/meals/assignment/MealAdherence/FoodLog/draft metadata and explicit unit/version constraints.
- **Jobs:** assignment notices/food image processing; no external identification yet.
- **API/UI:** authorized nutrition builder/recipe calculator, athlete meal/adherence/intake UI, Coach grant-based adherence-only view.
- **Security/privacy:** Coach cannot edit plans; adherence grant cannot expose detailed intake/other professional notes; unknown nutrition stays unknown.
- **Tests:** unit conversion/totals/snapshots, food edits do not rewrite old plans, Nutritionist permission, Coach positive adherence/negative editing cases, image privacy.
- **Exit:** confirmed actual records and reproducible versioned plans work without external AI; all role distinctions enforced.

## C09 — Progress, goals, health, photos and consent completion

- **Goal:** complete sensitive athlete data and explicit sharing UX.
- **Domains:** athletes health, progress, governance, assets.
- **Prerequisites:** C02 consent/retention/hold primitives, C03 baseline/assets, C06 relationships/archives.
- **Deliverables:** structured health categories/docs, daily/body/performance metrics, goals/milestones/meaningful progress, photo gallery/date/before-after timeline, consent dashboards/revoke/disconnect, archive consent and provider-purpose wording (external AI still disabled).
- **Migrations:** health declarations/versions, BodyMetric/DailyMetric/Goal/Milestone/ProgressPhoto, consent scopes, retention inventory mappings.
- **Jobs:** safe derivatives, revoked-artifact invalidation and daily projection refresh.
- **API/UI:** health/progress/logging/photo comparison, object/category grants and revocation.
- **Security/privacy:** private by default; no medical-record/diagnosis claims; revocation source/projection/download coverage, held evidence isolated.
- **Tests:** every baseline/health/daily field, photo grants per professional, no unrelated access, sensitive archive redaction, meaningful percentages/missing values.
- **Exit:** athlete independently logs and controls every sensitive share; revocation survives cached/derived views and archive retention does not imply permission.

## C10 — Messaging, WebSockets, attachments and broadcasts

- **Goal:** durable private coaching communication with recoverable real-time delivery.
- **Domains:** messaging, coaching, notifications, assets/governance.
- **Prerequisites:** C06 active relationship/group access, C09 sensitive grants, C01 Channels/C02 outbox.
- **Deliverables:** direct messages/replies to reports/workouts/nutrition, file/image attachments, important markers, private recipient broadcasts, cursor replay and unread notices.
- **Migrations:** conversations/messages/revisions/attachments/broadcast/delivery with idempotent message IDs/effect keys.
- **Jobs:** broadcast fan-out, push/in-app event dispatch, scan-dependent attachment availability.
- **API/UI:** canonical HTTP sends/uploads, authorized socket subscriptions, chat/broadcast composer; no calls.
- **Security/privacy:** origin/current membership checks on connect/action/delivery, no assistant inbox, no recipient-list leakage; end closes writes/new events, normal archive excludes chat.
- **Tests:** duplicate sends, Redis/socket reconnect/loss, per-recipient revoke races, malicious group subscription, attachment consent and terminated chat.
- **Exit:** committed messages survive event loss; broadcasts create one private delivery per eligible client and cannot leak other recipients.

## C11 — Check-ins, calendars, appointments and notifications

- **Goal:** recurring follow-up and reservable sessions with reliable reminders.
- **Domains:** progress check-ins, scheduling, notifications, coaching.
- **Prerequisites:** C06 relationships/groups, C09 photo consent, C10 event delivery; source-specific notification surfaces from earlier stages.
- **Deliverables:** versioned five-type forms/submissions/recurrence, availability/exceptions, atomic booking/cancellation/history, free/external-paid pre-coaching consultation, notification preferences/in-app/PWA push subscriptions.
- **Migrations:** check-in template/field/schedule/occurrence/submission, availability/appointment/events, push/delivery/preference records.
- **Jobs:** Beat occurrence/reminder scans, deduped due notices, invalid push cleanup; all specified reminder types covered.
- **API/UI:** form builder/answers/calendar/reservations/consultations, notification inbox/preferences and opt-in push; no calling UI.
- **Security/privacy:** appointment/intake purpose boundaries, generic push payloads, photo consent independent of form, schedule/timezone/DST correctness.
- **Tests:** duplicate Beat execution/occurrences, all field validation, simultaneous booking, cancellation snapshots, consent revocation and unsupported/denied push fallback.
- **Exit:** recurring check-ins and calendar work across local dates; retries produce one logical reminder/occurrence and no external coaching payment processing.

## C12 — Reports, timeline, analytics and business dashboard

- **Goal:** actionable client/business reporting with truthful provenance.
- **Domains:** analytics, coaching/manual RevenueRecord, billing entitlements, all activity selectors/assets.
- **Prerequisites:** C07–C11 source records, C06 permissions/entitlements, C09 consent.
- **Deliverables:** unified filtered client timeline, individual/weekly/custom bounded reports and PDF/CSV, active clients/conversion/churn/utilization/packages/sources, labeled manual/estimated revenue and product success metrics.
- **Migrations:** report definition/job/artifact, timeline/projection/metric version and RevenueRecord; no mutable authoritative activity duplication.
- **Jobs:** export generation/expiry, projection updates/reconcile, weekly summaries without AI.
- **API/UI:** metric/filter/report builders, dashboards/downloads, finalization for service archive.
- **Security/privacy:** reauthorize before generation/download, no photo leak through older PDFs, CSV formula escaping, strict workspace filters; Pro advanced gates.
- **Tests:** denominator/cohort/missing-data definitions, Persian PDF shaping/font, revenue labeling, cross-workspace/export revoke, no new reports from ended episode.
- **Exit:** every metric is traceable and exports private/RTL-correct; finalized archive reports obey consent rather than stale copies.

## C13 — Professional subscriptions and Iranian gateway integration

- **Goal:** sell Pro safely, separate from external coaching funds.
- **Domains:** billing, coaching admission, notifications/governance.
- **Prerequisites:** C06 central entitlements, C12 advanced gates; later-stage production gateway choice/review, fake first.
- **Deliverables:** monthly/annual Admin pricing/discount, order/payment adapter fake/live, server verification/reconciliation, paid periods/renewal, grace/downgrade/nondeletion enforcement and config invalidation.
- **Migrations:** prices/orders/Payment/SubscriptionPeriod and additive subscription details; uniqueness of gateway refs/activation effects; no package checkout tables.
- **Jobs:** pending payment reconciliation, expiry notices; effective rules always timestamp-derived.
- **API/UI:** Pro pricing/checkout/return/status/subscription page, authorized pricing/limit Admin controls.
- **Security/privacy:** callback untrusted, exact IRR/amount/merchant verification, once-only activation, no card secrets/automatic recurring debit.
- **Tests:** duplicates/fraudulent/late callbacks, vendor outage, grace boundary, lowering Pro cap, concurrent purchases/renewals, at-limit admission and retained clients.
- **Exit:** fake contract suite and reviewed provider sandbox pass; no return URL alone grants Pro and no package payment is processed/declared verified.

## C14 — Reviews, case studies, moderation and disputes

- **Goal:** consented reputation and formal reported-content resolution.
- **Domains:** marketplace, governance, progress/professionals/assets/coaching.
- **Prerequisites:** C06 verified relationships/archives, C09 photos/consent, C10 reported threads, C12 provenance.
- **Deliverables:** eligibility-based structured reviews/edit/delete history/one response, explicitly approved case-study revisions, reports/hiding/restrictions, DisputeCase/evidence/holds and staff assignment/outcomes.
- **Migrations:** reviews/revisions/responses/case-study/consent references, moderation/disputes/evidence/hold links.
- **Jobs:** public aggregate/purge/reconciliation, consent withdrawal removal and staff notices.
- **API/UI:** review/response, case-study draft/consent/publish, report/dispute forms and restricted staff queues.
- **Security/privacy:** qualifying relationship, no fake verified-payment/outcome labels, private evidence, source-content redaction and independent public consent.
- **Tests:** nonclient rejection, edit/delete history, one response, exact revision consent, revoke/changed study unpublish, staff-only held evidence.
- **Exit:** public reputation is traceable; reports/disputes resolve with audit and cannot expose unrelated private data.

## C15 — AI infrastructure and Coach Intelligence

- **Goal:** consent/role-gated insights and explicitly approved plan suggestions.
- **Domains:** intelligence, analytics, workouts/nutrition, billing/governance/assets.
- **Prerequisites:** C07–C09 plans/consents, C12 authorized reports, C13 Pro enforcement; production AI review deferred until this stage.
- **Deliverables:** adapter/fake, jobs/provenance/minimized input allowlists, weekly/adherence/trend/attention/follow-up insights, typed changes/diff/reasons, stale-safe human approval, separately reviewed food-image suggestions/athlete confirmation.
- **Migrations:** AIJob/AIInsight/AISuggestion/provider-release audit metadata, food-draft links; no direct plan writes by AI.
- **Jobs:** bounded AI generation/retries/cost limits/cleanup; publication remains synchronous human command.
- **API/UI:** professional insight/suggestion review, explicit approval/rejection and athlete confirm/correct food result.
- **Security/privacy:** default excluded files never transferred, reviewed feature+consent required, nutrition capability gate, revoked/stale base blocks release/approval; untrusted input is data.
- **Tests:** fake malformed/timeouts, no excluded payloads, consent withdrawal, unauthorized/duplicate/stale approval, AI metadata in immutable revisions, unconfirmed food not authoritative.
- **Exit:** failures/rejections cannot change plans; human-approved outputs pass normal domain checks and provider review before live processing.

## C16 — AI Mirror Beta

- **Goal:** validated on-device estimates for exactly three exercises.
- **Domains:** intelligence Mirror, workouts, progress/governance.
- **Prerequisites:** C07 workout integration, C09 explicit summary consent, FeatureFlag; selected existing pose runtime validated/licensed in this stage.
- **Deliverables:** Squat/Curl/Shoulder Press rep/ROM/tempo and limited observations, versioned per-exercise quality thresholds, Beta copy, insufficient_confidence/visibility states, derived-only sessions and opt-in shared summary.
- **Migrations:** AIMirrorSession/MirrorValidationPolicy versions and workout summary linkage; no raw video archive.
- **Jobs:** derived-summary ingestion/notifications only; no external pose-video job by default.
- **API/UI:** camera permission, supported-device guidance, Beta session/results and explicit share.
- **Security/privacy:** frames/keypoints transient/on-device, no diagnosis/upload/storage default, denied camera/low-quality produce honest failure.
- **Tests:** target-device recorded fixtures with consent, exercise-specific gating, camera denial, flag disable, exactly three enums, no network video egress and share revoke.
- **Exit:** validated exercises/observations meet recorded thresholds; uncertain metrics unavailable and feature can be disabled independently.

## C17 — PWA, offline workouts and sync

- **Goal:** owner workout logging survives connectivity loss without silent conflicts.
- **Domains:** workouts sync, frontend SW/IndexedDB, accounts/coaching/governance.
- **Prerequisites:** C07 stable session/set contracts, C02 session/CSRF, C06 end rules; C01 PWA-ready static organization (no early offline claim).
- **Deliverables:** manifest/Service Worker/app shell, selected minimal workout cache, local UUIDs/outbox, SyncOperation receipts/hash/version, per-item results/tombstones/conflict UX, foreground/manual retry and optional Background Sync.
- **Migrations:** receipts/idempotency/tombstones/server versions and retention-policy mapping, preserving earlier logs.
- **Jobs:** bounded receipt/tombstone cleanup respecting offline window; not primary sync execution.
- **API/UI:** versioned batch sync contract, synced/pending/conflict indicators, offline logging and reviewed correction UI.
- **Security/privacy:** per-account DB/cache/logout clearing, no health/photo/report/inbox caching, reauth before send; owner log sync survives disconnection without sharing to ended professional.
- **Tests:** replay/different payload/stale version, retry across crashes, same set ID, offline old-plan attribution, tombstone resurrection, account switching/CSRF renewal.
- **Exit:** duplicates prevented and actual conflicts surfaced on target browsers; nutrition/check-ins explicitly remain online.

## C18 — Admin, privacy exports/deletion and audit completion

- **Goal:** complete cross-domain operational controls already introduced incrementally.
- **Domains:** governance, accounts, all domain privacy handlers, assets/billing/analytics.
- **Prerequisites:** C02 request/hold/audit primitives and C03–C17 data inventory; numeric policies/evidence/staff capabilities approved before live execution.
- **Deliverables:** named Admin permissions, complete flag/config/metrics controls, data export, staged deletion/anonymization, affected-record holds/release, retention scheduler/inventory, erasure markers/provider cleanup and isolated restore runbook.
- **Migrations:** additive policy/version/inventory/export/delete job records and privacy mappings; no uncontrolled cascade or reset of custom User/history.
- **Jobs:** policy-driven retention, private exports, resumable deletes/hold review/provider erasure, stale artifact cleanup.
- **API/UI:** privacy request/status/download, staff hold/recovery/dispute/verification queues and explicit reasoned sensitive access.
- **Security/privacy:** no generic staff health export, restrict normal access immediately, held evidence isolated, backup aging and restore replay validated.
- **Tests:** one held record does not block unrelated erasure, repeated jobs safe, no public export, account auth stays revoked, restore replay/marker retention and expiry.
- **Exit:** end-to-end export/delete/hold/restore rehearsals pass; complete audit map covers important reads/writes and actual retention config is approved.

## C19 — End-to-end integration and security hardening

- **Goal:** verify the full V1 against real journeys and failure boundaries.
- **Domains:** all.
- **Prerequisites:** C01–C18 exit gates; no unapproved product changes or unresolved release policies disguised by flags.
- **Deliverables:** integrated Persian athlete/professional/assistant/staff journeys, negative object access/concurrency/failure tests, accessibility/responsive QA, provider contracts/migration upgrades; select/review production SMS adapter and validate OTP delivery in an authorized sandbox before release. Payment/AI selection is owned by C13/C15.
- **Migrations:** only reviewed additive/repair migrations needed by integration; no default-user swap or rewrite of immutable history.
- **Jobs:** exercise existing queues/outbox under restart/outage/duplicate delivery; no new feature generation.
- **API/UI:** all locked V1 surfaces/API schemas/error states and RTL exports; no unrelated features.
- **Security/privacy:** cross-tenant/source-derived data checks, CSRF/origins/uploads/AI exclusions/recovery/holds, no external coaching settlement.
- **Tests:** OTP→onboarding→request→capacity→plan→log→report→Pro→offboard/archive/review; offline conflicts, consent withdrawal during job/socket/download and subscription expiry.
- **Exit:** locked requirement traceability has zero missing capabilities; no critical permission/data-loss/concurrency defect; performance budgets measured and agreed for beta traffic.

## C20 — Deployment, observability and release readiness

- **Goal:** deploy an operable beta using the existing monolith, without Kubernetes.
- **Domains:** runtime/operations, provider adapters, governance/Admin support.
- **Prerequisites:** C19 complete; selected reviewed providers, policy/catalog/retention evidence signed off, production execution separately authorized.
- **Deliverables:** TLS/domain/storage/private network/secrets, pinned deploy artifacts, one Beat, release/migration rollback/runbooks, backup/restore proof, alerts/log scrubbing, staff procedures and truthful Beta notices.
- **Migrations:** reviewed deployment of existing chain with preflight backup/upgrade verification; no opportunistic schema redesign.
- **Jobs:** verify workers/scheduler/outbox/provider reconciliation/retention in production-like staging; safe retry/recovery drills.
- **API/UI:** final public/private routing, liveness/readiness, verified PWA/push/device compatibility and staff access controls.
- **Security/privacy:** no dev mocks/live debug, object ACLs/isolated downloads, redacted logs, approved external processing and deletion-safe restores.
- **Tests:** deployment checks, clean install/upgrade/restore, provider sandbox/live canary as authorized, health failures, alert drills and final smoke journeys.
- **Exit:** all V1 release gates documented/pass, owners can operate/recover/delete safely, deployment approval obtained and post-release monitoring assigned.

## Locked-capability coverage

| Requirement family | Coding homes |
|---|---|
| Phone/adult entry, one User, mock OTP, abuse/session/CSRF, recovery/referrals | C01–C03 |
| Baselines, independent athlete use, professional wizard, capabilities/verification/branding/locations/assistants | C03/C06/C07–C09/C11 |
| Marketplace criteria/SEO/public posts/favorites/compare/no card prices | C04–C05/C14 |
| External-paid packages/discounts/intake/requests/CRM/waitlist/capacity/separated relationships/groups/offboarding | C05–C06 |
| All advanced training features/libraries/media/templates/revisions/rollback/overrides | C07 |
| Iranian foods/custom foods/recipes/structured+free-text nutrition/adherence/intake | C08; image AI confirmation C15 |
| Health/categories/daily metrics/goals/milestones/photos/comparisons/consent | C03 primitives, C09 completion |
| Messaging/files/report replies/private broadcasts/real-time | C10 |
| Recurring check-ins/five types/calendar/consultations/sessions/notifications/push | C05–C06 initial notices, C11 completion |
| Timeline/private notes/reports/PDF/CSV/business metrics/manual unverified revenue/success measures | C06/C12 |
| Free five/Pro 100 central configuration, grace/nondeletion/monthly/annual/gateway | C06 admission; C13 paid integration |
| Verified reviews/revisions/response/case-study consent/reports/disputes | C14 |
| AI insights/diff/approval/provenance/provider exclusions/adapter/fakes | C15 |
| Mirror exactly three/Beta/flag/confidence/derived privacy | C16 |
| PWA/offline workouts/local IDs/idempotency/conflicts/account isolation | C17 |
| Admin/flags/privacy/export/deletion/holds/audit/backups | C02–C03/C06 primitives, C14/C18 completion |
| Locked stack, modular boundaries/security/history/tests/observability/release | C01 foundations, every stage gates, C19–C20 integration |

No locked capability is deferred outside V1 by this map. No stage converts a flag-disabled unimplemented feature into a claim of V1 completion. Optional precise maps/social feed/calling/cash referrals/native auth/microservices/custom model training remain excluded.
