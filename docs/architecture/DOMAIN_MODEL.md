# FitLink V1 conceptual domain model

Stage 1 model amended by locked Stage 2 decisions, 2026-10-03. Conceptual records, not migrations. Owners are authorization/organizational owners, not legal claims. Names follow [V1_ARCHITECTURE.md](V1_ARCHITECTURE.md); use [PERMISSIONS_MATRIX.md](PERMISSIONS_MATRIX.md) for access and the [risk register](../product/OPEN_QUESTIONS_AND_RISKS.md) for remaining operational details.

## 1. Shared conventions and invariants

Exposed entities use UUID public identifiers; internal database keys may be implementation details. All mutable records have created/updated times and optimistic version where concurrency matters. Timestamps are UTC; measured values carry explicit canonical units, original source/provenance and observed time. Money is integer IRR with explicit display conversion. Soft deletion is not a substitute for privacy deletion: archive, visibility removal, erasure and retention holds are separate states.

Within domains use relational references and uniqueness constraints. Typed cross-domain subject references carry type/UUID plus validated owner/context; no arbitrary client-supplied reference grants access. Published revisions and submitted answers keep snapshots with schema versions. Deletion of a library record cannot cascade away historical plans/logs. Private Asset references never imply public access.

Relationship scope allocations are explicit rows: active training and nutrition authority are nonoverlapping per athlete. Structured nutrition prescribing requires Nutritionist capability/authorization; Coach-only adherence reads use separate athlete consent, not prescribing authority. Optional contest-preparation scope definition remains unresolved. One professional may hold both capabilities/scopes; capability alone grants no athlete access. All capacity and client-limit checks use transactional state and the central entitlement service (Free five, beta Pro configurable default 100).

Each entity entry specifies purpose, principal fields/relationships, ownership, lifecycle and history. Unless stated otherwise, archive removes active selection/public display while keeping historical references until the approved retention/erasure workflow. No proposed indefinite retention is implicit.

## 2. accounts

| Entity and purpose | Fields and relationships | Ownership | Lifecycle and history |
|---|---|---|---|
| User — single account identity | public UUID, normalized unique phone, auth flags/auth version; later birth date/adult attestation, locale/timezone/state/profile/session links | account holder; staff administer state | active/restricted/suspended → deletion_requested → pending_deletion → deleted/anonymized → deletion_completed; audit phone/state; Foundation creates only minimal identity/flags in accounts/0001_initial with AUTH_USER_MODEL set before first migrate |
| OTPChallenge — controlled proof of phone possession | phone, purpose, keyed code digest, expiry, attempts, resend time, consumed time, delivery correlation | accounts service, never publicly readable | created → dispatched/failed → consumed/expired/locked; consume once atomically; redact code, bounded security history |
| InviteReferralLink — registration/source attribution | issuer User, opaque token, intended professional/package if any, expiry, usage metadata | issuer | active → revoked/expired; accepted attribution records; no monetary reward, no direct data access |
| AccountSessionControl — revocation handle | User, session identifier digest, auth version, last authentication, revoked time | User/accounts service | active → revoked/expired; audit global logout/recovery; no raw keys |
| RecoveryRequest — manual lost-phone process | requester/contact, claimed account reference kept confidential, restricted verification evidence, staff assignee/decision/reason, proposed new phone, new-number verification time | claimant limited status; authorized recovery staff | requested → verifying → approved/rejected → applied/closed; cannot apply without Admin authorization/account verification; no security questions; audit decisions and failures |
| PhoneChangeHistory — immutable identity changes | User, old/new phone references protected/redacted, RecoveryRequest or authenticated change context, authorizer/time, auth-version transition | accounts security staff | append-only after transactional unique-phone update; invalidate previous sessions/challenges/push state before resuming access; retention policy applies |

Baseline age enforcement is computed from birth date, not a mutable age integer. An assistant must also pass adult account entry.

## 3. athletes

