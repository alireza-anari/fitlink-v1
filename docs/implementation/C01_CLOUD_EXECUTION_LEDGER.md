# SDD ledger — plan: docs/superpowers/plans/2026-10-03-project-foundation.md

Cloud execution 2026-10-05; no prior Windows execution state used.

## Source verification and baseline
All twelve authoritative sources read and copied byte-for-byte. Historical DEPENDENCIES.md read only, not copied into active dependency documentation.
Baseline commit: 6c36e6a. 29 local Markdown links resolve. Sources unchanged.
Fresh dedicated repository/branch foundation/c01-cloud; no existing application tests.

## Pre-flight interfaces
- Tasks 1→2–14: locked Python/Node tooling; Docker missing at first prerequisite. No application task may be marked complete.
- Tasks 2→3→4: configuration-only boot precedes custom User; first DB-backed test/migration deferred until accounts.User is configured and PostgreSQL exists.
- Tasks 4→5→6: bounded DB/Redis probes feed readiness.
- Tasks 5→7/8/10/12: separate Redis logical databases for cache/broker/results/channels; real transport gates require running services.
- Tasks 9→10/12: private storage/init before MinIO runtime tests.
- Tasks 1→11→12→13→14: CSS scripts/locks precede generated assets, browser and CI checks.
- Tasks 10→11/12→14: shared locked image, static manifest and isolated clean rehearsal depend on Docker/Compose.

Ruling: Windows checkout/tool paths — use the fresh Linux repository and workspace-scoped Python installation — portability remains unverified until complete runtime gates pass.
Ruling: isolation — initialize the empty dedicated repository directly on the user-authorized foundation/c01-cloud branch — no shared branch/worktree exists to protect.
Ruling: absent Docker prerequisite — verify independent Task 1 dependency steps but keep Task 1 BLOCKED and do not advance into Task 2 — runtime pins and lock synchronization still need validation on a Docker-capable host.

## Task 1: in progress / BLOCKED
- Python default 3.12.14; uv 0.12.19; Node 24.19.0; npm 11.9.0; Git 2.51.1.
- Installed official uv-managed CPython 3.13.15 under workspace .runtime/python (not committed).
- curl -I --max-time 20 https://pypi.org/simple/django/: HTTP 200.
- curl -I --max-time 20 https://files.pythonhosted.org/: HTTP 404 at root, proving TLS/host reachability but not artifact download success.
- docker version and docker compose version: exit127, /bin/bash: docker: command not found.
- No dockerd/podman executable or /var/run/docker.sock found by local checks.
- Official Python lock resolution and npm metadata checks pending actual results.

## Tasks 2–14
Not started. No application code, migration or database-backed test run.

### Task 1 actual results
- uv lock: 71 packages resolved from https://pypi.org/simple.
- uv sync --frozen --group dev: 69 installed; official artifact downloads succeed.
- uv lock --check: exit0, resolved71 unchanged.
- uv run --frozen python --version: Python3.13.15, exit0.
- uv run --frozen python -m django --version: 5.2.17, exit0.
- uv pip check: 69 compatible, exit0.
- npm ci: exit0; npm ls --depth=0: matching Tailwind/CLI4.3.0.
- npm ls @parcel/watcher braces: watcher2.6.0; braces absent.
- npm audit: zero vulnerabilities, exit0.
- pip-audit --disable-pip --no-deps against uv frozen export: no known vulnerabilities, exit0. Ephemeral audit tool not committed as dependency.
- uv environment-lock temporary-file warning observed despite successful exit; parallel mutation safety is not validated.
Ruling: frontend patch selection — choose exact matching stable Tailwind/CLI4.3.0 after official metadata reports latest4.3.3, to avoid the reviewed braces advisory; fresh npm tree/audit confirms patched watcher2.6.0 without braces — newer patch fixes may be absent; reevaluate on intentional updates.
Task 1: BLOCKED (Docker/Compose prerequisite missing; dependency-only checkpoint saved, not completion).
Task 2–14: BLOCKED (not started; await Task1 runtime prerequisite).

Dependency-only checkpoint commit: 0b531d25a6c358f411fb078bc79f3bdbfffa5a30

## Resume — 2026-10-05 Cloud/CI authorization

Existing foundation/c01-cloud branch and commits 6c36e6a, 0b531d2, b5f1e1f
preserved. Working tree was clean. Plan and ledger reread; no source recreation.

Fresh checks: uv lock --check against official PyPI exit0; uv sync --frozen --group
dev exit0, 69 packages installed; npm ci exit0; npm ls --depth=0 exit0, matching
Tailwind/CLI4.3.0. Existing uv.lock/package-lock.json unchanged. Python3.13.15,
Django5.2.17 retained. uv temporary environment-lock warning persists.

