# C03 execution ledger — plan: docs/superpowers/plans/2026-10-06-c03-profiles-verification.md

## Authority and immutable baselines

- Explicit user authorization: execute C03 Tasks 1–14 sequentially; no C04,
  merge, deployment or protected-ref mutation.
- C02 head: 0905be6c6ca608d469fe33e87f514b22591132d1.
- C02 tree: ed788191bb6f5011e6b35a63823ae8183af7b53d.
- Approved plan head: 79fd62e583cbe81f335bb08fce0eb43ff36b0167.
- Approved plan tree: d60c49df3b79338c0694122fab03809f86c37f5a.
- Execution branch: profiles/c03-cloud, created at the exact approved plan head.
- Protected main: 8ede9a451db6103f4e3ebf65784ee9f16b96feb2.
- Protected foundation/c01-cloud: 75c551e5b9bbbfb7777ee52b09a1993b681e921a.
- Protected accounts/c02-cloud: 0905be6c6ca608d469fe33e87f514b22591132d1.
- Protected profiles/c03-plan: 79fd62e583cbe81f335bb08fce0eb43ff36b0167.

## Executor and provenance

- Linux x86_64 Cloud executor; Python 3.13.15 provisioned through uv 0.12.19;
  Node v24.19.0. Repository Python requirement and locks unchanged.
- Shell Git authentication unavailable. Authenticated GitHub API is used for
  exact materialization and guarded non-forced synchronization.
- All 255 tracked blobs/modes verified; no submodules; git write-tree equals
  d60c49df3b79338c0694122fab03809f86c37f5a before any edit.
- Synthetic local baseline c100272cc651b7f88629b5e5fa2a4fbc63063f6f maps to
  remote 79fd62e583cbe81f335bb08fce0eb43ff36b0167. Never publish synthetic ancestry.
- Exact immutable C01 fixture materialized separately and verified by the
  existing docker/c02_baseline.py: 4dff1ebd5a32ed0359552bf29012d9d1ecf09b24.
- Remote C02 run 37486370317 verified successful on implementation head
  935494eda888cdcfd7dffaac4c519f083cda9595; comparison to final C02 head shows
  only C02_HANDOFF, C02_EXECUTION_LEDGER and C02_SETUP documentation changes.
- Real-service strategy: hosted GitHub Actions PostgreSQL/Redis and inherited
  complete C01/C02 rehearsal; add MinIO/scanner/workers/browser in owning tasks.
  Local unit evidence never substitutes for required hosted service gates.

## Untouched baseline checks

- Python version, uv lock --check, frozen sync with dev group and npm ci: exit 0.
- Tailwind, both JavaScript syntax checks and collectstatic: exit 0.
- Full unit suite: 288 passed, 11.53s, no selected skips.
- Ruff check/format (221 files), mypy (85 files), Django test and production
  configuration checks, git diff --check: exit 0.
- Initial uv project-lock warning was environmental; writable ignored TMPDIR
  is used for subsequent commands. No dependency or source workaround.

## Preflight shared interfaces

| Producer → consumers | Contract checked |
|---|---|
| 1 → 2–14 | Additive relational schema, immutable evidence and finite governance values; no initial profiles or authoritative role JSON |
| 1 → 4/5/11/12/13/14 | Incremental hosted CI exists first; each owning task adds its service/test selection before completion |
| 2 → 3/4/6–12 | Current AccountActor, owner locks, finite account actions, receipts; role/flag/profile is not authority |
| 3 → 9/11/13 | Self-storage callbacks revalidate owner/schema and current consent; no professional baseline reader |
| 4 → 5/6/7/9/11 | Quarantine only; immutable opaque source; no READY before successful Task 5 processing |
| 5 → 6–14 | Durable attempts, separate long I/O, fresh lease/account/consent/hold check before derivative release |
| 6 → 7/8/10/12/14 | Separate identity/role evidence, declaration and decision counters; cosmetic edits preserve evidence |
| 7 → 8/12 | Immutable target snapshots; assigned named capability and fresh case step-up on reads and writes |
| 8 → 10/12/14 | Independent outcomes, restriction distinct from approval-linked revoke; C04 reader exposes verified_roles only |
| 9 → 13/14 | Holds/retention never authorize access; missing destructive policy denies cleanup |
| 10 → 11/12 | Owner-only preview and inert membership; no public routes or assistant operational authority |
| 11/12 → 13/14 | Real desktop/mobile owner/staff gates, native forms, CSRF and strict diagnostics |
| 13 → 14 | Audit every earlier head-bound hosted gate, then exact original C02 same-database upgrade and separate clean migration |

