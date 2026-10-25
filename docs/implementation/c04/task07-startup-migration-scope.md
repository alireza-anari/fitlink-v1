# C04 Task 7 startup classification and migration attribution — diagnostic only

Authorization: one new workflow run, attempt 1, maximum two independent jobs.
Task 7 remains IN_PROGRESS / NOT ACCEPTED. No acceptance retry or completion checkpoint.

Parent diagnostic checkpoint: 33109e4fbec882a032bb59276c59e89790b1e542,
tree d3965debbc7b2aefa5f2342ca22312b797bd8574.
The execution branch remains 2b2790cdf9019338ddeb09f9df2fdfb1fa0dd331,
tree f4a49666111ce27d6c12cc6aff89f3430c7ea243.

## Job A

Fresh ubuntu-24.04 runner, accepted Task 6 source
0787d7880f9fd27006bf76ae0f16e31536ef4503, tree
b207a0a8e946750a0dd1213f5460e51f67dd3000. Original frozen preparation,
Compose configuration/build and original `docker compose up -d --wait db redis
minio scanner` operation. Stop after that operation; no pytest, MinIO provisioning,
or historical acceptance claim. Service-start subprocess executes exactly once,
with its existing 180-second bound. Capture stdout and stderr privately via draining
pipes, retain at most 1 MiB each, count discarded bytes, and never upload either.
A pre-cleanup bounded Docker daemon/list/inspect observation exports only fixed
service labels, finite states/health and numeric status metadata. Rule IDs classify
observed fixed signatures; they do not establish an underlying root cause. Multiple
categories and unavailable/incomplete observations remain explicit. Startup outcome
and observation completeness are separate. An unexpected failure is not retried.

## Job B

Fresh independent runner, exact Task 7 candidate 2b2790cdf9019338ddeb09f9df2fdfb1fa0dd331.
The exact two original tests, fixtures, order and assertions from the preceding
migration diagnostic remain selected:

- tests/integration/c02/test_account_migrations.py::test_populated_c01_upgrade_preserves_identity_and_sessions
- tests/integration/c03/test_c03_migrations.py::test_optional_profiles_not_created

Real PostgreSQL, Redis, MinIO, scanner and original relevant runtime services,
immutable C01/C02/C03 content checks, migrations, no-op, drift and initialization
are retained. No full backend or acceptance manifest is executed. The existing
300-second two-test observation limit is unchanged. The inherited full-backend
900-second deadline and Foundation 1800-second deadline remain unchanged; this
workflow does not execute those complete gates. A single diagnostic controller
is bounded to 1800 seconds; cleanup is a separate owned-resource step.

Wrappers delegate originals exactly once and preserve return and exception identity.
Clone, rendering, reload, executor migrate and migration apply/unapply timings
retain setup/call/teardown attribution, monotonic wall/thread CPU clocks and inclusive
nesting semantics. Additional per-migration rows use finite indices into migration
filenames of installed app configs and actual configured migration modules, not
model/user data. They record number of declared operations per invocation, count,
wall and thread CPU; operation count is not a claim every operation completed on
a failing invocation. Exceptions and their text are not exported. Rows are bounded;
unknown identities or observer faults invalidate diagnostic completeness.

The original primary-process SQL aggregate and five-second host/PostgreSQL sampler
remain. No SQL text or parameters are exported. Short waits can be missed. Wrapper
bookkeeping/no-op calibration estimates only measured observer portions; the extra
per-migration wrapper, sampling, imports, ordering and indirect effects are not a
fully isolated overhead measurement. Inclusive rows overlap and must not be summed
across clone/render/migration layers. This run has no same-host Task 6 migration
comparison and no new minimal-observer control; historical comparisons cannot prove
source causality. A failed startup leaves migration timing explicitly unavailable.

## Preservation and controls

Only current-C04 diagnostic instrumentation/harness and this scope are changed on
a new isolated branch. Application code, published migrations, fixtures, locks,
original tests and mandatory acceptance workflows are unchanged. Owned project
labels, empty preflight resource checks, private ownership markers and exact label
cleanup isolate resources. Raw process output remains runner-private and is never
selected for artifact upload. Focused controls cover bounded capture, privacy,
classification, pre-cleanup sequencing, exact return/exception identity, nesting,
manifest/detail rejection, source selection and cleanup guards. No retry is coded.

Artifacts contain only bounded sanitized JSON and finite pytest/host journals.
They must be independently downloaded and SHA-256 checked before the docs-only
observation report is published on this diagnostic branch. That docs-only commit
must not trigger another run. Stop after reporting; further diagnostics, product
changes, acceptance attempts and phase transitions need separate authorization.