Ruling: Cloud Docker limitation — Work Cloud is authoring/unit/static host and
private GitHub Actions is the real Docker integration host; keep all approved
Docker/Compose/service/restart/browser/clean-startup gates mandatory PENDING_CI —
provisional Cloud work cannot establish runtime correctness or C01 PASS.
Ruling: Task1 completion — supersede earlier BLOCKED status with PASS WITH DOCKER
RUNTIME GATE DEFERRED TO CI after fresh non-Docker checks passed; retain dependency
commit0b531d2 unchanged — runtime compatibility remains unverified until Tasks10/14.

GitHub authenticated and repository metadata checked via connector.
Project candidate alireza-anari/fitlink-v1 is PUBLIC; push permissions exist but
user authorizes PRIVATE only. No other accessible repository is identifiable as
the FitLink project. No remote configured; no push attempted; no visibility
change, repository creation, merge or deployment performed.

STOP: private-project repository prerequisite missing. User must make
alireza-anari/fitlink-v1 private or supply/connect the correct private FitLink
repository with branch-write and GitHub Actions access. Do not accept tokens in
source files. Tasks2–14 remain unstarted; service gates PENDING_CI; C01 BLOCKED.

## Resume — private GitHub confirmed, Git transport blocked

2026-10-05: GitHub metadata confirms alireza-anari/fitlink-v1 visibility PRIVATE.
Authenticated account alireza-anari has push/admin permission. Actions runs API
is readable and returns total_count0. Actions execution/write permission has not
been proven by a workflow run; no workflow exists yet.

Configured origin=https://github.com/alireza-anari/fitlink-v1.git without credentials.
Attempted only GIT_TERMINAL_PROMPT=0 git push --set-upstream origin
foundation/c01-cloud. Exit128: could not read Username for https://github.com:
terminal prompts disabled. No configured Git credential helper, GitHub credential
environment or connected SSH agent was found. Credential values were not printed.

Connected GitHub API tools support file/object mutations but expose no authenticated
Git transport to transfer this existing local history unchanged. No replacement
history/bootstrap branch or main/master write was attempted.

External blocker: authenticated Git transport for this checkout is required to
perform the explicitly ordered initial push before Task2. Existing commits/locks
remain preserved. Tasks2–14 unstarted; C01 BLOCKED; no CI run or integration PASS.
No merge, release, visibility change, deployment or production action performed.

## Authenticated API checkpoint synchronization
Remote checkpoint mapping: local 0db6b27 -> GitHub 6f23ae50189005511aae8e35bbc170f77ef44863.
Exact local/remote tree: ec5c3b4cc435a8282c7f17b926609b77bd895409.
Remote Foundation branch created from bootstrap main8ede9a4; main unchanged.
Ruling: user-authorized Git Data tree synchronization uses a different remote
parent ancestry; preserve local history and verify tree equality, expected branch
head and non-forced fast-forward updates — hashes differ and must be mapped.

Task 2: Cloud PASS (16 settings/env tests RED→GREEN; Django check no issues).
Ruling: first red run overrides pytest addopts because config.settings.test does
not exist yet; missing config caused16 failures, not dependency failure — normal
--ds test overlay restored for green run. No database-backed test or migration.
Mapping: local f64557a3d263ee7d8ad444b206a81b60992298f4 -> GitHub 99938d27c078cb3974eab0237746f30b0f0f8d8e (tree e5169e5bbd6401877ace79b875dbca700be8f7e7).
Task 3: Cloud PASS (23 total unit tests green; custom User contract7 cases;
accounts/0001_initial generated and inspected; check no issues; no model drift).
AUTH_USER_MODEL=accounts.User configured before makemigrations. Minimal identity,
unusable passwords, UUID, phone uniqueness/check constraint and auth relations only.
No DB migration execution. Clean PostgreSQL/no auth_user gates PENDING_CI in
 tests/integration/test_initial_migration.py and test_user_model.py.
