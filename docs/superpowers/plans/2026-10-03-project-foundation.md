# Project Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Execution requires a subsequent user instruction; do not execute during Stage 2.

**Goal:** establish a reproducible, tested production-ready infrastructure skeleton, with only the minimal Custom User required to make the first migration safe.

**Architecture:** one Django monolith with ASGI web/Channels, Celery worker and one Beat process sharing the same release. PostgreSQL is authoritative; Redis supplies infrastructure; MinIO is local private object storage. This stage contains neutral infrastructure probes and an RTL base page, not business workflows.

**Tech Stack:** Python 3.13, Django 5.2 LTS, DRF, PostgreSQL, Redis, Celery/Beat, Channels/channels_redis, S3-compatible storage/MinIO, Django Templates/HTML, Tailwind CSS, Vanilla JavaScript ES Modules, uv, Docker Compose, pytest/pytest-django, Python Playwright/pytest-playwright, Ruff and mypy.

**Spec:** [V1_PRODUCT_SPEC.md](../../product/V1_PRODUCT_SPEC.md), [V1_ARCHITECTURE.md](../../architecture/V1_ARCHITECTURE.md), [DOMAIN_MODEL.md](../../architecture/DOMAIN_MODEL.md), [PERMISSIONS_MATRIX.md](../../architecture/PERMISSIONS_MATRIX.md), [ADR-001](../../architecture/ADR-001-modular-monolith.md), [ADR-002](../../architecture/ADR-002-authentication.md), [ADR-003](../../architecture/ADR-003-realtime-background-jobs.md), [ADR-004](../../architecture/ADR-004-storage-privacy.md), [ADR-005](../../architecture/ADR-005-ai-boundaries.md). Read these and [roadmap C01](../../implementation/V1_IMPLEMENTATION_ROADMAP.md) before execution. Resolve scope conflicts against the locked spec, not personal preference.

## Global constraints

- Python `>=3.13,<3.14`; Django `>=5.2,<5.3`. Install/lock compatible security patch releases during authorized execution, not Stage 2.
- Django Templates, HTML, Tailwind CSS, Vanilla JavaScript ES Modules, Persian RTL; no React/Vue/Next.js/SPA/microservices/Elasticsearch/Kubernetes.
- Django session/cookie authentication and CSRF; API version `/api/v1/`; UUID public identifiers.
- Minimal Custom User in accounts/0001_initial with AUTH_USER_MODEL configured **before any migration or database-backed test**; never default auth_user then replacement.
- PostgreSQL for dev/test/CI; no SQLite substitute for integration/constraints.
- No OTP, profile wizard, role models, recovery workflow, entitlement model, plan editor, consent/health models, payments, chat, AI/Mirror, PWA manifest/service worker or offline logger in Foundation.
- No production SMS/payment/AI vendor selection; no live third-party account needed.
- `sources/` and synced reference files are read-only. Stage exact file lists; never `git add .` or `git add -A`.
- Secrets in environment only; `.env`, credentials, local volumes, reports and caches ignored. Logs cannot emit bodies/cookies/auth headers or full config/connection URLs.
- Production boot fails closed on absent/invalid required secrets/endpoints/hosts; dev/test defaults never silently reach production.
- Optional future entitlements/retention remain centralized domain services; Foundation does not seed business configuration.

## Review focus

1. Production started with missing/whitespace/local-default configuration must fail clearly without logging the secret — Task 2 subprocess tests.
2. First migration on an empty database must resolve all auth references to accounts.User and create no auth_user table — Task 3 migration integration tests.
3. DB/Redis outage must leave liveness working and readiness unavailable without exposing endpoints/credentials — Tasks 4/5/6 failure tests.
4. Windows bind mounts/Linux containers must use the same locked dependencies/static outputs without masked virtualenv or executable-bit assumptions — Tasks 10/12 clean-Compose smoke.
5. Storage/ASGI/task integrations must work with private/fake configurations and reinitialize on restart without a live provider or unsafe public URL — Tasks 7/8/9 contract/integration tests.

---

## Cloud/CI execution amendment — 2026-10-05

The authorized execution host split preserves the approved architecture: Work
Cloud authors code and executes unit/static checks; a private GitHub repository's
GitHub-hosted Linux Actions runner executes mandatory real Docker/Compose gates.
No SQLite, embedded Redis, fake integration results or substitute architecture.

Task 1 status is **PASS WITH DOCKER RUNTIME GATE DEFERRED TO CI** after fresh
non-Docker checks pass. Its dependency commit/locks remain unchanged. Docker
runtime verification belongs to Tasks 10/14 and final C01 exit gates.

Cloud-authorable checks: settings subprocesses, minimal User contracts/imports,
migration generation/inspection without DB execution, mocked health/API probes,
Celery config/eager units, ASGI units, private fake storage, template/RTL/logging,
Tailwind/JS, Ruff/mypy, safe non-DB Django checks, build-only collectstatic and Git
hygiene. Real service checks must never be reported as passed from these units.

CI-required checks: zero-state PostgreSQL migrations/custom User/no auth_user,
PostgreSQL/Redis/cache/readiness, real Redis Channels delivery, non-eager Celery,
Beat process, private MinIO/unauthorized GET/signed URLs, Compose validation/image
builds/startup/reconnect, Compose Playwright and isolated clean startup rehearsal.
Mark unexecuted gates PENDING_CI. Tasks may advance provisionally only with green
Cloud contracts and exact deferred gates represented in CI. C01 PASS requires
both Cloud checks and actual Docker-capable CI results; final review follows green
CI and Important/Critical fixes require another CI run.

Only foundation/c01-cloud pushes to the project's verified private repository
are authorized. No merge/release/deployment/public repository/production secrets.
If the project repository is unavailable, unauthenticated or public, stop and
report the required private connection before further application implementation.

## A. Execution environment and migration strategy

This plan is written in the documentation-only FitLink mirror. Exact paths below are relative to the **approved implementation checkout root**, preserving these docs and leaving sources untouched. Default intended root is `C:/Users/Hanie/.codex/.chatgpt-projects/g-p-6ac14446a77081918e167d039951f7f3`; if the later execution request supplies a repository, use that root with the same layout and copied reference docs. Detect Git state first; initialize Git only if the authorized coding checkout is not already a repo. Never reset existing work or move/delete synced sources. Worktree/isolation choices occur at execution, not now.

Prerequisites for execution: Git, Python 3.13 via uv, uv CLI, Node 24/npm and Docker with Compose v2. Missing tool installation/network privilege follows the host's approval rules when coding is authorized. These are tooling requirements, not actions already performed. Tooling/backend/browser commands below are planned only.

Choose **minimal Custom User in Foundation** rather than an unmigrated temporary default-user skeleton. Use AbstractBaseUser + PermissionsMixin and a focused BaseUserManager; phone is USERNAME_FIELD, no username/email field or login endpoint. Fields: internal BigAutoField key, public UUID `public_id` default uuid4/unique/noneditable, canonical unique phone, is_active/is_staff/date_joined plus standard password/last_login/is_superuser/group/permission relations. Canonical phone accepts `+989` plus nine ASCII digits; full localized OTP normalization belongs to C02. Manager `create_user(phone: str, **extra_fields) -> User` always sets unusable password; `create_superuser(phone: str, **extra_fields) -> User` sets staff/superuser flags but also unusable password. No password provisioning/UI is introduced; staff login/step-up comes in C02/operational policy. The standard createsuperuser password prompt is not the Foundation provisioning path; no admin/login URL is mounted. Reject blank/noncanonical/duplicate phone and contradictory superuser flags. This minimum prevents unsafe replacement; adult/profile/state/auth-version workflow fields arrive additively in C02.

