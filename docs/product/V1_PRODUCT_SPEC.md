# FitLink V1 product specification

Stage 1 specification, amended by locked Stage 2 policies on 2026-10-03; written design only. Authority: the user's locked V1 brief and Stage 2 resolutions. This document does not authorize implementation. Remaining operational decisions are recorded in [OPEN_QUESTIONS_AND_RISKS.md](OPEN_QUESTIONS_AND_RISKS.md). Engineering assumptions are explicitly labeled and remain subordinate to locked requirements.

## 1. Positioning, audience and success

FitLink helps professionals **manage and grow their coaching business**. Training and nutrition are parts of a broader system covering existing clients, adherence, communication, verified reputation, acquisition, CRM and business monitoring. Iran is the initial market. This is a production-oriented beta for real coaches, nutritionists and athletes, with a Persian, RTL, responsive PWA interface. All account holders must be at least 18.

Success measures professional activation through real client-management activity, continued weekly use, lead conversion and willingness to pay for Pro. Registrations alone are insufficient. Product analytics must distinguish account creation, first accepted client, first published plan, first reviewed client report, repeated management activity, lead conversion, Pro purchase and renewal. No numerical success targets are invented in this stage.

## 2. Scope and invariant rules

- One phone-authenticated User can have AthleteProfile and/or ProfessionalProfile. Coach and Nutritionist are professional capabilities, not authentication models. An assistant uses that same User model with a limited professional membership.
- Athletes are free and may use personal logging without any professional. Athlete profiles are private; they never become marketplace profiles.
- Professionals may manage private clients and preview their profile before verification. Marketplace inclusion and all public publication/discoverability/indexing require approved identity and applicable credentials. The pre-verification preview is authenticated and owner-only, with no indexing or public media copies.
- Each active relationship names a clear responsibility scope. No athlete can have overlapping active professional authority for the same scope. Both-role professionals still need explicit scope assignments.
- Sensitive health information, files and progress photos are private by default. Relationship membership alone does not grant permission for sensitive data.
- Platform subscription payments and off-platform coaching-package payments are separate. FitLink does not process, settle or verify package payments in V1.
- Published workout and nutrition revisions are immutable. Assignments and logs refer to exact revisions. AI cannot publish or change a plan without an authorized professional's explicit confirmation.
- Only workout logging has full offline support. Other flows can require connectivity. AI Mirror supports exactly Squat, Biceps Curl and Shoulder Press.

Excluded: required email/password login; separate Coach/Nutritionist users; React, Vue, Next.js, SPA or microservices; precise-map search; in-app voice/video calls; social feed/following; referral cash rewards; automatic bank recurring payments; a full experimentation platform; training a proprietary pose model; automatic video upload/storage; diagnosis or medical-record claims; fake compatibility percentages; Elasticsearch/OpenSearch without a later proven need.

## 3. Shared entry journey and account lifecycle

The visitor chooses athlete or professional entry, confirms adult eligibility and uses phone OTP. A profile may be added later without creating a second account. OTP expires, has resend cooldown, bounded attempts and phone/IP limits; sending and verification errors do not reveal whether a phone is already registered. Development uses a mock SMS adapter. No general notifications are sent by SMS.

Account states: active/restricted/suspended → deletion_requested → pending_deletion → deleted/anonymized → deletion_completed. Suspension blocks authenticated product actions and public publication. A verified deletion request immediately restricts normal account access and revokes sessions, push subscriptions, assistants and ordinary sharing grants; retention/hold evaluation then controls deletion of individual records. Dispute, fraud/security and required audit holds block only affected records, not the entire account's unrelated data. Released holds resume processing. Retention durations come from a centrally configurable, versioned policy; approval of actual periods is a launch requirement. Backups age out under infrastructure policy, and restore must replay erasure markers before serving traffic. A user can request a private, expiring personal export excluding others' private notes/confidential dispute material.

