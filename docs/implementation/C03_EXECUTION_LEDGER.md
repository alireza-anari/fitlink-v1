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

Task 1: COMPLETE — exact implementation head 63edc7c; Actions 37698722147 GREEN.
Task 2: STARTED — policy behavioral RED; hosted owner/race test checkpoint pending.
Tasks 3–14: PENDING — not started.
C03 overall remains IN_PROGRESS; no C03 PASS claim.

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


## Task 1 final schema metadata closure

- Remote sync: local fcb58c4f623e0e7c8fb9d8aa00e265c85e640810 -> GitHub
  aecd669f569ea7d71330c122cccd1e59bda50499, parent c03ea673, force=false,
  exact tree bc48c116fec52b151f59a53881635b3549365e1d. API tree equality caught
  an executable-mode mismatch before any ref update; corrected mode to 100755
  and verified exact equality. No mismatched tree was published.
- Run 37694064318/job 113041164878 SUCCESS: actual logs inspected; 269 inherited
  PostgreSQL cases, real Redis quota restart/readiness, all 115 C03 cases,
  complete installed migration SQL, no drift and mypy passed.
- Foundation job 113041164466 FAILED during immutable C01 MinIO initialization,
  before immutable C01 backend tests. All 310 current and 70 original C01
  units/quality/build gates passed. Sanitized initializer provided no diagnostic
  text. This is not behavioral RED or full regression PASS; keep inherited gate
  intact and obtain required full success at the next corrected implementation
  head. Previous full successful immutable rehearsal remains 37654985277.
- Final field-contract review found missing creation/update stamps from §4 and
  missing derivative bounds/lease/lifecycle NULL checks. Unit timestamp test
  first failed locally: 1 failed/8 passed, missing required date fields.
- Remote sync: local f515ad77d144a17210ebc6076b4871bf91de5297 -> GitHub
  81cfcef91a0e589dd0419bd79e693129e0f0ba81, parent aecd669, force=false; exact
  tree a263cf44090584201848b2d915b68ad4d0685aee. Run 37694710083: unit job
  113043470508 observed 1 failed/310 passed on timestamp contract. PostgreSQL
  job 113043470779 observed 13 failed/115 passed; all newly added failures
  are missing timestamps or expected DID NOT RAISE constraints. All 269
  inherited service cases and actual Redis restart/readiness passed.
- Additive assets0005/athletes0007/professionals0014 add non-NULL timestamps;
  immutable rows preserve their first timestamps and existing mutation guards.
  Mutable records use automatic update stamps. Assets0006/athletes0008/
  professionals0015 exclude only this lifecycle stamp from snapshot comparisons;
  existing snapshot/source fields and target-set/reopening guards are retained.
- Assets0007 enforces derivative dimensions 1..1600 and SHA256, a real running
  attempt lease, and accepted/finalized/hash/size metadata for ready assets.
  Professionals0016 enforces revoked-assistant and decided-bundle timestamps.
  These schema fields confer no upload/read/staff authority. Tasks 4/5 still
  own actual safe processing and READY release with fresh fencing.
- Every new migration is explicitly included in cumulative SQL evidence. No
  dependency, old accounts/C02 migration, protected source/ref or route changed.
- Local timestamp correction: 311 full units passed (10.30s); Ruff/format,
  mypy 51 source files, Django and production checks, no migration state drift,
  shell syntax and diff checks passed. Final lifecycle checks below are pending
  exact-head hosted GREEN; Task 1 remains STARTED and Tasks 2–14 PENDING.


## Task 1 final implementation and populated upgrade assertion

- Remote sync: local fc66c4542649e6f03105778e70e89066100e2c84 -> GitHub
  d7becd521c48dd2a9c8829717bdc3cf44a9bd128, parent 81cfcef, force=false; exact
  tree a4aca137dd6452632fec0f3d913c4f6b37e5836b. Protected refs rechecked unchanged.
- Run 37695330008/job 113045539772 SUCCESS: actual logs inspected; all 128
  installed C03 cases, 269 inherited PostgreSQL cases, real Redis restart/readiness,
  all installed migration SQL, no drift and mypy 53 source files pass.
  Foundation job 113045540212 still running; no full PASS claim.
- Local final implementation: 311 full units (10.32s), Ruff/format 283 files,
  mypy 53 files, Django/production checks, no model-state drift, shell/diff checks
  pass. Final source checkout is clean before the following test-only review fix.
- Review finding: original optional-profile test merely reapplied latest migrations
  around a user; that is not the required populated-C02-to-C03 proof. Strengthened
  it to remove C03 tables in the isolated test DB, use the actual C02 historical
  User schema to populate identity/password/auth-version metadata, then apply all
  C03 migrations and assert preserved user fields and zero optional profiles.
  Finally always restores the latest graph. This changes only the migration test,
  with no production/schema change. The exact original C02 runtime/full rehearsal
  remains separately mandatory in Task 14 and is not claimed by this historical
  model test. Required hosted validation of the strengthened test is PENDING_CI.