| Entity and purpose | Fields and relationships | Ownership | Lifecycle and history |
|---|---|---|---|
| AthleteProfile — private personal context | one-to-one User, height, timezone/preferences, onboarding progress; references current baseline | athlete | onboarding → active → archived/erased; profile never indexed publicly; sensitive access audited |
| BaselineAssessment — multi-step initial context | athlete, revision, age at assessment, weight/measurements, goals, experience/level, days, facilities/equipment, lifestyle, sleep, energy, limitations, approximate records, nutrition habits; optional photo references | athlete | draft → submitted → superseded; dated answer snapshots retained; corrections do not rewrite old baseline |
| HealthLimitationsProfile — structured user declarations | athlete, current revision; category items for injury, movement limitation, allergy, medication, supplement, dietary restriction; Asset document links | athlete | draft/active → corrected/withdrawn; sensitive-storage Consent required; version/history minimized under retention policy; no medical diagnosis |
| HealthDeclaration — individually shareable health item | parent health profile, category, user text/structured value, observed dates, record version | athlete | active → superseded/deleted; specific item/category grants rather than all-or-nothing sharing; no copied values in general audit |

## 4. professionals

| Entity and purpose | Fields and relationships | Ownership | Lifecycle and history |
|---|---|---|---|
| ProfessionalProfile — private workspace plus deliberate public fields | one-to-one User, biography, specialties, experience, modes, languages, setup progress, profile/cover/logo Assets, validated accent/welcome/slug/publication state | professional | setup → private_ready → publication_requested/published/unpublished; all public publication/search/discovery/indexing require approved verification; owner-only authenticated preview before approval |
| ProfessionalRole — declared capability assignment | professional, Coach/Nutritionist enum, declared active state, separately derived credential verification status | professional declares capability; staff verify its evidence | declared_active → inactive/restricted; unique role per professional; capability changes audited; verification approval is a separate lifecycle and is not required for private management; not auth models |
| Credential — evidence of qualification | professional/role, type, issuer, title, dates, private Asset, verification state; separate allowed public summary/copy | professional; staff review | draft → submitted → reviewed/approved/rejected/expired/revoked; preserve review evidence under retention; default private |
| Verification — decision bundle for identity/capabilities | professional, identity checks, credential references, staff actor, reason, submitted/decision dates, revision | governance-authorized verification staff | submitted → under_review → approved/rejected → revoked/re-review; audit all decisions; badge scope reflects actual approved capabilities |
| ProfessionalLocation — broad in-person activity | professional, region/city, venue/address optionally published, modes | professional | active → archived; city/region lookup, no precise-map search; consent/publication review for address |
| AssistantMembership — limited workspace role | professional, assistant User, fixed role `client_support`, assigned client IDs, invitation and activation dates | professional workspace | invited → active → revoked/expired; assumption max two active assistants, configurable pending entitlements; no self-elevation or nested assistant invite; audit membership/client assignments |
| EducationalPost — simple profile content | professional, text, image Asset copies, publication/moderation status | professional | draft → published → hidden/archived/deleted; edits/history and reports; no feed/follower entity |

Verification is not required for private coaching. Private services check declared active capabilities and any staff restriction; Marketplace capability badges/inclusion check approved identity and corresponding credentials. Staff restriction overrides public eligibility even when verification was approved.

## 5. coaching (including CRM)