Lost-phone recovery in V1 is manual and Admin-mediated: explicit recovery request, verified identity/account evidence, authorized Admin decision, append-only phone-change history and audit, verification of the new number and invalidation of all previous authentication state before access resumes. Account existence/evidence is not disclosed to an unauthenticated requester. No security questions or unaudited bypass; recovery evidence standards are an operational review item, not an alternative recovery method.

## 4. Athlete journey

### 4.1 Independent onboarding and baseline

A resumable multi-step baseline assessment collects age/adult declaration, height, weight, goals, training experience and level, available days, equipment/facilities, lifestyle, sleep, energy, limitations/injuries, baseline measurements, optional progress photos, approximate performance records and basic nutrition habits. Mandatory completion gates coaching requests; personal logging remains available after minimal account/adult setup. Optional photos are never a condition of participation.

Baseline answers are dated and versioned when corrected. Approximate performance is labeled self-reported. Health & Limitations is a separate structured, user-declared profile: injuries, movement limitations, allergies, medications, supplements, dietary restrictions and related documents. It is not a medical record. Sensitive-data consent is separate from account terms and from sharing with a professional. Declining optional sensitive fields does not imply an empty health history.

### 4.2 Personal and coached activity

Athletes can record personal workouts, completion, food/nutrition adherence, actual food and quantities, weight, measurements, photos, sleep, water, steps and energy. Records distinguish self-entered, professional-prescribed and confirmed AI-assisted values. Corrections preserve revision metadata; deletes remove current visibility and follow retention rules.

Goals and milestones can be athlete-defined or professional-defined within the relationship's scope. They support target weight, measurements, weekly workout count and exercise performance. Timeline and progress percentages require meaningful baselines and units; missing data does not imply failure or 0% adherence.

The private photo gallery supports before/after, selected dates and timeline views. Each photo's sharing grant is explicit per professional; professional notes stay private to that professional's authorized workspace. Publishing a case study requires an additional consent independent of private sharing.

## 5. Professional setup and workspace

The resumable Professional Setup Wizard covers profile, image/cover, biography, specialties, experience, private credential documents, service type, online/in-person availability, multiple activity locations, packages and capacity, payment instructions, intake forms, availability/calendar, initial templates, communication preferences and branded public page. Branding includes logo, cover, accent color, welcome message and shareable URL. Baseline branding is supported; advanced branding is governed by entitlements, with the exact distinction open for review.

Verification: draft → submitted → under_review → approved/rejected; changes to verified identity/credentials can require re-review; approval can be revoked. Capability-specific credentials and public credentials are distinct. Only intentionally published credential summaries/documents can appear publicly; source identity documents remain private. Unverified professionals can work with privately invited existing clients through the same intake/acceptance workflow; invitation never grants automatic client-data access.

Professionals tag clients and create groups for broadcasts, check-ins, template assignment, reports and bulk operations. Every bulk operation rechecks each member's current relationship, role and consent. Group membership never creates permission.

Private client notes are dated, optionally pinned/categorized and linked to a workout, report, appointment or check-in. Athletes do not see these notes. Assistants receive only the fixed limited role described in the permissions matrix; no custom ACL builder exists.

## 6. Discovery, reputation and acquisition

### 6.1 Public profile and marketplace

An approved professional's SEO-friendly server-rendered public page contains images, biography, specialties, experience, verification state, selected public credentials, packages, reviews, consented verified case studies, simple educational text/image posts, service modes, locations, consultation availability and a request CTA. Page metadata and structured markup describe actual published facts; no unsupported rating, health or compatibility claims. Public content uses allowlisted public fields and sanitized text/branding.

