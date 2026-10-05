# C01 Foundation handoff

Status: Cloud checks green; mandatory Docker/integration/Playwright gates
PENDING_CI. This is not C01 PASS until actual CI succeeds and final review has no
unresolved Critical/Important finding. Use the execution ledger for current runs
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

Cloud: frozen locks/install, CSS/JS, static manifest/hashed render, 68 units,
Ruff lint/format, focused Django-aware mypy, Django checks/model-state drift and
offline production deploy checks passed. Cloud has no Docker/Compose or matching
Chromium; attempted browser setup errors are recorded, not counted as PASS.

CI workflow runs only on Foundation pushes with contents:read, pinned official
actions and generated test credentials. Its isolated rehearsal covers real clean
PostgreSQL migration/no auth_user, Redis/cache/readiness, actual worker/Beat,
Channels, private MinIO, all Docker builds, Redis/MinIO restart recovery and both
Playwright viewports. Any failed or skipped required test makes the run fail.

Final whole-Foundation review must cover the product/architecture/domain/
permissions/ADR001–005/roadmap/approved plan contracts; fix all Critical/Important
findings before C01 exit. See [setup](FOUNDATION_SETUP.md) for exact commands.

## Git and next stage

Only `foundation/c01-cloud` is synchronized through authenticated Git Data API
with expected remote-parent and exact tree equality. Main remains its separate
bootstrap ancestry, unmodified. No force update, merge, deployment, release,
package publication or production credential was authorized or performed.

C02 Accounts/OTP may be considered only after C01 PASS and a new explicit
instruction. This execution stops at Foundation. No later-stage work is started.