No interface redesign is authorized. The approved corrected plan remains unchanged.

## Task states

Task 1: STARTED — inherited gates green at 01d400d; metadata/source guards in progress.
Tasks 2–14: PENDING — not started.
No C03 task COMPLETE or C03 PASS claim.

## Task 1 CI bootstrap

- Initial contract RED: 5 failed / 8 passed (0.10s), expected missing C03 trigger,
  conditional cumulative entry point and test/service selection. No import or
  fixture failure. Log: .superpowers/task1-ci-red.log.
- Exact inherited C02 workflow is protected by its approved Git blob hash after
  removal of only the authorized trigger/step extension. Negative mutations
  cover omitted regression, changed immutable source, conditions, broadened
  triggers and continue-on-error. This contract is not real-service evidence.
- Minimal bootstrap retains both inherited jobs and all their commands/services;
  appends C03 cumulative invocation after actual Redis restart in the existing
  PostgreSQL job, conditional only on refs/heads/profiles/c03-cloud.
- Cumulative script requires actual PostgreSQL SELECT and Redis PING, fails
  closed without exception details, and explicitly selects installed C03 tests.
- Infrastructure checkpoint does not satisfy schema RED, Task 1 completion or
  authority to advance to Task 2. No domain models/migrations/routes added.

- Bootstrap GREEN: 13 focused cases (0.44s), 301 full unit cases (10.87s),
  no skips. Ruff/format, shell syntax and diff check pass.
- Focused security review: no widened inherited condition/permission/trigger,
  no service failure conversion to PASS, no private error text.
- Migration impact: none. Hosted bootstrap CI PENDING; Task 1 not COMPLETE.

## Recovery and bootstrap hosted evidence (2026-10-07)

- All four protected refs rechecked against the immutable SHAs above; unchanged.
- Existing isolated execution checkout is clean; preserve synthetic ancestry.
- Remote sync already completed before interruption: local
  bcd2bb9361a8f8ceff82600b903064ed32b94f90 -> GitHub
  7526b95bc0d780912c42329a10f08da4125a41c3; exact shared tree
  d3ecd4d0871c9b90a3d85ffaffc72125ee502dc8; remote parent is approved plan.
- Bootstrap Actions run 37521380280 SUCCESS at that exact source head:
  https://github.com/alireza-anari/fitlink-v1/actions/runs/37521380280.
- Actual job logs inspected: foundation 112467362448, c02-migrations
  112467362688, every required step successful, no selected skips.
- Foundation: 301 current units, immutable C01 70 unit/90 backend, exact
  C01 populated same-database upgrade prepare/verify, independent current
  588 backend tests, 38 C02 browser cases, two C01 viewport checks before
  and after service restarts, durable outbox restart prepare/verify, five
  Redis/Celery/Channels and one MinIO recovery case. All exit 0.
- Migration job: 269 inherited PostgreSQL cases, real Redis durable quota
  restart, real PostgreSQL SELECT/Redis PING readiness, 13 C03 bootstrap
  contract cases. All exit 0. Hosted service containers use inherited pins.
- Task 1 remains STARTED. Schema RED must be observed on PostgreSQL before
  implementing models. Tasks 2–14 remain PENDING.

## Task 1 schema test specification