Marketplace supports Coach/Nutritionist capabilities, online/in-person services and city/region filters. Specialty, athlete goals, experience, rating, verified review count, location, stored language, current acceptance capacity and service/package characteristics may refine results. PostgreSQL search is the V1 search engine. Professional cards omit package prices; profile/package details show price and terms. Results may be ordered using declared needs and authorized platform data, with simple factual relevance labels such as suitable specialty, within selected criteria and accepts online clients. No fake compatibility percentage or algorithmic good/bad label is allowed. Athletes may favorite professionals and compare at most three. Public search never indexes athlete health, photos or private notes.

### 6.2 Reviews and case studies

A review requires a platform-verified active or ended relationship with actual activation history; a pending request, waitlist or consultation is insufficient. It records overall rating, structured program quality, communication, follow-up, responsiveness and value criteria, written text, verified-client indicator and relationship duration where appropriate. Verification confirms the relationship, not payment or the truth of every opinion. A professional can issue one public response. Review edits, deletion tombstones, response changes and moderation actions remain available to authorized admins. Reports can trigger review moderation.

Case studies can contain before/after images, objective, cooperation duration, professional commentary and selected platform-verified progress. Verified means traceable to platform records; source self-reports are labeled accordingly. Consent names the exact content/revision, public audience, professional and included images/data. Publication needs explicit client approval; changes to content require fresh approval. Revocation unpublishes controlled copies and access links; already downloaded public copies cannot be recalled. This limitation must be disclosed when consenting.

### 6.3 Referrals, leads and conversion

Athletes and professionals have invite/referral links with non-sensitive tokens; there is no monetary reward. Lead sources: Marketplace, referral link, social/public profile and manual entry. Source attribution is recorded without embedding sensitive intake data in URLs.

CRM tracks interested package, source, status, private notes and follow-up reminders. Pipeline: New → Reviewing → Conversation → Accepted/Rejected; audited reopening is possible. A lead is an acquisition record, not a permission grant or a client account. Manual leads require the athlete to register/claim the invitation and submit intake; conversion invokes the same relationship acceptance rules. Notes do not authorize messaging an unregistered person's account.

## 7. Packages, requests, capacity and relationship lifecycle

Packages have title, description, duration, included services, capacity, price, payment instructions/schedule, cancellation terms, custom intake form and availability. Temporary discounts have explicit start/end, stated currency, calculation and original price; expired discounts are ignored. Instructions may describe card transfer, external link, installments or other written arrangements. No platform package checkout, settlement or escrow is implied.

Before request submission, the athlete completes standard intake plus package/professional questions and chooses responsibility scopes. The submitted intake, applicable form revision, package terms and price are snapshotted. States: draft → submitted → accepted/rejected/withdrawn/expired. Acceptance synchronously checks professional capability, account restrictions, package availability, active-client entitlement, capacity, athlete consent and conflicting authority. It creates the active ProfessionalClientRelationship atomically. Repeated acceptance returns the same outcome. Two simultaneous acceptances cannot oversell capacity or create overlapping authority.

Waitlist: waiting → notified → fulfilled/withdrawn/expired. A capacity opening triggers in-app/push notification. Notification is not a guaranteed seat; acceptance rechecks current capacity. No automatic relationship or health-data sharing occurs.

Relationship: active → ended, recording end date, reason and optional final professional summary. Athletes can disconnect immediately; all active operational access/writes and new-data delivery cease. Expiry of package duration triggers an end/renewal workflow rather than indefinite access. Restart creates a new episode with current intake/terms and fresh consents; it never reactivates old active grants.

The professional has a narrow read-only service archive: exact programs/versions they delivered, finalized reports/summaries, their dated professional notes and completed appointment history belonging to that episode, bounded by an archive manifest fixed at end. Athlete-provided historical data is visible only if it was actually used in a finalized delivered record and current purpose-specific archive consent permits it. There is no live athlete-profile/metric/timeline query, new report generation or future-data feed. Sensitive photos/documents stay denied unless the relevant archive grant remains valid; revocation redacts/removes access without silently destroying retained audit/history. If no archive grant exists, show only professional-authored service content without athlete-sensitive attachments. Messages are closed; historical snippets are not automatically included. Ordinary archive, finalized-record retention and restricted dispute/security/audit evidence are different access purposes. Holds grant no normal professional access. Athletes retain their own history under retention policy.