| Entity and purpose | Fields and relationships | Ownership | Lifecycle and history |
|---|---|---|---|
| ServicePackage — external-paid service offer | professional, role scopes, title/description/duration, included services, seat capacity, price/currency, payment instructions/schedule, cancellation terms, IntakeForm revision, availability | professional | draft → available/paused/full → archived; full is derived from seat occupancy; terms revisions preserved; no billing Payment relation for coaching checkout |
| PackageDiscount — time-limited package adjustment | package, type/amount, valid_from/to, original price snapshot | professional | scheduled → active → expired/revoked; derived effective price, audit edits |
| IntakeForm / IntakeQuestion — custom request questionnaire | owner professional, form revision, question stable UUID, type, label, required, choices/validation | professional | draft → published → superseded/archived; new answers reference exact form; bounded types, no arbitrary executable validation |
| IntakeSubmission — standard and custom answers | athlete, professional/package, baseline reference, form revision, answers, shared-sensitive object grants explicitly selected, package terms snapshot | athlete; submitted copy for request reviewer | draft → submitted → superseded/withdrawn; answers immutable on submission; review access limited to explicitly submitted scope |
| CoachingRequest — acceptance proposal | athlete, professional, package, selected scopes, IntakeSubmission, terms snapshot, source Lead/link, submitted/decision times/reason | athlete submits; professional decides | draft → submitted → accepted/rejected/withdrawn/expired; accepted request uniquely links relationship; replay returns same relationship; audit decisions |
| ProfessionalClientRelationship — contractual episode/access boundary | athlete, professional, accepted request, package terms, started_at/expected_end/ended_at/reason, final summary, previous episode, archive manifest | participants; professional workspace holds service records | active → ended; revoke operational grants/new-data access; narrow read-only archive obeys current consent/retention; restart is new episode |
| ArchiveManifest — fixed delivered-service boundary | relationship, cutoff, typed source IDs/revisions for delivered plans, finalized reports/summary, professional notes/completed appointments, provenance/classification | professional read-only, athlete own records separately | fixed at end → redacted/expired under consent/retention; source IDs cannot expand to future data; no chat/live metrics/AI drafts by default; holds grant staff evidence access only |
| RelationshipScopeAllocation — prevent conflicting authority | athlete, relationship, scope enum, active/ended timestamps | relationship service | allocate on acceptance, release on end; unique active athlete/scope; atomic locking; cannot be expanded without authorized new agreement |
| PackageSeatAllocation — transactional capacity | package, relationship, occupied/released dates | package/workspace | allocated → released; uniqueness per episode/package; oversubscription blocked; no automatic waitlist acceptance |
| WaitingListEntry — request capacity notification | athlete, package, joined_at, notification state, source, opt-out | athlete | waiting → notified → fulfilled/withdrawn/expired; one active entry per athlete/package; event deduplication and delivery log |
| ClientTag / ClientGroup / ClientGroupMember — organize active clients | workspace, label; group-member relationships with joined/removed dates | professional; assistant limited assignment action | active → archived; membership removal on relationship end; historical bulk targets retained, no new access from membership |
| ProfessionalNote — private client management notes | professional workspace, relationship, author, date/text, pinned/category, validated context reference, restricted-by-default classification, explicitly designated assistant_visible flag | professional workspace; assigned client-support assistant only for non-sensitive designated notes | active → revised/archived/deleted; author/edit audit; not athlete export content; sensitive values prohibited for limited assistant-facing notes |
| Lead — small acquisition pipeline | professional, optional claimed athlete, bounded contact/source, interested package, status, attribution link, follow-up due | professional workspace | New → Reviewing → Conversation → Accepted/Rejected; audited reopening; Accepted ties to successful relationship activation; no bypass via manual lead |
| CRMNote — private lead annotation | Lead, author, text, follow-up context/date | professional workspace | created → revised/archived; history; no blanket athlete permissions |
| RevenueRecord — unverified coaching money log | professional, optional relationship/package, amount/currency/date, recorded/estimated classification, note | professional | recorded → corrected/voided; labeled external/unverified; not gateway Payment or settlement |

Manual leads may store minimal contact information and source, not full third-party health records. The athlete must claim/register before becoming an authenticated client. A unique idempotency reference joins request, lead conversion and relationship creation. Lead status Accepted cannot be used as authorization.

## 6. workouts

