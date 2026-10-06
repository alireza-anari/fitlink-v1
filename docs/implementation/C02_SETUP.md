# C02 local and isolated CI setup

Use Python 3.13.15 through uv 0.12.19 and the pinned Node version in `.node-version`.
Run from the authorized `accounts/c02-cloud` checkout. Do not reuse verification
project volumes: the scripts reject them and retain existing data. Cleanup removes
containers/networks only; it does not delete volumes.

```sh
uv lock --check
uv sync --frozen --group dev
npm ci
npm run build:css
npm run check:js
uv run --frozen python manage.py collectstatic --noinput --settings=config.settings.build --ignore=src/styles.css
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen mypy config/settings/env.py config/health.py apps/assets/storage.py apps/accounts apps/governance config/use_cases config/account_middleware.py config/authentication.py config/permissions.py
uv run --frozen python manage.py check --settings=config.settings.test
uv run --frozen pytest tests/unit -q --strict-markers
uv run --frozen python docker/production_check.py
git diff --check
```

Task 16 unit verification requires the exact ignored `.runtime/c01` fixture.
CI checks out immutable commit `75c551e5b9bbbfb7777ee52b09a1993b681e921a`
with credentials persistence disabled. The source manifest independently verifies
every blob and reconstructs tree `4dff1ebd5a32ed0359552bf29012d9d1ecf09b24`.
Changed, missing, additional source or symlinked files fail before fixture use.
Only enumerated generated build/cache outputs and Git metadata are excluded.
Do not substitute main or current C02 code for this fixture.

```sh
python docker/c02_baseline.py .runtime/c01
sh docker/verify_c02.sh
```

The complete Docker gate runs original C01 source/tests/configuration with its
empty Beat schedule and real restart checks; a separate fresh C01 database is
then populated using C01 User and Django session code and upgraded in place with
C02. Finally an independent zero-state C02 database runs all current unit/backend,
browser, worker, Beat, Channels, private MinIO and restart gates. No selected skips
are accepted. Fixture sessions are synthetic and stored only in an ignored,
permission-restricted rehearsal manifest; their keys never appear in logs.

Development uses the explicit public test key ring and an in-memory Mock SMS
provider; it offers no code-retrieval endpoint or persistent Mock collector.
Generate local Compose credentials with `python docker/generate_env.py .env`;
the generator refuses to overwrite a file and never prints credentials.
Provider/configuration boundaries remain fail-closed in production: only disabled
SMS and step-up providers are installed, entry and staff recovery must be closed,
and an explicit protected key ring is mandatory. No vendor or production rollout
is part of C02.

Default OTP policy: six digits, 300-second expiry, 60-second resend interval,
five comparison attempts, one-hour quotas (phone sends 5, IP sends 20; failures
phone 10, IP 60). Recovery intake has independent daily phone 3/IP 10 limits;
receipt lifetime is seven days. Recent authority is at most 600 seconds and SMS
timeout at most three seconds. Values are validated by `security_config.py`;
do not relax them to obtain a test pass. Retained HMAC key IDs aggregate quotas.

PostgreSQL owns all challenge/proof/session/recovery/outbox state; Redis is
admission/broker infrastructure. OTP SMS is synchronous. Outbox Celery arguments
contain only event/lease UUIDs, with explicit registered metadata handlers,
bounded durable retries and idempotent effects. Exactly-once external delivery
is not promised. The sole approved Beat schedule scans every 30 seconds, at most
100 rows, with 60-second leases, eight attempts and backoff bounded at 300 seconds.

Browser access uses Django sessions and CSRF, current account state and auth
version, owner/object-scoped selectors and explicit command serializers. No JWT,
browser credential storage, CORS allowance, account directory or generic CRUD.
Staff recovery needs named capability, assignment, fresh case-bound step-up and
non-self authority; bare superuser status grants no shortcut.

Privacy confirmation defaults denied. Holds target only validated privacy-request
records. Overdue review does not silently release evidence. Full export, erasure,
production retention policy, real staff MFA/evidence standards and operational
provider selection remain later release dependencies.