Preliminary consultations may be booked before a coaching relationship, free or externally paid. Consultation booking exposes only booking/intake fields explicitly supplied for that purpose, not an athlete's longitudinal records.

## 8. Training, logging and offline journey

The platform exercise library has names, target muscles, instructions and standard instructional media. Professionals add private custom exercises/videos for their workspace and assigned clients. Exercise publishing does not silently modify old prescriptions. Reusable workout, training-day and full-program templates can be assigned individually or to groups; assignments create independent revision references, not mutable shared client prescriptions.

Programs include multi-week training blocks/mesocycles, workout days and prescriptions for sets, reps, load, duration, RPE, RIR, tempo, rest, warm-ups, supersets, dropsets, notes and approved substitutions. Week-specific prescriptions encode volume/intensity changes and deloads explicitly; progression must be readable rather than inferred from prose alone.

Programs move draft → published → superseded/archived. Each published revision records actor, timestamp, parent revision, change summary/diff and AI involvement. Rollback publishes a new revision referencing an earlier snapshot; history is never erased. Athletes may reschedule a day or choose an approved substitute; these are execution overrides, not edits to the professional's plan. Major change requests await professional approval.

Workout sessions and set logs retain both prescribed and actual values and exact program revision. States include in_progress, completed and abandoned; completed workouts can receive audited corrections. Personal workouts need no plan or relationship. Workouts logged against a previously downloaded revision retain that attribution even if a newer plan exists.

Offline: cache the app shell and explicitly selected workout instructions/revision only; use IndexedDB for local session/set records and queued operations with local UUIDs. Show unsynced, syncing, synced and conflict states. Synchronization needs a live authenticated session and CSRF, stable idempotency keys, duplicate prevention and version preconditions. Stale conflicting edits require athlete resolution; no silent last-write-wins for differing set values. Relationship disconnection does not prevent an athlete syncing their own logs, but prevents forwarding them to the ended professional. Nutrition and check-ins may remain online. Logout offers clear notice about unsynced work and clears account-scoped local data; a different account must never see it.

## 9. Nutrition and recurring check-ins

Nutrition plans combine structured foods and free-text instructions. The platform database covers common Iranian foods, with source/provenance, units and nutrition per reference quantity. Professionals/Nutritionists can add workspace custom foods. Plans contain meals, portions, calories, protein, carbohydrate, fat, alternatives and notes. Recipes store ingredients and quantities and compute reproducible totals from snapshotted food nutrition; missing nutrient values stay unknown. Reusable recipes and versioned plans prevent later food edits changing historical prescriptions.

Athletes mark planned meals followed/not followed, record actual quantities/intake and optionally upload food images. AI may propose food identity and approximate servings; the athlete must confirm/correct before those values enter the authoritative FoodLog. Unconfirmed suggestions stay drafts and never count as consumed nutrition. Structured nutrition-plan authoring/publishing requires explicit Nutritionist capability/authorization and an assigned nutrition scope. Coach capability never implies nutrition-plan edit rights. With a specific athlete grant, an active Coach can view a minimized nutrition-adherence projection, discuss adherence and make general non-prescriptive notes; the grant does not reveal nutritionist private notes, plan editing, health, photos or detailed intake by default. Advice prescribing foods/amounts/macros belongs to the authorized nutrition workflow. Contest-preparation responsibility remains an optional scope-design item, not a new V1 overlapping authority.

Custom recurring check-ins support text, numeric, 1–10 scale, multiple choice and photo fields. Templates/questions are versioned, scheduling produces dated occurrences, submissions reference the exact form, and retries cannot generate duplicate occurrences. Responses feed authorized reports/timelines/AI. Uploaded photos retain separate sensitive sharing controls; a form submission cannot override them.