Ruling: makemigrations attempts a migration-history read on absent PostgreSQL;
connection-refused warning is recorded, generation/drift commands exit0 — Cloud
proves model state only, CI must prove the real migration graph from zero.
Mapping: local a9f89200494d78c5d78f2b39fa24ff9c6607c47e -> GitHub ae3f95a9db240eb0ca449dfef82261d6dfa20623 (tree 21eae0b2c2a1e16b231994c3664bacf711545e53).
Task 4: Cloud PASS (24 unit tests; DB failure probe RED→GREEN; PostgreSQL17 image
resolved from official registry to immutable digest). Live SELECT1, zero-state
migration, auth_user absence and timeout/test-DB contracts PENDING_CI. No migrate
run in Work Cloud. The local/test role may create test_fitlink; never a prod role.
Mapping: local ffeed80a5e78034ff91b031e06eec6e00cb408fb -> GitHub 1bc1c85aec53e0dec3932805a9e9f7dd9a9196ac (tree 12aca4315046cbf971d4211afc431eedabd209c5).
Task 5: Cloud PASS (26 units; Redis config/failure probe RED→GREEN; private-loopback
Redis7.4 immutable image; distinct DB0/1/2/3; bounded2s cache/probes). Real Redis
PONG/cache roundtrip PENDING_CI. Dev/test reject remote Redis and PostgreSQL hosts.
Mapping: local e2a72765e5e87a3c1c673d5a0616685cda097573 -> GitHub b6972059eb9dcf83e8dc4c2ad4ea804ac6bfea97 (tree fd390338020fa54a5cb2b014559db166cb6ade5c).
Task 6: Cloud PASS (31 units; live/readiness/status RED→GREEN; generic no-store
responses; Django check clean). Real DB/Redis readiness and test-only protected
session/CSRF behavior PENDING_CI. No product API/auth endpoint.
Mapping: local a6657f7942add825656ff5c89db7d926140ccfd2 -> GitHub 99452d2278a4ac4f28afcdadb0d1c2506a85a996 (tree e3dfceb7ea39bad450719082e4c8c98352cbf1c0).
Task 7: Cloud PASS (35 units; Celery namespace/JSON/empty Beat/local apply
RED→GREEN). Non-eager15s actual worker roundtrip and Beat runtime PENDING_CI.
Redis result expiry86400s; no business job/schedule/outbox models.
Mapping: local e65b5c3f927381eb879a721603d07dc27dc8c7ab -> GitHub 1bd7db319eaaef5ad05e71f2713cf88ffd88779c (tree 814cb583952b0b10d602255866720e3a5812f3fe).
Task 8: Cloud PASS (38 units; ASGI HTTP/status, empty product socket routes,
untrusted-origin rejection RED→GREEN). Redis group send/receive/pool reconnect
PENDING_CI; actual Redis restart will precede another CI transport roundtrip.
Mapping: local f6fbaeaae1a3be0c9cd2d23a07f545dc69fd2919 -> GitHub d47709b61a886805dc5efc8e098d4fff89e7e802 (tree 281b260f5aa2fe9925d03380258fe66607ac37f3).
Task 9: Cloud PASS (49 units; private fake roundtrip/key/expiry and real S3 signing
without network RED→GREEN). Real MinIO object/signature/expired URL/anonymous403,
limited app policy and idempotent bucket init PENDING_CI. No Asset model/API.
Ruling: official MinIO distributions changed — DockerHub/Quay returned401 and
old dl.min.io archives410; official latest MinIO release instructs source builds
and fixes a privilege-escalation CVE. Build verified official release source
RELEASE.2025-10-15T17-29-55Z at9e49d5e7 and use official mc release asset checksum;
no unofficial mirror/older vulnerable image — Go is build-only and build time grows.
Docker definitions use the approved MinIO architecture and remain PENDING_CI.
Mapping: local 121de3aad2f75335de09087876798273e1964c88 -> GitHub dd5749291f4c11b12147014a1fe683946da4abca (tree b4d9f6b15de8d7e436012832f417b9e9eb649ecb).
Task 10: Cloud static authoring PASS; Compose YAML parsed and service/env/runtime
boundaries reviewed. Actual config/build/private MinIO/source compilation/nonroot
permissions/web/worker/Beat/restarts remain PENDING_CI; not a runtime PASS.
Ruling: runtime has no pytest/dev deps — use a separate locked checks image/service
for integration verification instead of installing test tools in running web —
CI must validate that the test service reaches the same runtime/infrastructure.
Ruling: suppress Celery/MinIO banners with --quiet and safe structured logs to avoid
connection/config dumps — runtime startup observability is explicit health/log events.
MinIO server runtime is the pinned Python base, so its Python health command is
actually provided; source-built image replaces unavailable official image distribution.
Mapping: local f45cb23584351a117afe1a00ec87918b286d33c1 -> GitHub 507388dc5acc3843a792404bac0e52348f87ac84 (tree b34c1aade3ea0712a8af3b2416c403cb9c88691b).
Task 11: Cloud PASS (56 units; six initial RED cases → GREEN; npm CSS/JS build;
secret-free collectstatic and hashed manifest/render regression verified).
Docker build/runtime static serving and browser remain PENDING_CI.
Ruling: collectstatic must exclude compile-only src/styles.css via
--ignore=src/styles.css: its Tailwind import is not a browser dependency. Actual
initial collectstatic failed missing src/tailwindcss; compiled CSS/module collect
and hashed template paths now pass. No product forms or routes added.
Mapping: local 34bfdc76be0565205ec851a2295389a895326137 -> GitHub 27b6486f0e13c6155caa353cfd804a77e5add0e2 (tree cc48971065a84c35d1035df3ba80e4dce9d80ab0).
Task 12: Cloud PASS (57 units; explicit Foundation route/model scope; no C02).
Both browser cases attempted: initial sandbox /tmp failure; workspace TMPDIR
removed that failure and confirmed Chromium executable absent. These are setup
errors, not behavioral TDD red or PASS. Matching browser/system dependencies are
provided by the e2e image; real two-viewport smoke remains PENDING_CI.
Failure integration tests include bounded real Redis refused connection and
redacted PostgreSQL exception/readiness503/live200. Real dependency restart,
worker/channel/storage recovery and all DB tests PENDING_CI. Pytest fails if any
selected mandatory case skips; no silent marker exclusion.
