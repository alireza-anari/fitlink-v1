# Cloud Foundation dependency checkpoint

C01 Cloud checks green; Docker/integration gates PENDING_CI. Current execution
evidence is in ../implementation/C01_CLOUD_EXECUTION_LEDGER.md.

## Verified tooling (2026-10-05)

Linux x86_64 managed container, kernel 6.18.44. Git 2.51.1, uv 0.12.19,
Node 24.19.0, npm 11.9.0. Default Python is 3.12.14; official uv-managed
CPython 3.13.15 was installed in the Cloud workspace and used for resolution.
Docker/Compose are absent: both `docker version` and `docker compose version`
fail with exit 127 (`docker: command not found`). No Docker socket, dockerd or
Podman executable was found. Immutable image references were subsequently resolved below.

## Official resolution

Python uses https://pypi.org/simple exclusively. PyPI returned HTTP 200;
files.pythonhosted.org completed TLS and returned HTTP 404 for its root (normal
for a host serving object paths). More conclusively, `uv sync --frozen --group dev`
downloaded official package artifacts and installed 69 packages successfully.
No unofficial mirror, TLS bypass, wheel commit or historical Windows tooling
was used. `uv.lock` resolved 71 entries (including application/platform entries).
`uv lock --check`, Python/Django version checks and `uv pip check` passed.
uv emitted an environment-lock temporary-file warning; actual sync and compatibility
checks exited zero. Do not infer parallel environment mutation safety from this run.

## Selected versions

| Package | Version |
|---|---|
| Python | 3.13.15 |
| Django | 5.2.17 |
| Django REST Framework | 3.18.1 |
| psycopg / psycopg-binary | 3.3.6 |
| Redis client | 6.4.0 |
| Celery | 5.6.3 |
| Channels | 4.3.2 |
| channels-redis | 4.3.0 |
| Uvicorn | 0.54.0 |
| django-storages | 1.14.6 |
| django-stubs | 5.2.9 |
| Playwright | 1.63.0 |
| Tailwind CSS / CLI | 4.3.0 / 4.3.0 |
| @parcel/watcher (transitive) | 2.6.0 |

All exact Python/transitive versions, official artifact URLs and hashes are in
uv.lock; frontend versions/integrities are in package-lock.json. Plan constraints
are preserved; no business-provider SDKs or frontend framework were added.

## Version rulings and security

Official npm metadata reports matching Tailwind/CLI 4.3.3 as latest. Select matching
stable 4.3.0 deliberately because the historical advisory warning identified the
4.3.3 watcher/braces dependency chain. The Cloud 4.3.0 tree resolves watcher 2.6.0
with no braces dependency. `npm ci`, `npm ls --depth=0`, and `npm audit` passed;
npm audit reported zero vulnerabilities at the time of execution.
An ephemeral pip-audit run against the frozen exported requirements also reported
no known vulnerabilities; the audit tool/export are not application dependencies. No override or
extra frontend package was needed. This is a fresh Cloud verification, not trust
in the old local lock.

Reviewed primary references:
- https://github.com/advisories/GHSA-vfj7-8cjw-p6xm
- https://www.djangoproject.com/weblog/2026/aug/04/security-releases/

Django stays on the locked 5.2 LTS line and resolves its available stable 5.2.17
security patch. A passing resolver confirms package metadata compatibility, not
application, container or integration behavior. Those remain unverified.

## Historical Task 1 prerequisite (superseded by Cloud/CI amendment)

The approved Cloud/CI amendment permits sequential Cloud authoring. Task 3 has
established accounts.User before any real migration. Docker gates now run only
in GitHub Actions; no Work Cloud runtime PASS is inferred.

## Immutable Cloud/CI image references

- postgres: `library/postgres@sha256:639ab7ceb90e13123085b741fb31ef493fba25463002f6da665352e7b534b652`
- redis: `library/redis@sha256:c6eabf748fc7a61dbb5a705c78bcf3d6377b1127a97d0ce965c11c44ba46896f`
- python: `library/python@sha256:2325bb286ec344af3e5898cc224b5844e2707ac6e26b1632516fd3edc84a5e26`
- node: `library/node@sha256:4196d66a565c6f195728d9952f161f4adfe2ad753052a08b7ec7f1c5a6bda42b`
- uv: `ghcr.io/astral-sh/uv@sha256:04d046b13e60d6bcec73cbc5e1cad25d680dea90c8573340950a0ac2d1aef424`
- go: `library/golang@sha256:a688600ca24f8a4d3ca77f95b0dd40704a9fc787c826660eb7ba0b641b8b175d`
- minio_source_sha256: `45521908307306e925c98d629e1c17d78c8b72b6ee242b1bfb1409f7d8ee5841`

MinIO source release2025-10-15 at9e49d5e7; mc release2025-08-13 asset SHA256
01f866e9c5f9b87c2b09116fa5d7c06695b106242d829a8bb32990c00312e891.
Official MinIO source-build guidance: https://github.com/minio/minio/releases/tag/RELEASE.2025-10-15T17-29-55Z
Build-only Go and mc artifact currently target Linuxamd64 GitHub runner; additional
platforms require separately verified official mc checksums. No binaries committed.

CI action refs resolved via authenticated official GitHub API:
- actions/checkout v4: 11d5960a326750d5838078e36cf38b85af677262
- actions/setup-node v4: 49933ea5288caeca8642d1e84afbd3f7d6820020
- astral-sh/setup-uv v6.8.0: d0cc045d04ccac9d8b7881df0226f9e82c39688e
Checkout does not retain credentials; workflow grants contents:read only and runs
only on foundation/c01-cloud pushes. No deployment, packages or release steps.
Celery has no typing marker; its single import has a specific import-untyped
suppression. Django model managers use explicit User generic; no blanket ignores.