- Added explicit private relational schema/event contracts and real PostgreSQL
  profile/role/draft/target/decision/revocation/restriction/metadata/immutable
  snapshot/runtime-role cases. Test factory calls schema assertion inside each
  test, avoiding collection/import/fixture failures as false RED.
- Local unit RED: 7 expected failures / 13 passed (0.43s): absent C03 schema
  and rejected new event envelopes. Log: .superpowers/task1-schema-unit-red.log.
- Cumulative hosted entry point explicitly selects all new test files.
- No schema implementation yet; hosted PostgreSQL behavioral RED pending.

- Test-spec sync: local b3c17f3199ec08ba1edd1b1332b99667add9d0ed ->
  GitHub 7a18a32c7706dcd11329f8aa778c4d8076311ffd, exact tree
  c1612b6a910dd100c9559a24e653de7e013f77b3, run 37571066990.
- Additional baseline/history guards: local
  6ff01e65dbe4db1fb2c7d0fb99a092a48c51eb27 -> GitHub
  a056d3b6f6609c39a2d01fc253348911a92ea508, exact tree
  20294e2445f276f0987f30be1156a530743df8d0.
- Foundation job 112629578318 exposed a collection error: C02 and C03
  test_schema_contract shared a top-level module name. Not behavioral RED.
  Reproduced locally; adding package markers only for tests/unit and its C03
  directory separates unit.c03 from existing modules. Complete unit+C03
  integration collection now succeeds: 326 tests. No assertions changed.

## Recovery of newer remote schema work (2026-10-07)

- Preserved original checkout at local 5f399ec6994a526e1e2b668bb6e94968c6f7df57
  and all 17 unpublished model/package files unchanged. Its exact committed tree
  is 6af62b216f2d0851fe73349c8b33f86fc5974d17, mapping to remote
  01e72afe62fa800745657e3b4d547bbe8978c616. The remote had advanced through
  18 additional C03 implementation/fix commits; no remote write preceded inspection.
- Recovered remote b16d1da51c1a08e43e2ab8c43d520cf395b2fd35 in a separate
  execution checkout. All fetched blobs and exact tree
  cc93e56c9fd2d3f705596ec14dd32f0b83a53f0b verified. Synthetic local recovery
  e8529a4090a0c68313349390d883ec81c45908c8 maps to that remote head;
  synthetic ancestry must never be published. Original unpublished files contain
  additional candidate constraints and remain available for Task 1 reconciliation.
- All four protected refs match the authoritative SHAs above. No merge/deploy.
- Run 37597270721 FAILED on b16d1da; both actual logs inspected.
  c02-migrations 112712855584 SUCCESS: 269 inherited PostgreSQL/service tests,
  actual Redis quota restart, migration SQL/drift, 40 cumulative C03 cases.
  foundation 112712855355: 310 units, immutable C01 70 units/90 backend,
  original service/browser restart checks, exact C01 populated upgrade,
  615 current backend and two ASGI browser cases passed. C02 browser gate:
  36 passed, two viewport failures at test_account_flows.py:33 asserting that
  AthleteProfile/ProfessionalProfile models do not exist. Later gates did not run.
- Ruling: apply approved plan section 16 and Task 1's narrow current-source
  scope extension to this browser assertion. Preserve account behavior checks
  and require zero AthleteProfile and ProfessionalProfile rows after actual
  account entry/preferences; exact installed-model/no-public-field assertions
  remain in current C03 schema tests. Immutable source expectations are unchanged.
  Cost if wrong: future profile-creation flow needs its own explicit test boundary.
- Strengthened the existing current-source privacy-intake scope adaptation with
  zero Asset rows after intake, retaining ErasureMarker absence and every original
  intake/auth/outbox assertion. No production behavior, route or migration changed.
- Local recovery prerequisites: copied verified immutable C01 source as real files
  (symlink rejected by existing verifier), rebuilt Tailwind; resulting complete
  unit run 310 passed in 11.28s, no skips. Both changed test files pass Ruff/format;
  git diff --check passes. Initial local prerequisite failures were fixture-path
  and missing built CSS, not product RED; neither assertion was weakened.