## 10. Communication, timeline and appointments

V1 has one-to-one professional/client messages, image/file attachments and contextual replies to workout/nutrition reports. Broadcasts target all active clients or selected groups and create private recipient deliveries; clients cannot see other recipients. Client replies are direct messages. Permissions are rechecked at delivery. No voice/video calling.

The unified client timeline projects authorized workouts, nutrition events, weight/body metrics, check-ins, appointments, plan changes, selected important messages and goals/milestones. It filters every source object by current access and consent; a projection must not become a backdoor to revoked information. AI can produce periodic summaries and flag notable changes.

Professionals define availability and cancellation policies. Appointments record scheduled time, reminders, history and private professional notes. States: scheduled → completed/cancelled/no_show; changes and rescheduling are audited. Reservation checks availability and overlapping bookings atomically. Cancellation terms are snapshotted and displayed; no automatic external refunds are performed.

Notifications include in-app and opt-in PWA push for messages, assigned plans, workout/nutrition reminders, requests/responses, capacity openings, check-ins and sessions. Communication preferences govern nonessential reminders. Push payloads are generic and contain no health details or message text; opening requires fresh authorization. Unsupported push falls back to in-app notifications.

## 11. Reports, business dashboard and AI

Professionals have individual client reports, weekly client overviews and a configurable report builder with date range, client, group and selected metrics. Reports export private PDF and CSV. Allowed filters/metrics form a bounded builder, not arbitrary database queries. Export jobs recheck rights before generation and before download. PDFs need Persian RTL/font verification; CSV must guard formula injection. Core individual reports remain usable for Free; advanced reporting is entitlement-controlled.

Business dashboards cover active distinct clients, new leads, lead-to-client conversion, churn, capacity utilization, popular packages and acquisition sources. Manually recorded coaching revenue is explicitly labeled recorded/estimated and unverified externally. Package prices alone do not prove revenue. Metrics have declared periods, denominators and source records; see architecture for definitions.

AI Coach Intelligence assists professionals with weekly summaries, adherence analysis, trends, attention signals, follow-up suggestions and draft training/nutrition changes within capability. Inputs include completion, adherence, weight trends, check-ins, sleep, energy, goals and timeline, limited by consent. Insights explain data period, missing data and uncertainty. They do not diagnose or label a professional good/bad.

Actionable suggestion workflow: generated draft → professional views proposed changes and diff plus explanation → explicitly approves/rejects → approved suggestion publishes through normal domain authorization/version services. Approval against a stale base revision fails and requires a new diff/review. Record actor, AI provider/model/version, relevant source IDs, suggestion and resulting revision without placing sensitive prompts in general logs. Provider abstraction is mandatory. Provider timeout/failure leaves existing plans unchanged.

By default, external AI receives no progress photos, health documents, identity documents, arbitrary private files or raw Mirror video. Prefer derived/minimized records; sending sensitive content requires a specifically designed feature, required explicit consent, provider/privacy review and auditable release. The separately designed optional food-image feature must pass these gates before external image processing; no generic attachment-to-AI endpoint is allowed. SMS/payment/AI production vendors are deliberately deferred to later integration stages; development/test use fake/mock adapters.

AI Mirror is labeled **Beta**, a differentiator rather than the central business model, and protected by a separate FeatureFlag. Use an existing browser/on-device pose library for Squat, Biceps Curl and Shoulder Press. Derived outputs: rep count, ROM and tempo plus limited validated observations. Versioned exercise-specific confidence/visibility thresholds gate each metric and observation. Below threshold, return insufficient_confidence or insufficient_visibility and explain in Persian that reliable analysis could not be completed; never fabricate feedback. No medical/injury diagnosis. Video is neither uploaded nor stored by default. Derived sessions stay private until the athlete grants summary sharing into the professional's workout report.

## 12. Subscription and operational administration