| Entity and purpose | Fields and relationships | Ownership | Lifecycle and history |
|---|---|---|---|
| Exercise — platform or workspace library | name, target muscles, instructions, standard media Asset references, owner workspace nullable for platform, approved substitution references, revision/source | platform curator or professional | draft → available → archived; snapshot name/instructions/media version into prescriptions as needed; custom video private to workspace/assigned clients |
| WorkoutTemplate — reusable design at three levels | professional, level workout/training_day/full_program, revision snapshot, exercise references, sharing within workspace | professional | draft → published → superseded/archived; group assignment copies immutable reference into independent athlete assignment |
| WorkoutProgram — plan identity | author professional, intended scope, title, current published ProgramRevision, archive state | professional; athlete receives assignment | draft → active → archived; identity never stores mutable current historical prescriptions |
| ProgramRevision — immutable prescription snapshot | program, revision UUID/sequence, parent, author/time, schema version/hash, change summary/diff, AI suggestion involvement, TrainingBlocks | professional author, assigned athlete read access | draft → published → superseded; published cannot update/delete in ordinary workflows; rollback creates new published child |
| TrainingBlock — weeks/mesocycle | revision, name, week range, objectives, deload indicator, week-specific structure | enclosing revision | mutable in draft only; immutable with revision; explicit volume/intensity and deload schedules |
| WorkoutDay — scheduled prescription unit | block/revision, week/day index, label, prescriptions, planned time/day reference | enclosing revision | immutable after publication; execution rescheduling separate |
| ExercisePrescription — exercise and set structure | WorkoutDay, exercise snapshot, order, set targets, reps/range, load, duration, RPE/RIR, tempo/rest, notes, warmup flags, superset group, dropset stages, approved substitutions | enclosing revision | draft → frozen; set targets stored structured, all required advanced prescription features retained |
| ProgramAssignment — relationship plan binding | athlete, relationship, program/revision, effective dates, superseded assignment, source template | professional; athlete reader | assigned → superseded/ended; preserve exact plan seen for old workout; disconnection stops new professional writes |
| WorkoutExecutionOverride — permitted minor athlete choice | assignment/day occurrence, athlete, rescheduled date or approved substitute ID, reason | athlete | pending/applied → revised/removed; eligibility checked, immutable plan unaffected; actual session stores applied override |
| ProgramChangeRequest — major athlete proposal | athlete, relationship, base revision, requested changes/reason, professional decision | athlete request; professional decision | submitted → approved/rejected/withdrawn; approval uses normal publication, not athlete edit rights |
| WorkoutSession — personal or assigned execution | athlete, optional assignment/revision, local UUID, start/end, completion state, observed dates, server version, optional approved Mirror summary | athlete | in_progress → completed/abandoned; corrected via expected version/history; personal sessions have no required professional |
| SetLog — actual set result | WorkoutSession, stable UUID, optional prescription/set target snapshot, actual exercise/load/reps/duration/RPE/RIR/tempo/rest, warmup/drop stage, note, revision | athlete | created → corrected → tombstoned; stable ID/parent check, audit and no resurrection on sync |
| SyncOperation — idempotent workout receipt | authenticated User, operation UUID, entity UUID, normalized hash, base version, result/status, received date | sync service for athlete | received → committed/conflict/rejected; committed atomically with writes; replays same result, changed payload 409; retention ≥ offline support window |

Private personal session sharing is subject to the same relationship/sensitive policy. A professional can view permitted results, not rewrite the athlete's actual set logs. External logs are not automatically attached to a different professional scope.

## 7. nutrition

| Entity and purpose | Fields and relationships | Ownership | Lifecycle and history |
|---|---|---|---|
| Food — Iranian/common or custom nutrition entry | name, reference unit/mass, calories/protein/carbs/fat, source/provenance, version, professional owner nullable | platform curator or professional workspace | available → revised/archived; old revisions remain usable; values can be unknown, never coerced to zero |
| Recipe / RecipeIngredient — reusable computed food composition | owner, revision, ingredients with Food version/quantity/unit, servings/yield, computed totals and calculation version | professional | draft → available → revised/archived; immutable ingredient/nutrient snapshot for historical meals; conversions require known unit mass |
| NutritionPlan — identity for structured/free-text plan | professional, title, current NutritionPlanRevision | authorized Nutritionist professional | draft → active → archived; explicit nutrition capability/scope required, never inherited from Coach |
| NutritionPlanRevision — frozen nutrition prescription | plan, parent, author/time, schema/hash, Meal rows, free-text instructions, diff/reason, AI involvement | prescribing professional, athlete through assignment | draft → published → superseded; explicit approval and rollback-as-new-revision |
| Meal / MealItem — prescribed meal/alternatives | revision, day/time/name, notes; Food/Recipe snapshots, quantity, macros, alternate choices | enclosing plan revision | draft → frozen; alternatives explicit, totals reproducible; free text may have unknown numeric totals |
| NutritionAssignment — athlete plan binding | athlete, relationship/scope, exact revision, effective dates | prescribing professional | assigned → superseded/ended; old adherence refers to correct revision |
| MealAdherence — planned-following record | athlete, assignment/meal occurrence, followed/not_followed/unknown, time/note | athlete | recorded → corrected/deleted; absence not nonadherence |
| FoodLog / FoodLogItem — actual confirmed intake | athlete, date/time, quantity/unit, Food/Recipe snapshot or free-text, nutrient totals/source, optional image Asset, confirmed AI draft reference | athlete | draft → confirmed → corrected/deleted; only confirmed AI quantities count; no silent provider write |
| FoodIdentificationDraft — nonauthoritative AI result | athlete/image, provider output, approximate candidates/servings/confidence, selected correction | athlete; generated through intelligence orchestration | pending → generated → confirmed/rejected/expired; confirmation transaction creates FoodLog; raw result kept private/minimized |