- Task 1 remains STARTED pending corrected-head hosted browser/service evidence
  and full schema review. Tasks 2–14 remain PENDING; no C03 PASS claim.

## Task 1 recovered scope gate and schema hardening

- Remote sync: local a7e6b5db5ab25042595cb76f87ffc05f1736f9e4 -> GitHub
  cdf20310c32ae17c38df982d5a5cbde704f3a69a; exact tree
  21f2dc61bd5ea41f248a3e8a3a12adef402d755f, actual parent b16d1da, force=false.
- Run 37643375645 SUCCESS. Foundation 112867716820 actual log inspected:
  310 current units; original immutable C01 70 units/90 backend and full original
  service/browser/restart gates; exact populated C01 same-database prepare/verify;
  615 current backend; all 38 C02 browser cases; C01 smoke before/after restart;
  durable outbox broker restart; 5 transport and 1 private storage recovery.
  c02-migrations 112867716437 successful, 269 inherited and 40 C03 cases.
  This verifies the scope correction, not complete Task 1 schema coverage.
- Immutability test checkpoint local 1044d2eb60dd1bd1a77e0105955bb1eddfc8ad42
  -> GitHub 39727f8c8e95c4119f9f0c78e8d6900ffc93328c; exact tree
  b8db761d6d093cf9388b25ba601aa85090e39ef5.
  Run 37643628719 / PostgreSQL job 112868606205 actual RED: 4 failed,
  42 passed. Submitted target draft reopening, target/evidence additions after
  submission and direct SQL submitted-baseline deletion were improperly allowed.
  All 269 inherited service cases and real Redis quota restart passed.
- Bounds test checkpoint local 7c8e6fbd21a36511c4cf7e1e3551d9e99fabd416
  -> GitHub 44e9914f08c35c259a9f0962103bb412cd21c830; exact tree
  5b8a7aff8a31fb3be7c9ad99b14475fb0c83abe5.
  Run 37654056491 / PostgreSQL job 112904544361 actual RED: 28 failed,
  42 passed, all expected DID NOT RAISE failures. The additional 24 cases cover
  approved baseline scalar/enumeration bounds, professional experience/accent/step,
  raster size/MIME/hash/subject bounds and non-self assistant metadata.
- Additive correction: athletes0003/0004, assets0003, professionals0006/0007/0008.
  Submitted evidence-set guards check both existing and destination parent state
  under locks; submitted targets cannot reopen as drafts; baseline deletion is
  denied to ordinary SQL. No retention bypass added. New bounds preserve valid
  partial-draft/unknown values; assistant metadata remains inert and non-self.
- Reconciled the corresponding preserved local candidate constraints against the
  approved ranges without overwriting the original unpublished files. Remaining
  candidate differences still require schema review; no blanket equivalence claim.
- Removed all eight C03 migration Ruff exclusions introduced by earlier remote
  work. Actual lint exposed 201 findings; formatter/import ordering and SQL
  whitespace wrapping fixed them. Normalized AST/SQL-token comparison verified
  unchanged semantics for all eight previously existing migration files. No old
  accounts/C02 migration changed. Current Ruff/format: 267 files pass.
- SQL-selection regression first failed on omitted athletes0003; cumulative
  entry point now emits every installed C03 migration and checks all new domain
  and asset modules with mypy. Inherited workflow and scripts remain intact.
- Task 1 remains STARTED/PENDING_CI. No Task 2 implementation or completion claim.


## Task 1 metadata and source-binding review (2026-10-08)

- Protected main, foundation/c01-cloud, accounts/c02-cloud and profiles/c03-plan
  rechecked; all match authoritative SHAs. Original checkout/unpublished files
  remain preserved. Recovery checkout remains on profiles/c03-cloud.