Free professionals: maximum five active distinct athlete clients and core client management. Pro: entitlement/configuration-driven active-client allowance, initially **100** for beta, AI Insights, advanced reporting/branding and other explicitly configured advanced tools. Admin can change the Pro limit without deployment through the central entitlement service/configuration. Monthly and annual plans, with annual discount, use Admin-configurable prices. Pro purchases use an Iranian payment gateway through an adapter; no automatic bank recurring charge. Price/currency/period are snapshotted per order, and activation occurs only after server-side gateway verification, once.

Subscription states: free → active_pro → grace → expired/free; successful renewal extends according to documented billing rules. Grace lasts exactly seven days after expiry. Existing clients are never deleted on downgrade or a configured limit reduction. After grace, a professional at/above five cannot add a new distinct client until below the limit or upgraded; Pro-only features are disabled under central rules, without destroying history. Capacity and subscription limits are independent. Entitlements are evaluated server-side from current dates/configuration even if a scheduler/cache is delayed. Assistant/group/Mirror tier choices remain catalog details; the Pro client cap decision is closed.

Admin manages users, professional verification/credentials, marketplace/reviews/content, reports/disputes, subscription prices, feature flags and product/business metrics. Important V1 flags: Mirror, Insights, Marketplace and professional registration. Flags disable entry/actions safely without deleting history; they never bypass permissions. No experimentation framework.

Users report profiles, educational content, reviews and relevant messages. Moderation reports move open → triaged → resolved/dismissed and may hide content temporarily or restrict/suspend users. A formal DisputeCase stores complaint subject, description, evidence/files, related relationship/context, state and resolution notes. Evidence is private; assigned staff access is reasoned and audited. Filing a report does not grant access to unrelated messages. Privacy exports/deletion requests and moderation outcomes are administered with explicit workflow/audit history.

## 13. Acceptance gates for later implementation

1. Unrelated professionals receive no athlete rows, counts, files, search results, timeline items or AI outputs, including guessed UUIDs.
2. Revoking a photo/sensitive grant prevents new downloads, cached report downloads, AI jobs and future broadcasts containing that material. Signed links have bounded exposure and are never permanent.
3. Concurrent acceptances respect package capacity, five-client Free limit and nonoverlapping scopes. Replays create one relationship.
4. Replayed gateway callbacks create one activation; returning from checkout alone creates none. Package instructions never generate platform Payment rows.
5. AI rejection, failure, stale approval and unauthorized approval cannot change plans. Rollback preserves all revisions and old logs.
6. Offline replay creates one session/set per stable ID; differing duplicate payloads and stale edits surface conflicts. Account switching exposes no local data.
7. Ending promptly revokes active access across HTTP, WebSockets, tasks, files/reports/projections. Narrow finalized service archives exclude future data and obey current consent/holds. Restart creates a new episode.
8. Unverified professionals appear in neither Marketplace nor public pages/discovery/indexes; private preview is owner-only.
9. Persian RTL, responsive interactions, accessible forms, date/unit labels and exported PDFs work with real Persian content.
10. Missing telemetry is displayed as unknown; externally recorded revenue, confirmed AI food values and platform-verified progress have truthful provenance.

## 14. Assumptions

- Stage 1 documents are in English for implementation precision; user-facing product copy is Persian. FitLink is the working product name.
- Users may hold both profile types. Athlete ownership always attaches to User, never to a professional workspace.
- Use declared birth date to compute age and record adult attestation; do not collect identity documents from all athletes merely for age validation. Stronger age assurance is a launch-policy review item.
- Store timestamps in UTC; render Tehran-aware schedules and Persian/Jalali dates, accepting explicit local dates with unambiguous conversion. Durations use elapsed time. Store metric units and distinguish display currency from gateway currency; details in architecture.
- Core Free includes personal client plans, one-to-one chat, basic individual reports and private workspace setup. Unspecified advanced tools are not silently paywalled; the final entitlement catalog requires review.
- One review per athlete/professional pair, editable with history across restarted episodes; one current public professional response. Concurrent relationship episodes count one distinct client for subscription limits and separately consume their package seats.
- Waitlist notifications do not reserve seats. No automatic plan changes, automatic paid renewal or automatic refund of external coaching payments.