Workspace custom foods may be authored by either capability as library content; **prescribing a client nutrition plan** uses the separate capability gate. Public food library access reveals no client intake or health.

## 8. progress (including check-ins)

| Entity and purpose | Fields and relationships | Ownership | Lifecycle and history |
|---|---|---|---|
| BodyMetric — weight/measurement/performance observation | athlete, metric type, value/unit, observed time, source/self-report flag, optional relationship context | athlete | recorded → corrected/deleted; history linked to goals/baseline; no duplicate overwrite by date alone |
| DailyMetric — daily sleep/water/steps/energy | athlete, local date/timezone, metric type/unit/value, source, version | athlete | recorded → corrected/deleted; bounded validation; absent is unknown; multiple observations versus daily aggregate explicitly distinguished |
| Goal — target with meaningful progress | athlete, creator, optional relationship/scope, metric/unit, baseline, target, start/due, visibility | athlete for personal; professional-authored within scope | active → achieved/paused/abandoned/archived; preserve updates, percentage only where denominator is meaningful |
| Milestone — goal checkpoint | Goal, target/due, evidence references, reached time | enclosing goal | planned → reached/missed/waived; corrections/history; not an invented medical conclusion |
| ProgressPhoto — private dated image | athlete, Asset, captured date, tags, caption, specific Consent references; notes separately linked | athlete | private → selectively_shared → revoked/deleted; no inherent public state; case-study public copy managed separately |
| CheckInTemplate / CheckInField — bounded recurring form | professional, revision, field types text/numeric/scale_1_10/multiple_choice/photo, validation/required/choices | professional workspace | draft → published → superseded/archived; published form snapshots preserved |
| CheckInSchedule — assign recurrence | template revision, relationship/group resolved recipients, interval/timezone, next due, active dates | professional | active → paused/ended; recurrence changes audited; group assignment reauthorizes recipients |
| CheckInOccurrence — dated assigned check-in | schedule, athlete/relationship, due date, exact template revision, status | relationship; response by athlete | due → submitted/missed/cancelled; unique schedule/athlete/due key avoids Beat duplication |
| CheckInSubmission — answers and attachments | occurrence, athlete, form snapshot, typed answers, photo Asset references, submitted/edited date | athlete | draft → submitted → corrected/withdrawn; historical answers; sensitive-photo grants separate from submission |

Photo notes use ProfessionalNote in coaching; images do not gain public visibility from a comment. Check-in data joins reports only through authorized selectors.

## 9. scheduling and messaging

| Entity and purpose | Fields and relationships | Ownership | Lifecycle and history |
|---|---|---|---|
| AvailabilityRule / Exception — bookable calendar | professional, timezone, recurring windows, duration/buffer, unavailable exceptions, mode/location | professional | active → revised/paused; bounded look-ahead slots; retain rule context for reservations |
| Appointment — consultation or active-client session | professional/athlete, optional relationship, kind, UTC interval, location/external call reference if supplied, cancellation-policy snapshot, externally_paid/free label | participants; professional schedule owner | scheduled → completed/cancelled/no_show; reschedules append history; overlap checks atomic; no in-app calling |
| AppointmentEvent — session history | appointment, actor/time, prior/new time/status, reason | schedule service | append-only; private notes reference ProfessionalNote; history not rewritten |
| Conversation — private professional-client channel | professional, athlete, relationship episode, current writability | participants | active → read_only/closed on end under final archive policy; no default cross-assistant inbox |
| Message — persistent direct/contextual content | Conversation, sender, stable client UUID, text, created time, reply_to, validated report/workout/nutrition context, important marker | sender within participant channel | sent → edited/deleted tombstone/moderated; revision evidence restricted; permission checked before access; WS loss does not lose row |
| MessageAttachment — private file binding | Message, Asset, purpose, scan status | message participants, subject to sensitive consent | pending_scan → available/rejected/revoked; no public attachment URL; deletion follows message/evidence retention |
| Broadcast — private recipient fan-out | workspace, author, sanitized body, selected active relationship/group IDs, scheduled time | professional | draft → queued → delivering/completed/partially_failed/cancelled; target snapshot plus per-delivery recheck; no recipient list exposure |
| BroadcastDelivery — individual message effect | Broadcast, relationship/recipient, Message result, status/attempts | professional + recipient for own delivery | pending → sent/skipped/failed; unique broadcast/recipient idempotency; client replies privately |

