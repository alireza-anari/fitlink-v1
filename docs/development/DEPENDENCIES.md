# Cloud Foundation dependency checkpoint

C01 status: BLOCKED at Task 1 runtime prerequisite; this is not a verified Foundation handoff.

## Verified tooling (2026-10-05)

Linux x86_64 managed container, kernel 6.18.44. Git 2.51.1, uv 0.12.19,
Node 24.19.0, npm 11.9.0. Default Python is 3.12.14; official uv-managed
CPython 3.13.15 was installed in the Cloud workspace and used for resolution.
Docker/Compose are absent: both `docker version` and `docker compose version`
fail with exit 127 (`docker: command not found`). No Docker socket, dockerd or
Podman executable was found. Container image digests remain unresolved.

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

## Next prerequisite

Provide a Docker-capable execution host with Compose and a usable daemon, rerun
Task 1 tooling checks and locked syncs there, then start Task 2. Do not run a
migration or DB-backed test until Task 3 establishes accounts.User. Application,
PostgreSQL/Redis/Celery/Channels/MinIO/browser/CI gates have not run here.