## 15. Requirement coverage index

Every row maps a locked brief area to a specification section and an architectural owner. Detailed records are in [DOMAIN_MODEL.md](../architecture/DOMAIN_MODEL.md), access rules in [PERMISSIONS_MATRIX.md](../architecture/PERMISSIONS_MATRIX.md), and technical boundaries in [V1_ARCHITECTURE.md](../architecture/V1_ARCHITECTURE.md). An unresolved policy is mapped, not silently considered approved.

| Locked brief area | Spec section | Architectural home |
|---|---|---|
| Vision, Iranian beta, Persian RTL, adult-only, success criteria | 1–3, 13–14 | accounts, professional analytics; architecture §§1, 13 |
| One User, profiles, capabilities, assistants | 2–5 | accounts, athletes, professionals; permissions |
| Phone OTP, expiry/cooldown/attempts/phone-IP throttles/mock/vendor abstraction | 3 | accounts; ADR-002 |
| Independent athletes, baseline assessment, personal/daily logs | 4 | athletes, workouts, nutrition, progress |
| Structured health/limitations, consent, private files | 4 | athletes, assets, governance; ADR-004 |
| Professional setup wizard, verification, private use | 5 | professionals, coaching, scheduling |
| Public profile, branding, SEO, credentials, posts | 5–6 | professionals, marketplace, assets |
| Marketplace capabilities/modes/city filters and full optional criteria | 6 | marketplace, PostgreSQL search |
| No card prices, no fake match percentages, relevance labels | 6 | marketplace public projection |
| Favorites and comparison up to three | 6 | marketplace |
| Verified reviews, structured criteria, response/history/reporting | 6 | marketplace, governance |
| Case study content, verified provenance and explicit consent | 6 | marketplace, governance, progress |
| Packages, discount, instructions, external payments, capacity/waitlist | 7 | coaching; not billing payments |
| Standard/custom intake, request acceptance/rejection, separated roles | 7 | coaching, professionals |
| CRM pipeline, sources, notes/reminders/conversion | 6–7 | coaching CRM submodule |
| Business metrics, recorded/estimated revenue | 11 | analytics, coaching RevenueRecord |
| Messages, files, report replies, broadcasts; no calls | 10 | messaging, assets, Channels |
| Client tags/groups and uses | 5 | coaching with per-domain bulk commands |
| Fixed limited assistant role | 5 | professionals; permissions |
| All workout prescription features, blocks, deload/progression | 8 | workouts |
| Exercise library/custom exercises/media | 8 | workouts, assets |
| Three template levels and bulk assignments | 8 | workouts, coaching group selectors |
| Immutable revisions, actor/time/diff/AI/rollback | 8, 11 | workouts, nutrition, governance audit |
| Athlete minor execution overrides/major requests | 8 | workouts, coaching access policy |
| Offline local IDs/sync/idempotency/duplicates/conflicts | 8 | workouts sync; architecture §6 |
| Iranian food database, custom foods, meals/macros/free text/substitutes | 9 | nutrition |
| Recipe ingredients/quantities/computed totals/reuse | 9 | nutrition |
| Actual food/adherence/images/explicit AI confirmation | 9 | nutrition, intelligence, assets |
| Recurring check-in builder, all five types/responses/AI | 9 | progress check-ins submodule |
| Goals/milestones/progress visuals | 4 | progress |
| Photo gallery/comparisons/timeline/notes/visibility | 4 | progress, assets, governance |
| Unified client timeline/all specified event types/AI summaries | 10–11 | analytics projections, intelligence |
| Private professional notes/pinned/category/context | 5 | coaching |
| Availability/reservations/status/history/reminders/cancellation | 7, 10 | scheduling |
| Preliminary free/externally paid consultation | 7 | scheduling; not billing |
| Individual/weekly/custom reports, filters, PDF/CSV | 11 | analytics, assets, Celery |
| AI intelligence inputs/outputs/diff/approval/audit/vendor abstraction | 11 | intelligence; ADR-005 |
| Mirror three exercises/on-device/derived-only/consent/limits | 11 | intelligence Mirror submodule |
| In-app/push examples and OTP-only SMS | 3, 10 | notifications, accounts |
| Free five/Pro/monthly/annual/admin pricing/Iranian gateway/no recurring | 12 | billing; architecture §9 |
| Seven-day grace/nondeletion/overlimit/entitlements | 12 | billing policy, coaching checks |
| Referral links/no monetary rewards | 6 | accounts, coaching attribution |
| Text/image professional content/no social feed | 6 | professionals |
| Formal ending/reasons/final summary/history/review/restart | 7 | coaching, governance |
| Moderation reporting/restrictions/formal disputes | 12 | governance |
| Admin functions/four important flags/no experimentation | 12 | governance, billing, professionals |
| Privacy consent/access/disconnect/deletion/export/audit | 2–4, 6–7, 12–13 | governance plus all domain policies |
| Locked backend/frontend/API/session/custom-user/UUID/PostgreSQL | 2 | architecture §§1–5; ADR-001/002 |
| Redis/Celery/Beat/Channels/storage/provider abstractions | 3, 8, 10–12 | architecture §§7–10; ADR-003/004/005 |
| Architecture principles/cohesive domains/history/testability/migrations | 2, 13 | architecture §§2–3, 10–14 |
| Written artifacts only/no scaffold/dependencies/migrations/product code | document status | Stage 1 boundary, all five ADRs |