Conversation becomes closed for new messages at end; ordinary service archive does not include the inbox by default. Athletes retain own history under retention. Selected finalized service excerpts, if explicitly manifested and privacy-permitted, are distinct from live chat access. Dispute evidence has independent staff controls and does not reopen chat.

## 10. marketplace and analytics

| Entity and purpose | Fields and relationships | Ownership | Lifecycle and history |
|---|---|---|---|
| PublicProfessionalProjection — allowlisted published/search data | approved professional UUID/slug, safe profile fields, public credential copies, eligible packages, modes/locations, review aggregates/capacity snapshot, SEO metadata | marketplace derived view | eligible → unpublished on restriction/revocation; query-time eligibility guards stale projections; no private documents |
| Favorite — saved professional | athlete, professional, created time | athlete | active → removed; favorites do not grant private profile access |
| ComparisonSelection — up to three professional IDs | athlete/session-scoped IDs, saved/updated date | athlete/visitor | add/remove/clear; reject fourth; compare same public fields as profile |
| Review — verified client opinion | athlete, professional, qualifying relationship IDs, overall and structured ratings, text, current ReviewRevision, visibility | athlete author; staff moderate | draft → published → hidden/deleted; one current review per pair assumption; verified relationship provenance; historical duration snapshot |
| ReviewRevision — edit/delete/moderation history | Review, actor/time, prior/current text/ratings or tombstone, reason | governance-authorized access | append-only; hidden/deleted content excluded from public aggregates, history retained per policy |
| ReviewResponse — one professional public answer | Review, professional, text, edit metadata | professional | draft → published → edited/hidden/deleted; one current response, history audited |
| CaseStudy — explicitly consented public story | professional/athlete, relationship, objective/duration/commentary, selected verified progress provenance, before/after Asset copies, content hash/revision, Consent | professional author; athlete approves | draft → consent_requested → approved → published → withdrawn/hidden/archived; changes require fresh consent; revoke removes copies/links |
| TimelineEvent — unified read projection | athlete, optional relationship/scope, event type/time, source UUID, minimal summary/classification | analytics-derived, permission-filtered | indexed → refreshed/removed on source change/consent withdrawal; never trusted for authorization; source gate on read |
| ReportDefinition — selected filters/metrics | professional, bounded date/client/group filters, selected metrics, format, saved configuration | professional workspace | draft/saved → archived; entitlement and rights checked; no arbitrary query language |
| Report — generated client/weekly/custom output | requester, definition snapshot, input period/source references, state, private Asset, expiry, access-context version | professional workspace or athlete for own export | queued → running → ready/failed/revoked/expired; recheck at generation/download; regeneration after stale permission, no public URLs |
| BusinessMetricSnapshot — professional/product measures | workspace/platform scope, period, metric definition/version, value/denominator/provenance, generation time | professional for own workspace; authorized staff for platform | computed → replaced/reconciled; derive from source truth; recorded coaching revenue labeled unverified |

Case studies may reference self-reported source data but cannot falsely label objective verification beyond what the platform observed. Public credential publication and case study consent use distinct scopes. Public review aggregates exclude moderated/deleted entries.

## 11. intelligence and notifications