- Prior hardening checkpoint local 5264c52 -> remote
  01d400d8edb0ed87d5f5880927e52d5723d27941; exact tree
  0b0f97023ddef1ae8e6291c2d99a15f81a2fb6f7. Run 37654985277 SUCCESS, actual
  logs 112907704235 and 112907704483 inspected: 269 inherited PostgreSQL
  cases, real Redis quota restart/readiness, 70 C03 cases, 310 current units,
  exact immutable C01 70 units/90 backend/full restart and viewport gates,
  populated same-database C01 upgrade, 645 current backend cases, all 38 C02
  browser cases, durable broker restart, 5 transport/1 storage recovery and
  final two viewport cases. No selected skip. This is not Task 1 COMPLETE.
- Local 59be325 -> remote faeddf1f00f05b1730c7c71952811a69e9bbbf39; exact
  tree 3e6dfe9d5cb58771e5ca99e1ff9c41398a58b6b4. Run 37655283516, job
  112908714722 actual RED: 9 failed/70 passed, all expected DID NOT RAISE.
  Missing decision hash/revision equality, bounded hashes/reasons and exact
  target/forward-history guards. All 269 inherited service cases passed.
- The last interrupted remote operation did not advance the ref. After verifying
  that fact, synchronized local 328702715e3335d3a84d25b353c81970446179f9 ->
  GitHub 641de2e429d2fba9f2979caf18c0fedf9830d219, parent faeddf1, force=false,
  exact tree 10417cb3d65e1bd52d661cc8d97d05f7227d70f5. Run 37693067389, job
  113037821328 actual RED: 33 failed/70 passed, comprising the prior nine and
  24 new receipt/typed-JSON/restriction defects. All 269 inherited cases and
  actual Redis restart/readiness passed.
- Local c7a1250e4bb80f32b5883656a3e06634f8c78133 -> GitHub
  c03ea673563678ca91b229e4daa7748c19ba0da5, actual parent 641de2e, force=false;
  exact tree cf2ddfe6f50589d28d657a74fdf9652b9e7a3ad4. Adds 11 source-binding
  and history-case regressions. Run 37693438514/job 113039051154 actual RED: 44 failed/70 passed;
  all 11 new failures are expected DID NOT RAISE. All 269 inherited cases
  and real Redis readiness/restart passed.
- Ruling: finite receipt commands use domain-local names matching the approved
  command inventory; future commands must extend these explicit enums in an
  additive migration. No arbitrary/private command string is permitted.
- Ruling: JSON schema v1 is enforced by closed domain-specific PostgreSQL
  CHECK functions (native SQL, not portable ORM field validation). Draft empty
  selections remain valid; submission completeness is Task 3/6. Approximate
  records accept only five exact keys, bounded decimal/unit/UTC/self-report
  values; no arbitrary C09 JSON. Costs: schema evolution requires a migration.
- Added professionals0009/0010 for scalar/history guards and locked exact target
  binding, athletes0005/professionals0011 for receipt/restriction constraints,
  athletes0006/professionals0012 for bounded JSON. Cumulative SQL selection
  includes each addition. Models and old migrations/accounts are preserved.
- Local nine-guard correction: all 310 units passed (9.63s), mypy 39 source
  files and Django check passed. Local server absence is not PostgreSQL evidence.
- Task 1 remains STARTED; required hosted GREEN pending. Tasks 2–14 PENDING.

- Added assets0004/professionals0013: accepted-source metadata remains immutable,
  credential profile/role/category identify a permanent evidence object, source
  owner/purpose/subject/checksum are checked under row locks on revision insert,
  and every target-specific history row binds its actual case. Lifecycle state,
  revocation and version changes remain available; no source replacement bypass.
- Added positive bounded-JSON regression for Persian specialties, language tags,
  UTC self-reported approximate measures and partial drafts with unknown values.
- Local checks: 310 units passed (9.82s), full Ruff/format 273 files, mypy 43
  files, production/Django checks, migration state no drift and diff/shell checks
  passed. PostgreSQL history unavailable locally, explicitly pending hosted gate.