Do not run `django-admin startproject` followed by `migrate`. Create settings/accounts metadata first and set `AUTH_USER_MODEL = 'accounts.User'`; only Task 3 generates/accounts migration. Use `settings.AUTH_USER_MODEL`, `get_user_model()` and swappable migration dependencies for future relations. Include Django auth/contenttypes/sessions/staticfiles; omit Django admin route/app until a later secured staff surface requires it. Django framework auth metadata tables may exist; **default auth_user table must not**. See [Django's first-migration requirement](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/).

## B. File map and responsibilities

All paths listed here are planned, not created in Stage 2.

| Exact paths | Responsibility |
|---|---|
| `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`, `.dockerignore` | Python constraints/locks, tools/test markers, excludes/build context |
| `package.json`, `package-lock.json`, `.node-version` | Node 24 and exact Tailwind CLI/JS build dependencies/scripts |
| `.env.example` | documented local/test values/placeholders only; never usable production secrets |
| `manage.py`, `config/__init__.py`, `config/urls.py`, `config/wsgi.py`, `config/asgi.py` | project entrypoints; urls have infrastructure/base routes only |
| `config/settings/__init__.py`, `config/settings/env.py`, `config/settings/base.py`, `config/settings/development.py`, `config/settings/test.py`, `config/settings/production.py`; `config/settings/build.py` introduced in Task11 | shared settings/typed validation; small environment overlays; isolated secret-free manifest static build |
| `apps/__init__.py`, `apps/accounts/__init__.py`, `apps/accounts/apps.py`, `apps/accounts/models.py`, `apps/accounts/managers.py`, `apps/accounts/migrations/__init__.py`, `apps/accounts/migrations/0001_initial.py` | minimal swapped User/manager only |
| `config/health.py`, `config/api.py`, `config/views.py` | liveness/readiness, public versioned status, neutral base page |
| `config/logging.py`, `config/middleware.py` | stdlib JSON formatter/redaction and request correlation |
| `config/celery.py`, `config/tasks.py`, `config/routing.py` | Celery bootstrap/private probe and empty WebSocket routing |
| `apps/assets/__init__.py`, `apps/assets/apps.py`, `apps/assets/storage.py` | narrow private storage protocol/adapters only, no Asset model/migrations |
| `templates/base.html`, `templates/foundation.html`, `static/src/styles.css`, `static/src/app.js`, `static/dist/app.css` (generated/ignored) | Persian RTL shell and generated static entrypoints |
| `Dockerfile`, `compose.yaml`, `docker/minio-init.sh`, `docker/healthcheck.py` | locked multi-target images/local services, private bucket init and bounded health probes |
| `tests/__init__.py`, `tests/conftest.py`, `tests/unit/`, `tests/integration/`, `tests/e2e/` | focused tests defined in tasks below; no product fixtures |
| `.github/workflows/ci.yml` | simple backend/static/Playwright smoke CI when GitHub is the target; locally runnable same checks regardless |
| `README.md`, `docs/development/FOUNDATION_SETUP.md`, `docs/development/DEPENDENCIES.md`, `docs/development/FOUNDATION_HANDOFF.md` | runbook, selected pins/images/reasons and exit evidence |

Test directories include `__init__.py` only where imports require them. Do not create placeholder apps/models/tasks for all sixteen domains.

## C. Dependency, settings and container design

### Dependencies and lock discipline

Use uv with `pyproject.toml` and committed `uv.lock`; package is an application (`tool.uv.package = false`). Broad deliberate constraints below are inputs; resolved exact versions/hashes are committed at Task 1. `uv sync --frozen` and `uv lock --check` are verification gates; only intentional updates regenerate locks. The [uv documentation](https://docs.astral.sh/uv/concepts/projects/sync/) distinguishes resolution and locked syncing. Record exact uv CLI patch/version in DEPENDENCIES and pin the same uv binary image/tag/digest in Docker/CI. Do not use `latest` images or unpinned actions in committed CI.

| Dependency constraint | Reason |
|---|---|
| `Django>=5.2,<5.3` | locked LTS framework |
| `djangorestframework>=3.16,<4` | versioned API/session baseline |
| `psycopg[binary]>=3.2,<4` | PostgreSQL driver, avoids compiler-heavy local bootstrap |
| `redis>=5,<8` | explicit cache/readiness/Celery transport dependencies; lock compatible patch |
| `celery[redis]>=5.5,<6` | worker/Beat with Redis transport; built-in Beat scheduler, no django-celery-beat until real DB schedule need |
| `channels>=4.2,<5`, `channels-redis>=4.2,<5` | ASGI socket abstraction/channel layer |
| `uvicorn[standard]>=0.34,<1` | one ASGI process with actual WebSocket transport support; no extra Daphne/Gunicorn |
| `django-storages[s3]>=1.14,<2` | Django storage/S3-compatible adapter and boto3 signing; no second hand-built SDK wrapper |
| Dev: `pytest>=8,<10`, `pytest-django>=4.9,<5`, `pytest-asyncio>=0.24,<2` | unit/DB/async channel tests |
| Dev: `playwright>=1.50,<2`, `pytest-playwright>=0.7,<1` | Python browser smoke; lock browser package/version together |
| Dev: `ruff>=0.11,<1`, `mypy>=1.15,<2`, `django-stubs>=5.2,<5.3` | one formatter/linter, focused typing with matching Django major/minor |
| Dev: `httpx>=0.28,<1` | ASGI request tests without live HTTP service |
| Node: `tailwindcss` and `@tailwindcss/cli`, exact matching stable 4.x versions | CLI build; no JS framework/bundler |

Dependencies whose constraints do not jointly resolve on Python 3.13 must be corrected within their supported major lines with documented evidence before committing; never silently upgrade Django/Python or add generic frameworks. Use stdlib os/json/logging/uuid for env/logging; Django cache is sufficient, no django-redis/django-environ/JSON-log library solely for convenience. No production AI/SMS/payment SDKs. No django-celery-results: durable domain jobs later live in PostgreSQL. Use built-in WhiteNoise-free static design: dev staticfiles handler, production static artifact served by deployment static server/CDN; no claim Uvicorn serves production static directly.

### Settings/environment contract

Base has shared apps/middleware/DRF/templates/static defaults; overlays modify differences. Entry points default development only locally, containers set module explicitly. Test uses test module, debug false, nonproduction test key, PostgreSQL/fake storage; integration explicitly overrides real Redis/MinIO. Dev/test allowed hosts include localhost,127.0.0.1,testserver,web so the Compose browser reaches web; production uses only required concrete configured hosts and never imports dev/test overlays. Custom manager rejects any password provisioning extra field; Foundation cannot accidentally save raw passwords through its creation API.

`env.str_value(name, default=None, required=False) -> str`, `env.bool_value(name, default=False) -> bool`, `env.int_value(name, default=None, minimum=None) -> int`, `env.csv_value(name, default=None, required=False) -> tuple[str, ...]`. Missing/blank required values raise ImproperlyConfigured naming the key only; bool accepts case-insensitive true/false/1/0 and rejects arbitrary text. No silent casting fallback or config dump.

| Environment keys | Behavior |
|---|---|
| `DJANGO_SETTINGS_MODULE`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` | prod key required, >=50 characters and rejects local/test placeholders; concrete hosts (no wildcard), HTTPS trusted origins as needed |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_SSLMODE` | discrete DB config, all required prod; dev host localhost/port5433, Docker host db/port5432; prod require SSL (`verify-full` default with approved CA/trust deployment), bounded connect timeout |
| `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, `CHANNEL_REDIS_URL` | dev host127.0.0.1:6380/DB0,1,2,3 respectively; Compose redis:6379; prod required authenticated TLS rediss URLs; bounded timeouts; namespaced prefix |
| `STORAGE_BACKEND`, `S3_ENDPOINT_URL`, `S3_BUCKET_NAME`, `S3_REGION`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_ADDRESSING_STYLE` | fake test or s3; production requires s3/HTTPS/private bucket credentials, rejects local/default key placeholders; local MinIO path style/signature v4 |
| `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`, `MINIO_APP_ACCESS_KEY`, `MINIO_APP_SECRET_KEY` | local container setup only; app uses limited bucket-scoped identity, not root; ignored local env holds generated values |
| `LOG_LEVEL`, `RELEASE_ID` | bounded levels; optional non-sensitive release identifier |
| `WEB_PORT`, `POSTGRES_HOST_PORT`, `REDIS_HOST_PORT`, `MINIO_HOST_PORT`, `MINIO_CONSOLE_HOST_PORT`, `E2E_BASE_URL` | local defaults8000/5433/6380/9000/9001; browser tests http://web:8000 in Compose |

Production sets DEBUG false, secure session/CSRF cookies, session HttpOnly/SameSite Lax, HTTPS redirects, HSTS and allowed hosts/origins; SECRET_KEY from environment. Trust proxy headers only when a controlled proxy strips them. `test` is not a production smoke-settings bypass; subprocess tests supply ephemeral valid config and assert startup failure cases. DB CREATE DATABASE permission is test-role-only, not runtime production role. .env is explicitly used by Compose; Django does not quietly auto-load dotenv.

### Compose contract

Services: `db`, `redis`, `minio`, `minio-init`, `web`, `worker`, `beat`, and profile `test` service `browser`. Channels is in **web's ASGI process**, not a separate server. PostgreSQL17, Redis7.4, Python3.13 slim Debian and Node24 build image are engineering baselines. Choose verified immutable patch tags/digests and compatible MinIO server/mc release pair during Task 1/10; record them, never commit floating latest. uv image also exact version/digest, per [official Docker guidance](https://docs.astral.sh/uv/guides/integration/docker/).

Web/worker/beat share image target `development`, project bind mount `/app`, `UV_PROJECT_ENVIRONMENT=/opt/venv` to avoid masking dependencies, and environment mapping to internal service hosts. Build CSS in Task11 before starting the static-enabled web: development bind mount uses host-generated `static/dist`, production copies baked sources/manifest static artifacts without bind mount. Runtime is nonroot, only runtime dependency group, `UV_NO_DEV=1`/`UV_NO_SYNC=1` so starting uv cannot install dev dependencies. `browser` uses an `e2e` target with matching Chromium/system dependencies installed at build, not web runtime; set PLAYWRIGHT_BROWSERS_PATH to a shared readable image path so root build/user run resolve the same browser. Node/npm stay out of runtime.

DB/Redis/MinIO data/Beat schedule have named volumes; ports bind127.0.0.1. DB/Redis use available native health commands. MinIO running status alone is not readiness: minio-init's compatible mc client performs a bounded readiness loop before private bucket/app-policy creation, then exits0; web/storage-dependent processes require service_completed_successfully. Do not assume curl/Python/mc is installed inside the server image. Init is idempotent/secrets-redacted; root credentials stay in init/server. Startup never migrates automatically. Compose readiness is not resilience ([Docker guidance](https://docs.docker.com/compose/how-tos/startup-order/)); test restart. One Beat uses writable /var/lib/celery/celerybeat-schedule and initially no schedules; verify running process/schedule file separately, not pretend it responds to worker inspect ping. Retention/production orchestration stay C18/C20.

## D. Common execution/check conventions

Only run after separate coding authorization. Host PowerShell commands are one per line, rooted in approved checkout. `uv run --frozen` never edits locks. Every behavior task begins with named failing test(s), confirms failure for the intended missing behavior, implements minimally, reruns and commits explicit paths. Configuration-only packaging/build tasks use meaningful smoke/contract checks rather than tests that merely repeat literal settings. Do not proceed on unexplained failures.

Backend markers: `unit` no services, `integration` local PostgreSQL/Redis/MinIO, `e2e` browser smoke. Set pyproject pytest `testpaths=['tests/unit']`, `addopts='--ds=config.settings.test'`: the explicit pytest-django CLI setting overrides Compose's development module, so container tests cannot accidentally use the development DB/settings ([pytest-django precedence](https://pytest-django.readthedocs.io/en/latest/configuring_django.html)). Explicit paths select other groups. Mark DB tests django_db, async auto mode and test-only routing. Test DB test_fitlink and synthetic phones only. Env subprocesses isolate inherited settings/UV_ENV_FILE.

Common verification after each task: run its named tests/checks plus impacted earlier tests. Commit message is given per task; use listed exact paths and exclude all `.env`/generated outputs. No automatic commits in Stage 2. If a command requires privilege/network approval at execution, request it then; do not replace tools/stack to bypass restrictions.

### Task 1: Lock tooling, dependencies and repository hygiene

**Files:** create `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`, `.dockerignore`, `package.json`, `package-lock.json`, `.node-version`, `docs/development/DEPENDENCIES.md`.

**Interfaces:** consumes locked stack; produces Python/dev dependency groups, scripts `build:css`, `watch:css`, `check:js`, and pytest markers/settings declarations. CSS script targets `static/src/styles.css` → `static/dist/app.css`; JS script uses `node --check static/src/app.js` when that file exists in Task 11. No runtime imports required yet.

- [ ] Check `git status --short` (or `git init` only in a new authorized checkout), `uv --version`, `node --version`, `npm --version`, `docker version`, `docker compose version`; versions/tools accessible and Python3.13 support available.
- [ ] Write dependency constraints/reasons/exclude rules. Ignore sources/, .env*, except .env.example; .venv/node_modules/static/dist/staticfiles/media/.pytest_cache/mypy/ruff caches/test-results/playwright artifacts/local secrets/schedule files.
- [ ] Run `uv python install 3.13`, `uv lock`, `uv sync --frozen --group dev`; only this first resolution generates Python lock. Record uv patch and Python patch, verify resolution stays Django5.2/Python3.13.
- [ ] Select exact matching Tailwind4 stable package patches from official npm metadata; run `npm install --save-dev --save-exact tailwindcss@4 @tailwindcss/cli@4`, then `npm ci`. Record resolved patches/npm/Node versions. Scripts build later; no framework package.
- [ ] Run `uv lock --check`, `uv run --frozen python --version`, `uv run --frozen python -m django --version`, `npm ls --depth=0`; expect Python3.13, Django5.2, matching Tailwind4 packages, no unresolved/invalid dependencies. Do not run migrate yet.
- [ ] Stage only the nine listed files and commit `chore: lock foundation tooling and dependencies`.

### Task 2: Boot project with typed environment/settings separation

**Files:** create `manage.py`, `config/__init__.py`, `config/urls.py`, `config/wsgi.py`, `config/asgi.py`, all six `config/settings/` files from B, `.env.example`, `tests/__init__.py`, `tests/conftest.py`, `tests/unit/test_environment.py`, `tests/unit/test_settings.py`; initial URL list may be empty. Accounts not installed until Task 3; no DB test/migration yet.

**Interfaces:** produces env readers with signatures in C, explicit three settings modules and minimal HTTP-only ASGI app. Task 3 installs accounts and AUTH_USER_MODEL before database actions. Tests in this task import/boot configuration only; do not provision default User database.

- [ ] Write subprocess tests named `test_missing_production_secret_fails`, `test_blank_required_value_fails_without_value_leak`, `test_invalid_bool_fails`, `test_production_rejects_wildcard_hosts_and_local_defaults`, `test_production_requires_tls_dependencies`, `test_development_and_test_are_separate_overlays`; assert named ImproperlyConfigured errors and no secret/URL values in stderr. Initially fail because settings/env readers absent.
- [ ] Run `uv run --frozen pytest tests/unit/test_environment.py tests/unit/test_settings.py -q -m unit`; confirm intended failure, not dependency error.
- [ ] Implement settings/readers and entrypoints, no auto-dotenv, no product URLs. Mark fixtures/subprocess env explicitly; document safe local versus required production keys in .env.example. Generated local secrets are not committed.
- [ ] Rerun named tests and `uv run --frozen python manage.py check --settings=config.settings.test`; expect passing env cases and no bootstrap import error, without DB creation. Task 3 must precede any DB-backed test/migrate.
- [ ] Stage listed files (config settings directory limited to its six specified files) and commit `chore: establish environment-aware Django bootstrap`.

### Task 3: Establish Custom User before the first migration

**Files:** create `apps/__init__.py`, seven `apps/accounts/` files from B, `tests/unit/test_user_contract.py`, `tests/integration/test_user_model.py`, `tests/integration/test_initial_migration.py`; modify `config/settings/base.py`, `tests/conftest.py`.

**Interfaces:** produces `accounts.User`, UserManager signatures in A, AUTH_USER_MODEL and reusable synthetic `user` fixture. No OTP/roles/adult onboarding/recovery/auth route. Database schema identity is the sole Foundation business exception.

- [ ] Write non-DB contract tests for AUTH_USER_MODEL/USERNAME_FIELD and unsaved User instance UUID/password methods; validate invalid phone/forbidden password before manager attempts save. Never call successful create_user in a unit test without DB. Run `uv run --frozen pytest tests/unit/test_user_contract.py -q -m unit`; fail on missing custom model, not database access. No default-User DB test.
- [ ] Create minimal accounts app/model/manager and set AUTH_USER_MODEL before generating anything. Confirm `get_user_model()._meta.label` is accounts.User with contract test passing.
- [ ] Run `uv run --frozen python manage.py makemigrations accounts --settings=config.settings.test`; inspect accounts/0001_initial contains User and only intended fields/auth relations. No dependency on future athlete/professional models.
- [ ] Write integration tests: `test_user_phone_unique_and_canonical`, `test_user_defaults_to_unusable_password`, `test_superuser_flags_require_true`, `test_public_id_is_uuid`, `test_empty_database_migrates_without_auth_user`, `test_all_auth_relations_use_custom_user`. Use a disposable test database/MigrationExecutor or dedicated disposable DB, never reset shared local data. Failure occurs if migration/constraint/wiring is wrong.
- [ ] Do not run DB tests yet: PostgreSQL is intentionally introduced in Task 4. Before this task's commit verify `uv run --frozen python manage.py check --settings=config.settings.test`, `uv run --frozen python manage.py makemigrations --check --dry-run --settings=config.settings.test` and non-DB tests. Require no pending changes and correct migration inspection. Task 4 runs the first DB-backed red/green/empty-DB gates before any dependent stage advances.
- [ ] Stage listed files plus explicit settings/conftest and commit `feat: define minimal custom user before initial migrations`.

### Task 4: Wire PostgreSQL and validate empty-database migration

**Files:** create initial `compose.yaml` with db only, `config/health.py` (DB probe only), `tests/integration/test_database.py`, `docker/healthcheck.py`; modify `config/settings/base.py`, `config/settings/test.py`, `.env.example`, `tests/conftest.py`, `docs/development/DEPENDENCIES.md`.

**Interfaces:** produces PostgreSQL DATABASES config from C, dev/test db service on127.0.0.1:5433, bounded DB probe `database_available() -> bool` later exposed in health. docker helper accepts dependency probe type, timeout and exit status; it logs no credential.

- [ ] Write `test_postgres_select_one`, `test_database_is_postgresql`, `test_test_db_is_separate`, `test_database_timeout_is_bounded`; assert SELECT1, PostgreSQL engine, no production database reused, connection failure returns false. Run unit/mock timeout assertion red before implementing helper.
- [ ] Configure pinned DB image/health/volume and isolated local env. Create ignored `.env` from example/generate dev credentials; never commit or log values. In the host PowerShell session set `$env:UV_ENV_FILE='.env'` so subsequent `uv run` commands explicitly load local env ([uv ENV_FILE](https://docs.astral.sh/uv/reference/environment/)). Omit DJANGO_SETTINGS_MODULE from this local file: manage.py defaults development, pytest.ini chooses test, Compose sets development explicitly. Isolated settings subprocess tests clear UV_ENV_FILE and relevant inherited environment. Container uv commands use Compose-injected env, not the host env-file variable.
- [ ] Run `docker compose up -d --wait db`, then `docker compose exec db pg_isready -U fitlink -d fitlink` with the local service user/db documented as fitlink. Use a privileged **local/test only** role capable of creating test_fitlink; prod role has no CREATE DATABASE.
- [ ] With documented host env run `uv run --frozen pytest tests/integration/test_database.py tests/integration/test_user_model.py tests/integration/test_initial_migration.py -q -m integration`; confirm all Task 3 DB gates on empty test DB. If failing, fix before applying local migrations.
- [ ] Run `uv run --frozen python manage.py migrate --settings=config.settings.development`, `uv run --frozen python manage.py showmigrations --settings=config.settings.development`, `uv run --frozen python manage.py makemigrations --check --dry-run --settings=config.settings.test`; expected all intended migrations applied/no model drift and introspection proves no auth_user.
- [ ] Stage listed changes only, commit `chore: verify PostgreSQL and safe initial user migration`.

### Task 5: Configure Redis cache and bounded infrastructure checks

**Files:** modify `compose.yaml`, `config/health.py`, `config/settings/base.py`, `.env.example`, `docker/healthcheck.py`; create `tests/unit/test_redis_config.py`, `tests/integration/test_redis.py`.

**Interfaces:** produces Django built-in RedisCache with prefix `fitlink`, REDIS_URL/Celery/channel URL split as in C; `redis_available() -> bool`, connection/read timeouts two seconds. Redis persistence is local convenience, not business source of truth.

- [ ] Write `test_redis_urls_are_separate`, `test_redis_probe_timeout_returns_false`; run `uv run --frozen pytest tests/unit/test_redis_config.py -q -m unit` red for missing configuration/probe.
- [ ] Add pinned Redis7.4 service/private loopback port/health/volume; initialize cache/probe with no import-time network calls and scrub URLs from exceptions.
- [ ] Run `docker compose up -d --wait redis`, `docker compose exec redis redis-cli ping`; expect PONG. In production auth/TLS secrets are mandatory, local service is private.
- [ ] Add integration `test_cache_roundtrip_and_prefix`, `test_redis_probe_success`; run `uv run --frozen pytest tests/unit/test_redis_config.py tests/integration/test_redis.py -q`; explicit path selection may override default marker filter as described below in verification note. Assert set/get/delete and bounded connection failure, not merely settings text.
- [ ] Stage changes and commit `chore: connect Redis infrastructure safely`.

### Task 6: Add health/readiness and versioned API boundary

**Files:** create `config/api.py`, `tests/unit/test_health_api.py`, `tests/integration/test_readiness.py`; modify existing `config/health.py`, `config/urls.py`, `config/settings/base.py`, `docker/healthcheck.py`.

**Interfaces:** `liveness(request) -> JsonResponse`, `readiness(request) -> JsonResponse`, `StatusView.get(request) -> DRF Response`; DRF default SessionAuthentication + IsAuthenticated, explicit AllowAny for public status. Paths `/health/live/`, `/health/ready/`, `/api/v1/status/`. DB/Redis probes already live at `config.health.database_available`/`redis_available` since Tasks4/5; helper invokes them/HTTP rather than duplicating logic.

- [ ] Write tests: liveness200/status ok even if dependency mocked down; readiness200 if DB+Redis good,503 if either unavailable; response generic and no host/credentials/traceback; API status returns service fitlink/api_version v1/status ok; test-only protected API denies anonymous and enforces session-CSRF unsafe requests. Run `uv run --frozen pytest tests/unit/test_health_api.py -q -m unit` red.
- [ ] Implement bounded readiness using SELECT1/Redis ping, no Celery inspect or external S3 object write on every web probe. Production worker/storage health is separately observed/tested, not implied by web readiness. Health private data no-store; readiness endpoint reveals only status, logs identify dependency without URL.
- [ ] Run unit tests and `uv run --frozen pytest tests/integration/test_readiness.py -q -m integration`; real PostgreSQL/Redis healthy yields200 and controlled probe failure yields503 with liveness200.
- [ ] Run `uv run --frozen python manage.py check --settings=config.settings.test`; stage listed paths/related moved helper code and commit `feat: add safe health and versioned status endpoints`.

### Task 7: Bootstrap Celery worker and single Beat

**Files:** create `config/celery.py`, `config/tasks.py`, `tests/unit/test_celery_config.py`, `tests/integration/test_celery_roundtrip.py`; modify `config/__init__.py`, `config/settings/base.py`, `.env.example`.

**Interfaces:** `config.celery.app` Celery application named fitlink, namespaced CELERY settings, task `config.tasks.infrastructure_probe() -> dict[str,str]` returns status ok without inputs/domain side effects. JSON serializer/accepted content only, Redis broker/result URLs, UTC, bounded retry/startup logging/result TTL86400 seconds, Beat initially no schedules. No production business task/outbox implementation yet.

- [ ] Write `test_celery_loads_django_namespace`, `test_celery_json_only`, `test_beat_has_no_product_schedules`, `test_probe_eager_returns_ok`; configure eager mode only for these isolated unit assertions and run red.
- [ ] Bootstrap app/autodiscovery/probe; production defaults are not eager. Include config.tasks explicitly; do not add django-celery-beat/results models.
- [ ] Run `uv run --frozen pytest tests/unit/test_celery_config.py -q -m unit`. Separate non-eager integration enqueues probe and fetches result with timeout15s against a running worker in Task10; document it now and mark runtime gate pending Task10, not falsely passing eager-only checks.
- [ ] Verify `uv run --frozen python manage.py check --settings=config.settings.test` with Celery import bootstrap loaded. Do not run or attach full Celery/Django configuration dumps; unit tests assert only named non-sensitive config values. Real transport validation is Task10.
- [ ] Stage listed files and commit `chore: bootstrap Celery and empty Beat scheduling`.

### Task 8: Bootstrap Channels in ASGI without product sockets

**Files:** create `config/routing.py`, `tests/unit/test_asgi.py`, `tests/integration/test_channel_layer.py`; modify `config/asgi.py`, `config/settings/base.py`.

**Interfaces:** ASGI ProtocolTypeRouter HTTP uses Django ASGI; websocket uses AllowedHostsOriginValidator/AuthMiddlewareStack/URLRouter with empty `websocket_urlpatterns`. CHANNEL_LAYERS uses channels_redis and dedicated URL/prefix. Test-only consumer/routing lives inside test module, not a production chat endpoint.

- [ ] Write `test_http_asgi_status`, `test_no_business_websocket_route`, `test_untrusted_origin_rejected`; run `uv run --frozen pytest tests/unit/test_asgi.py -q -m unit` red. Use HTTPX ASGITransport and `asgiref.testing.ApplicationCommunicator` for WebSocket scope/connect/close events with proper teardown. Avoid `channels.testing` package's Daphne live-test dependency; asgiref is already supplied by Django. No unnecessary test server package.
- [ ] Wire router/middleware/settings; initialize Django before importing routing so startup is safe; no import-time channel send/network calls.
- [ ] Add integration `test_redis_channel_send_receive`, `test_channel_layer_restart_reconnect`; create isolated per-test UUID channel/group, send/receive payload via real Redis and clean group membership.
- [ ] Run unit and `uv run --frozen pytest tests/integration/test_channel_layer.py -q -m integration`; expect real Redis delivery, no production socket room, untrusted origins refused.
- [ ] Stage files and commit `chore: bootstrap session-aware Channels ASGI`.

### Task 9: Private storage protocol, fake backend and local MinIO

**Files:** create four `apps/assets/` files from B, `tests/unit/test_storage.py`, `tests/integration/test_minio_storage.py`, `docker/minio-init.sh`; modify `config/settings/base.py`, `config/settings/test.py`, `.env.example`, `compose.yaml`, `docs/development/DEPENDENCIES.md`.

**Interfaces:** `PrivateObjectStore.put(key: str, data: bytes, content_type: str) -> None`, `.read(key: str) -> bytes`, `.delete(key: str) -> None`, `.signed_read_url(key: str, expires_seconds: int=60) -> str`; `get_private_store() -> PrivateObjectStore`. Fake test adapter and S3 adapter wrap Django storages/boto3; reject empty/absolute/traversal keys and expiry outside1..60. This protocol is infrastructure only; future Asset/domain services must authorize before using it. No public upload/download API or Asset model.

- [ ] Write contract tests parameterized fake/S3 where applicable: put/read/delete, missing key, invalid traversal/absolute key, maximum URL expiry, no public default ACL; run unit red. Fake signing may return clearly fake URL only in test settings; production config rejects fake backend.
- [ ] Implement typed protocol/fake/Django S3 adapter with private bucket/query auth, v4/path-style local endpoint. Credentials only env; no permanent public asset URL convenience. Asset app may be installed for adapter discovery without models/migrations.
- [ ] Configure pinned compatible MinIO server/mc init service, private bucket and limited app identity via sh script invoked explicitly (`sh`, independent of Windows executable bits), retry readiness with bounds. Bucket-init rerun must be idempotent and not print secrets.
- [ ] Run `docker compose up -d --wait minio`, `docker compose run --rm minio-init`, then `uv run --frozen pytest tests/unit/test_storage.py -q -m unit` and `uv run --frozen pytest tests/integration/test_minio_storage.py -q -m integration`. Integration writes only test UUID prefix, reads/deletes, proves unauthenticated GET403, valid signed URL reads and expired signature rejected (bounded synthetic signing-time test if waiting would be slow).
- [ ] Stage listed files and commit `chore: establish private fake and MinIO storage adapters`.

### Task 10: Reproducible web/worker/Beat Compose environment

**Files:** create `Dockerfile`; complete `compose.yaml`, `docker/healthcheck.py`, `.dockerignore`, `docs/development/DEPENDENCIES.md`. Real container smoke/transport checks validate this configuration task; do not add tests that simply mirror Compose YAML.

**Interfaces:** shared development/runtime/e2e targets; web command `uv run --frozen uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --no-access-log`; worker `uv run --frozen celery -A config.celery:app worker --loglevel=INFO`; Beat `uv run --frozen celery -A config.celery:app beat --loglevel=INFO --schedule=/var/lib/celery/celerybeat-schedule`. Disable Uvicorn raw access log so query strings are not logged; Task11 middleware logs bounded path/status/duration. No auto-migrate/install.

- [ ] Build dependency-only base and dev target with nonroot writable venv/schedule permissions, lock sync, no secret ARG/COPY .env, HTTP and worker health commands. Resolve/pin container digests; document Python/DB/Redis/Node/uv/MinIO/mc digests. Multi-stage production static build is completed in Task11.
- [ ] Run `docker compose config --quiet` (never print resolved secrets), `docker compose build web worker beat`; expect valid model/same locked image and no runtime installs. At this task base page/static not yet present; readiness/API only is the smoke.
- [ ] Run `docker compose up -d --wait db redis minio`, `docker compose run --rm minio-init`, `docker compose run --rm web uv run --frozen python manage.py migrate`, `docker compose up -d --wait web worker beat`. Fresh env must be ready; migrate uses previously inspected custom User chain only.
- [ ] Run `docker compose exec web uv run --frozen python manage.py check`, `docker compose exec web uv run --frozen celery -A config.celery:app inspect ping --timeout=5`, `docker compose exec web uv run --frozen pytest tests/integration/test_celery_roundtrip.py -q -m integration`; require worker pong and actual non-eager probe result, not merely configuration loads.
- [ ] Run `docker compose ps`, `docker compose logs --tail=30 worker beat`; startup visible without secrets, one Beat schedule empty. Restart Redis with `docker compose restart redis`, wait for readiness and rerun channel/cache/task integration to demonstrate bounded reconnect. Use disposable test-only failures, not destructive volume removal.
- [ ] Stage files and commit `chore: provide reproducible ASGI worker and Beat containers`.

### Task 11: Persian RTL template/static baseline and logging

**Files:** create templates/static/view/logging/middleware files from B, `config/settings/build.py`, `tests/unit/test_rtl_page.py`, `tests/unit/test_logging.py`; modify `config/urls.py`, `config/asgi.py`, `config/settings/base.py`, `config/settings/production.py`, `Dockerfile`, `package.json`/lock only if scripts need correction.

**Interfaces:** `/` neutral view, lang fa/dir rtl/viewport, heading `زیرساخت فیت‌لینک آماده است`, ES module static enhancement only. `RequestIdMiddleware(get_response)` accepts bounded UUID X-Request-ID or creates new UUID, returns header/request correlation and logs method/bounded path/status/duration (no query). `JsonFormatter.format(record) -> str` emits timestamp/level/logger/event/request_id/release_id and error class/frame locations; never raw exception text/locals/private payload. Correlation clears on exit. No body/cookie/auth/header/secret logging.

- [ ] Write render tests for lang/dir/viewport/Persian heading/static references/no auth forms; logging tests for valid/new/oversized request IDs, concurrent request isolation, exception visibility and explicit sensitive-field redaction. Run unit red.
- [ ] Implement baseline templates, minimal view, Tailwind4 input/explicit source scanning of templates, ES module. Avoid external fonts/scripts/providers in Foundation; system-font fallback only. Add stdlib JSON formatting/context middleware, exclude full URLs/queries/phone/cookie data from access logs; worker startup includes process/release without config dump.
- [ ] Run `npm ci`, `npm run build:css`, `npm run check:js`, `uv run --frozen pytest tests/unit/test_rtl_page.py tests/unit/test_logging.py -q -m unit`; require nonempty CSS produced and passing render/redaction tests.
- [ ] Use StaticFilesStorage for development/test; `config/settings/build.py` inherits base, uses fake storage/synthetic key/ManifestStaticFilesStorage and never opens DB, for `collectstatic` only. Production also uses ManifestStaticFilesStorage and the matching collected output. Development ASGI wraps ASGIStaticFilesHandler only in development (not WSGI StaticFilesHandler). Static output is a deployment artifact, not public upload storage. Asset stage compiles Tailwind, collectstatic uses build overlay, image has no baked production secrets.
- [ ] Run `uv run --frozen python manage.py collectstatic --noinput --settings=config.settings.build`, `docker compose build web worker beat`, `docker compose up -d --wait web worker beat`; verify CSS plus staticfiles.json exists for runtime and hashed template paths resolve in a build-settings render test. Generated outputs ignored; sources/locks committed.
- [ ] Stage listed source/tests/config only, commit `feat: add Persian RTL shell and redacted structured logging`.

### Task 12: Complete pytest/Playwright smoke and dependency failure gates

**Files:** create `tests/e2e/test_foundation_smoke.py`, `tests/integration/test_runtime_failures.py`, `tests/unit/test_foundation_scope.py`; modify `tests/conftest.py`, `pyproject.toml`, Dockerfile `e2e` target and Compose `browser` profile.

**Interfaces:** browser reads E2E_BASE_URL (default host http://127.0.0.1:8000, Compose http://web:8000); uses Python pytest-playwright fixture, Chromium only baseline. No additional npm browser framework. Failure gates exercise infrastructure, not business features.

- [ ] Write browser tests: desktop/mobile390x844 page has lang fa/dir rtl/heading, stylesheet200/module200/no console/page errors, no horizontal overflow, API status v1 and health readiness200. Write scope test that URL/schema set has no OTP/registration/profile/coaching/payment/chat/AI route/table and account migration minimum only; assert no admin/login route.
- [ ] Run browser test red before its environment is prepared; document browser-not-installed as setup failure, then meaningful fixture assertion failure if needed, not claim TDD behavior from a missing executable. Build e2e target installing matching `uv run --frozen playwright install --with-deps chromium` as build-only root then drop to app user. This is later coding execution only, per [Playwright installation](https://playwright.dev/python/docs/intro).
- [ ] Run `docker compose --profile test build browser`, `docker compose --profile test run --rm browser uv run --frozen pytest tests/e2e/test_foundation_smoke.py -q -m e2e`; require both viewport cases pass with baked matching browser, no live provider.
- [ ] Implement failure tests with monkeypatched/bounded connection failures and disposable local dependency restart: readiness503/live200, log redaction, storage private on restart, channel Redis delivery, Celery actual response after broker recovery. Test external-service outages without pausing >60s or deleting volumes.
- [ ] Run `docker compose exec web uv run --frozen pytest tests/unit -q -m unit`, then `docker compose exec web uv run --frozen pytest tests/integration -q -m integration`; require all earlier gates pass, no unexpected skip. Do not use a catch-all marker that silently excludes a required file.
- [ ] Stage tests/profile/build configs and commit `test: verify foundation browser and dependency failure boundaries`.

### Task 13: Lint/type/static checks and simple CI

**Files:** create `.github/workflows/ci.yml`; modify `pyproject.toml`, `docs/development/DEPENDENCIES.md`, `Dockerfile` only if check-image needs a change.

**Interfaces:** Ruff format/lint all Python, mypy focused config env/health/storage modules plus Django plugin for model awareness; no blanket ignore-errors. CI mirrors local locked/static/migration/test commands, PostgreSQL/Redis/MinIO service stack, one integration worker and browser smoke. Pin GitHub Actions to reviewed commit SHAs (record action version + SHA), not floating tags. No paid external observability/test service.

- [ ] Run `uv run --frozen ruff check .`, `uv run --frozen ruff format --check .`, `uv run --frozen mypy config/settings/env.py config/health.py apps/assets/storage.py`; fix actual errors, use narrow justified library stubs/ignores only. Do not add second format/lint suite.
- [ ] Design CI checkout/setup uv/Node24, `uv sync --frozen --group dev`, `npm ci`, static build/check, Compose test services plus worker, backend tests, `manage.py check` and `makemigrations --check --dry-run`; artifacts/logs sanitized, ephemeral test credentials generated per job. Never print resolved Compose config or commit a secret. Caching is optional keyed by locks, not required infrastructure.
- [ ] Include Playwright smoke using e2e target; browser/system deps are built from locked package, no downloaded remote athlete data. CI must fail on unexpected skips/migration drift/failed integration worker. Explicitly no auto-deploy, no production credentials.
- [ ] Run all local equivalents from Tasks10–12 plus `uv lock --check`; validate workflow syntax with repository host validation available at execution and confirm first CI run when remote repo exists. If no GitHub remote, retain portable command runbook and report CI remote result unverified rather than invent success.
- [ ] Stage listed paths and commit `ci: add locked foundation checks and smoke gates`.

### Task 14: Document clean startup and final Foundation handoff

**Files:** create `README.md`, `docs/development/FOUNDATION_SETUP.md`, `docs/development/FOUNDATION_HANDOFF.md`; modify `.env.example`, `docs/development/DEPENDENCIES.md`, this plan's checkboxes/evidence only, and roadmap C01 status only when execution truly passes.

**Interfaces:** setup/handoff is the downstream contract for C02, including exact pinned tools, env keys/host-vs-Compose mapping, minimal User guarantees, private storage API and all probe commands. No later business plan executed.

- [x] Document one clean sequence: ignored .env setup/generation → `uv sync --frozen --group dev` → `npm ci` → `npm run build:css` → `docker compose build web worker beat` → `docker compose up -d --wait db redis minio` → `docker compose run --rm minio-init` → `docker compose run --rm web uv run --frozen python manage.py migrate` → `docker compose up -d --wait web worker beat`. Document safe `docker compose down` (without `-v`) for ordinary shutdown; volume deletion is explicit destructive reset, never default.
- [x] Create ignored `.env.verify` with the same local contract and separate localhost ports8001/5434/6381/9100/9101 (choose another unused port only if occupied). Rehearse with `docker compose -p fitlink-foundation-verify --env-file .env.verify build web worker beat`, `docker compose -p fitlink-foundation-verify --env-file .env.verify up -d --wait db redis minio`, `docker compose -p fitlink-foundation-verify --env-file .env.verify run --rm minio-init`, `docker compose -p fitlink-foundation-verify --env-file .env.verify run --rm web uv run --frozen python manage.py migrate`, `docker compose -p fitlink-foundation-verify --env-file .env.verify up -d --wait web worker beat`. Project-specific named volumes/internal hosts isolate data from existing local services. Never purge existing volumes. Verify new test DB/no auth_user with the migration integration test.
- [x] Run final gates in that project: `uv lock --check`, Ruff/mypy commands in Task13, CSS/JS build, Django check, `makemigrations --check --dry-run`, all unit/integration tests, actual Celery probe, Redis channel delivery and browser smoke. Production settings subprocess tests must pass with fake config; production deploy check is evaluated locally with ephemeral valid secrets/config (`manage.py check --deploy --settings=config.settings.production`), any infrastructure trust warning recorded/fixed rather than ignored globally.
- [x] Inspect `git diff --check`, `git status --short`, staged paths and generated artifacts; no credentials/.env/media/node_modules/sources changed. Record command output summaries/selected pins/images/remaining remote-CI limitation in HANDOFF without secret values. Foundation guarantees baseline readiness, not production release certification.
- [x] Stage documentation/example only and commit `docs: record verified foundation setup and handoff`. Report C01 exit evidence and stop; do not begin OTP/C02 without next-stage authorization.

### Verification command note

Default discovery is tests/unit, with `--ds=config.settings.test` in addopts and no default -m filter. Explicit integration/e2e commands must execute all selected cases; Task5's mixed paths run both categories. Container tests use injected internal hosts; host commands after Task4 load .env through UV_ENV_FILE. Configuration subprocesses strip inherited module/env-file, and production checks supply isolated ephemeral env. `--frozen` means no lock update; none of these commands has been run in Stage 2.

### Exact commit commands

After each task's verification use its staging command below, then `git diff --cached --check`, `git diff --cached --name-only` (confirm no secrets/sources/generated artifacts) and its exact commit command. Directory staging here is limited to explicitly scoped source/test directories introduced by that task; inspect contents before staging and do not include unrelated work. Empty tasks are not committed. No `git add .`/`-A`.

| Task | Stage command | Commit command |
|---|---|---|
| 1 | `git add -- pyproject.toml uv.lock .python-version .gitignore .dockerignore package.json package-lock.json .node-version docs/development/DEPENDENCIES.md` | `git commit -m "chore: lock foundation tooling and dependencies"` |
| 2 | `git add -- manage.py config tests/__init__.py tests/conftest.py tests/unit/test_environment.py tests/unit/test_settings.py .env.example` | `git commit -m "chore: establish environment-aware Django bootstrap"` |
| 3 | `git add -- apps/__init__.py apps/accounts config/settings/base.py tests/conftest.py tests/unit/test_user_contract.py tests/integration/test_user_model.py tests/integration/test_initial_migration.py` | `git commit -m "feat: define minimal custom user before initial migrations"` |
| 4 | `git add -- compose.yaml config/health.py config/settings/base.py config/settings/test.py .env.example tests/conftest.py tests/integration/test_database.py docker/healthcheck.py docs/development/DEPENDENCIES.md` | `git commit -m "chore: verify PostgreSQL and safe initial user migration"` |
| 5 | `git add -- compose.yaml config/health.py config/settings/base.py .env.example docker/healthcheck.py tests/unit/test_redis_config.py tests/integration/test_redis.py` | `git commit -m "chore: connect Redis infrastructure safely"` |
| 6 | `git add -- config/api.py config/health.py config/urls.py config/settings/base.py docker/healthcheck.py tests/unit/test_health_api.py tests/integration/test_readiness.py` | `git commit -m "feat: add safe health and versioned status endpoints"` |
| 7 | `git add -- config/celery.py config/tasks.py config/__init__.py config/settings/base.py .env.example tests/unit/test_celery_config.py tests/integration/test_celery_roundtrip.py` | `git commit -m "chore: bootstrap Celery and empty Beat scheduling"` |
| 8 | `git add -- config/routing.py config/asgi.py config/settings/base.py tests/unit/test_asgi.py tests/integration/test_channel_layer.py` | `git commit -m "chore: bootstrap session-aware Channels ASGI"` |
| 9 | `git add -- apps/assets config/settings/base.py config/settings/test.py .env.example compose.yaml docker/minio-init.sh docs/development/DEPENDENCIES.md tests/unit/test_storage.py tests/integration/test_minio_storage.py` | `git commit -m "chore: establish private fake and MinIO storage adapters"` |
| 10 | `git add -- Dockerfile compose.yaml docker/healthcheck.py .dockerignore docs/development/DEPENDENCIES.md` | `git commit -m "chore: provide reproducible ASGI worker and Beat containers"` |
| 11 | `git add -- templates/base.html templates/foundation.html static/src/styles.css static/src/app.js config/views.py config/logging.py config/middleware.py config/urls.py config/asgi.py config/settings/base.py config/settings/build.py config/settings/production.py Dockerfile package.json package-lock.json tests/unit/test_rtl_page.py tests/unit/test_logging.py` | `git commit -m "feat: add Persian RTL shell and redacted structured logging"` |
| 12 | `git add -- tests/e2e/test_foundation_smoke.py tests/integration/test_runtime_failures.py tests/unit/test_foundation_scope.py tests/conftest.py pyproject.toml Dockerfile compose.yaml` | `git commit -m "test: verify foundation browser and dependency failure boundaries"` |
| 13 | `git add -- .github/workflows/ci.yml pyproject.toml docs/development/DEPENDENCIES.md Dockerfile` | `git commit -m "ci: add locked foundation checks and smoke gates"` |
| 14 | `git add -- README.md docs/development/FOUNDATION_SETUP.md docs/development/FOUNDATION_HANDOFF.md docs/development/DEPENDENCIES.md .env.example docs/superpowers/plans/2026-10-03-project-foundation.md docs/implementation/V1_IMPLEMENTATION_ROADMAP.md` | `git commit -m "docs: record verified foundation setup and handoff"` |

## E. Exit gates and scope trace

| Foundation requirement | Owner task / evidence |
|---|---|
| Python3.13/Django5.2/repeatable deps/settings/env | 1–2, locked sync/env failure tests |
| Safe minimal User/first migration | 3–4, empty PostgreSQL and auth_user absence |
| PostgreSQL/Redis/cache | 4–5, real roundtrips/timeouts |
| DRF/session/CSRF/version API/health/readiness | 6, public status/test-only protected endpoint/503 cases |
| Celery/Beat/Redis backend | 7/10/12, actual non-eager probe, one empty Beat |
| ASGI/Channels/channels_redis | 8/10/12, HTTP/Redis delivery/origin rejection |
| S3 baseline/MinIO/fake/private bucket | 9/12, protocol and unauthorized GET tests |
| Docker reproducible web/db/redis/worker/beat/minio | 10/14, clean isolated startup/restart |
| Tailwind/templates/Persian RTL/static/ES modules | 11–12, CSS build and two viewport smoke |
| Logging/request correlation/exceptions/startup | 11–12, redaction/context/log visibility |
| pytest/pytest-django/Playwright/tool checks/CI | 1/12–13, local gates and remote CI if available |
| Docs/secrets/environment hygiene | 1–2/14, explicit staged paths and clean diff |
| PWA-ready boundary only | 11–12, modular static/template organization; actual PWA/offline postponed to C17 |

## F. Stage 2 plan self-review

Plan-only review completed against locked requirements. Corrections: first User migration precedes DB tests; pytest forces test settings even in development containers; host env injection is explicit; real transport gates distinguish eager/config-only checks; ASGI test harness avoids an unnecessary Daphne dependency; static build has a defined secret-free overlay/manifest, ASGI static handler and bind-mount strategy; runtime cannot install dev deps; Playwright root-build/user-run share browser path; raw access/config/exception logs cannot leak secrets; MinIO readiness uses available mc in init, not assumed server-image tools. All fourteen file/interface/task/commit boundaries and twenty roadmap exits were checked. No later business workflow or application source was created; pins/digests are checked only during authorized execution. No implementation command has been executed in Stage 2.

Framework reference for transport dependency: [Uvicorn installation](https://uvicorn.dev/installation/). Static artifact semantics: [Django staticfiles](https://docs.djangoproject.com/en/5.2/ref/contrib/staticfiles/). These support technical boundaries, not new product requirements.

The implementer must still write the named tests and code during an authorized coding stage; this document contains decisions/assertions/commands, not implementations. A later request selects execution method and authorizes the plan; Stage 2 stops here.

## C01 execution evidence (2026-10-05)

Tasks 1–14 Cloud authoring/checks executed sequentially; runtime checkboxes remain
unchecked until actual GitHub Actions evidence. See
[execution ledger](../../implementation/C01_CLOUD_EXECUTION_LEDGER.md) and
[handoff](../../development/FOUNDATION_HANDOFF.md). Task 1 locks are preserved.
Task 11 collectstatic adds `--ignore=src/styles.css` for compile-only Tailwind
input. Runtime tests use the separate checks image rather than adding dev tools
to web/worker/Beat. These Cloud/CI rulings do not change product scope. C02 has not
started; final review and Docker integration remain pending at this checkpoint.

### Final C01 exit evidence
Tasks1–14 complete under the authorized Cloud/CI amendment. Actual Actions
run37295879078 on remote6e6b46c (local377a56b, exact treee3f63eb4) is SUCCESS.
All named runtime categories, clean PostgreSQL/custom User/no auth_user, real
Redis/cache/Celery/Beat/Channels/private MinIO, all Docker builds, startup,
Redis/MinIO restart recovery and both browser viewports genuinely ran and passed.
70 Cloud units and90 combined backend cases passed; no required cases skipped.
Final Foundation review: three earlier Important security findings fixed with
regressions; final scope/evidence check has no unresolved Critical/Important.
Historical PENDING_CI wording above describes earlier checkpoints and is now
superseded by this evidence. No C02, main modification, merge or deployment.