| Entity and purpose | Fields and relationships | Ownership | Lifecycle and history |
|---|---|---|---|
| AIJob — provider execution envelope | requester/workspace, capability, source context IDs/period, consent/entitlement references, provider/model, task ID, timeout/cost/status | authorized request initiator | queued → running → succeeded/failed/cancelled; recheck before release; no broad sensitive payload in broker/logs |
| AIInsight — private professional summary/signal | professional/relationship, AIJob, source period/IDs, summary, reasons, confidence/missing data, observed_at | professional workspace | generated → viewed/dismissed → stale/revoked/expired; insight is not a plan or diagnosis; restricted assistant visibility |
| AISuggestion — human-reviewed structured draft | professional/relationship, AIJob, target plan/base revision, proposed typed changes/diff/reasons, actor decision/date, resulting revision | authorized prescribing professional | draft → ready → approved/rejected/stale/failed; approval atomically publishes via domain service; no autonomous changes |
| AIMirrorSession — derived Beta pose session | athlete, exercise enum of three, timestamp, available rep/ROM/tempo estimates, per-metric quality/visibility status, runtime/validation-policy version, optional workout link/share Consent | athlete | local → synced_private → explicitly_shared → revoked/deleted; low quality yields insufficient_confidence/insufficient_visibility, not feedback; no raw video/keypoints by default |
| MirrorValidationPolicy — exercise-specific analysis gates | exercise/model/runtime version, thresholds, camera/visibility requirements, validated observation allowlist, device evidence, approver/date | authorized Mirror validation staff/configuration | draft → validated → effective → retired; feature stays Beta/flag-protected; record policy version in sessions for reproducibility |
| Notification — durable in-app event | recipient User, type, safe title, authorized target reference, read date, originating event key | recipient | unread → read/dismissed/revoked; deduplicate recipient/event/type; no sensitive payload in push |
| PushSubscription — browser endpoint permissions | User, endpoint/keys, consent/preference, device label, created/last success | User | active → invalid/revoked; remove on logout/global revocation when appropriate; treat endpoint/keys as secrets |
| NotificationPreference / DeliveryAttempt — channel choice and retries | User/category/channel opt-in; Notification/provider response/attempt/backoff | User; transport service | preference changes audited where material; attempts pending → delivered/failed/skipped; SMS not a notification channel |

AI data provenance/version is private domain evidence; general audit stores only relevant IDs and changed-field names. A rejected food draft, insight or suggestion never becomes authoritative activity.

## 12. billing, assets and governance

