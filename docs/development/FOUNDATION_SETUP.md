# Foundation setup

Use Linux amd64, Python 3.13.15, uv 0.12.19, Node 24.19.0/npm 11.9.0 and Docker
with Compose v2 and BuildKit. Exact packages, image digests, official MinIO source
checksum and CI action pins are in [DEPENDENCIES.md](DEPENDENCIES.md). MinIO now
builds from verified official source; the first Go/browser build can take minutes.

## Local clean startup

From this branch's repository root, generate ephemeral development credentials
without displaying them. Generation refuses to overwrite an existing file and
sets mode0600. `.env` is ignored; never commit it or use it in production.

```sh
python docker/generate_env.py .env
uv sync --frozen --group dev
npm ci
npm run build:css
npm run check:js
uv run --frozen python manage.py collectstatic --noinput --settings=config.settings.build --ignore=src/styles.css
docker compose build web worker beat minio minio-init
docker compose up -d --wait db redis minio
docker compose run --rm minio-init
docker compose run --rm web uv run --frozen python manage.py migrate --noinput
docker compose up -d --wait web worker beat
```

The generator selects loopback ports8001(web),5434(PostgreSQL),6381(Redis),9100(S3),
9101(MinIO console), avoiding ordinary default service ports. Open
http://127.0.0.1:8001/. Ordinary shutdown is `docker compose down`, without `-v`.
Volume deletion is a destructive reset and is never the default procedure.
The local PostgreSQL role can create disposable test DBs; production must use a
separate least-privilege role and service-managed credentials.

Compose explicitly injects internal db:5432, redis:6379, minio:9000 URLs. Host
commands use `uv run --env-file .env --frozen ...`; the generated file includes
matching loopback URLs and credentials. Django itself never loads dotenv.
Cache/broker/results/channels use Redis DB0/1/2/3 respectively. `test_fitlink` is
reserved for pytest. Production/test settings cannot be selected interchangeably.
MinIO-init uses root only to create a private bucket and bucket-scoped app policy;
web/worker/Beat receive only app credentials. Do not print resolved Compose config.

## Required checks and isolated CI rehearsal

```sh
uv lock --check
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen mypy config/settings/env.py config/health.py apps/assets/storage.py
uv run --frozen python manage.py check --settings=config.settings.test
uv run --frozen pytest tests/unit -q --strict-markers
uv run --frozen python docker/production_check.py
sh docker/verify_foundation.sh
```

The last script generates ignored `.env.verify` and uses only the isolated
`fitlink-foundation-verify` project and project-specific volumes. It validates
Compose without dumping secrets, builds all runtime/check/browser/production
images, runs init and clean migration before startup, checks Django/model drift,
runs every unit/integration test against real PostgreSQL/Redis/MinIO/worker,
checks exactly one Beat, executes both browser viewports, restarts Redis and
MinIO without volume deletion and reruns transport/private-storage/browser gates.
It shuts down only its own containers on exit and retains volumes. A genuinely
clean rehearsal requires that this named project has not previously been used;
use a fresh disposable Docker host, as each GitHub Actions job does. If a failed
local rehearsal already created `.env.verify`, deliberately choose a new isolated
project/env file or review and remove only that ignored file; no silent overwrite.

The script's backend commands run through the separate `checks` image because
runtime images intentionally exclude pytest and other development dependencies.
Browser/system libraries are installed at image build time, then tests run as
nonroot `app`. pytest treats every unexpected skip as failure.

## Configuration and static/logging boundaries

Development defaults are explicitly local/synthetic. Production import requires
random secret, concrete hosts, verify-full PostgreSQL, authenticated TLS Redis,
HTTPS S3 and explicit private bucket/app credentials. It disables DEBUG, enforces
secure session/CSRF cookies, SSL redirect and HSTS. Proxy trust and public TLS/
static delivery must be designed for an actual deployment; no deployment is
performed here. Offline `check --deploy --fail-level=WARNING` uses ephemeral
synthetic config and makes no service connection.

Tailwind source is compile-only and excluded from collectstatic. The production
image contains a matching hashed manifest; production does not serve static
files through the development ASGI handler. Future serving/CDN configuration is
a deployment concern. Upload storage always stays private and separate.

Request IDs accept only bounded UUIDs and reset after each request. Structured
logs emit safe method/route-pattern/status/duration and exception class/frame
locations. Raw messages, exception text, bodies, cookies, authorization headers,
query values and credentials are excluded. Uvicorn raw access logging is disabled.