- Task 1 remains STARTED; no advance to Task 2 before complete hosted gates.

## Task 1 complete regression evidence and ownership-anchor review

- Source run 37695330008 on d7becd521c48dd2a9c8829717bdc3cf44a9bd128:
  both jobs SUCCESS. Foundation 113045540212 logs inspected: exact immutable
  C01 source and populated same-database upgrade, 703 current backend cases,
  38 C02 browser cases, ASGI/viewport smoke and actual transport/storage/broker
  restart probes all pass. This resolves the earlier transient MinIO failure.
- Test checkpoint local 3a190106dfd6c3c0a104a12500373094ae594e4b -> remote
  d3561a7c153d64190ccdfc2fba8cd80a5a120f71, exact tree
  a2ae67165c26cde1922da16de3c89ce928428aec, parent d7becd5, force=false.
  Run 37695980919 both jobs SUCCESS. PostgreSQL 113047689710 logs: all 128
  installed C03 cases including populated historical C02 upgrade, 269 inherited
  cases, actual Redis restart/readiness, migration SQL/no drift/mypy pass.
  Foundation 113047689562 logs: exact C01 upgrade, 703 current backend,
  38 C02 browser, ASGI/viewport and actual restart probes pass. No selected skip.
- Final FK review: child-side evidence binding guards are bypassable by changing
  their parent role/profile identity directly. Baseline correction parent also
  lacked same-athlete enforcement. These are intrinsic ownership anchors under
  approved section 4, not new service scope. Added six adversarial tests for
  permanent profile owner, role profile/kind, baseline athlete and same-athlete
  correction parent. Required behavioral PostgreSQL RED is pending; production
  guards unchanged in this test checkpoint. No task advance yet.

## Task 1 ownership-anchor behavioral RED and correction

- Test sync: local add33f5 -> remote 166cb88135d372bdad6d1bdb116dc85c47fdfcc5,
  parent d3561a7, exact tree f790a50fb35c3df7e96518bffa4bc6381872c4ce,
  force=false. Run 37698230699 PostgreSQL job 113055125704 actual logs inspected:
  six expected DID NOT RAISE DatabaseError failures, 128 installed C03 passes;
  all 269 inherited PostgreSQL cases and real Redis restart/readiness passed.
  Each fixture reached its intended violation, no collection/fixture failure.
- Additive athletes0009/professionals0017 prevent changing permanent profile
  owners, role profile/kind and baseline athlete. Corrections lock and require
  a parent of the same athlete. Existing lifecycle/state/version changes remain
  available. Added positive owned-correction and role-deactivation regression.
  Cumulative entry point explicitly inspects both new SQL migrations.
- Focused review: child evidence pointers now retain their original parent
  authority identity across bulk/direct SQL. No User/accounts migration, route,
  public field, authorization bypass, or new domain behavior introduced.
- Local verification: 311 units passed (10.61s), Ruff/format 285 files,
  mypy 55 files, Django/production checks, no model-state drift, shell syntax and
  diff checks pass. Local PostgreSQL unavailable; exact-head hosted GREEN remains
  mandatory. Task 1 STARTED/PENDING_CI; Tasks 2–14 PENDING.

## Recovery inspection and Task 1 completion (2026-10-08)

- Recovery was read-only first: both checkout statuses, HEAD/tree/logs, all
  staged/unstaged diffs and untracked paths, canonical ledger, remote execution
  ref and run 37698722147 inspected before any change. Original checkout remains
  at 5f399ec with all 17 unpublished files; preserved candidate copy also remains.
  No reset, clean, stash, rematerialization or overwrite occurred.
- Recovery checkout local 5ee402fd66e21f49a28d19b722ca10d1c8bd18ec maps to remote
  63edc7c0bd641fea0da3e3ddbd9d4bc6cd06853e; both exact trees equal
  bad6dce76654a836cbd58b524b1fdee65868e6cd. No unpublished newer work in this
  checkout. All four protected refs rechecked and unchanged.
- Run https://github.com/alireza-anari/fitlink-v1/actions/runs/37698722147:
  both jobs completed SUCCESS on exactly 63edc7c. Actual complete logs inspected,
  not inferred from the previous pending checkpoint.
- PostgreSQL job 113056735108: all 269 inherited service tests; real Redis
  durable quota prepare/restart/PING/verify; actual PostgreSQL/Redis readiness;
  every installed additive migration SQL; no model-state drift; mypy 55 files;
  all 135 selected C03 CI/schema/constraint/evidence cases including populated
  historical C02 upgrade and final ownership guards. Exit 0, no selected skips.
- Foundation job 113056735314: 311 current units, Ruff/format 285 files, mypy
  88 files, frozen dependencies/static/Django/production checks; exact immutable
  C01 source verification, original 70 units/90 backend cases and all original
  viewport/transport/storage restarts; populated exact C01 same-database
  prepare/verify; 710 current backend cases; two ASGI smoke and 38 C02 browser
  cases; durable outbox broker restart and final 5 transport/1 storage/2 viewport
  cases. Every required step exit 0, no selected skips.