| Entity and purpose | Fields and relationships | Ownership | Lifecycle and history |
|---|---|---|---|
| SubscriptionPlan / PriceRevision — Admin-configurable Pro offer | monthly/annual period, IRR amount, annual discount representation, effective dates, entitlement catalog version | authorized billing staff | draft → effective → retired; immutable purchased snapshot; no automatic recurring mandate |
| Subscription — professional access period | professional, paid period references, start/end/grace_end, derived effective state, plan/entitlements | professional; billing service | free → active_pro → grace (seven days) → expired/free; verified renewal; never cascade-delete clients |
| Payment — platform Pro purchase only | purchaser/professional, order UUID, price/period snapshot, amount/currency, gateway authority/ref, verification state/time | purchaser and authorized billing staff | created → pending → verified/failed/cancelled; pending_reconciliation on uncertainty; unique gateway reference and activation effect; append verification history |
| SubscriptionPeriod — immutable paid activation | subscription, verified Payment, dates, price/entitlement snapshot, activation key | billing service | issued → corrected only via audited compensating action; one effect per Payment; no package funds |
| EntitlementConfiguration — central configurable rules | catalog version, Free maximum five, initial beta Pro active-client limit 100, allowed features/limits/effective dates | authorized billing staff | draft → published → superseded; editable without deploy; resolve through central service, invalid/missing config fails closed; lowering caps retains clients; purchase price terms remain snapshotted |
| Asset — file authority metadata | owner User/workspace, purpose/validated subject, opaque key, private/public-copy class, size/checksum/MIME, scan/derivative state | source owner; assets controls delivery | pending_upload → quarantined → ready/rejected → revoked/deleted; source/derivatives mapped for erasure; public copy only from approved publication |
| Consent — explicit purpose-limited grant | athlete, grantee, purpose (active sharing, archive sharing, nutrition_adherence_read, reviewed AI feature, Mirror summary, case study), specific objects/categories, version/hash, grant/revoke/expiry, text version | athlete | proposed → granted → revoked/expired; active grants end with episode; archive grants independent and never implied; consent alone cannot permit default-excluded external-AI files |
| FeatureFlag — coarse product system switch | key Mirror/Insights/Marketplace/professional_registration, enabled, actor/reason/time | authorized product staff | enabled ↔ disabled with audit; no A/B assignment platform; deny actions without deleting history |
| AuditEvent — metadata evidence | actor or system/task, action/result, time, subject type/UUID, context, reason, redacted changes, correlation ID | governance restricted staff | append-only → retained/purged under approved policy; no ordinary user edits; sensitive read/action evidence |
| OutboxEvent — reliable side-effect trigger | aggregate type/UUID, event type/version, safe minimal payload, committed time, dispatch state/attempts, dedup key | transactional service/governance infrastructure | pending → claimed → dispatched/retry/exhausted; durable reconcile after crash, at-least-once consumer effects |
| ModerationReport — report eligible content/user | reporter, validated subject/context, category/reason, submitted_at, staff assignee, decision | reporter limited view; assigned staff | open → triaged → resolved/dismissed; optional temporary hiding; record all actions, no arbitrary reported-object access |
| DisputeCase / DisputeEvidence — formal complaint | parties, subject/description, relationship/context, private Asset evidence, assigned staff, resolution notes/outcome | filing party plus assigned dispute staff with bounded party visibility | submitted → triaged → investigating → resolved/closed; reopening audited; confidential notes separated; evidence legal holds require policy |
| PrivacyRequest — export/deletion workflow | User, kind, verification time, status, inventory/version, policy version, private export Asset, retained exception summary | User; privacy staff | export requested → verified → processing → completed; deletion requested → verified → pending_deletion → evaluating_holds → deleting/anonymizing → completed or partially_held → resumed; immediate normal-access restriction; bounded retries/audit |
| RetentionPolicy — central lifecycle durations | data class/purpose, configurable duration, effective/version/approval dates, infrastructure backup policy reference | authorized privacy/operations staff | draft → approved/effective → superseded; no scattered domain constants; actual values require release sign-off; past/current policy decisions recorded |
| RecordHold — temporary record-specific erasure block | typed subjects, dispute/fraud/security/required-audit purpose, authorizer, reason, review/expiry/released time | privacy/security/dispute staff only | proposed → authorized_active → reviewed/released/expired; prevents affected deletion only, never restores normal athlete/professional access; all changes audited |
| ErasureMarker — restore-safe deletion/revocation record | pseudonymous subject UUID, action/time, retained-data exception metadata, expiry | privacy operations only | applied → replayed on restore → retired per policy; no health/phone payload; prevents deleted data becoming live after backup restoration |

Admin capabilities are actions on these records, not a new consumer authentication model. Operational admin cannot automatically read all private medical/photo/chat content. Payment correction/refund handling for Pro may require later gateway-specific workflows; external coaching refunds remain outside platform settlement.

## 13. Lifecycle cross-checks and erasure boundaries

| Trigger | Immediate authoritative changes | Later side effects |
|---|---|---|
| Relationship accepted | request accepted; episode/scopes/seats allocated; distinct-client cap checked; submitted intake reference fixed | notice, timeline event, CRM projection |
| Relationship ended/disconnected | episode ended; scopes/seats released; active grants revoked; writes/new data denied; fixed ArchiveManifest under current archive consent | socket closure, waitlist notices, job cancellation, stale output purge; retained finalized records remain read-only/filterable |
| Sensitive grant revoked | Consent terminal revocation; access version increases | private output invalidation/public copy purge when relevant; signed URL residual window disclosed |
| Plan revision published | new immutable revision/assignment/audit/outbox; expected base checked | notification/report projection, never rewriting completed logs |
| Pro expires after grace | effective entitlements become Free from timestamps | UI notices and projection updates; preserve clients/plans/history |
| Verification revoked or user suspended | public eligibility denied immediately | search/page purge, notifications, staff review |
| Account deletion accepted | auth revoked, public/sharing access removed, inventory frozen | bounded erase/anonymize across domains/storage/providers, retention exceptions and backup markers |

All history remains private/permission-filtered. Deletion erases/anonymizes nonheld records under configurable RetentionPolicy; RecordHold isolates temporarily retained evidence without ordinary access. ErasureMarker outlives restorable backups; backups expire by infrastructure policy and restores replay markers before traffic. Numeric retention durations/evidence standards remain operational release items; the workflow/archive policies are locked and closed.
