# C02 Accounts, OTP, Authentication and Base Authorization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans after a separate execution authorization. Steps use checkbox (`- [ ]`) syntax. **Planning only: no step below has been executed.**

**Goal:** safe adult phone entry, browser sessions and the smallest account/governance policy foundation required by subsequent private domains.

**Architecture:** retain the completed Django monolith and permanent `accounts.User`. PostgreSQL owns challenges, delivery state, account/session versions, recovery, audit and outbox; Redis provides atomic admission limiting, with a durable quota guard. Accounts owns identity rules; governance depends on accounts; project composition wires synchronous transactions without reversing that dependency.

**Tech Stack:** existing Python 3.13/Django 5.2 LTS, DRF, PostgreSQL 17, Redis, Celery/one Beat, Django sessions/Templates, Tailwind, Vanilla JavaScript ES Modules, pytest and Playwright. Preserve `uv.lock`, `package-lock.json` and the C01 runtime/security hardening. No dependency installation or change during planning.

**Spec:** [Product](../../product/V1_PRODUCT_SPEC.md), [risks](../../product/OPEN_QUESTIONS_AND_RISKS.md), [architecture](../../architecture/V1_ARCHITECTURE.md), [domain model](../../architecture/DOMAIN_MODEL.md), [permissions](../../architecture/PERMISSIONS_MATRIX.md), [ADR-001](../../architecture/ADR-001-modular-monolith.md), [ADR-002](../../architecture/ADR-002-authentication.md), [ADR-003](../../architecture/ADR-003-realtime-background-jobs.md), [ADR-004](../../architecture/ADR-004-storage-privacy.md), [ADR-005](../../architecture/ADR-005-ai-boundaries.md), [roadmap C02](../../implementation/V1_IMPLEMENTATION_ROADMAP.md#c02--accounts-otp-authentication-and-base-authorization), and [C01 ledger](../../implementation/C01_CLOUD_EXECUTION_LEDGER.md).

## Global constraints

- This document authorizes no coding, migration generation/execution, dependency change, remote write, merge, deployment or C03 work. Its assumptions are proposed implementation decisions for review, subordinate to the locked sources.
- Preserve `AUTH_USER_MODEL = 'accounts.User'`, its integer key/public UUID/canonical unique phone and unusable passwords. Never replace User, edit `accounts/0001_initial`, create `auth_user`, or introduce email/password consumer login.
- Additive migrations only. Preserve existing rows and UUIDs; create no AthleteProfile, ProfessionalProfile, role/relationship/CRM model or feature-domain placeholder.
- Browser authentication is Django database sessions plus CSRF, including anonymous OTP operations. No JWT, browser credential in localStorage/IndexedDB, native authentication adapter or Django admin/password-login route.
- All account holders are 18+. Compute age from a declared birth date and separately record attestation; phone possession is not age evidence. Account terms never substitute for sensitive-data consent.
- Keep named staff capabilities, case assignment, fresh step-up and audit mandatory. `is_staff` and `is_superuser` are insufficient by themselves. Staff MFA/evidence standards remain release dependencies, not bypass permissions.
- Governance may import accounts only. Accounts imports no governance/assets/profile/feature app. Composition under `config/use_cases/` wires providers, authorization and audit/outbox callbacks; business decisions remain in their owning domains.
- No full privacy export/deletion execution, scan/upload pipeline, ErasureMarker/restore execution, entitlement, notification SMS, AI/Mirror or experimentation implementation. C18 owns full privacy execution; future stages own affected-domain revocation handlers.
- Preserve explicit Uvicorn safe `log_config`, disabled raw access logging/proxy trust, Redis TLS certificate/hostname checks and URL query rejection, production configuration validation, private S3 and strict browser-console checks.
- UTC timestamps, Tehran civil-date age checks, Persian RTL and explicit date-calendar labels. Exposed resource IDs are UUIDs; opacity never authorizes access.
- No plaintext OTP in PostgreSQL, Redis, outbox, audit, logs, URLs, files or persistent mock storage. Transient generator/provider arguments and in-memory test collectors are the only plaintext handling.
- PostgreSQL/Redis concurrency and atomicity gates run genuinely in Docker-capable CI; no SQLite, fakeredis or mock concurrency substitute. Cloud executes available unit/static checks. Required cases cannot skip silently.

## Review focus

1. A delayed SMS acknowledgement must not resurrect a challenge invalidated by resend/recovery; Task 5 tests late acknowledgements against a newer generation.
2. Redis reset, process crash or failed cross-store cleanup must not reopen used quota or issue a session; Tasks 4/6 test durable reservations and failure injection.
3. A simultaneous suspension/phone change must not leave a just-issued session valid; Tasks 7/8/9 test both transaction orderings with separate PostgreSQL connections.
4. Staff superuser status or a submitted step-up/evidence ID must not substitute for verified authority; Task 8 tests forged, stale, wrong-case and self-approval inputs.
5. A C01 user without a birth date, a leap-day birthday or a calendar conversion ambiguity must not acquire product access incorrectly; Tasks 1/2/6/15 cover migration and date boundaries.

## 1. Confirmed C01 baseline and actual interfaces

Read-only verification on 2026-10-05 confirmed:

| Item | Confirmed state |
|---|---|
| Remote | private `alireza-anari/fitlink-v1`, `foundation/c01-cloud` |
| Remote head | `75c551e5b9bbbfb7777ee52b09a1993b681e921a` |
| Matching local head | `5881a2792beca2dbd56cfb9ec6cecf910879d6ab` |
| Exact shared tree | `4dff1ebd5a32ed0359552bf29012d9d1ecf09b24` |
| Actual CI | run `37296846443`, SUCCESS on that remote head |
| Application models | only `apps/accounts/models.py:User`; assets is a storage adapter, not an Asset model |
| Initial migration | `apps/accounts/migrations/0001_initial.py`; custom User and its auth relations |
| Public routes | `/`, `/health/live/`, `/health/ready/`, `/api/v1/status/` |
| Auth defaults | DRF SessionAuthentication/IsAuthenticated; status explicitly public; Django CSRF middleware installed |
| Redis databases | cache 0, broker 1, result 2, Channels 3 |
| CI discovery | `tests/unit`, `tests/integration`, `tests/e2e`; selected skips fail the session |
| Runtime | separate development/checks/e2e/production images; browser shares web network namespace and uses real loopback |

Existing `canonical_phone()` and `UserManager.create_user()` accept only canonical ASCII phones; keep that persistence boundary. New input normalization occurs before those calls. Existing scope tests assert exactly the C01 model/route/field set, and the Beat test asserts an empty schedule: evolve only these stage-specific allowlists when their authorized C02 additions arrive. Do not delete, skip or weaken the C01 behavior/security assertions. Existing production test fixtures and `docker/production_check.py` will need synthetic new secret/config values, not an enabled production Mock provider.

C01 source remains the baseline fixture for the upgrade rehearsal; never infer it from the unrelated bootstrap `main` ancestry.

## 2. Selected design and explicit implementation assumptions

### Alternatives considered

| Approach | Assessment |
|---|---|
| Synchronous bounded SMS + PostgreSQL digest/delivery state | Selected. No durable code payload or broker dependency; uncertainty requires a new challenge, never optimistic login. Adds bounded web latency. |
| Queued SMS with encrypted durable code envelope | Deferred. Would require reviewed encryption/key lifecycle and delivery reconciliation; digest alone cannot reconstruct a code. No plaintext Celery argument is acceptable. |
| Redis-only challenge/attempt state | Rejected. Does not provide the durable, transactional identity/audit/recovery guarantees. |

### Phone, client address, date and configuration

- `normalize_iranian_mobile(raw: str) -> str`: limit raw input to 64 characters; map only ASCII, Persian `۰..۹` and Arabic `٠..٩` digits; allow space, hyphen and parentheses as separators; reject bidi/control/zero-width characters, letters and other digit scripts. Accept local `09xxxxxxxxx`, national `9xxxxxxxxx`, `989xxxxxxxxx`, `+989xxxxxxxxx` and `00989xxxxxxxxx`; yield exactly `+989` plus nine ASCII digits. Reject extensions, multiple plus signs, landlines, wrong lengths and non-Iranian prefixes. All rate/security keys use the result, never raw input.
- `client_ip(peer: str, forwarded_for: str | None, trusted_cidrs: tuple[str, ...]) -> str`: default trusts no proxy. Use ASGI's unchanged peer/`REMOTE_ADDR`; ignore forwarding headers from an untrusted peer. For a trusted peer, validate at most 10 bounded X-Forwarded-For entries and walk right-to-left through trusted hops to the first untrusted address. Reject malformed trusted chains before admission. Normalize IPv4-mapped IPv6; do not enable Uvicorn `proxy_headers` or trust all networks. Production proxy must overwrite/append the documented header and have approved CIDRs.
- `parse_birth_date(raw: str, calendar: Literal['gregorian','jalali']) -> date`: digit normalization, explicit calendar, strict date components, Gregorian date storage. Persian UI offers labeled Jalali inputs and a labeled Gregorian fallback; no silent calendar guessing. Plan a small isolated stdlib calendar adapter using a reviewed, license-attributed Borkowski/Jalaali conversion reference, with published reference vectors and exhaustive roundtrips for the declared UI-supported range 1200..1500 Jalali. Outside that range use the explicit Gregorian input rather than approximating. No package or CDN installation is planned. `Intl.DateTimeFormat` is display enhancement only, never the authorization authority.
- `require_adult(birth_date: date, attested: bool, at: datetime) -> None`: use Tehran's civil date and Gregorian anniversary comparison; reject future/invalid dates, missing attestation and age <18. February 29 reaches its anniversary on March 1 in a non-leap year. This calendar convention is an implementation assumption requiring age-policy review before live entry; do not claim verified age.
- New typed `AccountSecurityPolicy` retains ADR-002 defaults: 6 digits, expiry 300s, resend 60s, 5 attempts/challenge, rolling 3600s sends phone/IP 5/20, failures phone/IP 10/60. Positive bounded configurable values; malformed/zero values fail boot without logging values. C02 engineering defaults: SMS timeout 3s, recent OTP/step-up 600s, recovery receipt lifetime 7 days, outbox scan 30s/batch 100/lease 60s/max 8 attempts/backoff capped 300s. These are not retention periods.
- `ACCOUNT_SECURITY_KEYS_JSON` is an environment-only bounded key ring (maximum 3 key IDs, each decoded key at least 32 bytes); `ACCOUNT_SECURITY_ACTIVE_KEY_ID` must exist. Domain-separate HMAC for OTP, phone/IP identifiers and receipt/session handles. Store key IDs, not keys. Retained keys must cover outstanding security-record lifetimes; aggregate durable quotas across retained key IDs during rotation. Removal requires an audited invalidate/warm-up procedure; it cannot silently reset limits.
- Dev/test uses `MockSmsProvider` whose send outcome and memory collector are deterministic; OTP generation still uses `secrets.randbelow(1_000_000)` formatted to six digits. Test collectors are private Python fixtures, never a web OTP-reading route. Production rejects Mock, test code generators, fake step-up and unknown providers. Default production `AUTH_ENTRY_ENABLED=False` and `STAFF_RECOVERY_ENABLED=False`; routes fail closed. Enabling entry requires a reviewed configured non-Mock adapter; none is selected/implemented in C02. Other Foundation checks can boot with synthetic keys and disabled entry.

### OTP lifecycle, admission and enumeration resistance

`OTPChallenge` binds UUID, canonical phone, purpose, phone generation, optional target User UUID/auth version, optional recovery/change context, HMAC key ID and digest, issue/expiry, delivery state, attempts and terminal timestamps. Purposes are server allowlisted: `login`, `recovery_new_phone`, `phone_change_old`, `phone_change_new`; client input cannot turn a proof into another purpose. Do not serialize challenge rows.

1. Normalize/validate and enforce CSRF before SMS or quota effects. Admit both phone/IP dimensions atomically with Redis Lua; then apply the authoritative PostgreSQL quota check under sorted security-anchor locks. Count attempted delivery, including timeout/failure, conservatively; no refund on crash/DB refusal.
2. Lock the permanent phone anchor, enforce cooldown and retire all earlier same-purpose/context challenges by incrementing its generation. Commit digest-only `pending` challenge + cooldown + security admission + metadata audit. No User is created at request time.
3. Send the transient code outside database locks through the 3s-bounded provider with an idempotency correlation UUID. Re-lock and mark `sent` only on an explicit accepted result for the still-current, unexpired generation. Timeout/uncertainty/exception is `failed`; no automatic retry can reproduce the discarded code. Crash while pending leaves it unverifiable; the next permitted request creates a new generation.
4. Return `202 {"status":"accepted","challenge_id":"<opaque UUID>","resend_after_seconds":60}` for valid admitted requests regardless of new/existing/restricted/suspended phone or delivery failure. Accepted means attempt recorded, not guaranteed delivery. Genuine throttling uses uniform 429/retry metadata based only on quotas/cooldown; global limiter outage uses uniform 503. Invalid phone syntax uses uniform 400 and never queries account existence. Provider work is the same for existing/unknown phones; do not branch into a faster account-existence path or claim perfect network timing equality.
5. Verify takes normalized phone + opaque challenge ID + six digits; purpose/context come from the route/service. Unknown/mismatched/expired/failed/consumed/locked proof returns the same `400 {"status":"verification_failed"}` without attempts/account/delivery details; use a dummy keyed comparison on absent rows. Shape errors disclose syntax only. Valid possession may legitimately expose only that person's signed-in account.
6. Reserve a potential failure slot for both phone/IP dimensions before comparison. PostgreSQL counts pending+failed reservations within the rolling hour under locks; Redis does the same atomically. Correct proof releases its slot; wrong/unknown proof finalizes failure. A crash/uncertain cleanup conservatively retains the reservation through its window. Finalization failure mints no session. Redis reset cannot bypass the PostgreSQL guard; Redis unavailability cannot be bypassed by that guard.
7. Commit incorrect-attempt increments/audit even when returning a failure result; raising an exception across `atomic()` must not roll back the attempt budget. The fifth incorrect attempt locks the challenge; the fifth correct attempt can consume it. Expiry uses `at >= expires_at`; resend at exactly 60s is allowed. Always use server time.
8. Correct login proof, adult gate, current account state, unique User creation/lookup, proof consume and rotated saved database session commit together. A failed audit/outbox/session write rolls back the transition and returns no authenticated cookie; conservative admission can remain spent. A non-login verification also consumes the code exactly once and records a durable verified proof on the challenge (`consumed_at`, bound context/User/auth version, `proof_applied_at=NULL`). Applying recovery/change later uses that verified, unexpired, not-yet-applied proof under row locks and sets `proof_applied_at` in the identity transaction; it never compares or consumes the code again. Code replay fails even before application. No non-login proof logs the claimant in.

**Cross-store rule:** Redis and PostgreSQL are not claimed to have a distributed transaction. PostgreSQL is the final durable authority; leaked Redis reservations can reject extra requests but cannot grant extra access. A security service never treats a Redis exception as an allow decision.

### Lock ordering and session revocation

Create anchors with database uniqueness and conflict-safe insert before selecting them for update, including the first request for a previously unseen phone/IP. Global order: security-rate anchors sorted `(kind,key_id,key_digest)` → phone anchors sorted canonical phone → involved User rows sorted internal ID → challenge/recovery/privacy rows → session controls/staff grants/step-up rows → audit/outbox append. Services discover candidate IDs without locks, acquire in order, re-read and retry at most 3 times if the identity mapping changed. No request retries after an SMS send.

`AccountSessionControl` stores only a keyed session identifier digest/key ID, User, issued auth version, scope, authentication time, expiry and revoked time. The existing Django session table remains the session backend. Session payload has User ID, issued auth version and scope, never roles/capability decisions. Every private request re-reads User/state/auth version and control; mutation services recheck under the User lock. Missing rows/version, DB outage or revocation fail closed. Raw session cookies/keys never enter account/audit/outbox logs.

| Account condition | Permitted behavior |
|---|---|
| active + recorded adult eligibility | normal owned account actions |
| C01 legacy row missing adult data | no product actions; verified phone entry may complete adult attestation |
| restricted | fresh `account_control` session only: self status, permitted privacy intake/status, logout; no product/staff/referral writes |
| deletion_requested/pending_deletion | fresh `account_control` session only: self/privacy status and logout; no new normal sharing/grants |
| suspended or `is_active=False` | no login/product session; manual recovery/receipt channel does not restore privileges |
| deleted/anonymized/deletion_completed | reserved terminal states for C18; no C02 transition or access |

Restrict/suspend, verified deletion, global logout and successful phone change increment `auth_version` and revoke controls/current OTP state synchronously. Recovery preserves restrictions/suspension; it cannot reactivate an account. Global logout is stronger than single-session logout. Future channels/jobs/push/profile handlers must call the same gate; C02 implements no absent future domain.

### Manual recovery and authenticated phone change

- Anonymous recovery intake accepts claimed old phone, proposed new phone and a contact preference, not account UUID discovery. Store a nullable confidential target resolution and return the same 202 + random receipt for existing/unknown accounts. The receipt is a restricted status capability, not an authenticated session; store only its HMAC, use HttpOnly/SameSite cookie (Secure in production), and never URL/localStorage it.
- Status is only `received`/`closed`, with no target/account existence/evidence/decision/rejection reason. Unknown and rejected cases do not have a distinguishable immediate-close path. Receipt missing/invalid/expired gives generic 404; UUID alone grants nothing. Apply separate bounded phone/IP intake limits using the same atomic admission substrate (engineering defaults 3/phone/day, 10/IP/day) and bounded input; recovery cannot become an unlimited alternate OTP-send route.
- Explicit StaffCapabilityGrant + assigned case + fresh server-issued StaffStepUpGrant + reason + separation from the claimant/target are required for target resolution, evidence reads and decision. No Django `has_perm()` superuser shortcut. No self-grant API or broad user CRUD/admin endpoint.
- RecoveryEvidenceMetadata stores bounded classification, verification outcome, reviewer/time, content checksum and an opaque secured evidence-system reference only. No identity-document bytes/free-form evidence transcript, Asset upload endpoint or consumer evidence browsing in C02. Actual evidence access must occur through an approved secured operational procedure; absent that procedure, production recovery stays disabled.
- Staff approves/rejects only after evidence review. A fresh `recovery_new_phone` OTP binds the case and proposed phone; it proves no old-account identity. Apply rechecks current case version, authority, proof age ≤300s, unchanged target identity, current account restrictions and new phone uniqueness inside one transaction.
- Update the existing User phone, append immutable PhoneChangeHistory, increment auth version, mark the already-verified new-phone proof applied, retire old challenges/controls, append audit/outbox and mark the case applied atomically. Unique conflict never merges users or transfers another account's phone; staff gets safe 409, claimant gets coarse status. Replays return the same completed effect. No automatic authenticated session is returned.
- Normal authenticated phone change is a separate owned command, requiring fresh `phone_change_old` and `phone_change_new` proofs bound to the same change UUID/User/auth version. Recovery cannot stand in for either proof. Same uniqueness/history/revocation transaction; clients must sign in again with the new phone.

## 3. Planned schema and migrations

All rows use created/updated UTC times as appropriate; exposed entities have public UUIDs. Security/audit/history User references use PROTECT or typed UUID as specified, never cascading deletion of evidence. No schema exists yet beyond C01.

| Model / change | Essential fields and constraints | Owner/task |
|---|---|---|
| User additions | `birth_date` nullable DateField; `adult_attested_at` nullable; `adult_attestation_version` bounded string; `locale='fa'`; `timezone='Asia/Tehran'`; `state`; `state_version>=1`; `auth_version>=1`. Preserve C01 fields/UUID/phone check. Attestation timestamp/version require birth_date; terminal/suspended state implies inactive; active/restricted/pending states imply active. | accounts / 2 |
| OTPPhoneState | canonical unique phone, generation>=0, next_send_at; no User creation or claim from anchor existence | accounts / 2 |
| SecurityRateAnchor | kind phone/IP, HMAC key ID/digest; unique `(kind,key_id,key_digest)` | accounts / 2 |
| SecurityRateEvent | UUID reservation, phone/IP anchor FKs, kind send/verify_failure/recovery_intake, pending/failed/succeeded outcome, timestamp; indexes `(anchor,kind,at)` and unique reservation ID; no code/raw IP | accounts / 2 |
| OTPChallenge | lifecycle fields from §2; purpose/state enums, attempts 0..5, expiry>issue, terminal/delivery consistency; nullable `proof_applied_at` permitted only for a consumed non-login challenge; unique `(phone_state,generation,purpose,context_uuid)` with a non-null sentinel context UUID for login; indexes phone/purpose/time, expiry, bound User/version | accounts / 2 |
| AccountSessionControl | User, digest/key ID unique, auth version, normal/account_control scope, last authentication, expiry>created, revoked time; indexes User/revoked/expiry | accounts / 2 |
| RecoveryRequest | UUID, nullable target User, confidential claimed/proposed phones, assigned staff, state/version, receipt digest/key ID/expiry, evidence decision/authorizer/reason, new-phone challenge/verified time, applied time; one applied effect per case | accounts / 8 |
| RecoveryEvidenceMetadata | case FK, verification type/outcome/checksum, opaque evidence reference, reviewer/time; restricted selectors only | accounts / 8 |
| PhoneChangeIntent | UUID, User, old/new canonical phones, issued auth version, expiry/version, old/new verified challenge FKs, applied time; one live intent/User; distinct purpose-bound proof references | accounts / 9 |
| PhoneChangeHistory | User UUID/reference, protected old/new phone fields, recovery or authenticated-change context UUID (exactly one), actor/time, old/new auth versions; unique effect context; immutable SQL/ORM guard | accounts / 8–9 |
| StaffCapabilityGrant | User, bounded capability enum, valid_from/until/revoked, granting actor/reason; unique live User/capability; no custom ACL builder | governance / 3 |
| StaffStepUpGrant | User/auth version, capability, verified method/provider reference, expiry, trusted issuer; no caller-created assertion accepted | governance / 3 |
| AuditEvent | UUID, pseudonymous actor/system identity, action/result enum, subject type/UUID, correlation UUID, reason code, changed-field names, time; strict metadata allowlist; append-only SQL and ORM | governance / 3 |
| OutboxEvent | event UUID/type/schema version, typed aggregate UUID/version, minimal ID-only payload, dedup key unique, state/attempts/available_at/lease, dispatched/exhausted metadata; indexes due/lease | governance / 3 |
| OutboxDeliveryReceipt | event/handler/effect key unique, completed_at; durable idempotency, not exactly-once transport | governance / 13 |
| Consent + ConsentScope | subject User, optional grantee User, purpose, validated typed scope/context UUID/category rows, immutable text version/hash, granted/revoked/expiry, version; unique scope entries, expiry after grant; revoked grant never reactivated | governance / 10 |
| FeatureFlag | four unique keys `marketplace`, `professional_registration`, `ai_insights`, `ai_mirror`, enabled/default false, version, actor/reason/time; no assignments/experiments | governance / 11 |
| InviteReferralLink + ReferralAttribution | issuer User, opaque random token digest unique, expiry/revocation; recipient User unique attribution, source link UUID/time. No profile/package FK or cash reward | accounts / 11 |
| PrivacyRequest | User, export/delete kind, UUID, requested/verified/pending_execution/pending_deletion status, verified authentication reference/time, policy version reference if approved; owner/status index; one open request/User/kind | governance / 12 |
| RetentionPolicy | data class/purpose, version, duration nullable until approved, effective/approval/legal-basis metadata, backup policy reference; unique class/purpose/version; effective requires approved concrete values | governance / 12 |
| RecordHold | validated typed record UUID, authorized purpose/reason/actor, review/expiry/release; bounded subject, expiry>created; active hold never confers ordinary access | governance / 12 |

Migration sequence: accounts `0002_account_security` adds nullable age/attestation plus version/state fields and security tables; a separate additive data migration maps existing `is_active=False` rows to suspended without inventing DOB/attestation; then validate the state/attestation constraints. Governance `0001_initial` depends on the required accounts security migration and uses swappable User dependencies. Later migrations add recovery/history, consent, flags/referrals, privacy metadata and outbox receipts in their owning tasks. Exact later migration numbers are assigned during execution, not guessed over existing migrations.

First-schema race-sensitive invariants: phone and UUID uniqueness; anchor uniqueness; unique generation/context; unique receipt/digest/effect; single-use transitions under row locks; active-case/open-privacy uniqueness; positive auth/state version; immutable audit/history. Database constraints complement services, not replace current authorization.

Audit/history update/delete guards must reject QuerySet, model and direct SQL mutations. Production migrator/owner and runtime principals are distinct; runtime gets INSERT/SELECT but no UPDATE/DELETE on audit/history. A privileged C18 retention role/process is reserved, ungranted to runtime and unavailable to ordinary staff/superuser services. Do not use a caller-settable PostgreSQL session flag as a trigger bypass. CI tests both owner-trigger enforcement and a restricted runtime role; no production credentials are involved.

## 4. File map and shared contracts

Keep existing `apps/accounts/models.py` for User, importing focused `security_models.py`, `recovery_models.py` and `referral_models.py` for registration. Do not create a conflicting `models/` directory beside it. Governance's `models.py` registers focused `audit_models.py`, `staff_models.py`, `consent_models.py`, `flag_models.py`, `privacy_models.py` and `outbox_models.py`.

| Area | Planned files / responsibility |
|---|---|
| Account values/config | `apps/accounts/contracts.py`, `phone.py`, `dates.py`, `security_config.py`, `security_keys.py`, `client_ip.py` |
| Security state/logic | `security_models.py`, `limiter.py`, `lua/otp_admission.lua`, `sms.py`, `otp.py`, `sessions.py`, `policies.py`, `selectors.py`, `state.py` |
| Recovery/referrals | `recovery_models.py`, `recovery.py`, `phone_change.py`, `referral_models.py`, `referrals.py` |
| Governance | `apps/governance/{__init__,apps,models}.py`; focused models/services `audit.py`, `staff.py`, `consents.py`, `flags.py`, `privacy.py`, `retention.py`, `outbox.py`, `tasks.py` |
| Wiring/security adapters | `config/use_cases/{__init__,identity,recovery,privacy,consent}.py`, `config/event_handlers.py`, `config/account_middleware.py`, `config/authentication.py`, `config/permissions.py`; update settings/URLs/Celery wiring only in their owning tasks |
| Presentation | accounts `forms.py`, `serializers.py`, `views.py`, `api.py`, `urls.py`; governance `api.py`, `views.py`, `urls.py`; `templates/accounts/`, `templates/governance/`, `static/src/accounts.js` and labeled calendar enhancement |
| Verification | new `tests/unit/c02/`, `tests/integration/c02/`, `tests/e2e/c02/`; `docker/verify_c02.sh`, `docker/c02_upgrade_probe.py`, CI workflow extension and exact baseline fixture rehearsal |
| Handoff | `docs/development/C02_SETUP.md`, `C02_HANDOFF.md`, future `docs/implementation/C02_EXECUTION_LEDGER.md` |

Central value types in `apps/accounts/contracts.py`: frozen `SecurityOutcome(action,result,subject_uuid,correlation_id,changed_fields,reason_code)`; `AccountSecurityPolicy`; `AdmissionResult(allowed,retry_after,reservation_id)`; `OtpRequestResult(status,challenge_id,resend_after_seconds)`; `OtpProofResult(valid,purpose,challenge_id,user_uuid,context_uuid)`; `SessionScope` (`normal`/`account_control`); `RecoveryReceipt(request_uuid,raw_receipt)`; `IdentityChangeResult(user_uuid,auth_version,context_uuid)`. Raw receipt is returned once and never repr/logged. Secrets/code-bearing provider input objects have redacted repr.

`OutcomeRecorder = Callable[[SecurityOutcome], None]` is supplied by the composition root; accounts imports only its own contract. `config/use_cases/identity.py` controls one transaction and wires the recorder to `governance.audit.append_event()` and `outbox.append_event()` on the same PostgreSQL connection. Required callbacks cannot default to a no-op. Views/tasks call public use cases, never an unaudited identity mutator. Typed denied results commit attempts/audit; exceptions are reserved for rollback/unavailability.

Future ownership/scope validation enters governance through explicitly server-produced `ValidatedConsentScope` / `ValidatedRecordSubject` values and an installed validator callback, not arbitrary API UUIDs. C02 exposes no grant endpoint for nonexistent feature objects. No dynamic feature imports or generic plugin/event framework.

## 5. Exact verification conventions (future execution only)

Commands below are planned, not run during this planning task. Prefix Cloud commands with `TMPDIR="$PWD/.superpowers/tmp"` when required by the host. `uv run --frozen pytest tests/unit/c02/... -q --strict-markers` is the Cloud gate. Real-service tests use the checks image against isolated PostgreSQL/Redis; set no `reuse-db` option.

For task integration commands, with an already provisioned isolated C02 project:

```bash
docker compose -p fitlink-c02-verify --env-file .env.c02.verify --profile test run --rm checks uv run --frozen pytest <task paths> -q --strict-markers
```

This invocation is abbreviated as `CI(<task paths>)` in task text; it is not a shell command or a skipped gate. Tasks also state literal pytest paths. The final `docker/verify_c02.sh` must use the same prefix, generate ignored mode-0600 credentials, refuse pre-existing project volumes, perform migrations/build/startup and clean down without `-v`. Rehearsals use new project names when prior volumes exist. No secrets/config dumps or destructive default cleanup.

Every task uses RED → minimal implementation → GREEN → full available checks → explicit staging → coherent commit. Expected GREEN means exit 0, all selected cases passed, no selected skips. Missing implementations should fail on the named contract, not a silently deselected test. If red is an environment/import problem, diagnose and record it rather than claiming behavioral TDD.

### Task 1: Canonical inputs and fail-closed security configuration

**Goal:** one tested input/key/policy contract before durable models or authentication.
**Files:** create accounts `contracts.py`, `phone.py`, `client_ip.py`, `dates.py`, `security_config.py`, `security_keys.py`; tests `tests/unit/c02/test_inputs.py`, `test_security_config.py`; modify environment examples/settings and production-check synthetic fixtures only as needed.
**Schema:** none.
**Interfaces:** produce all §4 value types and §2 normalization/IP/date/policy functions; `security_digest(kind: str, value: str, key_id: str) -> str` uses keyed domain separation.
- [ ] Write tests first: Persian `۰۹۱۲۳۴۵۶۷۸۹` and Arabic `٠٩١٢٣٤٥٦٧٨٩` both normalize to `+989123456789`; all accepted forms converge, invisible/mixed foreign digits/extensions fail. Published date vector `1395-01-23` → `2016-04-11`; non-leap Esfand 30 fails; age one day before/on 18th birthday, Feb 29 and Tehran/UTC date boundary differ correctly. Spoofed forwarded headers cannot change an untrusted peer; mapped IPv6 and multi-proxy chains normalize consistently.
- [ ] RED: `uv run --frozen pytest tests/unit/c02/test_inputs.py tests/unit/c02/test_security_config.py -q --strict-markers`; expected named missing contracts fail.
- [ ] Implement strict parsing/key/policy functions; retain manager's canonical-only save boundary. Validate exact ADR defaults, bounded timeouts/key ring and production Mock/fake-step-up rejection with entry disabled/enabled configurations.
- [ ] GREEN: rerun the RED command; `uv run --frozen python docker/production_check.py`; `uv run --frozen ruff check .`; `uv run --frozen ruff format --check .`.
**Security:** keys/invalid values never appear in exception text/repr; no untrusted proxy wildcard or client-controlled time/calendar fallback.
**CI gate:** the same subprocess/input tests, no real provider/network; preserve C01 configuration regressions.
- [ ] **Commit:** `feat: define C02 canonical identity and security configuration` (only named modules/tests/settings/example changes).
**Exit:** inputs, defaults, date assumptions and disabled production adapters have explicit green contracts.

### Task 2: Additive account/security schema and legacy eligibility

**Goal:** add durable primitives without replacing identity or inventing adult data.
**Files:** accounts `models.py`, `security_models.py`, additive migrations; settings app configuration; `tests/unit/c02/test_schema_contract.py`, `tests/integration/c02/test_account_migrations.py`; evolve the exact C01 stage scope allowlist in `tests/unit/test_foundation_scope.py`.
**Schema:** User additions, phone/rate anchors/events, OTPChallenge and AccountSessionControl from §3; nullable legacy DOB/attestation; inactive→suspended data mapping before constraint validation.
**Interfaces:** produce registered models and unique-anchor acquisition for later services; existing public UUID and phone manager interfaces unchanged.
- [ ] Write migration tests with C01 active/inactive users, fixed UUIDs/phones/unusable passwords and session rows. Assert identity/rows preserved, missing DOB remains null, inactive remains denied, no `auth_user`, all new constraints reject invalid rows.
- [ ] RED: `uv run --frozen pytest tests/unit/c02/test_schema_contract.py -q --strict-markers`; real RED in `CI(tests/integration/c02/test_account_migrations.py)` before implementing.
- [ ] Add models/migrations in dependency order; inspect generated SQL and backward dependencies. Add explicit C01+C02 model/field allowlist; preserve canonical manager/security tests.
- [ ] GREEN: `uv run --frozen python manage.py makemigrations --check --dry-run --settings=config.settings.test`; `uv run --frozen pytest tests/unit/c02/test_schema_contract.py tests/unit/test_user_contract.py tests/unit/test_foundation_scope.py -q --strict-markers`; `CI(tests/integration/c02/test_account_migrations.py tests/integration/test_initial_migration.py)`.
**Security:** no automatic adult attestation/state reactivation, default-user table, cascade erase or password provisioning.
**CI gate:** true MigrationExecutor C01→C02 upgrade and fresh PostgreSQL migration; retained data and constraints inspected.
- [ ] **Commit:** `feat: add account security state with additive migrations`.
**Exit:** safe upgrade is proven, not inferred from model import or makemigrations.

### Task 3: Append-only audit, transactional outbox and staff authority primitives

**Goal:** synchronous security outcomes have durable evidence and explicit staff gates.
**Files:** create governance app/config, `audit_models.py`, `outbox_models.py`, `staff_models.py`, `models.py`, `audit.py`, `staff.py`, migrations; wire `config/use_cases/__init__.py`; tests `test_audit_contract.py`, `test_audit_transactions.py`, `test_staff_authority.py` under C02 unit/integration directories.
**Schema:** AuditEvent, OutboxEvent, StaffCapabilityGrant, StaffStepUpGrant; database append-only audit trigger and restricted runtime privileges test.
**Interfaces:** `append_event(outcome: SecurityOutcome) -> UUID`; `append_outbox(event_type: str, aggregate_uuid: UUID, version: int, payload: dict, dedup_key: str) -> UUID`; `require_staff(actor, capability: str, case_uuid: UUID | None, step_up_id: UUID, reason_code: str, at: datetime) -> None` with current DB checks.
- [ ] Write tests first for atomic rollback, metadata allowlist rejecting OTP/phone/IP/session/evidence/body fields, idempotent dedup, and model/QuerySet/direct SQL mutation denial. Assert bare superuser/staff, stale/wrong-user/wrong-capability step-up and self-issued grants cannot authorize recovery.
- [ ] RED: `uv run --frozen pytest tests/unit/c02/test_audit_contract.py -q --strict-markers`; `CI(tests/integration/c02/test_audit_transactions.py tests/integration/c02/test_staff_authority.py)`.
- [ ] Implement narrow append/authority services and migrations, strict payload schemas, separate owner/runtime/retention access; mock step-up only in isolated development/test. No admin permission shortcut or open grant CRUD.
- [ ] GREEN: rerun RED commands; `uv run --frozen python manage.py check --settings=config.settings.test`; migration drift check.
**Security:** future retention privilege is not granted to ordinary runtime/staff; audit callback writes participate in the domain transaction, not only `on_commit`.
**CI gate:** actual PostgreSQL rollback/direct SQL/grants with dedicated connections and `SET ROLE` cleanup.
- [ ] **Commit:** `feat: establish governance audit outbox and staff authority`.
**Exit:** audit durability/immutability and lack of superuser bypass are demonstrated.

### Task 4: Atomic phone/IP limiting with durable conservative quotas

**Goal:** enforce all four ADR quotas across concurrent requests, crash and Redis loss.
**Files:** accounts `limiter.py`, `lua/otp_admission.lua`; unit `test_limiter_contract.py`; integration `test_otp_limits.py`, `test_limiter_failures.py`; Compose/settings add `OTP_RATE_REDIS_URL` on logical DB 4 with retained production TLS validation.
**Schema:** use Task 2 anchors/events; no new durable Redis-only state.
**Interfaces:** `reserve_admission(phone: str, ip: str, kind: str, at: datetime) -> AdmissionResult`; `finalize_verification(reservation_id: UUID, valid: bool, at: datetime) -> None`; bounded immutable policy from Task 1.
- [ ] Write tests first: in 3600s exactly 5 phone/20 IP send admissions; exactly 10 phone/60 IP pending+failed verify slots; successful slots released; limits shared across normalized phone variants and canonical IPs. Parallel first requests do not create duplicate anchors/overshoot; at the exact expiry boundary old events cease counting.
- [ ] RED: `uv run --frozen pytest tests/unit/c02/test_limiter_contract.py -q --strict-markers`; `CI(tests/integration/c02/test_otp_limits.py tests/integration/c02/test_limiter_failures.py)`.
- [ ] Implement single atomic Redis scripts for both dimensions, idempotent reservation UUIDs, bounded socket timeouts and sorted PostgreSQL locks/counts. No refund on uncertain sends/aborted admissions; release only proven-success failure slots. Aggregate retained key versions.
- [ ] GREEN: rerun RED commands; inject Redis connection refusal, SCRIPT FLUSH/NOSCRIPT, process interruption, quota-key deletion and Redis restart. No outage fallback to DB-only allow and no cross-store atomicity claim.
**Security:** HMAC rate keys/no raw IP; recovery intake shares the substrate with its separately configured quotas; never use DRF's non-atomic throttle cache as the authoritative limiter.
**CI gate:** actual Redis Lua races and PostgreSQL guard; multi-thread/process connections, synchronization barriers, no sleep-based assertion of concurrency.
- [ ] **Commit:** `feat: enforce atomic OTP admission and durable quota guards`.
**Exit:** all quotas/outage/reset cases fail safely without over-admission.

### Task 5: Bounded synchronous SMS and challenge issuance/resend

**Goal:** send only a transient code while durable challenge generations govern eligibility.
**Files:** accounts `sms.py`, `otp.py`; `config/use_cases/identity.py`; unit `test_sms_provider.py`, `test_otp_digest.py`; integration `test_otp_issue.py`; account-stage scope/migration fixture changes if required.
**Schema:** existing Task 2 challenge/delivery fields only.
**Interfaces:** `SmsProvider.send_otp(phone: str, code: str, correlation_id: UUID, timeout_seconds: int) -> DeliveryResult` (`accepted`/`failed`/`unknown`); `request_otp(phone: str, ip: str, purpose: str, context_uuid: UUID, at: datetime, record: OutcomeRecorder) -> OtpRequestResult`. Public composition provides the provider and required recorder.
- [ ] Write tests first: cryptographic six-digit shape including leading zero, distinct context/key digests and constant-time compare call; cooldown 59s denied/60s allowed; resend retires prior generation; late acceptance/failed send/timeout/crash-pending cannot become verifiable; no request creates User.
- [ ] RED: `uv run --frozen pytest tests/unit/c02/test_sms_provider.py tests/unit/c02/test_otp_digest.py -q --strict-markers`; `CI(tests/integration/c02/test_otp_issue.py)`.
- [ ] Implement §2 issuance; provider I/O outside locks, late result conditional on generation/current expiry. Mock is deterministic transport with a threadsafe memory collector; no code-reading endpoint, DB sink, file or banner. Uniform public results for new/existing/restricted phones and delivery errors.
- [ ] GREEN: rerun RED commands; `uv run --frozen pytest tests/unit/test_logging.py tests/unit/test_settings.py -q --strict-markers`; capture sentinel codes/phones/provider exceptions and assert absent from logs/audit/outbox.
**Security:** explicit accepted state required for verify; no SMS Celery task or retry of an unreconstructable digest; production Mock rejection retained.
**CI gate:** same provider contracts with no live vendor, real PostgreSQL/Redis request/resend/late-ack races.
- [ ] **Commit:** `feat: issue digest-only OTP challenges through bounded SMS`.
**Exit:** SMS failures never create sessions or revive retired proof.

### Task 6: Atomic proof consumption, adult eligibility and one User

**Goal:** single-use proof resolves an eligible existing/new identity synchronously.
**Files:** accounts `otp.py`, `policies.py`; composition `identity.py`; unit `test_otp_verify_contract.py`, integration `test_otp_consume.py`, `test_adult_entry.py`.
**Schema:** existing security/User fields; no profile model.
**Interfaces:** `verify_otp(phone: str, challenge_id: UUID, code: str, purpose: str, context_uuid: UUID, ip: str, at: datetime, record: OutcomeRecorder) -> OtpProofResult`; login composition later adds Task 7 session effects in the same transaction.
- [ ] Write tests first for 299s valid/300s expired, wrong attempts 1..5, locked sixth/replay, resend rejection, wrong purpose/context/generation/version, unknown challenge dummy comparison, missing delivery acknowledgement and malformed digits. Two simultaneous correct verifies: exactly one consume; concurrent first registration: exactly one User with preserved canonical uniqueness.
- [ ] RED: `uv run --frozen pytest tests/unit/c02/test_otp_verify_contract.py -q --strict-markers`; `CI(tests/integration/c02/test_otp_consume.py tests/integration/c02/test_adult_entry.py)`.
- [ ] Implement durable attempt/failure results without rollback, target/version binding, adult checks before User creation or product eligibility, User creation through existing canonical manager and required transactional recorder. Non-login proofs remain sessionless; consume their codes at verification and persist their context-bound eligibility for later one-time application. Add a regression where code replay fails before application, then two concurrent applications yield one effect and rollback leaves the proof unapplied.
- [ ] GREEN: rerun RED commands; audit failure rolls back identity/proof transition, leaves no unaudited login; wrong-code failures still commit attempt/audit. Under-18/missing attestation never creates an eligible identity/profile or session.
**Security:** new/existing failed proofs have identical bodies/status and account-independent work; do not expose remaining attempts or membership before possession.
**CI gate:** PostgreSQL select-for-update/unique races with barriers/separate connections and actual Redis reservations.
- [ ] **Commit:** `feat: consume OTP proofs atomically with adult entry gates`.
**Exit:** replay/races/expiry/adult tests pass without default User or Redis-only consumption.

### Task 7: Versioned browser sessions and reusable account-state gates

**Goal:** rotate sessions and enforce current authorization across requests and writes.
**Files:** accounts `sessions.py`, `state.py`, `policies.py`, `selectors.py`; `config/account_middleware.py`, `authentication.py`, `permissions.py`, settings/wiring; unit `test_account_policy.py`; integration `test_sessions.py`, `test_account_state_races.py`.
**Schema:** Task 2 session controls/state/auth versions only.
**Interfaces:** `issue_session(request, user, scope: SessionScope, at: datetime, record: OutcomeRecorder) -> None`; `revoke_sessions(user, scope: Literal['current','all'], at: datetime, record: OutcomeRecorder) -> None`; `require_account_action(user, action: str, scope: SessionScope) -> None`; `visible_account(actor, public_id: UUID)` scoped selector.
- [ ] Write tests first: authenticated key differs from pre-login anonymous key; old key denies access; session cookie contains no role/code; missing/stale/revoked control fails. Test single/global logout, restricted/control allowlist, suspension, pending deletion, legacy missing adult data, current-state re-read and cross-user detail/list/count denial.
- [ ] RED: `uv run --frozen pytest tests/unit/c02/test_account_policy.py -q --strict-markers`; `CI(tests/integration/c02/test_sessions.py tests/integration/c02/test_account_state_races.py)`.
- [ ] Implement session-save/proof/audit transaction with explicit rollback cleanup of request session state. Add account middleware after Django AuthenticationMiddleware; keep C01 RequestId/Security/CSRF middleware behavior. DRF adapter and every mutator enforce the same policy; unknown new actions default deny. State transition service increments versions/revokes synchronously.
- [ ] GREEN: rerun RED commands, C01 logging/health/session-CSRF integration tests; race login vs suspension/revocation in both serializations. DB outage yields generic unavailable and no auth access, while Foundation liveness works.
**Security:** no cached roles, no stock `has_perm()` universal staff bypass, no optimistic post-commit session mint; production cookie flags preserved.
**CI gate:** real Django database sessions and PostgreSQL races; cookie CSRF/session-fixation HTTP tests.
- [ ] **Commit:** `feat: enforce versioned sessions and current account policies`.
**Exit:** stale auth cannot survive a committed restriction/change, even with an unexpired cookie.

### Task 8: Manual lost-phone recovery with restricted staff decisions

**Goal:** implement the locked audited manual process without identity disclosure or reactivation.
**Files:** accounts `recovery_models.py`, `recovery.py`, migrations; composition `recovery.py`; governance staff service; unit `test_recovery_contract.py`; integration `test_recovery_authorization.py`, `test_recovery_apply.py`.
**Schema:** RecoveryRequest, RecoveryEvidenceMetadata, immutable PhoneChangeHistory; receipt/effect/proof/version constraints from §3.
**Interfaces:** `open_recovery(old_phone: str, new_phone: str, ip: str, at: datetime, record: OutcomeRecorder) -> RecoveryReceipt`; `recovery_status(request_uuid: UUID, receipt: str, at: datetime) -> Literal['received','closed']`; `decide_recovery(actor, request_uuid: UUID, expected_version: int, decision: str, reason_code: str, step_up_id: UUID, at: datetime)`; `apply_recovery(actor, request_uuid: UUID, expected_version: int, step_up_id: UUID, reason_code: str, at: datetime, record: OutcomeRecorder) -> IdentityChangeResult` through checked composition.
- [ ] Write tests first for unknown/existing intake/status shape, rejected-case non-disclosure, invalid/expired/foreign receipt, evidence cross-case reads, bare staff/superuser denial, self-approval, missing assignment, forged/stale/wrong-user step-up, unresolved evidence and disabled production recovery.
- [ ] RED: `uv run --frozen pytest tests/unit/c02/test_recovery_contract.py -q --strict-markers`; `CI(tests/integration/c02/test_recovery_authorization.py tests/integration/c02/test_recovery_apply.py)`.
- [ ] Implement bounded intake, confidential target resolution, restricted metadata-only evidence, assigned/capability/step-up gates and approved→fresh new-phone proof→atomic apply. Recheck authority and target version under locks; preserve original public UUID/password/state/attestation. No own-case approval or profile/evidence-upload surface.
- [ ] GREEN: rerun RED commands; race two accounts for one new phone and apply vs suspension; exactly one phone owner/effect, old sessions/challenges denied, same completed result on replay, failed audit/history/unique conflict rolls everything back.
**Security:** claimant never receives target existence or staff rejection reasons; new-phone possession alone does not identify the old account; history protected and append-only.
**CI gate:** real PostgreSQL uniqueness/transaction/session invalidation, real Redis quotas, deterministic non-production step-up adapter.
- [ ] **Commit:** `feat: add audited manual recovery and atomic identity restoration`.
**Exit:** recovery cannot bypass staff authority, existing phone ownership or account restrictions.

### Task 9: Owned authenticated phone change with dual possession

**Goal:** normal phone changes cannot abuse the recovery or new-phone proof channel.
**Files:** accounts `phone_change.py`; composition `identity.py`; integration `test_phone_change.py`; unit `test_phone_change_contract.py`.
**Schema:** reuse challenge/history/control models and unique authenticated change context; add PhoneChangeIntent from §3 to persist both verified proof bindings; no code.
**Interfaces:** `begin_phone_change(actor, new_phone: str, at: datetime, record: OutcomeRecorder) -> UUID` returns a bound change UUID; `apply_phone_change(actor, change_uuid: UUID, at: datetime, record: OutcomeRecorder) -> IdentityChangeResult` requires both consumed-code, verified, not-yet-applied fresh proofs and current auth version.
- [ ] Write tests first: wrong/foreign/stale purpose/context proofs deny; old proof cannot stand in for new and recovery proof cannot stand in for either; no cross-user change; both numbers must be owned/proven at application time.
- [ ] RED/GREEN commands: `uv run --frozen pytest tests/unit/c02/test_phone_change_contract.py -q --strict-markers`; `CI(tests/integration/c02/test_phone_change.py)`.
- [ ] Implement begin/proof/apply with Task 8 history and lock rules; normalize destination and use shared quotas/provider. After successful apply, revoke old auth and require a new login; do not migrate an old session to the new identity silently.
- [ ] Verify phone uniqueness race, simultaneous recovery/change, global logout/changed-version failure and immutable one-effect history.
**Security:** no client-supplied target User, no staff or consumer shortcut, no restore of suspended/restricted state.
**CI gate:** separate PostgreSQL connections for competing changes; current sessions/challenges invalidated atomically.
- [ ] **Commit:** `feat: require dual phone possession for authenticated changes`.
**Exit:** normal changes and recovery share guarantees but not proof permissions.

### Task 10: Purpose-limited Consent core without future-domain grants

**Goal:** provide reusable grant/revoke primitives without claiming absent domain authority.
**Files:** governance `consent_models.py`, `consents.py`, migrations; composition `consent.py`; unit `test_consent_scope.py`; integration `test_consent_core.py`.
**Schema:** Consent/ConsentScope with subject/grantee, purpose/text hash/version, typed server-validated scopes, expiry/revocation and optimistic version.
**Interfaces:** `grant_consent(actor, scope: ValidatedConsentScope, text_version: str, content_hash: str, at: datetime, record: OutcomeRecorder) -> UUID`; `revoke_consent(actor, consent_uuid: UUID, expected_version: int, at: datetime, record: OutcomeRecorder)`; `has_current_grant(subject_uuid, grantee_uuid, purpose, scope, at) -> bool`.
- [ ] Write tests first: ownership, exact purpose/grantee/scope/version, expiry, terminal revocation, no account-terms bundling, guessed UUID denial, cross-user list/count denial and inability to fabricate a feature subject. AI/case-study/archive grants are separate and cannot override default excluded inputs.
- [ ] RED/GREEN commands: `uv run --frozen pytest tests/unit/c02/test_consent_scope.py -q --strict-markers`; `CI(tests/integration/c02/test_consent_core.py)`.
- [ ] Implement normalized scope rows and current-state selectors; grant/revoke/audit/outbox commit together, concurrent revoke vs grant/version conflict is safe. Unknown/uninstalled subject validators deny; no profile/relationship/assets imports or public feature-grant API.
- [ ] Verify deletion/account restriction denies new grants; old grants are not reused as authentication/object permissions. Existing typed C02 account-owned subjects and test-only validator fixtures exercise the core without fabricating live sensitive records.
**Security:** consent is an additional predicate, never independent read authority; no actual health/photo/provider flow in C02.
**CI gate:** PostgreSQL scope/version/expiry/rollback and cross-user tests.
- [ ] **Commit:** `feat: define purpose-limited consent core and revocation`.
**Exit:** later callers have a narrow validated interface, with no C03 scope creep.

### Task 11: Coarse feature switches and non-sensitive referral base

**Goal:** future entry switches and acquisition attribution confer no privileges.
**Files:** governance `flag_models.py`, `flags.py`; accounts `referral_models.py`, `referrals.py`; migrations; unit `test_flags.py`, `test_referrals.py`; integration `test_flag_referral_state.py`.
**Schema:** four FeatureFlag rows (explicit safe defaults disabled), InviteReferralLink and one initial ReferralAttribution per recipient.
**Interfaces:** `feature_enabled(key: str) -> bool` fresh authoritative DB read, unknown key disabled; `set_feature(actor, key, enabled, expected_version, reason_code, step_up_id, at)` audited; `issue_referral(actor, at) -> str`; `resolve_referral(token: str, at)` safe descriptor; `bind_attribution(user, token, at, record)` idempotent, only after adult verified registration.
- [ ] Write tests first: each exact key toggles independently, unknown disabled, unauthorized flag writes denied, no flag grants object access/deletes history; token entropy/digest/expiry/revocation, anonymous resolution discloses no phone/private identity and creates no access; restricted issuer/recipient/self-attribution denial.
- [ ] RED/GREEN commands: `uv run --frozen pytest tests/unit/c02/test_flags.py tests/unit/c02/test_referrals.py -q --strict-markers`; `CI(tests/integration/c02/test_flag_referral_state.py)`.
- [ ] Implement versioned flag edits and opaque referrals, canonical first-party safe redirects, clean-URL referral landing with restricted signed attribution cookie/Referrer-Policy. Preserve first attribution under concurrency; no workspace/package/profile FK or reward calculation.
- [ ] Verify professional entry honors `professional_registration` without creating a profile/capability; other three flags are services only until their stage exists. Flag DB failure disables the feature, never uses cached enabled state.
**Security:** raw referral tokens never appear in audit or logs; invitation is attribution, not client grant or lead conversion.
**CI gate:** real PostgreSQL first-attribution/flag-version races and failure behavior.
- [ ] **Commit:** `feat: add operational feature switches and safe referral attribution`.
**Exit:** all four switches and referral core work independently of future apps.

### Task 12: Verified privacy intake and retention/hold metadata

**Goal:** accept owned export/deletion requests and immediately restrict accepted deletion, without executing C18.
**Files:** governance `privacy_models.py`, `privacy.py`, `retention.py`, migrations; composition `privacy.py`; unit `test_privacy_contract.py`; integration `test_privacy_intake.py`, `test_hold_metadata.py`.
**Schema:** PrivacyRequest, versioned RetentionPolicy, record-specific RecordHold; no generated export, erasure worker or ErasureMarker.
**Interfaces:** `request_privacy(actor, kind: Literal['export','delete'], request_id: UUID, at: datetime, record: OutcomeRecorder) -> UUID`; owner-scoped `privacy_status(actor, request_uuid)`; `is_record_held(subject: ValidatedRecordSubject, at) -> bool`; authorized policy/hold metadata services require named capabilities/reason/step-up.
- [ ] Write tests first: owned recent OTP authentication ≤600s required; replay returns one open request; cross-user list/status/UUID/count denies; export intake returns no file/job execution. Verified delete creates pending-deletion request, restricts User, bumps auth version, revokes all controls/challenges and C02 owned grants synchronously.
- [ ] RED/GREEN commands: `uv run --frozen pytest tests/unit/c02/test_privacy_contract.py -q --strict-markers`; `CI(tests/integration/c02/test_privacy_intake.py tests/integration/c02/test_hold_metadata.py)`.
- [ ] Implement requested→verified→pending_execution/export or pending_deletion/delete intake transaction using accounts callbacks through composition. Require explicit confirmation and recent proof; stale auth first reauthenticates, never accepts an unverified deletion. For existing C02 Consent grants, revoke synchronous normal sharing; absent future profiles/push/assistants receive only typed future hooks, not fake tables/claims.
- [ ] Implement draft/approved/effective retention metadata with no invented durations; typed case-scoped holds require a validator, authorizer/reason/review/expiry. Unknown feature subjects fail closed. Hold never reopens normal access or blocks unrelated metadata intake.
- [ ] Verify no purge/file-generation/provider call occurs, legacy data survives, concurrent logout/recovery/deletion cannot restore ordinary access, failed audit rolls back intake/restrictions and request uniqueness is enforced.
**Security:** no generic object eraser, blanket account hold or all-staff export permission. Numeric legal/backup policy approval remains a live-data gate.
**CI gate:** real PostgreSQL intake/version/uniqueness/revocation races; old cookies deny immediately.
- [ ] **Commit:** `feat: add verified privacy intake and bounded hold metadata`.
**Exit:** C02 creates/restricts requests only; C18 work is visibly pending.

### Task 13: Durable outbox dispatch and bounded retry scan

**Goal:** committed events survive broker/process failure without duplicate C02 effects.
**Files:** governance `outbox.py`, `outbox_models.py`, `tasks.py`, receipt migration; `config/event_handlers.py`, settings/Celery imports; unit `test_outbox_contract.py`; integration `test_outbox_worker.py`, `test_outbox_races.py`; evolve `test_beat_has_no_product_schedules` to the one authorized outbox-scan allowlist.
**Schema:** OutboxDeliveryReceipt; due/lease/retry fields already introduced in Task 3.
**Interfaces:** `scan_outbox(at: datetime, batch_size: int=100) -> int`; `dispatch_event(event_uuid: UUID, at: datetime)`; explicit named C02 handlers for `account.security_changed`, `consent.revoked`, `privacy.intake_recorded`, `feature_flag.changed`. Payloads contain UUID/version/result descriptors only.
- [ ] Write tests first: domain rollback produces no event; crash after commit/before enqueue recovers by scan; duplicate dispatch/scanners produce one durable receipt/effect; lease expiry recovers; attempts exhaust after 8, backoff ≤300s; unknown type/schema becomes safely exhausted rather than dynamically imported.
- [ ] RED/GREEN commands: `uv run --frozen pytest tests/unit/c02/test_outbox_contract.py -q --strict-markers`; `CI(tests/integration/c02/test_outbox_worker.py tests/integration/c02/test_outbox_races.py)`.
- [ ] Implement `select_for_update(skip_locked=True)` claims, leases and actual non-eager Celery UUID dispatch; transactional local effect+receipt per handler. Only one Beat process scans every 30s. C02 handlers do bounded account-control cleanup/metadata delivery and recheck current state; no future push/email/SMS/privacy execution handler.
- [ ] Verify actual worker roundtrip and recovery after Redis restart/broker unavailability, stale-version handler skip and idempotent privileged retry. Retrying an exhausted event requires named staff authority/reason/audit, not arbitrary edit CRUD.
**Security:** OTP send stays synchronous; no sensitive durable task payload. Do not claim exactly-once external delivery. `on_commit` enqueue is an optimization; durable scanner is the recovery guarantee.
**CI gate:** real worker/Redis/PostgreSQL competing scans and crash-boundary injection; C01 Celery/Beat transport guarantees remain tested.
- [ ] **Commit:** `feat: dispatch security outbox events with bounded recovery`.
**Exit:** no committed event is silently lost solely because enqueue/broker failed.

### Task 14: Versioned API adapters with anonymous CSRF and scoped reads

**Goal:** expose explicit commands through reviewed use cases, not model CRUD.
**Files:** accounts/governance `serializers.py`, `api.py`, `urls.py`; `config/urls.py`, auth adapters; unit `test_api_schema.py`; integration `test_auth_api.py`, `test_recovery_api.py`, `test_privacy_api.py`, `test_anonymous_csrf.py`; stage route allowlist.
**Schema:** none.
**Interfaces:** routes in §6; serializers map to the already-defined use-case signatures. Public OTP/recovery views explicitly apply Django `csrf_protect` at dispatch even for anonymous APIView requests; no reliance on authenticated-only DRF enforcement.
- [ ] Write tests first: anonymous OTP request/verify/recovery intake with missing/wrong token/cross-origin fail 403 before provider/limiter/database mutation; legitimate token succeeds. Private APIs use current account control and object-scoped selectors; guessed UUID gives 404 without conflict details. Uniform phone and rejected recovery responses match headers/body shapes.
- [ ] RED/GREEN commands: `uv run --frozen pytest tests/unit/c02/test_api_schema.py -q --strict-markers`; `CI(tests/integration/c02/test_auth_api.py tests/integration/c02/test_recovery_api.py tests/integration/c02/test_privacy_api.py tests/integration/c02/test_anonymous_csrf.py)`.
- [ ] Implement bounded JSON/form payloads, explicit field allowlists, no-store sensitive responses, same-origin CORS, generic errors, safe 429/503 metadata. Account `/me/` exposes only owner's bounded fields; no phone-search/list-users endpoint. Staff APIs require current assignment/capability/fresh step-up for every read/mutation.
- [ ] Verify login/session-save/audit failure gives no auth cookie; all adapters call public composition use cases; no password/email/JWT/admin endpoints. Preserve Foundation endpoints, ASGI and safe logging regressions.
**Security:** status IDs alone never authorize recovery/privacy/evidence access; schema excludes provider/evidence/session internals.
**CI gate:** real PostgreSQL/Redis cookie-CSRF API tests with `Client(enforce_csrf_checks=True)`/APIClient equivalent.
- [ ] **Commit:** `feat: expose CSRF-safe C02 identity and privacy commands`.
**Exit:** all transport-level denial/enumeration contracts are real HTTP assertions.

### Task 15: Persian RTL account, recovery and privacy forms

**Goal:** accessible server-rendered entry and control flows, without profile onboarding.
**Files:** accounts `forms.py`, `views.py`; governance `views.py`; templates accounts/governance; `static/src/accounts.js`, calendar enhancement; tests `tests/unit/c02/test_forms.py`, `tests/e2e/c02/test_account_flows.py`, `test_recovery_privacy_flows.py` and private memory-provider fixture.
**Schema:** none.
**Interfaces:** HTML forms call the same use cases as Task 14; enhancement is optional, CSRF always present, redirects remain safe relative first-party targets. Dates use Task 1 server parsing.
- [ ] Write tests first for adult declaration/under-18 stop, Jalali/Gregorian labels/digit entry, phone/OTP request/verify, cooldown display with server-authoritative rejection, logout, owned preferences/status, restricted control page, recovery intake/coarse receipt status, dual-phone change and export/delete confirmation.
- [ ] RED/GREEN commands: `uv run --frozen pytest tests/unit/c02/test_forms.py -q --strict-markers`; `npm run build:css`; `npm run check:js`; planned script extension `npm run check:js` checks both existing/new modules; `docker compose -p fitlink-c02-verify --env-file .env.c02.verify --profile test run --rm browser uv run --frozen pytest tests/e2e/c02 -q -m e2e --strict-markers`.
- [ ] Implement Persian copy, labels/errors/focus/keyboard behavior, native form fallback and bounded enhancements. No C03 wizard/role assignment, false successful SMS message, countdown authority or auth data in browser storage. Mask account phone display; no private evidence/decision reason in claimant pages.
- [ ] Browser tests run desktop 1280×900 and mobile 390×844 with strict pageerror/console assertions, active COOP/secure context, no overflow and static/module success. For C02 full request→verify tests use a static-aware Django `live_server` inside the pytest browser process against real PostgreSQL/Redis and a private in-memory Mock collector; Playwright gets the transient code via fixture memory, never an app route/log/file. Preserve the separate actual Compose ASGI C01 smoke against web loopback. Explicitly distinguish these two evidence categories.
- [ ] Verify JavaScript-disabled submission, CSRF reload/rotation, expired code, unknown/existing failure copy, under-18 no session and old-session denial after phone change/deletion. Staff pages use same capability/step-up checks; no generic admin/evidence upload.
**Security:** no browser diagnostic suppression, insecure-origin flags, client-derived birth-date/role trust or token persistence. Calendar reference attribution/vectors remain local; no CDN script.
**CI gate:** real browser HTTP flows plus actual Compose web/ASGI Foundation smoke and current auth configuration; Mock does not mock sessions/policies/database.
- [ ] **Commit:** `feat: add Persian RTL C02 account and recovery flows`.
**Exit:** entry/control works with and without enhancement; no profile workflow appears.

### Task 16: Exact C01 upgrade rehearsal, full CI and handoff review

**Goal:** prove C02 additive behavior on the exact completed C01 database and preserve all Foundation guarantees.
**Files:** `.github/workflows/ci.yml` only on separately authorized C02 branch; `docker/verify_c02.sh`, `docker/c02_upgrade_probe.py`, isolated role/bootstrap helpers; `tests/integration/c02/test_dependency_direction.py`, `test_upgrade_from_c01.py`, `test_regression_scope.py`; docs `C02_SETUP.md`, `C02_HANDOFF.md`, future execution ledger/roadmap evidence only after actual pass.
**Schema:** no new business schema; inspect all planned migrations/constraints and retained data.
**Interfaces:** documented startup/verification, migration baselines, security policy/provider contracts and current-account authorization contract for C03.
- [ ] Verification-first: archive immutable local C01 commit `5881a2792beca2dbd56cfb9ec6cecf910879d6ab` (tree §1) into ignored fixture directory. If only remote ancestry exists, authenticated fetch/materialization of remote `75c551e...` must verify the same tree before fixture use. Do not archive main, HEAD or an unrelated approximation. No credential embedded in shell Git.
- [ ] In a new isolated PostgreSQL database/Compose project, boot C01 code and apply its migrations, create deterministic synthetic active/inactive users and normal session rows using C01 code, record UUID/phone/count/password metadata and table set, and assert no auth_user. Apply C02 migrations to the SAME database, then assert identity/rows/history preserved, null legacy DOB, inactive state mapped, old legacy auth cannot gain product access and no auth_user. Also run an independent zero-state C02 migration and `makemigrations --check --dry-run`.
- [ ] Full Cloud gate commands: `uv lock --check`; `uv sync --frozen --group dev`; `npm ci`; `npm run build:css`; `npm run check:js`; `uv run --frozen ruff check .`; `uv run --frozen ruff format --check .`; `uv run --frozen mypy config/settings/env.py config/health.py apps/assets/storage.py apps/accounts apps/governance config/use_cases config/authentication.py`; `uv run --frozen python manage.py check --settings=config.settings.test`; `uv run --frozen pytest tests/unit -q --strict-markers`; `uv run --frozen python docker/production_check.py`; secret-free collectstatic with C01 compile-input exclusion; `git diff --check`. Expected exit 0; no blanket typing/security suppression.
- [ ] Full real CI command: `sh docker/verify_c02.sh`. It must preserve every C01 build/startup/readiness/worker/Beat/Channels/private-MinIO/unsigned403/signed-expired-URL/static/browser/restart gate; run `pytest tests/unit tests/integration -q --strict-markers` and both C01/Task 15 browser categories; exact baseline upgrade, limited runtime-role audit/history tests, real simultaneous quota/consume/recovery/session races, Redis outage/reset/key rotation guard, outbox broker recovery and isolated clean startup. Selected skips make CI fail.
- [ ] Evolve C01 stage-specific route/model/field and empty-Beat allowlists to exactly C01+C02, documenting why; keep Foundation auth/User/password/TLS/logging/storage/transport assertions unchanged. C01 baseline suite also runs on the immutable baseline fixture, so the original Foundation proof is retained rather than merely renamed.
- [ ] Review against all linked sources and §7 matrix: challenge/delivery/session ordering; audit callback rollback; lock order; privilege/session-control escape; provider fail-closed config; staff/evidence/receipt disclosure; import direction; no C03/C18 implementation. Fix every Critical/Important defect with RED→GREEN regression, inspect real failed CI step/log and correct root cause; never blindly rerun or count mocks as real transport success.
- [ ] Document effective values, approved/deferred assumptions, secret-free commands, migration/source hashes, actual run URLs/test counts, local→remote mappings, minor findings and operational gates. Report PASS only after all Cloud gates, actual Docker CI and final review are green. Planning PASS is separate from C02 implementation PASS.
**Security:** no main modification, merge/deploy/vendor selection/production secrets; CI must run on the authorized C02 branch rather than assuming C01's branch-only trigger will fire there.
**CI gate:** exact upgrade + zero-state and complete actual-service/browser regression suite, no destructive volume cleanup or existing-data reuse.
- [ ] **Commit:** `ci: verify C02 security races and exact Foundation upgrade`, then `docs: record verified C02 handoff` after genuine results.
**Exit:** C02 execution report can prove every required category; STOP before C03.

## 6. API/UI and jobs contract

| Route / command | Auth and behavior |
|---|---|
| GET `/accounts/entry/` | Persian adult/entry-choice/phone page and CSRF bootstrap; hint does not create a role/profile |
| POST `/api/v1/auth/otp/request/`, `/verify/` | explicit anonymous CSRF; bounded/uniform §2 contracts; verify supplies labeled birth date/attestation when required |
| POST `/api/v1/auth/logout/`, `/logout-all/` | current versioned normal/control session + CSRF; revoke current/all as requested |
| GET/PATCH `/api/v1/account/me/` | owned bounded UUID/state/locale/timezone/preferences; mutable allowlist excludes phone/auth version/flags/roles/staff/birth-date changes without dedicated verified flow |
| POST `/api/v1/account/phone-change/`, `/proof/request/`, `/proof/verify/`, `/apply/` | owned current session and bound change UUID; old/new purpose server selected, dual fresh proof |
| POST `/api/v1/recovery/requests/`; GET `/api/v1/recovery/requests/<uuid>/status/` | anonymous intake CSRF; status receipt cookie mandatory, coarse shape only |
| POST `/api/v1/recovery/requests/<uuid>/new-phone/request/`, `/verify/` | receipt + CSRF, new-phone proof bound to case; same OTP limits, no session issuance |
| GET `/api/v1/staff/recovery/<uuid>/`; POST `/evidence/`, `/decision/`, `/apply/` under that case path | only explicit assigned detail/evidence metadata/decision/apply commands with fresh named capability/step-up; no broad account search or model CRUD |
| POST/GET `/api/v1/privacy/requests/`; GET `/api/v1/privacy/requests/<uuid>/` | owner/control policy, CSRF for intake, recent verified auth/confirmation; status only, no file or deletion execution |
| GET `/i/<opaque-referral-token>/` | clean redirect + non-sensitive attribution; no login/data grant; no-referrer policy |
| HTML `/accounts/verify/`, `/accounts/me/`, `/accounts/phone-change/`, `/accounts/recovery/`, `/privacy/requests/`, `/staff/recovery/<uuid>/` | server forms and explicit commands above; no general admin, profile wizard, consumer password/email or private-file surface |

400 validation/failed proof; 403 CSRF/current-account/authorization denial (DRF SessionAuthentication convention); 404 outside visible object scope; 409 authorized state/version/unique conflict; 429 quota; 503 global dependency/config unavailability. Access checks precede conflict details. Private/auth/recovery/receipt responses are no-store and same-origin. Successful login JSON contains own account UUID/scope, no reusable bearer token; Set-Cookie carries the Django session only. Invalid credentials never distinguish phone membership.

Only background work planned: UUID-based outbox dispatch and one bounded retry scan. SMS delivery is synchronous, so no SMS job/reconciliation queue stores a code or issues a login. Pending/unknown delivery stays unusable; resend retires it. No export/deletion execution, general notifications, AI, scanning or future cron schedule.

## 7. Test / CI matrix and acceptance trace

| Required category | Owning tasks | Concrete evidence |
|---|---|---|
| Persian/Arabic digits, valid/invalid Iranian mobile | 1 | normalization equivalence + invalid/control/foreign-digit cases |
| Expiry, resend cooldown/invalidation, wrong exhaustion | 5–6 | exact 59/60s and 299/300s boundaries, fifth wrong/correct case, late ack |
| Single-use/replay/concurrent verify/create | 2/6 | PostgreSQL barriers/separate connections; one identity/consume |
| Phone/IP sends/failures, key rotation, reset/outage | 1/4 | actual Redis Lua + PostgreSQL 5/20/10/60 durable guard; no DB-only fallback |
| Unknown/existing-phone and rejected recovery resistance | 5/6/8/14/15 | same status/schema/headers/no private details; account-independent provider path |
| SMS failure/timeout/pending crash | 5–7 | challenge not accepted, no auth cookie/session, no resurrected old code |
| Session rotation, CSRF, logout and auth invalidation | 7/14/15 | anonymous and authenticated CSRF, old cookie rejection, version/current state |
| Restricted/suspended/under-18/legacy adult state | 1/2/6/7 | age/calendar boundaries; default-deny/control scope; no invented DOB |
| Recovery authorization/new-phone unique race | 3/8 | forged/wrong/stale step-up, bare superuser, self-approval, conflicting new owners |
| Normal phone change old/new possession | 9 | purpose/context separation, concurrent change/recovery and old-auth rejection |
| Audit/history redaction, rollback and immutability | 3/5/8/12 | sentinel tests + direct SQL + restricted DB role; no code/payload evidence |
| Outbox idempotency/retry/crash/broker recovery | 3/13 | actual worker, two scanners, stale leases, one durable receipt/effect |
| Consent/FeatureFlag/referral | 10/11 | exact owner/purpose/scope/version/expiry; four keys; no privilege transfer |
| Privacy intake/hold metadata; no C18 execution | 12 | current ownership/recent proof/revocation, typed hold, no file/purge/job |
| Cross-user object/detail/list/count denial | 7/8/10/12/14 | actual selectors/API tests with foreign UUID and no scope disclosure |
| Production configuration/IP trust/logging | 1/3/5/7/14 | production mock/fake/weak config rejection, proxy spoof test, C01 TLS/Uvicorn regressions |
| Exact C01 upgrade and no auth_user | 2/16 | same populated baseline DB upgraded; UUID/password/session/row checks; fresh migration |
| C01 regression/real infrastructure/RTL | 15/16 | baseline original suite plus evolved exact C02 scope guards; all real Compose gates |
| Import and scope boundaries | 10/12/16 | AST dependency tests, no future app imports/models/routes, no plaintext persistent code |

## 8. Execution ledger, Git and handoff strategy

- Future coding starts only on separate authorization. Create/verify an isolated `accounts/c02-cloud` checkout/branch from the exact C01 tree, never main or a replacement Foundation. Branch naming/synchronization permission must be explicitly included in that authorization; this planning turn writes no remote ref.
- Create `docs/implementation/C02_EXECUTION_LEDGER.md` at execution start, identity line `# C02 execution ledger — plan: docs/superpowers/plans/2026-10-05-c02-accounts-authentication.md`, recording immutable C01 SHA/tree, plan commit, execution mode and every task status. Preserve the C01 ledger unchanged.
- Each task records BASE/local commit, RED command/result, GREEN command/test counts, Cloud checks, exact deferred CI categories, run/job URLs and reviewed failure diagnosis, migration IDs/SQL review, changed file list, rulings and explicit exit. Do not reconstruct completed tasks from memory; resume from ledger + local/remote state.
- When shell Git is still unauthenticated and remote writes have been authorized, synchronize only that C02 branch using authenticated Git Data operations. Read expected remote parent, use a non-forced fast-forward, verify exact tree and record local→remote mapping. Never touch main/Foundation refs or fabricate old commit metadata.
- Use real CI until green or a genuine external blocker; Docker absence in Cloud alone is not an execution blocker. Failed/skipped/outage tests are not PASS. Never mark the C01 baseline rerun as a C02 result.
- Independent execution review: focused review gates for quota/OTP consume/session/recovery/migrations, then whole-C02 source/spec review. Planning self-review is inline and does not authorize implementation.
- Proposed execution model: GPT-6.1 Sol at xhigh reasoning for sequential TDD implementation; GPT-6 Astra at xhigh for independent security/concurrency and final review. Critical identity transactions justify review gates; isolated deterministic input/UI tasks can use high reasoning. The executor must follow explicit user-selected execution mode.
- Final coding report distinguishes implementation PASS/BLOCKED, actual CI, upgrade/no-auth_user proof, security findings/rulings and operational release dependencies. Stop after C02; C03 requires a new bounded plan/authorization.

## 9. Planning self-review and open operational dependencies

**Planning self-review result: PASS; implementation is UNSTARTED.** A separate review pass against linked product/architecture/domain/permissions/ADR-002/roadmap C02 and the confirmed C01 tree found the following defects in the first design decisions and resolved them in this plan:

| Planning defect checked | Resolution |
|---|---|
| DRF anonymous login might bypass CSRF | Explicit dispatch-level protection and mutation-before-provider tests in Task 14 |
| Accounts importing governance to audit | Typed required callbacks + composition transaction; governance retains one-way dependency |
| Async digest-only delivery cannot reconstruct OTP | Choose synchronous bounded SMS; no durable plaintext/encrypted-envelope speculation |
| Redis reset or concurrent failure admission can reopen quota | Pending failure reservations + PostgreSQL sorted-anchor guard; conservative cross-store semantics |
| User first-request/no-row locking gap | Unique durable anchors and insert/conflict/relock protocol; Task 4 real first-admission races |
| Audit ORM-only immutability or caller-set trigger bypass | SQL guard and separate restricted principal tests; no runtime retention privilege |
| Session save after consumed proof or rollback can mint cookie | One transaction with explicit save/rollback cleanup; Task 7 fault/race tests |
| Non-login code consume and identity application conflated | Consume code once at verification; apply durable context/version-bound proof once in the identity transaction; no second code comparison |
| Optional phone-change storage and unspecified apply signature | Explicit PhoneChangeIntent and typed recovery application inputs |
| Generic staff/superuser/evidence ID implies authority | Explicit grants/assignment/verified fresh step-up; production procedure gate and self-approval denial |
| Restricted login escapes into ordinary endpoints | Scoped control session, default-deny action list, recheck current state at request and write |
| Legacy C01 User missing DOB is silently eligible | Nullable preserved data, adult-entry completion gate, exact populated upgrade test |
| Birthday calendar and browser date interpretation ambiguous | Explicit labeled conversion/server age authority/reference vectors; operational convention noted |
| Governance sees future domains or arbitrary UUIDs | Server-validated typed scopes, no feature imports/CRUD/grant routes |
| Privacy intake silently implements C18 deletion/export | Request/revocation/metadata only; no generated file/erase/restore job |
| C01 exact-scope/empty-Beat tests cannot remain literal | Preserve original baseline suite, evolve only precise authorized C02 allowlists |
| C02 branch never triggers C01-only workflow | Task 16 requires explicit authorized branch trigger and actual run evidence |
| Browser retrieves plaintext OTP from an app endpoint | Private in-process Mock memory collector + real live_server; separate actual Compose ASGI smoke preserved |

No consumer password/email login, JWT/token storage, persistent plaintext OTP, account-existence query API, non-atomic consume, default auth_user, profile/C03 implementation, C18 execution, production SMS vendor or generic admin bypass is planned. No implementation task or planned application check is claimed to have executed.

Operational release dependencies (already aligned with the risk register): approved SMS vendor/adapter and delivery contract before enabling production entry; trusted proxy/TLS/network topology; legal/adult attestation text and birthday-calendar convention; manual recovery evidence checklist, secured evidence system, explicit staff capability provisioning and real MFA/step-up verifier before enabling production recovery; retention/hold/backup policy versions and approved numeric periods before live data; HMAC key custody/rotation and distinct database principals; abuse monitoring and conservative quota capacity review. Defaults never substitute for these approvals. Actual sensitive subject/relationship validation arrives in its owning stage.

### Framework references consulted for planning

- [DRF SessionAuthentication and login CSRF](https://www.django-rest-framework.org/api-guide/authentication/#sessionauthentication): anonymous login needs explicit CSRF enforcement; this supports Task 14, not a product-policy change.
- [Redis Lua execution](https://redis.io/docs/latest/develop/programmability/eval-intro/): atomic single-server scripts support admission; this is not a distributed PostgreSQL/Redis transaction guarantee.
- [Jalaali conversion reference](https://github.com/jalaali/jalaali-js): published conversion/leap vectors and disclosed calendar range differences guide Task 1's isolated, license-reviewed adapter; no library was installed or implementation copied during planning.

**Next action:** review this plan and explicitly authorize the C02 branch/execution method before any implementation.