- Recovery executor restored Python 3.13.15 with unchanged frozen locks and
  npm ci. Fresh local 311-unit run (11.99s), full Ruff/format, mypy 55 files,
  Django/production checks and diff checks pass. No local PostgreSQL is available;
  actual hosted evidence above is the required Task 1 service completion gate.
- Task 1 checklist reviewed: CI bootstrap and behavioral RED checkpoints,
  additive optional/unique schemas, matching evidence/revocation/target bindings,
  NULL/metadata/immutability/runtime-role guards, historical populated upgrade,
  original regressions and no drift are all covered by recorded actual runs.
  Reviewed migration splitting/names differ from proposed filenames but preserve
  the approved additive schema and no User/accounts/original migration changes.
- Task 1: complete (validated source 63edc7c, tree bad6dce; cumulative hosted
  docker/verify_c03_incremental.sh and inherited full rehearsal → SUCCESS).
  This completion document does not replace implementation-head evidence.
  Task 2 is next; no merge, deployment, C04 or future-domain work.

## Task 2 start and test specification

- Task brief read from the approved plan; local BASE 6fbbe3f, remote BASE
  90e406fea89636822be46f0a6a99194abf07add2; shared tree 91567cb.
- Four actual behavioral policy failures: valid active declared adults are
  denied athlete/professional profile read/write by the current finite account
  action gate. Local policy RED: 4 failed/13 passed (0.08s). No import or fixture
  failure is counted as behavioral RED.
- Added named optional dual profile, own-selector/foreign UUID, current actor,
  receipt authorization/conflict/current DTO, registration false/outage,
  synchronous audit/outbox rollback and bounded metadata dispatch specifications.
  Added independent PostgreSQL create/create, same-key, and both orders of
  create versus logout/restriction/suspension/pending-deletion specifications.
  New service contracts are asserted inside tests, never imported at collection.
- Cumulative hosted script includes all three Task 2 test modules and retains
  Task 1 and every inherited command. New CI selection contract requires these
  owner/race gates. Workflow, old migrations, immutable fixture and old suites
  unchanged. Hosted test execution is pending; no Task 2 implementation yet.
- Task 2: Ruling: same-transaction outbox applies to professional creation via
  approved professional.profile_changed. The approved inventory has no athlete
  profile-created event; athlete creation records audit plus receipt, and Task 3
  emits athlete.baseline_changed only after a baseline exists. Do not fabricate
  a baseline/event or extend the approved inventory. Cost if wrong: a separately
  approved metadata event would require additive governance schema changes.

- Test-spec sync local 169a76d -> remote fa636833df15fbbec1ed9f6d19dd121fcabc3df7,
  exact tree 67bd30c20f3a49b285dacfdefb97a701d7ed5489, parent 90e406f,
  force=false. Run 37721913275 actual job logs inspected.
- Foundation 113131260699: quality/collection checks pass; the four expected
  profile-action behavioral failures and 325 unit passes. No product regression
  success is claimed for later steps skipped after this intentional RED.
- PostgreSQL 113131260865: all 269 inherited cases, actual Redis restart and
  PostgreSQL/Redis readiness, and all 136 Task 1/CI cases pass. Task 2 yields
  65 failures/13 passes: four genuine existing-policy denials plus 61 explicit
  missing-command/selector/policy contracts. The latter are specification
  failures, not executed create/race/denial behavior; do not mislabel them as
  PostgreSQL race RED. All fixtures collect and execute without fixture errors.
  Implementation will first establish the missing command boundary, then verify
  its PostgreSQL behavior before claiming Task 2 completion.

## Task 2 minimal owned command boundary

- Extended only four finite athlete/professional profile read/write action names;
  all existing action behavior remains unchanged. Owner selectors revalidate the
  current actor under User lock, then exact profile ownership, and return typed
  private DTOs. Foreign/missing/archived UUIDs use the same unavailable result.
- Explicit creation uses current locked_actor, derived owner and synchronous
  metadata audit; professional creation also checks the fresh locked registration
  switch and emits only approved professional.profile_changed metadata. Registered
  its bounded current owner/version metadata handler; no routes, roles, baseline,
  public copies or external effects. No migration changes.
- This minimal boundary deliberately does not yet implement retry receipts or
  duplicate-create recovery. Hosted tests must exercise those actual behaviors
  before their correction; this checkpoint is not Task 2 GREEN/COMPLETE.
- Local policy/whole unit GREEN: 329 passed (10.63s). Ruff/format 300 files,
  mypy 52 files, Django and diff checks pass. Mypy initially caught record lambdas
  returning the audit UUID where OutcomeRecorder requires None; explicit typed
  record callbacks fixed that boundary without suppressing the check.
- Task 2 STARTED/PENDING_BEHAVIORAL_CI; Tasks 3–14 remain PENDING.
