# C01 Foundation handoff

Status: C01 PASS. Cloud checks and mandatory Docker/integration/Playwright
gates passed in GitHub Actions run37295879078 (remote6e6b46c, local377a56b).
Final Foundation review has no unresolved Critical/Important finding. Use the execution ledger for current runs
and all local→GitHub mappings. Historical dependency work was preserved.

## Implemented contract

Only four public routes exist: `/`, `/health/live/`, `/health/ready/` and
`/api/v1/status/`. The latter reports v1; readiness checks bounded SELECT1/Redis
PING, returning generic503 on failure; liveness remains dependency-independent.
DRF defaults to session authentication and authenticated permission; the status
endpoint explicitly allows anonymous access. No admin/auth/product endpoints.

`AUTH_USER_MODEL='accounts.User'` precedes the first real migration. Minimal User
has internal integer ID, unique public UUID, unique canonical Iranian mobile,
unusable password, Django permission flags/relations, last_login and date_joined.
Manager rejects passwords/noncanonical phones; PostgreSQL enforces phone format
and uniqueness. Initial migration creates only User; clean PostgreSQL and absence
of `auth_user` require actual integration evidence, never SQLite/config inference.
No OTP, AthleteProfile, ProfessionalProfile or other C02/domain model exists.

Private storage protocol exposes put/read/delete/signed_read_url(1..60 seconds).
Fake storage serves unit tests only; S3 adapter uses explicit private bucket,
no public ACL, signatureV4 and bounded network calls. Live tests require unsigned
403, valid signed content and expired signature403. Object keys reject traversal.
Asset metadata, upload UI and scan workflows belong to later stages.

Celery uses JSON only, non-eager operation, bounded connection/task timeouts and
one empty Beat process. The sole infrastructure task returns harmless probe
status. ASGI provides Django HTTP plus session-aware, trusted-origin Channels
middleware with no product WebSocket route. Real channels_redis group delivery
and worker response are distinct from unit/configuration checks.

Persian fa/RTL templates use system fonts, generated Tailwind4 CSS and one neutral
ES module. No external font/script/provider or application form. Browser smoke
must prove desktop/mobile layout, static200, module execution, no console errors,
no overflow, API/readiness success against Compose.

## Verification and review

Cloud: frozen locks/install, CSS/JS, static manifest/hashed render, 70 units,
Ruff lint/format, focused Django-aware mypy, Django checks/model-state drift and
offline production deploy checks passed. Cloud has no Docker/Compose or matching
Chromium; attempted browser setup errors are recorded, not counted as PASS.

CI workflow runs only on Foundation pushes with contents:read, pinned official
actions and generated test credentials. Its isolated rehearsal covers real clean
PostgreSQL migration/no auth_user, Redis/cache/readiness, actual worker/Beat,
Channels, private MinIO, all Docker builds, Redis/MinIO restart recovery and both
Playwright viewports. Any failed or skipped required test makes the run fail.

Final whole-Foundation review covered product/architecture/domain/permissions,
ADR001–005, roadmap C01 and approved plan. The earlier independent review found
three Important security issues; all are fixed and regression-tested: explicit
Uvicorn safe logging, Redis TLS downgrade rejection, and production validation.
Final evidence/scope verification found no remaining Critical/Important issue.
See [setup](FOUNDATION_SETUP.md) for exact commands.

## Git and next stage

Only `foundation/c01-cloud` is synchronized through authenticated Git Data API
with expected remote-parent and exact tree equality. Main remains its separate
bootstrap ancestry, unmodified. No force update, merge, deployment, release,
package publication or production credential was authorized or performed.

C02 Accounts/OTP may be considered only after C01 PASS and a new explicit
instruction. This execution stops at Foundation. No later-stage work is started.

## Actual CI exit evidence

Run [37295879078](https://github.com/alireza-anari/fitlink-v1/actions/runs/37295879078),
job111716846769, completed SUCCESS on2026-10-05. Frozen dependencies, Tailwind/JS,
hashed static, Ruff/format, mypy, Django/unit/production and full clean Compose
rehearsal all succeeded. Logs:70 Cloud units;90 combined unit/integration cases;
2 browser viewport cases;5 Redis/cache/Channels/Celery post-restart cases;
1 private MinIO post-restart case;2 browser viewport cases after restarts.
No required test skipped or error filtered. Clean PostgreSQL17 applied
accounts.0001_initial; actual integration asserts accounts.User, accounts_user
and absence of auth_user in the fresh test_fitlink database.

Browser uses real loopback in service:web network namespace; active COOP and
window.isSecureContext are required. Production security headers remain intact.
Desktop1280x900 and mobile390x844 pass RTL/static/module/API/readiness/no-overflow
and strict console/pageerror checks before and after dependency restarts.

Deferred Minor: CSRF-origin hostname validation could share the production host
validator for consistency. Accepted configured origins still require HTTPS,
no wildcard/path/query/fragment; Foundation exposes no production login/admin.
Pinned setup actions emit a Node20 deprecation warning while the runner uses
Node24; their steps succeed. Historical uv temporary-lock warning is retained.
These are not runtime gate failures or production deployment certification.