## 16. Stage 1 self-review record

The locked brief was re-read by section and by its enumerated requirements after drafting. Coverage includes affirmative capabilities, excluded features, architectural constraints and required artifact content, not only the entity names. No requirement lacks an architectural home. Material ambiguities and conservative interim restrictions are in the risk register; coverage does not mean those policy choices are approved. Stage 1 completion is not production or policy approval.

| Required self-review | Result and evidence in the design |
|---|---|
| Every locked requirement | Mapped in §15 and detailed journey sections; reviewed against the original brief |
| Architectural home for all requirements | Sixteen-app ownership table and entity tables cover all areas; no orphan feature identified |
| Consistent names | ProgramRevision/NutritionPlanRevision, ProfessionalRole, AssistantMembership and Appointment used across docs/ADRs; 55 requested entity names/refinements verified present |
| Role/permission consistency | Six role columns, active scopes, separate sensitive Grant and fixed Support role; Nutritionist authoring and Coach adherence-only grants are explicit |
| Sensitive data becoming public | Private quarantine, separate sanitized public copies, allowlisted projections, content-specific publication consent; no public export/private-source URL |
| Circular dependencies | Foundation-to-feature direction checked; feature outputs use outbox/projections; reverse publishing is composition orchestration, not activity-to-intelligence imports |
| Sync/async boundaries | Acceptance/capacity/reservations/consent/version approval/payment activation synchronous; scans/exports/provider generation/delivery asynchronous |
| Coaching payments accidentally on-platform | ServicePackage/RevenueRecord separate from Payment/SubscriptionPeriod; consultations external/free, no settlement claims |
| AI silently changing plans | Explicit diff/reasons/human approval with expected revision, role/entitlement checks and immutable publication; stale/rejected/error paths leave plan unchanged |
| Unrelated professional data access | Scope/Grant predicates on querysets/files/jobs/WS/AI/projections; source checks on derived outputs; group/lead/UUID cannot authorize |

Document integrity checks verify ten requested files, local links and absence of placeholder sections. No application tests, scaffold, dependency installation, migrations or product code were produced.
