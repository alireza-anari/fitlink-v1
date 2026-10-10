# C03 execution ledger — plan: docs/superpowers/plans/2026-10-06-c03-profiles-verification.md

## Authority and immutable baselines

- Original user authorization: execute C03 Tasks 1–14 sequentially. Latest
  authorization is Task 4 ONLY, then STOP; Tasks 1–3 remain COMPLETE. No Task 5,
  C04, merge, deployment or protected-ref mutation.
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
Task 2: COMPLETE — exact source d619d7e; Actions 37723166576 both jobs GREEN.
Task 3: COMPLETE — exact source f58ba8af713c8105611e383d844281c6df77171f; Actions 37735571394 both required jobs GREEN; actual complete logs inspected.
Task 4: IN_PROGRESS — preserved-checkpoint preflight complete; behavioral RED and real MinIO gates pending.
Tasks 5–14: PENDING — not started.
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

## Task 2 PostgreSQL behavioral checkpoint and receipt correction

- Minimal-boundary sync local 550ff9ac00d94fa5a164468ceb430d673c7edd2c ->
  remote 1c92d8bdfecaad4dfd1402ea430bffd9a88f4146, exact tree
  df41c6183971aff11a80667969038b73df6e7c3e; parent fa63683, force=false.
- Run 37722467130 PostgreSQL job 113133046549 actual logs inspected: 269
  inherited cases, real Redis quota restart and PostgreSQL/Redis readiness,
  all 136 Task 1/CI cases pass. Actual Task 2 command execution: 16 failed/62
  passed (17.77s). Fourteen are behavioral RED: duplicate SQL failures on
  create/replay/concurrent same/different operations, archived retry errors,
  and the registration switch wrongly blocking an existing owned retry.
- Two failures are test-fixture defects, not behavioral RED: expires_at equal
  to created_at violates the retained C02 session_expiry CHECK before the
  command. Corrected only the synthetic test time to created_at+1 second and
  call at that valid expiry boundary. The C02 constraint is unchanged.
- All 32 independent-connection create-versus-logout/restriction/suspension/
  pending-deletion cases pass in both committed orders on the minimal boundary;
  current owner/foreign UUID/state/rollback/metadata tests execute real services.
- Correction serializes User, current owned profile and owner-scoped receipt;
  checks command plus normalized input hash, binds the result UUID, and rebuilds
  a safe current DTO. New keys return the existing profile with their own receipt;
  same keys reuse one receipt. Only first creation audits/emits a created effect.
  Archived/missing/foreign results remain unavailable; current authorization
  precedes receipt conflicts. Registration is checked only for a new professional
  row, with the existing locked authoritative switch, never for owner setup.
- Focused security review: dual domains stay independent; no actor/owner supplied
  by payload, no profile/role/staff/flag permission bypass; immutable account
  actions outside the four finite additions retain prior behavior. No migration,
  dependency, route, baseline/role seed, public projection or future-domain change.
- Local corrected source: 329 units (10.62s), Ruff/format 300 files, full inherited
  mypy plus profile modules 140 files, Django/production and diff checks pass.
  Real corrected-head PostgreSQL and complete inherited rehearsal remain pending;
  Task 2 is not COMPLETE and Task 3 has not started.

## Task 2 complete head-bound regression evidence

- Correction sync local 2f8392b47efb24bf8fb21afd9327552555d5328d -> remote
  d619d7ee7e495e377157e4e1f99e111f103caeca; exact tree
  d7f4270f71a698e7940c5f205db9b335a9b8f793; parent 1c92d8b, force=false.
  Original checkout and all 17 unpublished files remain unchanged; recovery
  checkout clean after synchronization.
- Run https://github.com/alireza-anari/fitlink-v1/actions/runs/37723166576:
  completed SUCCESS on exactly d619d7e; both complete job logs inspected.
- PostgreSQL job 113135238455: 269 inherited cases; real Redis durable quota
  restart/readiness; actual PostgreSQL SELECT/Redis PING; full additive SQL/no
  migration-state drift/mypy 63 files; 136 Task 1/CI cases (23.76s) and all 78
  Task 2 cases (11.87s). Duplicate/same-key creation, current owner denial,
  receipt/current DTO/archival/flag/rollback and all 32 state/logout serialization
  cases pass. Corrected valid expiry fixtures reach actual permission denial.
- Foundation job 113135238351: 329 current units, full quality/frozen/static/
  production checks; exact immutable C01 source and original 70 units/90 backend
  with viewport/transport/storage restart checks; populated exact C01 same-DB
  upgrade prepare/verify; 789 current backend cases (254.35s), two ASGI smoke and
  all 38 C02 browser cases (262.26s); durable outbox broker restart; final five
  transport/one storage/two viewport cases. All required steps exit 0; no selected
  skips. This is current-source evidence, not the deferred exact C02 upgrade.
- Task 2 checklist/security/migration review complete; no unresolved required
  gate. Task 2: complete (source d619d7e, tree d7f4270; focused real-service command,
  cumulative gate and whole inherited rehearsal → PASS). Task 3 is next; Tasks
  3–14 remain unimplemented. No overall C03 PASS, C04, merge or deployment.

## Task 3 started — baseline and self-storage contracts

- Task 2 completion checkpoint local b7bb97a preserves verified source d619d7e.
  Task 3 starts from that clean preserved workspace; no Task 1/2 restart.
- Added specification tests for bounded field/unknown-input exclusion, resumable
  drafts, optimistic receipt/current DTO, optional decline, immutable corrections,
  self-grantee consent/common callback checks, current revoke/expiry filtering,
  audit rollback and independent-connection save/submit/revoke/begin races.
- Test-spec CI selection extends only the cumulative installed gate. Missing APIs
  assert within collected tests; absent contracts are not mislabeled real SQL or
  race behavioral RED. Existing profile SQL permits arbitrary onboarding_step;
  a direct-SQL regression now captures that concrete installed-interface gap.
- Task 3 STARTED/PENDING_RED; Tasks 4–14 PENDING. No later work begun.

## Task 3 test-spec RED and initial command boundary

- Test-spec local f78f51a -> remote 9424a32173c6d8be7dc60730f9c2d0ee2430510e;
  exact tree d1124179622fa5404327f12332e53537830502c5, parent d619d7e, force=false.
- Run 37725704752 actual complete job logs inspected: foundation 113143249624
  has 50 missing field/callback failures and 330 inherited units pass. PostgreSQL
  113143249492 has 269 inherited, real Redis restart/readiness, 137 Task 1/CI and
  78 Task 2 cases pass. Task 3: 76 failures, comprising 75 explicit missing APIs
  and one real behavioral SQL RED: health_upload persisted as onboarding_step
  instead of raising IntegrityError. Missing interfaces are not race RED.
- Field/callback boundary now passes all 50 local cases. Established commands
  lock User, owned profile, draft/snapshot and receipt; current self-storage is
  supplied through composition and rechecked at every projection/mutation.
  Submitted clear is refused in favor of immutable correction; draft clear
  requires no consent. Server duration has no invented production default;
  fixtures explicitly select 60 seconds. Fixed engineering disclosure descriptor
  remains subject to the existing approved-wording release dependency.
- Before expanding SQL receipt commands or repairing the step CHECK, exercise
  this command boundary against actual PostgreSQL. No Task 3 GREEN claimed.

## Task 3 behavioral checkpoint and executor disconnection

- Boundary local f8f97a8d149617f4b974832e1e3accf211ffe761 -> remote
  35d8f24e9cf058982759f447453dfeb16ca303b8; exact tree
  0cac0d4b3bb3664b00571d7ac8f2ec520fd440aa; parent 9424a32, force=false.
  Local boundary quality: 380 units (10.83s), Ruff/format 311 files,
  mypy 27 relevant files and diff check pass. Local migration-state check reports
  no model changes; local PostgreSQL unavailable, hosted service is authoritative.
- Run https://github.com/alireza-anari/fitlink-v1/actions/runs/37726128979
  is source-bound to exactly 35d8f24. PostgreSQL job 113144593985 completed
  FAILURE; its complete actual log was inspected. 269 inherited cases (74.22s),
  real Redis durable restart and PostgreSQL/Redis readiness, 137 Task 1/CI cases
  (28.12s) and all 78 Task 2 cases (13.60s) pass.
- Task 3 actual command execution: 9 failed / 67 passed (10.46s). Eight failures
  are real SQL receipt CHECK denials for baseline.grant_storage, preventing
  optional/correction/revoke cases from reaching later behavior. One is the
  reproduced missing onboarding-step CHECK. Resume, required-only decline/
  submission, optimistic save/replay, cross-owner denials, audit rollback,
  save-versus-submit and duplicate begin execute and pass. Do not label blocked
  consent/revoke/correction cases GREEN. Foundation job 113144593715 was still
  in the full inherited rehearsal at the last inspection; no completion claim.
- Required next repair: a minimal additive Task 3 migration for finite wizard
  steps and the two grant/revoke receipt command values, preserving all old
  accepted values. This repairs the demonstrated installed-interface gap in
  Task 3, not a Task 1 restart or a rewrite of existing migrations. Its SQL,
  no-drift and corrected-head full regression gates remain mandatory.
- Later unpublished local changes remain in the active recovery checkout:
  apps/athletes/baseline.py (owner-serialized receipt read and consent ordering),
  apps/athletes/validation.py (Decimal(8,2) upper boundary correction),
  config/use_cases/c03_privacy.py (locked current consent rows),
  tests/integration/c03/test_baseline_races.py (both committed save/revoke orders),
  tests/unit/c03/test_baseline_fields.py (upper boundary regression).
  The added decimal boundary first failed on the actual validator, then all
  51 field/callback units passed after correction. These local changes are not
  remotely synchronized or fully verified. Preserve and inspect them on resume.
- The executor transport disconnected during a subsequent read-only inspection:
  "exec-server transport disconnected; failed to resume exec-server session:
  recovery timed out after 25s". Read-only pwd/status retries stalled and were
  stopped; no reset, cleanup, stash, discard, checkout-over or replacement was
  attempted. Final local status could not be re-read after that disconnection.
- This remote documentation-only forward checkpoint records the blocker because
  local file execution is unavailable. Source files remain exactly those of
  35d8f24. On recovery, compare this remote ledger delta with local HEAD f8f97a8
  and its five known unpublished edits; reconcile the ledger without overwriting
  those edits. .superpowers/task3-sync.json still describes the source checkpoint.
  Original fitlink-v1 checkout and its 17 unpublished files were never changed.
- Protected refs were re-read and remain exactly the immutable heads recorded
  above. Task 3 BLOCKED_EXECUTOR / REQUIRED_CORRECTIONS_PENDING, not COMPLETE;
  Tasks 4–14 PENDING. No overall C03 PASS, C04, merge or deployment.

## Task 3 recovery inspection and bounded corrections (2026-10-08)

- Latest user authorization narrows this execution to Task 3 only. Tasks 1 and 2
  remain COMPLETE; no restart. Stop after Task 3 is fully verified and its ledger
  synchronized. Tasks 4–14 remain PENDING; no Task 4, C04, merge or deploy.
- First performed read-only status, HEAD/log, all staged/unstaged diffs, ledger,
  remote execution ref, full source-tree comparison and both requested Actions
  logs. Existing local HEAD f8f97a8/tree 0cac0d4 and remote 636803b/tree bfed96e
  differ in exactly one blob: the recovery ledger. All other 345 blobs/modes match.
  No staged changes. Four unpublished modified files remain: baseline.py,
  c03_privacy.py and baseline_races/baseline_fields tests. All are preserved.
  Original checkout remains at 5f399ec/tree 6af62b2 with all 17 unpublished files.
- Reconciled only the existing remote ledger delta in a local forward docs commit
  9589a736c71bb963f73237238883367877f0ac71. Its exact tree is bfed96e, matching
  636803b. Other unpublished files were neither staged nor changed by reconciliation.
- Read actual complete logs for preceding run 37726128979 (jobs 113144593715/
  113144593985) and current checkpoint run 37726731278 (jobs 113146490210/
  113146490439). Both source-equivalent runs reproduce the same nine failures:
  eight legitimate grant command receipt inserts hit athletes_receipt_command;
  one direct SQL health_upload step is wrongly allowed. Both foundation jobs
  reached 9 failed/857 passed backend cases after original C01 and populated
  same-DB upgrade; later browser/restart gates were skipped by this RED, not PASS.
  Both PostgreSQL jobs pass 269 inherited, real durable Redis restart/readiness,
  137 Task 1/CI and 78 Task 2 cases, then Task 3 9 failed/67 passed.
- The prior remote note records a decimal fix that did not persist through executor
  loss: validation.py is unchanged at its original integer upper bound. Its newer
  test did persist. Re-ran it: actual RED rejects 999999.99; restored the exact
  Decimal(8,2) bound already enforced by installed SQL. 51 field/callback units
  then pass. Recovered all four actual unpublished files, not a presumed fifth.
- Ruling: add athletes0010 for the exact installed Task 3 gaps — bound wizard
  steps to the approved nine-step vocabulary and add baseline.grant_storage/
  baseline.revoke_storage to the existing receipt CHECK. All six prior accepted
  receipt commands remain; no User/accounts/original migration rewrite or data
  backfill. This is the smallest repair of Task 3's advertised interfaces, despite
  its planned migration-impact-none assumption. Cost if wrong: rollback must
  disable this feature/roll forward rather than orphan newly accepted receipts.
- Preserved owner-serialized receipt reads and locked current-consent rows.
  Current consent anchors are now acquired before receipt/effect writes; current
  authorization and exact ownership still precede receipt interpretation.
- Security review found shared optional-default list aliasing in project(): a
  caller's local result mutation appeared in a later denied-consent result.
  A real projection regression failed with that leaked list. Copy projected
  values before returning; no new data fields, authority, or sharing surface.
- Cumulative CI adds only sqlmigrate athletes0010; all installed Task 3 tests,
  inherited workflow/blob contract, old service gates and scripts remain mandatory.
  Local and corrected-head hosted completion gates are pending.

- Reviewed the newly reachable frozen-snapshot assertion against the installed
  SQL guard and inherited evidence test: immutable UPDATE raises PostgreSQL
  42501/InsufficientPrivilege (ProgrammingError), not CHECK-class IntegrityError.
  Corrected only that Task 3 assertion to require ProgrammingError plus exact
  SQLSTATE 42501; retained the real SQL UPDATE and snapshot immutability. This
  test correction is not a product failure and weakens no database guard.
- Local corrected work: full 382-unit suite (10.02s); Ruff/format 312 files;
  inherited exact mypy command 91 files plus all three domain trees 68 files;
  Django test/production, frozen lock, JS syntax, shell syntax and diff checks
  pass. Local no-drift model comparison reports no changes; real database
  history/SQL remain hosted gates. Initial generated-migration formatting and
  a duplicated mypy argv target were command/format issues, fixed without
  exemptions or suppressions. Corrected-head PostgreSQL and full rehearsal
  remain PENDING; Task 3 is not COMPLETE.

## Task 3 sensitive read audit review gate

- Self-review against approved plan section 14 (reads audited, no outbox) and
  DOMAIN_MODEL AthleteProfile sensitive-access audit found own_baseline currently
  returns optional sensitive values without synchronous audit. Add two actual
  PostgreSQL regressions: metadata-only baseline.read with no outbox, and audit
  failure preventing any private result. Current actor/consent/ownership remain
  real; no mocked authorization or collection error substitutes for RED.
- This is a Task 3 completion gap, not new scope or later privacy infrastructure.
  The nine existing fixes remain in exact corrected source 519f33e/tree 80fe9b5,
  run 37734616101. Its completion does not waive this additional review gate.
  Task 3 is still IN_PROGRESS; do not close or advance.

## Task 3 read-audit behavioral RED and correction

- Original-nine correction sync local b101b512f3ac3cdd9eff39462d97f42a20121390
  -> remote 519f33eef437b512198439b7133c18abdce2bb35, exact tree
  80fe9b56306ce045c44c61330deeec1b99233c4f; parent 636803b, force=false.
  Run 37734616101 PostgreSQL job 113171225506 complete SUCCESS; actual full
  log inspected: 269 inherited (83.90s), real Redis restart/readiness, exact
  athletes0010 SQL preserving six old commands and admitting only two new ones,
  bounded step CHECK, no drift/mypy 68, 137 Task 1/CI (32.32s), 78 Task 2
  (16.35s) and all 80 Task 3 cases (12.25s). Original nine failures resolved.
- Audit-spec local 847072a -> remote 71ee9492ed1b2c93a1cbc2b6240f3713f2d326a0,
  exact tree 69052ea490d115d00f17de77dfcab946061a72c9; parent 519f33e,
  force=false. Run 37735002926 PostgreSQL job 113172428650 actual complete
  log inspected: 269 inherited, real restart/readiness, 137 Task 1/CI, 78 Task 2
  pass; Task 3 2 failed/80 passed. Actual RED: successful private read writes
  zero audit rows; audit outage returns a private result (DID NOT RAISE).
  These are behavior failures, not missing APIs, fixtures or collection errors.
- Ruling: add only baseline.read to the finite governance audit allowlist using
  additive governance0014; owner selector accepts the composition recorder and
  writes metadata synchronously under its existing account/profile/baseline/
  consent locks before returning. No outbox for reads and no private answer in
  audit. This satisfies the approved read-audit privacy invariant, not a new
  audit framework. Cost if wrong: narrowing rollback must retain accepted read
  history; use feature disable/roll-forward, never delete audit history.
- Preserved original 17 unpublished files byte-for-byte verified against the
  recovery backup (zero missing or changed files). No original checkout changes.
- Additional read correction and exact-head full hosted gates pending; Task 3
  remains IN_PROGRESS. Tasks 4–14 unstarted; stop is still Task 3 completion.

## Task 3 COMPLETE — exact-source GREEN and stop checkpoint (2026-10-08)

- Final implementation local head ecf9044bf6d75ccae54615ef8be6684825621f92
  maps to published f58ba8af713c8105611e383d844281c6df77171f, with identical
  exact tree dc3c0b03fa95e297e67f962df24f3eef8ff88b68. Published parent is
  71ee9492ed1b2c93a1cbc2b6240f3713f2d326a0; expected-head lease, force=false.
- [Actions 37735571394](https://github.com/alireza-anari/fitlink-v1/actions/runs/37735571394)
  is completed SUCCESS on exactly that implementation head. Both required jobs
  are SUCCESS and their actual complete logs were inspected:
  [PostgreSQL 113174191330](https://github.com/alireza-anari/fitlink-v1/actions/runs/37735571394/job/113174191330)
  and [foundation 113174191575](https://github.com/alireza-anari/fitlink-v1/actions/runs/37735571394/job/113174191575).
- PostgreSQL: 269 inherited cases (83.24s), actual Redis restart and durable
  quota prepare/verify with PONG, real PostgreSQL/Redis readiness, reviewed
  athletes0010/governance0014 SQL, no drift, mypy 68 files, 137 Task 1/CI
  cases (32.53s), 78 Task 2 (16.39s), all 82 Task 3 (13.39s). Exit 0;
  zero failed or selected skipped cases. Original nine behavioral failures and
  both sensitive-read audit regressions are GREEN.
- Full rehearsal: frozen/static checks, Ruff/format 313 files, mypy 92 files,
  Django test/production checks and 382 units (12.66s); exact immutable C01
  tree 4dff1ebd5a32ed0359552bf29012d9d1ecf09b24, original 70 units/90 backend
  and all original service/browser/restart gates; populated exact C01 same-DB
  upgrade prepare/verify; independent clean migration/no drift; 872 current
  backend (278.11s), 2 ASGI (3.01s), 38 C02 browser (264.41s); actual durable
  outbox broker restart prepare/verify; final 5 transport (1.44s), 1 private
  MinIO (1.80s), 2 viewport (3.34s). Healthy PostgreSQL/Redis/MinIO/web/worker/
  beat observed. All required steps exit 0; no failed or selected skipped cases.
- Earlier full logs also inspected: original-nine corrected run 37734616101
  foundation 113171225687 SUCCESS (870 backend plus complete inherited gates);
  read-audit spec run 37735002926 foundation 113172428915 RED, exactly two
  intended audit behavior failures with 870 other backend cases passing. These
  historical results do not substitute for final source run 37735571394.
- Fresh local task-done whole-unit verification: 382 passed in 12.11s, exit 0,
  no skips. Prior final-source local Ruff/format, inherited and domain mypy,
  Django test/production, lock/JS/shell/diff checks remain passing. Local lack
  of PostgreSQL is handled by the named authoritative hosted gates above,
  never by simulated service evidence or skipped tests.
- Final review: current account/owner authority precedes receipt interpretation;
  consent is revalidated under locks; decline/expiry/revoke filters optional
  values; correction preserves submitted history and excludes optional copies;
  unknown health/photo fields remain rejected; metadata-only read audit commits
  before private result release, with no read outbox. Two bounded additive SQL
  corrections retain all prior accepted values. No private fields in audit or
  outbox. Approved production consent duration/wording remains a release-policy
  dependency; absent duration fails closed, with no policy invented here.
- Protected refs verified unchanged at their fixed heads above. Original checkout
  remains preserved, including all 17 unpublished files verified byte-for-byte
  against recovery copies (zero missing or changed). No reset/clean/stash or
  history rewrite; synchronization uses real published ancestry and a lease.
- This completion checkpoint changes only this ledger; it preserves the linked
  validated implementation source. A documentation-only CI run is not substituted
  for required source GREEN. Task 3 COMPLETE. Tasks 1–2 remain COMPLETE; Tasks
  4–14 remain PENDING. STOP after safe ledger sync. No overall C03 PASS, Task 4,
  C04, merge or deployment.

## Task 4 preflight and execution scope (2026-10-08)

- Read-only recovery first: clean local 2d98e3b20244be0270a5d3218eebe85618049823,
  exact tree eae91e0178960d38f1d316359abda6add671d7b5, equal to published
  4843e7a48a91e57ab007a71faf914deb61eaf48d. Preserve intentional local ancestry;
  no reset/rematerialization. All staged/unstaged diffs empty; no Task 4 files,
  brief or partial implementation. Tasks 1–3 COMPLETE in both ledgers.
- Remote is exactly 4843e7a, with parent f58ba8a. Actions 37735571394 on f58ba8a
  and ledger-only 37737724668 on 4843e7a both completed SUCCESS. Original
  checkout remains 5f399ec/tree 6af62b2 with all 17 unpublished files preserved.
  All four protected refs unchanged. Approved plan and Task 4 brief read.
- Task 4 BASE is local 2d98e3b. Only owned professional evidence/branding
  quarantine ingress, private storage and its same-task real MinIO gates.
  No scan/decoder/sanitization/READY or source delivery; Task 5 unstarted.
- Ruling: install only the minimal same-origin authenticated multipart ingress
  adapter in Task 4 because latest explicit user contract requires actual Django
  multipart uploads now; full owner UI/adapters remain Task 11. Whole multipart
  request is capped at 10,000,000 bytes (stricter than plan's overhead allowance).
  Cost if wrong: future adapters must reuse this bounded parser/command boundary.
- Ruling: reuse professional-domain command receipts via trusted composition
  callbacks for upload begin/finalize/abandon, extending only their finite CHECK
  in a named additive migration if needed. Assets never import professionals.
  Existing schema has no asset receipt and no accepted upload receipt commands;
  unsafe retry inference is insufficient. Cost if wrong: narrowing downgrade must
  retain accepted receipts, disable the feature/roll forward rather than erase.
- Ruling: a separate exact-C03-only storage job uses existing private MinIO
  source build, Compose isolation and restricted app credentials. Inherited
  workflow/jobs/timeouts/services remain byte-identical after removing only C03
  extensions. PostgreSQL cumulative Task 4 suites and real storage suites are
  explicit mandatory selections; no unavailable-service skips or fake-only PASS.
- Test specification: actual session-authenticated HTTP begin/body/finalize/
  abandon and UUID/CSRF/authority/privacy assertions, PostgreSQL independent
  connection reservation/finalize/logout/archive/quota races and real MinIO
  conditional-write/HEAD/bounded-read/anonymous read+write-denial cases added.
  Synthetic malformed raster headers prove admission coherence only, not a
  safety decision. No upload implementation, scanner or dependency added yet.
- Local initial RED: 21 failed/15 passed (0.97s): five expected CI-extension
  failures and 16 missing bounded ingress/validation contract assertions. This
  missing-API evidence is not represented as behavioral domain RED. After
  installing the exact-C03-only storage gate, all 20 CI contract cases pass
  (0.81s); inherited workflow blob still exact. New test/script Ruff/format,
  shell syntax and diff checks pass. Hosted actual HTTP/storage behavioral
  failures are the next required gate, not collection or fixture failures.
- Initial test checkpoint local 4afa78d6c7af12d0085d02b02357412ab062145e ->
  published 759f1531c9d1a008818546ec61c5112aec32494c, exact tree
  576abcb70305d19a06d6c2374c11691a0195d96f; parent 4843e7a, force=false.
  Run 37745213821 foundation 113204962404 actual complete log: quality passes,
  16 missing-contract failures/386 passing units. Storage job 113204962375
  builds and starts actual MinIO/PostgreSQL/Redis and migrates, then fails before
  tests: direct script invocation omitted repo root from sys.path. Not domain
  RED or storage PASS. Reproduced exact ModuleNotFoundError locally and fixed
  only the entrypoint path, following existing probe pattern without suppressions.
  Fail-closed subprocess regression plus all 21 CI contracts now pass (1.46s).
- Early ASGI and pre-CSRF request-cap tests added before implementation: two
  missing-cap failures (0.20s). Ruling: cap the actual ASGI body before Django
  spooling and the WSGI body before CSRF multipart parsing; otherwise a custom
  DRF parser alone cannot enforce the user request-size contract. Cost if wrong:
  later adapters must retain the same early scoped ingress boundary. No broad
  body-limit changes to existing C02 routes. Hosted behavioral RED still pending.
- Probe correction checkpoint local 8f0dd48a0f2a042c02c1ef64ac6cd6c4e683d2ce
  -> published 199dfb63c565446e5acbd1370f1cddc6fa4a96f2, tree
  02ffb6ace824e137a5b63dc5dd9683b4bf56f461. Run 37745994600 PostgreSQL
  job 113207499024 times out in cumulative C03; prior 113204961886 likewise.
  Connector returns BlobNotFound for both completed cancelled job logs, so their
  behavioral test results remain unknown. MinIO job is not yet complete. No
  service gate is claimed GREEN or intended behavioral RED from this metadata.
- Independently reproducible real transport RED: existing Django ASGI application
  accepts 10,027,008 actual request bytes into route handling (404) rather than
  enforcing the required 400 cap (one failure, 0.39s). Scoped pre-Django and
  pre-CSRF caps make this and absent/lying-header wrapper cases pass (3/0.20s).
  Bounded conditional-write/read and declaration/admission primitives now pass;
  combined Task 4 units and CI contracts 40 passed/1.76s, no skips. No owner
  lifecycle, finalization, readiness or scanner implementation in this checkpoint.
- C03-only explicit pytest commands now have a 180-second process timeout and
  30-second faulthandler trace with verbose case names to diagnose stalled gates.
  Timeout is a failure, never a pass/skip. Inherited commands/timeouts untouched;
  actual hosted PostgreSQL and private MinIO behavioral evidence still required.
- New diagnostic checkpoint local 587f1d3c79fc6eeefb48966ee93ee5d877ebe99d
  -> published 4f9a4bf3f55a35150acae7af0eca72908f18dbcc, exact tree
  82702e6ec2c420f54b1ad98c17c4167a777a0696; run 37749178799. Foundation
  quality step succeeds, but service jobs still expose no usable logs. Neither
  real-service behavioral RED nor private MinIO PASS has been established.
- Direct actual unauthenticated Django POST admission behavior RED: 404 where
  required 403 (no DB/auth mocks). Core ownership/finalization remains unimplemented
  pending required hosted behavioral evidence. Additional specs reject identical
  foreign object binding, new-operation finalization, changed replay, invalid
  lifecycle states and archived-owner replay.
- Configuration cap assertions RED 4/12 passing (0.11s), then bounded positive
  upper limits implemented for bytes, pending count, daily bytes and admission
  expiry. Test/production inherit the same validated base limits; production
  continues to require real private S3. All 410 local units pass (18.48s), no
  skips; full Ruff/format 324 files, inherited mypy, Django/production checks
  pass. No live service evidence is inferred from these local checks.
- Diagnostic ruling: bound the whole C03 cumulative command (300s) and owning
  storage command (900s), including setup/probes/SQL, and force termination ten
  seconds after timeout. Earlier per-pytest bounds cannot locate a stall before
  pytest or guarantee signal termination. Named phase messages and traceback
  output remain secret-free; timeout is failure, inherited gates untouched. These
  are diagnostics, not a claimed root-cause fix. Required service RED/GREEN and
  actual logs remain blocking completion gates. Task 4 IN_PROGRESS; no Task 5.
- Recovery checkpoint 2026-10-08 08:42 UTC: latest published Task 4 diagnostic
  head 411fc4f6206e07de4b60b6e20cf5d1568c96e63c, tree
  9bb06ddebbc0538797aa7eae58a35db705ff16ba; local committed counterpart
  8675b63cdc358d7b5365da1b7679a0bbac7420d1. Source run 37750691259:
  PostgreSQL 113222883457, private MinIO 113222883688, foundation 113222883770
  remain in_progress per actual API metadata. PostgreSQL cumulative step starts
  08:36:09; no terminal result exposed after the configured 300s/kill grace.
  Earlier diagnostic run 37749178799 PostgreSQL 113217906722 is cancelled.
  Earlier cancelled service logs still return BlobNotFound; no root cause or
  behavioral results inferred. Do not replace this gate with a passing local unit
  assertion or advance to implementation acceptance/Task 5.
- Unpublished valid Task 4 test refinements preserved: suspended-account fixture
  satisfies existing state/is_active CHECK; cross-user body rejected before I/O;
  changed source key during receive and profile archival during finalize races.
  Focused changed-spec Ruff/format and diff checks pass; service execution pending.
- All protected refs rechecked unchanged; original checkout remains 5f399ec/tree
  6af62b2 and all 17 unpublished files match preserved copies byte-for-byte.
  Task 4 remains IN_PROGRESS/PENDING_CI, ownership/finalization core not yet
  implemented; Tasks 1–3 COMPLETE. No Task 5, C04, merge or deployment.
- Recovery/diagnosis-only preflight 2026-10-08 09:11 UTC: status, complete
  staged/unstaged diffs, local history, Task 4 plan and ledger inspected before
  edits. Local 8675b63 tree equals authoritative published 411fc4f/tree 9bb06dd;
  all three unpublished ledger/lifecycle/race refinements above are retained.
  Task 4 partially implemented; Task 5 not started. Tasks 1–3 remain COMPLETE.
- Runs 37749178799 and 37750691259: every job/step inspected and all six actual
  log downloads attempted. PostgreSQL jobs 113217906722/113222883457 and storage
  113217907034/113222883688 are cancelled while their owning step is still
  recorded in_progress; post/cleanup steps pending. Foundation 113217907065
  subsequently cancelled at 09:25:28 with the exact rehearsal still in_progress;
  113222883770 still in_progress at 09:36. Actual logs return BlobNotFound,
  including cancelled jobs retried at 09:36. Last confirmed progress is only the
  enclosing step; last SQL/test/container/cleanup child remains UNKNOWN for each
  boundary. No shared cause, DB deadlock or MinIO failure is inferred.
- Independent actual local ownership experiment: GNU timeout exits 124 while
  a deliberately detached child survives and retains the inherited output pipe;
  communicate() then times out. The newly created child alone was terminated.
  This disproves a general complete-process-tree guarantee of the existing
  wrapper, but does NOT establish that this mechanism caused the hosted hangs.
  Local Docker and /proc are unavailable; hosted ownership evidence is required.
- Diagnostic ruling: passively observe the unchanged three real-service commands
  on the exact execution ref. Sanitized tagged PID/PPID/PGID/session/wait/stdin
  observations, finite Compose state/container children, query-free PostgreSQL
  activity/blocker facts, MinIO readiness and disk availability emit flushed
  JSONL, with a pinned exact-ref always() diagnostic artifact step. No environment,
  credentials, SQL text, private object keys/content or raw container health logs
  are collected. An independent stateless real Docker/Compose timeout probe
  tests the existing ownership mechanism; only its own new fixture is removed,
  with no volumes. Probe success cannot substitute for any application gate.
  Existing service commands, timeouts and immutable C01/C02 scripts are retained.
- Local diagnostic infrastructure RED: 7 failed/18 passed because the strict
  inherited workflow normalization did not recognize the narrow diagnostic
  additions. Exact canonical normalization now retains the original C02 blob
  guard and negative gate-removal assertions: 27 passed/1.12s including sanitized
  diagnostic output, bounded metadata execution and real nonzero exit propagation.
  Full local units 414 passed/12.04s before two added diagnostic observation cases;
  both added cases passed in that focused 27-case run. Full Ruff/format (327
  files), inherited mypy (92 files), Django and production checks pass. These are
  local infrastructure results, not service PASS or a root-cause conclusion.
  Task 4 IN_PROGRESS/PENDING_CI; diagnosis only, no ownership core or Task 5 work.
- Final diagnostic source local unit gate: 416 passed/11.99s, no skips. Diagnostic
  observation additions preserve the strict inherited workflow blob contract.
- Published diagnostic checkpoint local 1e89cc9 -> remote 8a07f478c54b54d8aa7d74d1ab1d3125db7e2261,
  tree 54b25eb199bebbd8ff437c5577307f0b64b7b05f, normal parent 411fc4f,
  force=false; source Actions 37758067055. Protected refs remain unchanged.
  Actual complete probe log 113247454008: real Compose fixture starts, existing
  GNU timeout returns 124, container_alive_after_timeout=true. Probe fails closed
  (exit 1) and removes only its own stateless fixture. This proves a hosted Docker
  ownership defect, still not the identified cause of the three original hangs.
  Foundation log 113247454148 is a distinct diagnostic-source formatting failure
  before rehearsal: two newly added test lines were not re-formatted after their
  addition. Corrected formatting only; no inherited check bypassed. Other two
  service jobs remain under observation; no service PASS or behavioral RED claimed.
- Formatting-only follow-up local 7a1cb77e4dcdbddb833e562b3922ecbd41b08ffe ->
  published 343fb9225ffed4c74cb9040d7a2f2ad8dccb40a2, exact tree
  764ca89b6da3462fa08fc7eed9bcdd25e69cbff7, normal parent 8a07f47,
  force=false. All 327 files pass formatting. Source run 37758279748; second
  actual complete probe log 113248159872 reproduces returncode 124 with an alive
  started Compose container, exit 1. Foundation metadata shows quality succeeds
  and the exact C01/C02 rehearsal is again active (113248160414); cumulative
  PostgreSQL 113248160157 and private storage 113248160080 are active.
- Additional actual local boundary experiments: the exact uv run timeout path
  terminates its Python child in the timeout process group and closes its output
  pipe; nested uv run with environment synchronization enabled completes in
  0.12s without timeout. Neither local experiment establishes hosted behavior.
  At 09:46:54 original diagnostic PostgreSQL 113247454019 remains in_progress
  beyond its 300s/kill grace; no diagnostic artifact is exposed. Actual live-job
  log requests still return BlobNotFound. Exact child/SQL/test progress for A/B/C
  remains unknown; do not claim a shared cause or fix from the independent probe.
  Live GitHub UI inspection is the next evidence path; browser fallback requires
  user approval under the browser capability instructions after connector errors.
  This ledger update is intentionally preserved unpublished while requesting
  that access; source checkpoint and both existing hosted runs remain intact.
- Approved read-only browser fallback 2026-10-08 12:01 UTC: inspected only the
  exact run 37758279748 page. GitHub renders "Page not found" / 404 and a
  "Sign in" link; one reload returns the same page. No job/step output,
  timestamps, annotations, last command/test or diagnostic snapshots are exposed.
  This does not establish why access fails, whether authentication would grant
  access, or the current terminal state of any job. No browser mutation, login,
  cancellation, rerun, repository edit or protected-ref action performed.
  Per explicit user instruction, STOP on insufficient UI evidence. Last child
  progress in PostgreSQL 113248160157, storage 113248160080 and foundation
  113248160414 remains UNKNOWN; only the enclosing steps in earlier API metadata
  are confirmed. Shared-versus-separate cause remains unresolved. The two real
  Compose ownership RED probes remain independent evidence, not proof of any
  individual stall's cause. No speculative correction or gate change made.
  Existing work and unpublished notes retained; Task 4 incomplete; no Task 5/C04.
- Diagnostic-infrastructure-only recovery 2026-10-08: status, HEAD/log, all diffs,
  existing wrapper/workflow/tests and ledger inspected before modification.
  Local 7a1cb77/tree 764ca89 equals published 343fb92/tree 764ca89. All previous
  unpublished ledger notes retained. Run 37758279748 now completed: three suspect
  jobs cancelled, all later diagnostic artifact steps pending. This proves the
  evidence-upload failure; it does not identify the original stalled children.
- Bounded-supervisor RED: real TERM-ignoring child does not return within eight
  seconds, and a successful observed command returns zero: 2 failed/6 passed,
  8.36s. New supervisor starts its own child session with isolated stdout, uses
  finite 240s PostgreSQL / 600s storage / 900s foundation observation windows,
  flushes a final redacted snapshot, terminates the owned process group and
  detached/adopted children using Linux subreaper ancestry plus start-time checks,
  and returns failure. Raw child output is never relayed or saved as an artifact;
  only repository-known test paths/functions, migration names and finite phase
  progress are admitted. Independent draining avoids diagnostic backpressure.
- Fresh-runner ownership preflight refuses existing known Compose projects.
  Cleanup targets only new container IDs under that phase's exact known project
  labels; no global prune, down -v, volume removal, unrelated container deletion
  or persistent/external data deletion. Metadata commands and cleanup have short
  bounds; unknown observation/cleanup facts remain explicit, never a PASS.
  The original three shell commands, installed suites and production timeouts
  remain unchanged on separate hosted runners. Exact-ref workflow messages and
  every JSONL terminal event mark EXPECTED DIAGNOSTIC FAILURE, including an
  observed command that exits zero. The pinned always() artifact steps remain;
  the independent ownership probe now uploads its redacted supervisor evidence.
- Local focused diagnostic/CI contracts 31 passed/3.52s; full units 420 passed/
  16.40s, no skips. Full Ruff/format (327 files), inherited mypy (92 files), Django
  and production checks pass. Hosted real Docker probe additionally exercises a
  detached, TERM-ignoring host child that drops the ownership environment marker
  and a stateless real Compose container; termination and container removal must
  be checked from actual logs/artifacts, not inferred from local mocks.
  Local Docker and /proc remain unavailable. Task 4 incomplete; original three
  stall causes UNKNOWN pending preserved hosted evidence; no functional Task 4
  correction, Task 5, C04, merge or deployment.
- Final local diagnostic source unit verification: 420 passed/14.29s, no skips.
  Existing unpublished recovery/browser notes are included verbatim in this
  checkpoint; only diagnostics, their tests/workflow and this ledger changed.
- First bounded checkpoint local bf306c5dd141ab96ce41422b2c9a533efe5c1a05 ->
  published 8efac02d0ec6aee6f003bbb102f314429842abc6, exact tree
  a7c71c4d0767d2c9212dc35fe901929f433f7967; normal parent 343fb92,
  force=false. Source run 37782066499, protected refs unchanged.
  Actual probe log 113327374996 repeats original Compose ownership RED but the
  new cleanup contract is NOT verified: detached host child terminated, running
  container observation false and container removal false. Artifact 11552087967
  uploaded successfully; its returned download fails HTTP 403/error 1010 on this
  host. No ZIP content claim. Add sanitized metadata-query failure categories
  and relay the already-redacted probe JSONL into its normal completed job log
  to expose the failure without raw stderr, secrets or a browser fallback.
- First actual bounded PostgreSQL log 113327374865: unchanged cumulative command
  progresses through Task 4 cases and exits 1 naturally at 116.5s (before 240s).
  Final snapshot 116.7s: no owned host processes, no PostgreSQL active/blocking
  rows; host/container cleanup complete. Artifact 11552258441 uploaded. Storage
  log 113327374956: unchanged command exits 1 naturally; final 276.8s, no owned
  host processes or containers; cleanup complete. Artifact 11553340034 uploaded.
  Neither reproduces its historical hang in this run. These are diagnostic
  observations, not service PASS, original root-cause proof or functional fixes.
  Foundation 113327374407 remains under its bounded observation window.
- Metadata-evidence checkpoint local faa69b2069433913d93a8df55363bf20e76ed744 ->
  published c3769b09d229d29de4b8b4b4f9baf237a3607ba6, exact tree
  236e922145b6cc1248ea0267f5d7b2e7ea45a303; run 37783207165.
  Actual complete probe log 113331261184 exposes the precise infrastructure RED:
  at 3.1s Docker inspect returns 1 / inspect_missing_health_field. The classifier
  matches Docker's fixed "map has no entry for key Health" failure, without
  relaying raw stderr. Stateless container lacks a healthcheck; direct
  .State.Health lookup breaks the whole container snapshot, so cleanup has no
  owned IDs and reports complete=false. The detached host child is correctly
  adopted and terminated. Final JSONL and terminal event survive; artifact
  upload follows. Correct only this diagnostic template: index the optional
  Health key, report health="none" when absent, retain metadata/privacy limits.
  This diagnosed observability/cleanup defect is distinct from the original
  three hangs; no functional asset-ingress correction is authorized or made.

## Authorized published-state recovery — 2026-10-09

Automated workspace maintenance deleted all four former C03 worktrees.
The unpublished ledger lines, original local index, staged/unstaged/untracked
workspace-only files and any other state absent from surviving published Git
objects have no backup and cannot be restored byte-for-byte. They are classified
UNRECOVERABLE_UNPUBLISHED_STATE. One bounded non-destructive salvage search of the
remaining workspace found no ledger, reflog, Git objects/worktrees metadata or
editor recovery files: UNRECOVERABLE_UNPUBLISHED_STATE_CONFIRMED.

The user explicitly authorized reconstruction from published checkpoints and
hosted evidence, superseding preservation requirements for destroyed material.
This ledger retains every committed historical byte above and appends only new
source/evidence-backed recovery findings. No missing unpublished content is
fabricated, approximated or represented as restored.

Fresh source: storage diagnostic 206b7aa72f099533701f4eef3f64277e9555f6a7,
tree 37cf42e36bb52c7712a7ccc8478de9bfa93fd349. Git clone includes surviving
ancestry; execution d50b82e9fba64199f09b1e65615c6c6b9ce416cc is an ancestor.
Verified refs: profiles/c03-cloud d50b82e9fba64199f09b1e65615c6c6b9ce416cc;
PostgreSQL diagnostic e034e9d2501b2d1e6f4a0689af923e900596bd3b;
profiles/c03-plan 79fd62e583cbe81f335bb08fce0eb43ff36b0167;
accounts/c02-cloud 0905be6c6ca608d469fe33e87f514b22591132d1;
foundation/c01-cloud 75c551e5b9bbbfb7777ee52b09a1993b681e921a;
main 8ede9a451db6103f4e3ebf65784ee9f16b96feb2. Protected/unrelated refs
match known published checkpoints; none modified. Tasks 1–3 retain committed
completion evidence; Task 4 remains incomplete; Task 5/C04 unstarted.

Authoritative subsequent evidence to re-inspect: PostgreSQL Slice A
37842121259 SUCCESS on e034e9d2. Storage 37886246054 attempt 3/job 113687873212
on 206b7aa7: migrations/probe succeeded; pytest startup exited 1 with
ModuleNotFoundError then ImportError; no test journal; all 91 acceptance cases
unverified; services healthy/readiness 200; cleanup complete; artifact
c03-slice-b-storage 11598036850. This is a recovered evidence summary, not
restoration of the deleted unpublished ledger. Current work continues Task 4 only.

## Recovered Task 4 — import and private CORS closure

Local console-entry reproduction on published 206b7aa7 identifies missing module
docker and importing plugin docker.c03_pytest_triage. A focused actual-command
collection regression failed with exit 1, then passed after changing only storage
pytest invocation to Python's module entry point. 35 focused checks / 462 units,
mypy and Django/production checks passed. Published b1a835d3621b52b3fb8c995fba8de4131f293bc0,
tree 90a78e3e89ccc438e6d5138d4213591abf177098, storage diagnostic only.
Hosted 37895422247/job 113705565729 executed all 91 cases: 90 passed / 1 failed,
pytest exit 1. Exact remaining RED: real private roundtrip test line 48,
foreign-origin preflight exposes access-control-allow-origin. Artifact 11600167114;
natural exit/cleanup complete. No missing-import identity guessed from old logs.

Pinned official MinIO source 9e49d5e7a648f00e26f2246f4dc28e6b07f8c84a,
internal/config/api/api.go, defines MINIO_API_CORS_ALLOW_ORIGIN and '*' default,
including empty values. cmd/api-router.go matches configured patterns against
browser Origin. Set a non-origin sentinel 'none' in private service configuration;
no valid URL or opaque null origin matches it. Existing real denial assertion
unchanged, strengthened to also test app-like localhost and opaque null origins.
Four policy regressions RED then GREEN; 466 units GREEN. Generated pytest fixture
copies caused an initial format failure; moved those copies intact under ignored
.runtime and rechecked all tracked source: Ruff/format GREEN.

Published 7361d9c8fd6e9db057f3e68988474e2258ee6838, tree
1609336d1b2db94681d90bebddbdb4d0ff6f589e. Hosted Slice B 37896016320 /
job 113707419863 SUCCESS: all 91 cases completed, 91 passed / 0 failed / 0 skipped;
pytest exit 0 at 22.330s. Supervisor natural command exit 0, terminal 173.6s,
host/container cleanup complete, no deadline/cutoff. Actual required private-store
nodes inspected: internal bounded write/read/head, immutable replay rejection,
anonymous GET/PUT and bucket-list 403, foreign/app/null CORS denied, real Django
multipart -> private MinIO -> quarantine finalization, no public ACL/derivative,
owner/foreign/staff raw-source unavailability, missing/size/type/foreign storage
facts rejected, inherited signed-read bound. Complete real MinIO acceptance,
not fake-only readiness. Task 4 remains incomplete pending cumulative/inherited CI.

Transition out of diagnostic-only CI now adds explicit bounded acceptance mode:
only natural command exit 0 plus exact true host/container cleanup may PASS;
deadline, cancellation, unknown cleanup or nonzero exit fail closed. Existing
diagnostic mode still never passes. 9 new acceptance regressions RED then GREEN;
40 focused acceptance/CI/ownership checks and 475 cumulative units GREEN.
Inherited C02 workflow blob check and all negative gate-mutation tests retained;
original verify_c02.sh/verify_foundation.sh and protected C01 source unchanged.
Independent timeout probe now passes only when its actual bounded ownership
contract is verified, not merely because its GNU-timeout observation returned.
No Task 5 processing/scanner/worker behavior introduced. Full execution-source
hosted verification still pending; no Task 4 COMPLETE claim yet.

Slice B successful artifact verified: c03-slice-b-storage ID 11600148393,
12829 bytes, digest sha256:f68118360cf7e0dc99ad716fc7d94543944b407b18b0a75fef96214dc80e7435.
Final local required checks: 475 units passed in 26.65s; required mypy 93
source files passed; Django test and production checks passed; Ruff and format
343 files passed. An optional broad mypy scan included untouched inherited
configuration lacking typing/stubs; no unrelated configuration changed.
Application/use-case files remain byte-identical to verified Slice A e034e9d2.

Prepare execution publication on an isolated fresh profiles/c03-cloud worktree
based exactly on d50b82e9. Copy evidenced Task 4 source and gate/test changes;
exclude both isolated diagnostic-branch workflows. No diagnostic branch is
merged and no protected ref is changed. This implementation checkpoint still
requires actual cumulative PostgreSQL, real storage, timeout ownership and
complete inherited Foundation results before Task 4 COMPLETE.

Focused read-only code review found no Critical production findings. Important
supervisor ownership gaps corrected with 2 RED→GREEN regressions: reject failed
subreaper setup before launching any child, and treat truncated process inventory
as unavailable rather than clean. Review confirmed no remaining Important or
Critical finding after correction. Explicit user maximum request/object cap of
10,000,000 bytes overrides the earlier plan multipart-overhead allowance; the
existing measured request cap and security assertions are unchanged.

## Execution checkpoint d4e25040 — current Foundation RED

Published guarded fast-forward from exact d50b82e9 parent: d4e250402992f3f182b285ca433de79eae9718c6,
tree 381994de1a6cc270122209872f55f1d7cf91f927. Both isolated diagnostic
workflows excluded; no diagnostic branch merged. Hosted run 37897396645
completed FAILURE, with three successful jobs: c02-migrations 113711771590
(269 C02 cases passed, cumulative C03 selection 395 planned cases, natural
exit 0 at 81s and verified cleanup), c03-storage 113711771589 (all 91 passed,
0 failed/0 skipped, pytest exit 0 at 22.337s, natural exit/cleanup 176.9s),
and c03-timeout-probe 113711771492 (actual GNU124 escaped container observed;
supervisor fixture detached child terminated, owned container removed, bounded
deadline failed closed with cleanup true). Artifacts: PostgreSQL 11600559605;
storage 11601605035; timeout ownership 11600653719.

Foundation job 113711771224: required host quality/static/frozen gate passed,
477 units in 21.91s. Exact C01/C02 wrapper returned naturally 1 at 581.2s,
not a timeout/deadline. Artifact 11600823345. Last active child command was
current fitlink-foundation-verify checks: uv run --frozen pytest tests/unit
tests/integration -q --strict-markers. This follows immutable C01 and the
exact same-database upgrade phases. Services were healthy, MinIO ready200,
no PostgreSQL blockers; changing test DB activity shows work rather than
a fixed DB deadlock. Cleanup host/containers true. Exact failed node was not
retained by existing stdout redaction; no functional cause is guessed.
Prior successful Task3 Foundation37735571394 took19m50s, but the current
RED returned before15-minute observation cap; no timeout is changed here.

Add only opt-in current-source pytest node/phase/failure metadata journal,
loaded after conftest bootstrap. Immutable C01 source/compose and original
verify_c02.sh/verify_foundation.sh commands remain byte-identical. A bounded
non-terminating case observer cannot change test verdicts; existing whole-gate
supervisor owns deadline and cleanup. No raw exceptions/private payloads
emitted. Full diagnostic JSONL uploaded; safe failed reports and exits printed.
Task4 remains incomplete pending exact RED evidence and remaining GREEN gates.

The refinement regression initially exposed absent local C01/static fixtures
and an unintended uv environment installation; restored exact committed C01
fixture/archive and verified generated CSS, used the existing frozen Python
environment. No test weakened. Review caught a new-test Git-history dependency
in depth-one hosted checkout; fixed to reviewed immutable script blob IDs
bebab2374dd3daf2d234cf5c0a94300ce3796b8a and
344898c20c0d5ede46fe7d5e653df378c267d9b7 without fetching/changing protected refs.

Refinement verification GREEN: 28 focused checks, 480 cumulative units in
28.39s, Ruff/format345files, diff checks. Review confirmed no remaining
Critical/Important finding. Publish diagnostic refinement only, no product
correction or timeout change; continue autonomously to obtain exact node.

## Foundation internal-error observation — a61f6e3b

Hosted run37899524638 on a61f6e3b65fb05fa51a9c92c19de60d242f3744a,
tree025336a6a78636b2d735d1bcaf76e0793ead66cf: C02/cumulativePG, real
MinIO91 and ownership jobs GREEN again. Foundation113718559637 natural
exit3 at559.7s, cleanuptrue. Reporter records952passed /0failed/0skipped
case calls, pytest exit3 at189.527s. This is a pytest INTERNALERROR, not
a recorded failed assertion. Its exception identity/trace is the exact
remaining observation; no product or timeout correction is inferred.
Artifact11601892064 contains redacted journal; binary download transfer
to this host returns403, so use emitted logs. Safe session snapshot120s
shows active evidence-guard teardown in PostgreSQL fixture flush, no
blockers; this does not identify the later internal error.

Local focused test_c03_triage_evidence (all4 prior cases) under active
Foundation reporter passes; collection ordering alone cannot prove a
hosted failing node. Add only pytest_internalerror hook with bounded
class/category, last static node, source frames without locals/messages.
Focused missing-hook regression RED. Preserve all gates and code; continue
to obtain exact exception rather than guessing a source correction.

New wrapper regression initially leaked its fake working directory/env
into later local tests; cumulative suite caught20 fail-closed boot/check
failures. Scoped fake cwd/env with monkeypatch restoration. This test did
not exist in either prior hosted RED, so it cannot explain them. Both
internalerror-hook and visible-output regressions observed RED then GREEN.

Internal-error refinement local verification: 482 cumulative units passed
in36.75s, focused24passed, Ruff/format345files and diff checks GREEN.
Read-only review: no Critical/Important findings. Isolated diagnostic
branch diagnostics/c03-task4-foundation-triage created at
5f53cfda706a8bccbe3fad7ca569e9dd607751da,
tree8070dbb44077ae04d7d3eff8fcb3a0297f60c8ea, parent exactlya61f6e3b.
Six diagnostic-only files; this unpublished ledger excluded.
Run37901832441 now executing job113725939593. It is expected diagnostic
failure and cannot establish Task4 PASS. Execution ref remainsa61f6e3b.

## Complete Foundation command observed GREEN on isolated diagnostic source

Run37901832441 / job113725939593, source5f53cfda, completed expected
diagnostic FAILURE solely because its workflow explicitly rejects a zero
observed gate status. The unchanged full verify_c02.sh command itself
returned0 naturally at871.2s; host/container cleanup complete. Current
reporter: 1033passed/0failed/0skipped call reports, all three recorded pytest
exits0 (220.017s,1.017s,0.461s); no internalerror/cutoff. Original immutable
C01, same-database upgrade, current regressions/browser/restart commands
all completed because the original set-e script reached its natural0 end.
Artifact11603845636 c03-foundation-internalerror,63978bytes, digest
13237572a5dc46d1a211ee4c5f99ff4b5a79a885f8f0b624289b25995507a0e7.
The earlier internalerror did not recur; its exact class/cause remains
unestablished. No speculative application or timeout correction made.
Publish the reviewed metadata-only refinement/tests plus this ledger to
the execution ref by guarded fast-forward, then require actual complete
execution CI GREEN before Task4 completion. No diagnostic branch merged.

## Evidenced Foundation reporter defect and correction

Execution14f81dff4fc5736b73af1d46b70cbd6e33d8de0c/tree
6a17f7a8872718a8193e6250a85e70e87877ed3b, run37903523863 FAILURE:
PostgreSQL113731382616 GREEN (269C02passed61.52s; all395selectedC03
cases verified by collection, cumulative natural0at92.1s, cleanuptrue);
storage113731382404 GREEN (91passed/0failed/0skipped, pytest0at22.41s,
natural0at181.9s, healthyPG/Redis/MinIO200, cleanuptrue); ownership
113731382805 GREEN (actual124escapedcontainer then bounded owned cleanup).
Artifacts PG11603122258,storage11603421642,ownership11603132904.

Foundation113731382184 natural3at573.8s, cleanuptrue;953passedcalls,
0failed/0skipped reports. Exact retained internalerror: AssertionError,
active tests/unit/test_c03_triage_evidence.py::
test_failure_preserves_http_assertion_and_trace_without_response_body.
Trace: docker/c03_pytest_triage.py:226 pytest_runtest_makereport ->
:207 failure_data -> _pytest/_code/code.py:270 statement. Installed
pytest code asserts fullsource is not None; optional source was unavailable.
This is an evidenced reporter defect, not a PostgreSQL lock or upload
functional failure. Artifact11603444163 retains class/static frames.
The underlying original test report was replaced by this reporter error;
fixing it may reveal the original verdict, which must remain authoritative.

Two focused regressions observed RED: real compiled missing-source frame
reproduces exactAssertionError; missing pytest source for a known repository
assertion loses expected status. Correction catches only source-availability
errors; retains original exception/status/frames, and recovers the expected
HTTP status from an enumerated static repository test line only. Never emits
raw source, payload, exception message or unknown private file. Existing
tests/production behavior/inheritedcommands/timeouts unchanged.
37focusedpassed8.67s;484fullunitspassed40.00s;Ruff/format345files/diffGREEN.
Read-only review: no Critical/Important finding; original pytest report and
nonzero verdict remain unchanged. Publish only reporter, regressions and
append-only ledger to execution ref; all hosted gates must still PASS.

## Relocated pytest bytecode source mapping RED to GREEN

Source7fba2047b5afe788928edffb305ea51f2687b375/tree
33518c6a567380b64e4a82e477d37ec93529f418, run37905152598 FAILURE:
PG113736730699 GREEN (269C02passed73.23s, cumulative395natural0
at109.9s, cleanuptrue); storage113736730575 GREEN (91passed/0failed/
0skipped,pytest0at14.197s,natural0at145.9s,cleanuptrue); ownership
113736730808 GREEN. Artifacts PG11604137326,storage11603553895,
ownership11604430638.

Foundation113736730711 now returns natural1at584.8s with original
verdict preserved (rather than INTERNALERROR):1026passed/3failed/0skipped.
Exact failed nodes in tests/unit/test_c03_triage_evidence.py:
- test_failure_preserves_http_assertion_and_trace_without_response_body:
  KeyError at74, expected_http_status absent; actual404 retained.
- test_internal_pytest_error_records_only_class_and_code_locations:
  AssertionError at107, code location mismatched.
- test_missing_pytest_source_uses_only_known_repository_assertion:
  KeyError at145, expected_http_status absent; actual404 retained.
Each test code frame maps external in the container, despite its current
static source being present. Cleanup complete; artifact11603564867.

Installedpytest rewrite._read_pyc validates source mtime/size then
marshal.loads the cached code unchanged; original co_filename survives.
A real local pytest cache portability reproduction passed on its first
source root, then failed after source+cache copy2 and original root rename:
same_path=false and compile_origin_exists=false. Both source copies and
evidence preserved under ignored.runtime; no raw private paths emitted.
This proves the path portability mechanism independently. Hosted raw path
prefix was deliberately redacted; inference from external frames, missing
source and host-unit-before-container execution is consistent with this
mechanism. The earlier isolated5f workflow omitted host current-unit tests
and completed the whole rehearsal0, also consistent with fresh cache paths.

All three unchanged failing functions compiled under relocated source
filename reproduce their exact KeyError/AssertionError REDs locally.
Normalize only an exact known static TESTS suffix AND known function to
its canonical repository path; fallback assertion lookup uses the actual
frame function. All three GREEN. A privacy regression additionally caught
framework-looking parent overriding canonical paths; preserve canonical
mapping precedence, so private parent text never appears. Unknown files/
functions remain external and cannot enable source fallback. No arbitrary
file read, raw source/private payload emission or verdict conversion.
488fullunitspassed34.30s;11activeFoundation reporter casespassed2.66s;
Ruff/format345files/diffGREEN. Read-only review: no Critical/Important
finding. Only reporter/test/append-only ledger change; application,
inheritedscripts and timeouts unchanged. Continue required hosted gates.

## Task 4 COMPLETE — authoritative recovered execution handoff

Current task status supersedes earlier historical IN_PROGRESS entries:
Tasks1–3 COMPLETE unchanged. Task4 COMPLETE on validated implementation
1edf4e69bedd562708b9dbc0a252015ebfd1a7c6,
tree0491ffb8de1cb44533cc6dd3f8621213e8ed9b52.
Tasks5–14 NOT STARTED. C04 NOT STARTED. C03 overall IN_PROGRESS.
No merge, deployment, force push or protected/unrelated ref mutation.

Authoritative full execution run37907594072 SUCCESS; actual complete job
steps/logs inspected, all four jobs GREEN:
- foundation113744715421: frozen/static/Ruff/format/mypy/Django/production
  checks passed;488hostunitspassed17.78s. Unchanged complete
  verify_c02.sh rehearsal natural0at683.2s, host/container cleanuptrue.
  Immutable pinnedC01 baseline, populated same-database exact upgrade,
  current full regressions, native browser gates and real Redis/MinIO/
  worker restarts all reached the original set-e command end successfully.
  Current check/restart journal1039passed/0failed/0skipped; all3pytest
  exits0 (138.241s,0.303s,0.673s). No internalerror or cutoff.
- c02-migrations113744715848:269C02passed72.94s; real Redis restart
  durable-limit probe passed; complete installedC03 selection395cases
  (verified local collection, including Task4 lifecycle/races/authority),
  naturalcommand0at108.6s, host/container cleanuptrue. Global conftest
  rejects selected skips. This is cumulative compatibility verification,
  not a repeat of completed Task1–3 implementation or isolated SliceA.
- c03-storage113744715710: REAL privateMinIO, healthyPG/Redis/MinIO,
  readiness200; migration/probe/pytest phases succeed;91passed/0failed/
  0skipped, pytest0at19.001s; naturalcommand0at165.3s and cleanuptrue.
  Required real store nodes inspected: authenticated immutable bounded
  operations; anonymousGET/PUT/bucket-list403; foreign/app/nullCORSdenied;
  actualDjango multipart into privateopaque source; finalization verifies
  authoritative object facts and leaves it private/quarantined; missing,
  oversized, size/type/binding changes fail closed. Lifecycle/owner/
  fresh-account/replay races pass. Rawsource owner/foreign/staff delivery
  unavailable, no signedPUT/browsercredentials/directupload path.
- c03-timeout-probe113744715729: originalGNU124 container escape observed;
  bounded supervisor fails closed and verifies detached-child termination
  plus owned container removal. Both cleanup facts true. No global prune
  or persistent/external data deletion. This independent ownership proof
  does not retrospectively attribute all historical hangs to one cause.

Run37907594072 artifact metadata verified:
- c03-foundation-diagnostics11605782119,60294bytes,
  sha256:396f7cd53470643178fcbe3245fa9c7cba9d1e1f5030ee856177577659126e8e.
- c03-storage-diagnostics11605585981,14972bytes,
  sha256:ef0bc047ba1e490469958976c2d29556fbd72b38fc184f761c49eabf1f25b2de.
- c03-postgresql-diagnostics11605336208,4717bytes,
  sha256:645918a36ab08e3597a4b24f95881044f0f9b4efd0c3cc7994585d0619730f70.
- c03-timeout-probe-diagnostics11604769289,900bytes,
  sha256:93c6d96f618f33eb69c37e34937149e57ea4aeefbba086b3fde8478c7b4fb7c4.

Source1edf push run initially invisible, then37907594072 appeared and
finishedGREEN without duplicate publication; delayed visibility resolved.
SliceA e034e9d2/run37842121259 remains authoritativeGREEN unchanged.
Task4 production wiring recovered faithfully from publishedSliceA; current
recovery corrections address pytest launcher, privateMinIOCORS and
fail-closed diagnostic ownership/source portability. No scan, sanitizer,
image decoding, derivative creation or READY shortcut; Task5 not begun.
Focused security reviews found no remaining Critical/Important issue,
with RED→GREEN regressions for identified Important ownership/diagnostic
issues. Inheritedscript blobs and protected main/C01/C02/plan refs remain
exactly the immutable SHAs recorded above.

This handoff preserves the committed historical ledger prefix exactly.
UNRECOVERABLE_UNPUBLISHED_STATE_CONFIRMED remains final: deleted original
index/unpublished lines/local-only files were not restored or fabricated.
New workspace/evidence comes solely from published refs and verified
source/CI plus explicitly identified new local diagnostic reproductions.
Completion publication changes only this append-only ledger; implementation
source is identical to the validated1edf checkpoint. Preserve branch and
all surviving new workspaces; STOP after Task4 handoff.

## Task 5 authorized preflight — 2026-10-09

Latest explicit authorization: Task 5 ONLY, autonomous execution until PASS or
new external blocker. Tasks 1–4 remain COMPLETE; Tasks 6–14/C04 unstarted.
Fresh isolated clone at exact published 1f0b12b6c92bfc8fb201911637f3f19b9ff8481f,
tree 8815763c6eab87b55429b13cf3d8e430064f7e3f; status/diffs/untracked empty.
No usable prior checkout/Task 5 work existed here. Complete published ledger and
approved plan read. No deleted unpublished state fabricated or backup requested.
All four protected refs match ledger authority. Task 4 run 37907594072 verified
SUCCESS at exact 1edf4e69/tree0491ffb8; all four complete jobs/logs inspected:
113744715421/113744715848/113744715710/113744715729. Confirmed 488 host units,
1039 Foundation passed/0 failed/0 skipped, inherited269PG, MinIO91/0/0,
owned timeout fixture cleanup. Documentation rerun is not a prerequisite.
Python3.13.15/frozen69packages installed, exact C01 fixture verified from Git
archive, npm/build/JS succeeded; untouched full unit baseline488passed72.28s.
Existing timeouts/ownership design and immutable scripts remain binding.

Dependency review before change: official Pillow12.3.0 release/security/advisory
pages and ClamAV1.5.4 release/official INSTREAM/Docker docs reviewed2026-10-09.
Pillow restricted JPEG/PNG parsing needs full pixel rebuild and native isolation;
PDF/EPS/JPEG2000/font/viewer paths are excluded. Latest stable verified12.3.0,
MIT-CMU; pin exact version and uv artifact hashes. ClamAV1.5.4 incorporates the
August2026 parser security fixes; separate GPLv2 daemon, no libclamav linking.
Official clamav/clamav:1.5.4_base registry manifest resolved to
sha256:7769870154c74ce31b0047dd8771e81f7c4269278bc005782e9e419e4922c73d
(amd64 child4bd758114dbe0964edf6742cd8ddd98ed73eb8fcd70ce8bb4f53b19a79f07fe1).
Real signature readiness/isolation and hosted service evidence still pending.
No safety/vulnerability-free claim inferred from a version pin.

## Task 5 continuation checkpoint

Preserved all seven modified and ten untracked Task5 files at exact1f0b12b6,
with no staged changes or production processor. All protected refs reverified
unchanged via GitHub API; complete Task4 run/jobs/logs recheckedGREEN.
Task5 prior26failures are missing-contract assertions, NOT behavioral RED.
Ruling: establish minimal fail-closed callable boundaries before counting actual
behavioral RED; do not label missing imports/contracts as product evidence.
Cost if wrong: boundary checkpoint still cannot satisfy any completion gate.
Existing CI selection test failed on omitted new processing script; include that
owning gate in the installed-suite union, retaining exact inherited workflow.
Compose browser inherits the new app networks together with network_mode;
clear only browser's inherited networks to keep its original web loopback mode.
No process/service/supervisor timeout changed. Publishing tests/infrastructure
for required hosted RED; Task5 IN_PROGRESS, noTask6/C04/merge/deployment.

Task5 test/infrastructure checkpoint remote c0f5d420/tree6cf6e118 (local0baffa9
same tree); diagnostic checkpoint cc3901ab/tree5f0e2a9 (local5479e38 same tree).
Never publish synthetic local ancestry. Hosted37926898643 processing/storage
fail before tests; diagnostic37927253837 processing113809055020 establishes
Compose network_mode_conflict. !reset[] retains a networks key that conflicts
with browser network_mode. Remove networks from app anchor; attach scan-private
only to checks/worker, preserving browser's original loopback network_mode.
This is evidenced infrastructure correction, not processing behavioral RED.
Local minimal callable boundary19failed/7passed:10pixel results unavailable,
isolation probe unavailable and scanner return/limit/timeout defects. Hostile
cases passing solely because unavailable are NOT decoder validation evidence.
Initial socket test process remained alive because fail-closed stub did not
connect to a non-daemon test listener; terminated only that owned pytest child.
Subsequent bounded image-only11failed/7passed reproduces pixel/isolationRED.
Scanner now passes finite parsing/deadline/socket/cap cases. Decoder implemented
with separate isolated CPython, no inherited secrets/fds, fixed30s timeout,
bounded pipes/CPU20s/address space512MiB/output10MB, nonroot+no_new_privs and
strict amd64 syscall allowlist forbidding file opens/writes/network/fork/exec.
Full pixel reconstruction strips metadata. Hosted validation PENDING: local
executor root cannot os.setgroups (EPERM), so it correctly returns unavailable;
no root fallback, skip or security bypass. Hosted runner/container is nonroot.
Durable attempt handler installed without longI/O; claim/release remain explicit
fail-closed stubs for real hosted behavioralRED. Task5 remainsIN_PROGRESS.

Hosted37927731734/source61be29ec: PG/storage/ownershipGREEN, scanner runtime
started healthy and required tests executed; processingnatural1at193s cleanup
true, but raw pytest verdicts were not retained. Added existing metadata-only
triage journal to processing gate; exact behavioral evidence is pending that
run, not inferred from error class alone. Foundation actual5JPEGfailed/510passed;
PNG clean metadata removal and isolation probeGREEN. Fresh independent process
on syntheticEXIF JPEG imports TIFF/ImageOps/ImageMath during decode; preloaded
those before sandbox, retained explicit JPEG/PNG OPEN allowlist. Fix0ef7f67b/
treefcd8d41d (local007fda7) and triage43f9e884/tree4bcbc571 (localab56c53).
No service or task timeout widened; no raw exception/image/URL/log telemetry.

Schema review finding before Task5 migration: installed attempts have lease
and processing_version but no durable ownerauth/assetversion/subject authority
snapshot. A restarted process cannot establish whether claim-time authority
changed using only process-local facts. Ruling: separately named additive
assets0008 will store owner_auth_version, asset_version and a restricted SHA256
authority_hash, defaultempty only for legacy pending rows, positive/bounded when
running. No User/oldmigration changes or feature backfill. Cost if wrong: strict
binding may require harmless retry after unrelated profileversion changes.
Task5 synthetic JPEG/PNG fixtures and SHA256 manifest created; no real evidence.


### Task 5 durable processing implementation checkpoint (2026-10-09)

- Authoritative case journal on remote head 43f9e884c5d066db0303cd4956a50602b4117b35, tree 4bcbc571f71475201881d9d9fa69a4f1687420f5: run 37928283771 processing job 113812440767 exited naturally 1, owned cleanup complete. 50 actual call reports: 28 passed and 22 failed. The receipt/recovery test failed at line 29, and duplicate/revocation/restart tests at claimed line 48 (`scan_due_assets` returned 0). Real ClamAV clean/malicious/signature readiness passed; all JPEG/PNG sanitizer and isolation cases passed. This establishes behavioral processing RED after healthy required services, not a fixture failure. Storage, PostgreSQL and ownership jobs passed on the same head; foundation quality/unit checks passed, inherited service rehearsal still in progress when inspected.
- Implemented lease claims, historical failed attempt retention, eight-attempt ceiling, 300-second retry backoff, UUID-only non-eager prompts, periodic reconciliation, and independent source-read/scan/decode/object-write outside transactions. All inherited task/process/service/supervisor bounds retained.
- Separately named additive assets0008 adds persisted owner_auth_version, asset_version and authority_hash, plus running-authority CHECK. The schema finding/ruling was recorded above before generation. Legacy pending metadata defaults to unclaimed values; running rows without authority are rejected rather than retrospectively authorized. No User, old migration, or accepted-source mutation.
- Composition supplies trusted profile/role/credential and exact-record hold/consent fences. Holds never grant reads or cause deletion; no nonexistent professional consent grant is invented. User/parent locks precede Asset. Derivative inventory commits pending before immutable private write, allowing exact-byte adoption after crash. Fresh release rechecks authority, lease, revocation, source and scanner freshness.
- Server-controlled PNG compression is fixed at level 9; reconstructed pixels carry no input metadata. Production configuration rejects enabled processing until sanitized delivery is installed.
- Added bounded hosted test-only scanner barrier: commit receipt without prompt, discover through reconciler, actual Celery scan, SIGKILL worker, restart Redis, recover expired lease through production task, verify one ready effect and retained source; actual scanner outage/restoration checks follow. This checkpoint remains IN PROGRESS until actual hosted evidence passes; source contract is not service PASS.
- Local Ruff lint/format and targeted mypy passed; 30 scanner/CI tests passed. Migration drift reported none (local PostgreSQL unavailable, so hosted SQL remains required).

### Task 5 hosted implementation follow-up

- Published remote88cf08f90256f0bfeae78409b07da8bbf43dba60, tree e41640f59d049d48c2daeb0ecb57309efd6e639d; local3c62a86 has the same tree. Run37929851534 processing job113817617769: all53 behavioral calls passed, no skipped cases; the subsequent real-worker preparation exited RuntimeError before any worker-crash evidence. Source inspection identified append_outbox's mandatory transaction guard in probe preparation; the test fixture is corrected to use its required transaction, with no production bypass. This diagnosis remains to be verified on the next head.
- Foundation job113817617844 stopped at an inherited unit assertion requiring the exact C02 Beat schedule (1failed515passed). Preserve that assertion and original Beat schedule/command verbatim: add a separate config/c03_celery app and asset-beat service, with an explicit test proving both exact schedules. New scheduler configuration initially failed its focused test because the Django namespace resolved the uppercase setting; explicit CELERY_BEAT_SCHEDULE on the separate app passed (5focused tests). No inherited C01/C02 test was changed.
- Parent subprocess wait TimeoutExpired leaked instead of returning a bounded state. Added a focused test, observed1 behavioral failure, then caught only that timeout and verified1pass. No decoder timeout widened.
- Review finding before further schema changes: processing generation alone does not identify the sanitizer algorithm, and repeated broker-acceptance ambiguity currently retries forever within one pending attempt. Add separately named assets0009 with a finite prompt_attempt counter (0..8) and explicit algorithm_version. Empty legacy pending rows remain unclaimed; running authority must contain the server algorithm and positive prompt counter. No old migration or source facts change. Added actual PostgreSQL broker-exhaustion and algorithm-record tests first; hosted behavioral RED remains required before that correction.


### Task 5 finite retry correction checkpoint

- Remoteef0ab68ffdbc41e41a57cba808db9056f97cb82c, tree623c7da510c0702530d4eba1181457dfee33dc66, local642deec; run37930610537 processing job113820094331 completed natural1 with cleanup complete. All55 established calls passed including real daemon INSTREAM oversize rejection, actual incomplete-stream timeout and post-fault health. Broker exhaustion failed a behavioral assertion; algorithm persistence failed on absent field. Added assets0009 only after this RED and the prior schema ruling.
- Eight prompt attempts per processing attempt now bound broker outages. Exhaustion retires active attempts/rejects without a derivative. Claimed attempts record and recheck `jpeg-png-pixels-v1`; the database checks prompt bound and running algorithm. Existing lease/retry/decoder/Celery/CI limits unchanged.
- Disabled runtime must not claim pending work: an added focused boundary test observed1fail, then passed after composition stopped unconfigured reconciliation. Explicit injected test boundaries remain available for isolated tests; production processing is still closed.
- Unexpected worker exception sentinel previously escaped to Celery: focused test observed1fail, then passed after task returned finite unavailable without exception text; expired durable leases recover independently. This is denial, not ready/PASS.
- Processing artifacts now retain case/probe journals alongside existing supervisor evidence using the same pinned artifact action and exact branch condition. Metadata-only probe failure frames assist diagnosis without raw exception text/locals/bytes/keys.
- Setup/dependency record added with verified upstream patched releases/licenses, immutable digest, input/output/native process limits, signature freshness, network topology, durable inventory, unchanged inherited Beat, production closure and explicit operational release dependencies. Maintenance role is documented; no person or approved policy is invented.
- Local lint/format, targeted assets/composition mypy and39focused scanner/CI/Celery/timeout tests passed. PostgreSQL SQL/migration constraints and actual worker kill/restart remain mandatory hosted checks on this corrected head. Task5 remains IN PROGRESS.

### Task 5 real worker recovery GREEN and final review follow-up

- Remote18422913c0d6b3431419a9b590efad0932bd2ab9, treec90c3920ab3319962ae170a0e40330e6498d3c0b; local6d4818b has identical tree. Run37931443670 processing job113822893199 passed naturally0 in201seconds with60passed/0failed/0skipped behavioral calls and complete owned cleanup. Actual probe stages proved receipt committed without prompt, real Celery worker scanned, SIGKILL worker, actual Redis restart, expired lease recovered once through production task, scanner outage denied, and real post-fault scanner health. Storage, PostgreSQL and ownership jobs also passed; full inherited foundation remained running when inspected. Task5 is not yet COMPLETE.
- Final inline review follows the plan's no-per-task-delegation scope. Checked native input boundary/resources/descriptor and environment isolation; exact private scanner networking/signatures; transactional lock order and no long I/O; durable attempt/prompt ceilings, UUID-only queue, stale release fences and pending derivative inventory; separately named migrations; unchanged inherited scripts/tests/schedule/timeouts; production closure and deferred delivery/retention. No independent reviewer claim is made.
- Found a signature reload attestation race: pre-scan database28000 and post-scan28001 were accepted as CLEAN28001 although the bytes might have used28000. A focused regression first failed (actual clean vs expected stale), then passed after enforcing unchanged VERSION across INSTREAM. No scanner deadline changed.
- Extended actual service evidence with a real daemon unknown-command reply interpreted fail closed and post-check health. Extended the isolated probe with a second committed receipt and no prompt, discovered and released solely by actual separate asset-beat/non-eager worker within new40-second probe subprocess bounds and the unchanged600-second supervisor.
- Local35scanner/CI contract cases passed;94-file inherited/composition mypy and whole-repo Ruff lint/format passed. Existing tests/unit/test_celery_config.py, all tests/unit/c02 and tests/integration/c02, docker/verify_c02.sh and docker/verify_foundation.sh are byte-identical to the Task5 starting head (empty targeted git diff). Final hosted exact-head verification remains required for these final corrections.


### Task 5 parent-death isolation review finding (2026-10-09)

- Final source e08e6b7efcbe3d5c4db3d2546755affa47bb168e/tree b39f2d4f65e1d56019a0aca45a6b705f0c19c161 is published; local cae07b0 had the identical tree before the workspace executor disconnected. All work through that checkpoint is durable. Continuation uses exact immutable GitHub reads and non-forced expected-head API checkpoints; no synthetic local ancestry is pushed.
- Run37932068118 processing job113824969945 passed, including the actual separate Beat missed-prompt recovery. PostgreSQL, storage and ownership jobs passed; foundation remained in progress when inspected. This is not yet an overall completion claim.
- Important review finding: decoder CPU/address-space/syscall bounds plus parent timeout do not bound a blocked decoder's lifetime if Celery hard-kills the parent. A hostile native parser could wait without CPU; a pipe can remain open through another descriptor owner. Add actual parent-SIGKILL probe with grandparent-held stdin writer, verified live seccomp/nonroot child, and strict owned-process cleanup. Observe behavioral hosted RED before adding Linux PR_SET_PDEATHSIG and parent-race check after privilege drop. No existing timeout/resource/process/CI bound is widened. New probe subprocess is bounded20seconds inside unchanged600-second supervisor.

### Task 5 observed parent-death RED and bounded correction

- Remote0a7b35850aa8f983096a47fe02053b6455171908/tree3d39c6b36d634824829a30c8c65ab261c0a6227b, run37932885972 processing113827695270: actual nonroot/seccomp decoder marker followed by parent-death AssertionError at parent_death line254. All62 behavioral calls and earlier real recovery/outage/automatic Beat probes passed; natural exit1 in305.7seconds, owned host/container cleanup complete. This is genuine behavioral RED, not a service absence or timeout converted to PASS.
- Parent now supplies its trusted process ID in the otherwise minimal child environment. After privilege drop (which clears PDEATHSIG), child checks that PID, installs Linux PR_SET_PDEATHSIG(SIGKILL), then checks again before clearing environment/installing seccomp/reading input. Unsupported isolation and startup reparenting fail closed. The actual probe parent supplies the same contract; grandparent retains the writer to distinguish signal death from EOF.
- Run37931443670 foundation113822892938 hit the unchanged900-second observation deadline while executing inherited C02 browser tests, after1096passed/0failed/0skipped full unit/integration calls. No complete inherited PASS is claimed. The existing opt-in metadata-only pytest reporter flag was present on checks but missing from browser. Added that same flag to browser to expose per-case verdicts/stacks; no inherited script/test/browser assertion, scheduler, service deadline, or supervisor bound changed.
- API-only checkpoint because workspace executor remains disconnected; no local test claim. Hosted lint/format/type/production checks, actual parent-kill GREEN and complete inherited gates remain required. Task5 IN PROGRESS; Task6/protected refs/merge/deployment remain untouched.

### Task 5 parent-death probe marker review

- d7014e69f39353021c3ce43fd69a8010dece51da/tree1005ddb8124878e857ab2a1a1734d877b6f6b3ea is under run37933928212. Hosted quality/static/frozen checks passed; service gates still running when reviewed.
- Inline probe review noticed Docker's inherited seccomp mode2 and image uid1000 could satisfy the old marker before child isolation. Strengthened the actual blocked-child prerequisite to all nonroot UIDs, NoNewPrivs1, seccomp mode2 and at least two filters (Docker plus decoder). Parent cannot be killed by the probe until the additional child sandbox is observed. This prevents claiming startup fail-closed as blocked-parser parent-death evidence. Same5-second startup/2-second death/20-second probe and600-second supervisor bounds retained.

### Task 5 final exact-head verification history

- Latest implementation da89a64082ff5aee8b76ac6369725c0050381726/treea9445ee4e72e74f930ebd81c1fd6275d79e8f0c6: run37934189103 attempt1 processing/storage/PostgreSQL/ownership passed. Foundation113832013448 reached unchanged900-second observation deadline; final evidence elapsed901.9seconds,1138passed/0failed/0skipped and all C02 browser cases completed with exit0. Cutoff was during actual Redis restart/worker health after browser, not a browser assertion failure. Cleanup complete; remaining inherited restart gates were not claimed passed.
- Direct d701→da89 comparison changed only the probe's installed-sandbox marker (9added/1removed lines) and five ledger lines. The same production implementation at d701/run37933928212 foundation113831138711 completed natural0 in799.1seconds,1146passed/0failed/0skipped with complete cleanup. This evidence justified ONE failed-job-only rerun at unchanged da89 rather than code/timeout/test changes. No service, process, supervisor, test, artifact or CI bound was altered.
- Run37934189103 attempt2 reran foundation only (113839196776); the other four successful results carry forward from exact same-head attempt1, whose original executed job IDs/logs are retained below. Final run conclusion SUCCESS, exact head/tree verified through GitHub API. Both foundation attempts' artifacts are separately retained despite the shared display name: failed artifact11618277209/digestsha256:4b06d5d2d62b093bd724b81815a00dddd278e6266a9dc4e2d5d3be0fcdd03c1a; successful artifact11620450325/digestsha256:cd0ba5c8e205137c152cb7140e56ee03e08c81c577e1e00971d644000642a259. No failed evidence was overwritten or relabeled.

## Task 5 COMPLETE — verified private scan/sanitization and durable recovery

Authoritative implementation: `da89a64082ff5aee8b76ac6369725c0050381726`,
tree `a9445ee4e72e74f930ebd81c1fd6275d79e8f0c6`.
Full exact-head Actions run `37934189103`, attempt2, completed SUCCESS. Actual acceptance logs and all five job verdicts were inspected before publishing this documentation-only completion.

- Foundation attempt2 job113839196776:521 host unit cases passed, frozen dependency/static/JS/build/Ruff/format/mypy/Django/production checks passed; exact immutable C01 baseline rehearsal, same-database upgrade and complete inherited C02/browser/worker/broker/channel/MinIO restart gates passed. Current-source case journals record1146passed/0failed/0skipped, every reported pytest session exit0, supervisor natural0 in895.2seconds and complete owned host/container cleanup. The900-second window is unchanged and has little remaining runtime margin; earlier failures remain failures.
- Processing job113832013660:62passed/0failed/0skipped calls, natural0 in231.7seconds, owned host/container cleanup complete. Actual PostgreSQL/Redis/private MinIO/non-eager Celery/private ClamAV with healthy signatures exercised CLEAN/malicious/unknown/timeout/limits, immutable source and sanitized metadata-free pixels. Actual worker SIGKILL and Redis restart recovered expired lease once; scanner outage denied and health restored; actual separate Beat recovered a committed receipt with no prompt; verified nonroot/NoNewPrivs/additional-seccomp decoder died on parent SIGKILL with grandparent-held input writer.
- Storage job113832013461:91passed/0failed/0skipped calls, natural0 in178.2seconds, owned cleanup complete; inherited private MinIO/read/write/ownership contracts remain intact.
- PostgreSQL job113832013469: unchanged inherited269 account/constraint cases passed; additive SQL inspection and complete installed C03 actual PostgreSQL/Redis lost-counter contracts passed; cumulative supervisor natural0 in105.8seconds with complete cleanup, no migration drift. Assets0008/0009 were separately named only after the recorded prior schema findings/behavioral RED. No User or existing migration/backfill changes.
- Ownership job113832013678: actual finite timeout fixture reached expected observation cutoff and cleaned its exact owned host/container resources. This expected fixture verdict is not substituted for acceptance success; all acceptance gates separately exit naturally0.
- Protected references verified unchanged through GitHub branch inventory: main8ede9a451db6103f4e3ebf65784ee9f16b96feb2; foundation/c01-cloud75c551e5b9bbbfb7777ee52b09a1993b681e921a; accounts/c02-cloud0905be6c6ca608d469fe33e87f514b22591132d1; profiles/c03-plan79fd62e583cbe81f335bb08fce0eb43ff36b0167.
- Task4→final implementation comparison confirms inherited C01/C02 scripts/tests and existing Celery Beat schedule untouched. All existing process/service/supervisor/CI deadlines retained; observed failures/cutoffs remain recorded and were never bypassed, skipped or relabeled as PASS. Foundation at0a7b/run37932885972 also completed natural0 in752.2seconds,1104passed/0failed/0skipped after earlier900-second cutoffs; final exact-head evidence supersedes neither those failures nor their recorded scope.
- Inline review complete within the plan's no-delegation scope: dependency/security/license/maintenance review; native process/fs/network/resource/parent-death boundaries; exact-version signature attestation; no content egress; no long I/O transaction; durable UUID-only prompts/leases/algorithm/authority fences/retry ceilings; inventory-before-write/idempotent adoption; owner/subject/purpose/revocation/hold/consent freshness; source privacy and production closure. No independent reviewer claim.
- This completion record is documentation only, appended after verified implementation; hosted evidence is bound to the exact implementation head/tree above. Workspace executor disconnected after localcae07b0/treeb39f2d4f65e1d56019a0aca45a6b705f0c19c161; later API checkpoints are authoritative remote descendants, not claimed locally executed/synced. No synthetic local ancestry, force push, protected-ref write, merge or deployment.
- Production remains closed until authenticated isolated sanitized delivery and operational release prerequisites exist. No raw-source route or public projection introduced. Task6 and all later tasks remain unstarted under this authorization.

## Task 6 start and test-spec checkpoint (2026-10-09)

- Fresh isolated execution checkout, no pre-existing local Task 6 work. `git status --short --branch` clean on profiles/c03-cloud; GitHub branch and ls-remote both exactly 0d1372061207aeadb0e16a897454ee076a641476/tree5cc44e5e5c5437c62bcedcfeb71ba696b6f3fd0e. Preserved authoritative Tasks1–5 completion and Task5 da89a64082ff5aee8b76ac6369725c0050381726/run37934189103 attempt2. No historical workspace recovery or Task5 rerun requested.
- Task6-only behavioral specs added before implementation. Local `uv run --frozen pytest tests/unit/c03/test_professional_fields.py tests/unit/c03/test_verification_binding.py -q --strict-markers` observed16failures on missing field/binding contracts, exit1; separate CI selection test observed1failure on omitted mandatory selection. Minimal Task6 selection added to existing cumulative entrypoint, existing workflow/trigger/service/process bounds unchanged. Hosted PostgreSQL behavioral RED required before service implementation.
- Local Python/uv available; Docker/PostgreSQL binaries unavailable. Existing hosted services are the service authority; no SQLite substitution or skipped integration claim. Task6 IN PROGRESS, no migration authorized, no Task7/C04/merge/deploy/protected-ref changes.

### Task 6 hosted RED and bounded implementation

- Test-spec localae278e6de3a3863078416454da9b58946e2b3861 maps to remote701078b3fb308dae929dbed4fb876f2c14b3fa7f, identical treeb4af0969846ac4f897dbcc68800649a30da92968. Shell push lacked authentication; use expected-head, non-forced GitHub API commits with actual remote parents and exact tree comparison, preserving local unpublished work. No synthetic ancestry is published.
- Run37949114753 PostgreSQL job113882979129 executed real PostgreSQL17.11/Redis7.4.11,269 inherited C02 cases passed; real Redis restart/quota gate and established C03 gates reached Task6 selection. Task6 failures occurred during actual calls after healthy services, with AssertionError missing private setup/credential contracts (one assistant AttributeError); supervisor natural exit1 in128.8seconds, complete owned cleanup. Source collection alone is not this evidence. Foundation113882978749 quality/static/frozen checks passed before16Task6 unit failures (522other unit cases passed); no subsequent inherited foundation acceptance claim. Storage113882979186, processing113882979228 and ownership113882979284 succeeded on this test-spec head; inherited Task5 implementation remains untouched.
- Implemented typed private field/credential contracts, resumable owner saves, two independent roles, broad locations, target-specific counters/stale history, append-only credential revisions and current same-owner/purpose/processed-asset validation. Submission/staff decision/publication/owner UI/assistant lifecycle remain absent. No model/migration/dependency changes.
- Ruling: create_credential accepts a metadata-only draft with current_revision=NULL, then existing Task4 upload/Task5 processing bind to that credential UUID before revise_credential attaches its ready evidence — required by existing exact credential upload subject policy and supported by Task1 nullable pointer; no upload policy relaxation or fabricated ready asset. Such a draft is never submitted/verified authority. Cost if wrong: later adapter must preserve the two-stage flow.
- Ruling: Task6 bound-edit effects use synchronous target history/audit and the installed professional.profile_changed outbox in the same owner transaction; verification.changed consumer belongs to Task7 and is not installed early. Cost if wrong: Task7 must wire its own consumer before submission, rather than consuming an unhandled event now.
- Focused unit field/binding tests16passed. Local37-file professional/composition mypy, Ruff and Django checks passed. Initial full local unit run520passed/18failed: six inherited immutable-C01 fixture tests lacked their fixture; ten clean raster cases and isolation probe fail closed because Work host cannot supply the tested native sandbox; static manifest lacks generated CSS. These environmental failures are retained, not relabeled GREEN or fixed by changing validated Task5/C02 tests. Hosted complete current-source foundation remains mandatory.
- Added opt-in existing metadata-only pytest journal for Task6 command only, with exact case/count/exit reporting and preserved failing exit code; existing service/test/process/supervisor bounds and workflow remain unchanged. Task6 IN PROGRESS pending focused and cumulative hosted GREEN/security review.

### Task 6 corrective behavioral RED and review (2026-10-09)

Implementation candidate `caea3448d6c91df92acd851fc086f80cdac24aea`, tree `92337f2f7746bea2621856964c444077d317bd41`, hosted run `37950917446` attempt 1: real PostgreSQL job `113889154234` failed naturally (exit 1, 126.4s, complete process cleanup). Metadata-only artifact `11624984400` records focused **55 passed / 1 failed / 0 skipped**, pytest exit 1: `test_credential_receipt_version_and_reclassification_denied` expected immutable-target rejection but received `ProfileNotFound` from declaration lookup. Fix checks immutable category/role before active-role lookup; assertions remain unchanged. Submitted history, safe assets and PostgreSQL race cases passed in this focused candidate, but this is not final acceptance.

Fresh inline security review follows approved plan §16 (no reviewer delegation authorized). It also reproduced an over-restrictive declaration validator: `test_all_declarations_can_be_deactivated_during_private_setup` was real behavioral RED locally, **1 failed / 14 passed**, because empty role selection was rejected. Minimum correction permits empty declarations during private setup; readiness still requires an active declared role. Added regression coverage for every deactivation combination, independent pending-target staleness/counters, identity-name-only staleness and first Nutritionist addition preserving an existing Coach approval. No approval command or staff authority was added to create these fixtures.

Local cumulative unit rerun after installing immutable C01 fixture and building static assets: **527 passed / 11 failed**; remaining failures are inherited native-sandbox clean-pixel/isolation tests on this restricted host. Task 5 sandbox behavior remains untouched and fail-closed. Hosted processing/native-sandbox gates remain mandatory for final acceptance. Task 6 remains IN_PROGRESS until the corrected implementation SHA has new authoritative hosted GREEN.

### Task 6 continuation: corrected-head evidence and final security review

- Preserved clean local Task6 head `a4988e3a1f6739adb4a489ab6a941d8e84189518`; authoritative remote implementation `0153cef544dbf3675fbf6eadf6959b9bb06a8e77` has the identical tree `c0f68f26e9201524f2be68b5cdf8f4d98581dbf0`, and actual remote parent `caea3448d6c91df92acd851fc086f80cdac24aea`. No reset, synthetic-ancestry push, migration or implementation change was made during continuation.
- New corrected-head run [37951875791](https://github.com/alireza-anari/fitlink-v1/actions/runs/37951875791), attempt1: PostgreSQL job [113892445254](https://github.com/alireza-anari/fitlink-v1/actions/runs/37951875791/job/113892445254) passed naturally0 in133.1seconds, complete owned cleanup. Exact required five-file focused command executed against real PostgreSQL17.11/Redis7.4.11: **67passed/0failed/0skipped**, pytest exit0,17.363seconds. Downloaded PostgreSQL artifact11626605845 matched SHA256 `11915e9bfb77aa846a90f4e2076bea3fd873763990402cf715f21b486c8741d2`; its actual call and exit journal was inspected. The cumulative entrypoint additionally passed all installed Tasks1–4 schema/ownership/baseline/upload/receipt/race contracts, additive SQL, drift and domain mypy; inherited269 C02 PostgreSQL cases and real Redis lost-counter restart probe passed beforehand.
- Processing job [113892444707](https://github.com/alireza-anari/fitlink-v1/actions/runs/37951875791/job/113892444707) passed naturally0 in257.4seconds with62passed/0failed/0skipped and complete owned cleanup. Artifact11625988785/SHA256 `e4d782f8aa7b09546681e9e57733318523516421bc0f357a2d6656dd220b84e2` confirms real private ClamAV/MinIO/non-eager worker, receipt-before-prompt, actual worker SIGKILL/broker restart/expired-lease recovery, scanner outage and restored health, actual separate Beat missed-prompt recovery, and blocked additional-seccomp decoder parent-death termination. Storage job [113892445187](https://github.com/alireza-anari/fitlink-v1/actions/runs/37951875791/job/113892445187) passed naturally0 in171.8seconds with91passed/0failed/0skipped and complete cleanup; artifact11625689555/SHA256 `c94e58750a7b0b3f6f0ae9d1fb976438eee189589b2f1bef7e53cb22e2719c92` inspected. Timeout/process-ownership job113892445184 passed its expected finite-cutoff/owned-cleanup fixture; this is distinct from acceptance gates' natural exit0.
- Foundation attempt1 job113892445138 passed frozen dependencies, static/JS/CSS build, Ruff/format/mypy/Django/production and539host unit cases. Its inherited service rehearsal hit the unchanged900second observation deadline (elapsed901.9), with1211passed/0failed/0skipped and complete cleanup. This remains a failure, not full foundation PASS. Failed artifact11627331634/SHA256 `7b0d14288e6f2e0d1c491d60f67f00a16fe0826a6b3e0c4bf0c30589bbde8f26` retained. Ruling: one failed-job-only retry at the unchanged implementation SHA, following Task5's established bounded-run precedent; no test, service, process, supervisor or CI timeout change. Cost if wrong: retry still cannot satisfy the gate unless the complete rehearsal exits naturally0.
- Fresh continuation checks: focused field/binding/CI unit command42passed; whole-repo Ruff lint/format375files and git diff--check passed;130-file inherited-plus-professionals mypy, Django test/deploy checks and frozen lock check passed. Whole local unit command actually ran:528passed/11failed, exit1. Named failures remain the ten `test_clean_pixels_strip_all_metadata` avatar/logo/cover/identity_evidence/credential_evidence PNG/JPEG cases and `test_isolation_denies_network_disk_write_and_privilege`, whose native sandbox cannot initialize on this restricted host. No local cumulative GREEN is claimed. Same-source hosted539unit cases and actual processing sandbox gates are the authoritative environment evidence.
- Separate fresh inline security/scope review: every setup/credential read and mutation derives its owner from a current locked AccountActor before receipt/version details; AssistantMembership is never consulted for authority. User/profile/sorted-role/credential/case/target/asset locks serialize edits, receipt replay and independent PostgreSQL races. Identity and each role increment only their own evidence counter; declaration toggles increment only that role's declaration/ordinary version and retain evidence/decisions. Stale pending targets retain original snapshots/links and append target-specific history, without replacing unrelated approval history or advancing evidentiary decision counters. SQL guards preserve immutable revision/source/owner/role/category bindings. Attachment requires current same-owner exact-purpose/subject safe Task5 processing generation and private ready derivative; foreign/quarantined/unready/rejected/revoked assets fail closed. DTOs expose no source keys/hashes/URLs, and raw delivery remains forbidden. Cosmetic fields never invalidate evidence. No submission/staff decision/restriction/eligibility/public projection, owner/staff UI, Task7/C04 import/route, migration, dependency, inherited C02 test/script, Task4/5 processor or branch-trigger change. Review is explicitly author self-review; the approved no-delegation scope was preserved. No unresolved Critical/Important finding or deferred minor identified.
- Protected refs rechecked by ls-remote: main8ede9a451db6103f4e3ebf65784ee9f16b96feb2; foundation/c01-cloud75c551e5b9bbbfb7777ee52b09a1993b681e921a; accounts/c02-cloud0905be6c6ca608d469fe33e87f514b22591132d1; profiles/c03-plan79fd62e583cbe81f335bb08fce0eb43ff36b0167. Task6 remains IN_PROGRESS while attempt2 foundation job113929659861 runs; successful attempt1 service executions retain their original job IDs above.

Attempt2 foundation job113929659861 reached the unchanged900second deadline (elapsed900.9),1203passed/0failed/0skipped; the final snapshot shows active inherited C02 browser `test_dual_phone_change_proofs_and_session_invalidation` at7.563seconds, healthy PostgreSQL/Redis/MinIO/web/worker/Beat, no database wait rows, host cleanup complete but container cleanup incomplete. This is a failed gate, including its cleanup result. Artifact11633085380/SHA256 `6a65695ccb957bc1caf976c91be189ae9d175cbf30f17488dae124845bde818c` retains this attempt separately from attempt1. Current-source unit/integration session exited0 in258.966seconds, versus226.025seconds in attempt1;539host unit cases and all quality/static/production checks passed again. Ruling: a second failed-job-only retry at unchanged0153cef, based on both attempts having no assertion failures, different cutoff points and measured runtime variation; the failed cleanup is retained rather than converted to PASS. No code, test, timeout, selection, infrastructure gate or Task7 change. Cost if wrong: another bounded failed attempt, and Task6 cannot advance without complete natural-exit/cleanup evidence. Task6 remains IN_PROGRESS for attempt3.

Attempt3 foundation job113936587209 also reached the unchanged900second deadline (elapsed902.4),1206passed/0failed/0skipped, complete owned host/container cleanup. Actual C02 browser session exited0 in207.069seconds; cutoff was while the inherited `docker compose up -d --wait redis` awaited Redis health after its real restart. Current-source unit/integration session exited0 in267.097seconds, versus226.025seconds in attempt1;539host unit cases and quality/static/production again passed. Inspected the complete unchanged verify_c02/verify_foundation commands and final owned-process/service snapshots: no blocked database rows or assertion failures; cutoff moved from browser to broker startup, with measured runtime variation. Ruling: one further failed-job-only attempt at unchanged0153cef, without moving builds outside observation, prewarming/reallocating a gate, changing tests/timeouts or interpreting successful substeps as acceptance. Cost if wrong: a bounded fourth failure; Task6 remains IN_PROGRESS until the full inherited chain naturally exits0. A transient local exec transport disconnection occurred during read-only review; GitHub inspection continued, the local transport recovered and existing ledger edits were preserved. No backup or source reconstruction was requested.

Attempt3 failed artifact11633727038/SHA256 `fc83616d66d59970b57d31ea7001e1bb7ebc0c03da4060c4cea14a0e1f41fcb5` is retained separately; its failed conclusion was not overwritten or treated as PASS.

## Task 6 COMPLETE — verified private professional setup and exact target binding

Authoritative final implementation: `0153cef544dbf3675fbf6eadf6959b9bb06a8e77`, tree `c0f68f26e9201524f2be68b5cdf8f4d98581dbf0`. New implementation-head Actions run [37951875791](https://github.com/alireza-anari/fitlink-v1/actions/runs/37951875791), attempt4, completed **SUCCESS**. Actual run head/tree, all five job verdicts and acceptance logs inspected before this completion record. Attempts2–4 reran foundation only; successful original same-head attempt1 PostgreSQL/storage/processing/ownership executions remain the authoritative executed job IDs recorded above, not newly executed service claims.

- Foundation attempt4 job [113943907111](https://github.com/alireza-anari/fitlink-v1/actions/runs/37951875791/job/113943907111):539host unit cases passed; frozen uv/npm dependencies, CSS/ES modules/hashed static build, Ruff lint/format,95-file inherited/composition mypy, Django test/production checks passed. Complete unchanged exact immutable C01 rehearsal, populated same-database upgrade, current-source complete installed unit/integration C03+C02 suites, actual C02 browser suite, real outbox/Redis/worker/channel reconnection and MinIO restart/final browser smoke all passed. Current-source journals contain **1214passed/0failed/0skipped**, every reported pytest exit0. Supervisor natural0 in713.3seconds, complete owned host/container cleanup; unchanged900second observation window. Successful artifact11634935082/SHA256 `b1ba97650338f5dd73a228a1260da544ac7dd527afb45c02436df3dbda006b4b` is separately retained from all three failed artifacts. Measured variation confirms why no earlier cutoff was relabeled as success.
- Final run job inventory: foundation113943907111 SUCCESS; carried same-source processing113943962886, storage113943908260, PostgreSQL113943909446 and ownership113943909797 SUCCESS. Their actual originally executed attempt1 IDs are113892444707/113892445187/113892445254/113892445184, respectively. Focused Task6 **67passed/0failed/0skipped** and all inherited Task1–5 mandatory service/constraint/race/processing gates remain GREEN at this exact implementation head.
- Security review completed as explicitly recorded author self-review. No unresolved Critical/Important finding or deferred minor; prior behavioral corrections and their RED evidence remain above. Both is exactly two independent declaration rows, with no verified authority; identity and each role have independent evidence/declaration/decision binding semantics. Immutable credential/source/submitted history, private processed attachments, current owner/session authorization, assistant denial, receipt/version/race behavior and cosmetic non-invalidation were verified. No migration, User/schema change, raw-source delivery, public profile/location/search, owner/staff UI, submission/approval/revocation/eligibility, Task7 or C04 behavior was introduced.
- Completion publication is documentation only, retaining the exact validated source SHA/tree and all failed evidence. Guarded non-forced API fast-forward uses the actual remote0153cef parent; no synthetic local Task6 ancestry is pushed. Preserve the local execution checkout and its legitimate existing Task6 commits. Protected references must be rechecked before and after publication. No merge, deployment or later task is authorized or performed. Stop after Task6.

## Task 7 recovery and test-spec checkpoint (2026-10-09)

Exact fresh Git checkout on profiles/c03-cloud: a9aeeb77ddf3a4b0b28ae553c9a510feed8d45ea,
tree a87ad180f7bd013a3b340f036ad0b86a61755c2c. Clean status, staged/unstaged/untracked
inspection empty; no legitimate Task7 work lost or replaced. Remote ls-remote
and authenticated Git ref agree. Task6 implementation0153cef and run37951875791
attempt4 SUCCESS/all five jobs verified. Tasks1–6 remain complete.
Read approved plan and installed schema/guards. Task7 migration impact NONE.
No per-task delegation, Task8/C04, merge/deploy or protected-ref changes.
Python3.13/frozen environment recovered inside scratch; local PostgreSQL/Docker
unavailable, existing hosted gates are mandatory. Unit contract RED8failed,
exit1 on missing five commands/three DTOs. New CI selection test observed1fail
on omitted Task7 gate, then minimum exact selection added; inherited gates,
workflow, timeouts and services unchanged. Task7 behavioral PostgreSQL RED
pending hosted test-spec execution. Test fixtures are synthetic only.

### Task 7 hosted RED and minimum implementation

Test-spec remote302062fa13dbe88e20d6848fc196508201bba2a7/tree4563ebdc64d1b158cb86e45f88cace87003f1c2b;
localc6249b2/e67956ad preserves the original script executable bit, which the
first API tree incorrectly encoded100644. Restore100755 in next guarded tree;
content unchanged. No forced ref or synthetic local ancestry is published.
Run37975683660 PostgreSQL113973261390:269C02 cases passed, Redis quota restart
prepare/verify passed, PostgreSQL17.11/Redis7.4.11 and inherited C03 gates healthy.
New four-file Task7 selection actually executed:29failed/0passed/0skipped,
pytest exit1 in9.143seconds. Downloaded artifact11638432107/SHA256
705ca9fb81cde2c42512a2174c679d07056069051e35ae541c170ebfbc926db1:
actual call traces end at verification_helpers.command AssertionError after
real owned profile/setup/credential fixtures. Natural gate exit1 in123.5seconds,
complete host/container cleanup. Foundation113973261744 passed quality/build
then8new contract failures/540passed; its missing artifact follows early RED,
not a service acceptance claim. Storage113973261867 and ownership113973261910
passed. Processing remains separately observed; this is not Task7 completion.

Implemented draft preparation/submission with immutable relational identity/
role evidence snapshots, targeted withdrawal/history, capability-backed live
assignment/reassignment/start, bounded minimal queue and assigned audited
metadata/derivative reads. Original source delivery remains uniformly denied.
Safe processed asset policy moved verbatim from composition into professionals
and composition delegates to it, preserving Task6 behavior and removing reverse
config imports from domain selectors. Only private derivative IDs/MIME/bytes
(repr-hidden) cross delivery; no source keys, raw hashes or signed URLs.
No migration, decision/revocation/restriction/eligibility/public/Task8 behavior.

Ruling: current-source Task6 absence assertion must now permit exactly
submit_verification, while retaining binding-helper assertions and every Task8
absence assertion. This is a stage-specific scope guard extension, not weakened
Task6 positive behavior. Cost if wrong: explicit Task8 negative assertions and
new Task7 contract still reject premature decision/publication commands.

### Task 7 candidate and review regression specs

Candidate remote10a08c2c8f131db97c61939a29d6839bec989b84/tree
d9791c963f917499456ed62f03b8e653eec21c44 (local38aa1fd identical tree),
new run37976991026. Local51focused Task6/Task7/CI unit cases passed;39-file
mypy,381-file Ruff lint/format and diff checks passed. Drift detected none;
local PostgreSQL is unavailable so SQL/concurrency acceptance remains hosted.
Original executable script mode restored and exact local/API tree equality
verified. No synthetic local ancestry or forced publication.

Fresh inline security review adds actual PostgreSQL regression specs for draft
prepare CAS, submit/edit and reassign/read independent connections, queue25+
cursor and mutation audit rollback. Two suspected Important gaps are pinned
before corrections: draft preparation does not advance its profile CAS anchor;
queue lacks the same operational production closure as assigned-case reads.
A seeded verified_mfa fixture must not open a production queue while no approved
provider/config switch exists. Corrections wait for hosted behavioral RED on
these new specs; no claim of success from source inspection.

### Task 7 corrective RED checkpoints (not acceptance)

Candidate10a08c2/run37976991026 completed FAILURE. Foundation113977679726:
548 unit cases passed; complete installed suite journal1174passed/28failed/
0skipped. One inherited credential rollback failure was AttributeError at its
professional_verification.append_event monkeypatch;27 Task7 cases denied at
accounts.policies.require_account_action because the plan §10 explicit
professional.verify_submit action had not been installed. PostgreSQL113977679618
stopped on that inherited rollback failure before Task7 (artifact11639787171,
not a focused Task7 result). Storage/processing/ownership all succeeded.

Regression-spec93b49191fd2b1bc3c73b0d1edde2b11890880bf7/run37977384614:
foundation113978975341 stopped on unused fixture variable Ruff error;
PostgreSQL113978975649 stopped on the same inherited audit seam. Both failures
are retained, never represented as behavioral RED for the new production/CAS
specs. Processing/storage/ownership succeeded; no weakening or skip added.

Restored the existing trusted append_event seam through a dynamic governance
wrapper so both inherited binding failure injection and current audit failure
injection work. Fixed unused regression fixture binding. Locald9ddd59,
remote dce19ebd46dec4b9fd90ba7a5b2a4794b4b027ae/tree
 df3d77e8169b2bbcdb24d5f157e5e79616f9f05d, run37977960616.

A focused new finite-action unit contract observed1failed/8passed at the exact
require_account_action denial; minimum explicit professional.verify_submit
allowlist addition then26passed with inherited profile policy units. It adds
only the approved action, not a wildcard, grant or account schema change.
This is installation of the Task7 submission dependency, not a restart/redo of
completed Task2. Strengthened fixtures keep real current sessions while
checking actual credential expiry, revoked sessions, inactive owner, non-self
case authority and unbound derivative zero-I/O denial. Reassignment-result
regression now rejects private snapshot/evidence metadata reaching the old
reviewer after assignment has ended. Locald3b6719, remote
 a3e24d7c3bd12fc3da2f7303781126120c6e9517/tree
 a66338a44b936a6a07a264e82be147a24be4101f, run37978323018.
Ruff381 files and95-file inherited/composition mypy pass locally. Hosted
behavioral RED/GREEN remains mandatory; no Task7 COMPLETE claim.

### Task 7 observed review RED and minimum corrections

Run37978323018 PostgreSQL113982149132 actually reached all four focused files:
42passed/4failed/0skipped, exit1 in16.520seconds. Task6 separately67passed/
0failed/0skipped, exit0 in12.631seconds. Artifact11639444517/SHA256
5785194cfca39d5983822971b11078a02afa1bdda5141446e13e11ebc7c10f4a
inspected: failures are draft competing-payload CAS assertion, production queue
not raising, reassignment-result private metadata assertion, and invalid
owner-inactive fixture IntegrityError (account_state_active_consistency).
Natural PostgreSQL gate exit1 in118.9seconds with complete cleanup. All earlier
C02/PostgreSQL/Redis and inherited Task1–6 selections passed before Task7 RED.

Minimum corrections: successful prepare advances the locked profile CAS version
without touching evidence/decision counters; replay remains prior to the fence.
Queue applies the same test/development-only operational closure as assigned
case authority. Assignment result keeps the approved StaffDTO type but exposes
identity/evidence only when the new live assignee is the acting reviewer;
reassignment to another reviewer returns metadata without private evidence.
No generic directory, production MFA shortcut or later-task decisions added.
Inactive-owner fixture now uses valid suspended/is_active=false semantics,
retaining the inherited database consistency constraint unchanged.
Local54 focused inherited-profile/Task6/Task7/CI unit cases,88-file domain mypy,
381-file Ruff lint/format and diff checks passed. Hosted focused/cumulative GREEN
must still be obtained on the exact corrected published source head.

### Task 7 focused GREEN and independent final review

Corrected implementation remote deccbdc8645105c294593ac917b27241c0f5e90b/tree
6dfe634c856a061b9a3af838e146af8ec62ab55f (local09fbbb6 identical tree),
new run37979084358. PostgreSQL113984707573 SUCCESS: exact four-file Task7
selection46passed/0failed/0skipped, exit0 in20.858seconds; Task6 separately
67passed/0failed/0skipped, exit0 in16.310seconds. Real independent-connection
submit/edit/prepare/assignment/read races passed. Artifact11640766171/SHA256
ae9fc9f35a70bd097a9714936d62b9c9cff6b9719ef07d1ace38ca795bc587c7
inspected; natural gate0 in152.2seconds with complete owned cleanup. Existing
C02, Redis restart/quota, schema/constraint/Task1–6 gates retained. Full run
foundation still pending, so this is focused GREEN, not Task7 COMPLETE.

Explicit requesting-code-review skill dispatched a separate read-only reviewer
on the precise base/head (no full session history). It found no Critical or
Important production-code issue. Both Minor findings addressed: historical
identity fixture now really submits, assigns and starts review, then seeds an
independent capable reviewer's immutable historical terminal outcome/counters;
adds rejected/revoked/expired identity-reuse denial, without adding any decision
command. Reviewer caught missing revoked_approval in the new fixture; linked
the exact same-target historical approval, preserving installed CHECK/SQL
guards. Task7 counts now filter the exact selected node prefixes; validated
against the actual prior mixed Task6/Task7 artifact, yielding42/4/0 rather than
including67 Task6 cases. Command selections, strict markers, timeouts and all
inherited service gates unchanged. Ruff381/diff/shell syntax and35 relevant
unit cases pass locally. New final head must revalidate stronger tests and
all inherited gates before completion.

Local complete unit diagnostic had537passed/11failed on this restricted host:
ten existing PNG/JPEG clean-pixel sanitizer cases and existing isolated-process
network/disk/fork/nonroot case. Their privileged sandbox cannot run locally;
no test/code/sandbox relaxation was made. Hosted unit/real processing gates are
mandatory authority. Local migration drift reports none but PostgreSQL is
unavailable locally; no local SQL/concurrency acceptance claimed.

### Task 7 final-head service evidence and retained failed runs

Final validation source remote7a6457a7e969393bcc43417f86597340ad0ef613/tree
38d1c9173ab32915e9e4c798a2bdd7a2cde4fffb (local8d7b226 identical tree),
new run37979891641 attempt1. PostgreSQL113987416117 SUCCESS: exact Task7
selection49passed/0failed/0skipped (all-phase skips0), pytest exit0 in22.512s;
Task6 separately67passed/0failed/0skipped, exit0 in16.081s. Real independent
connections cover duplicate submit, submit/evidence edit, competing prepares,
assignment CAS, reassignment/read; stronger valid/invalid historical identity
fixtures all passed. Real PostgreSQL17.11/Redis7.4.11;269 inherited C02 cases
and durable Redis quota restart prepare/verify passed. Natural cumulative
PostgreSQL gate0 in149.8s, complete cleanup. Artifact11640062992/SHA256
21f99c50eb075bf9c29ef953397c0321817f7aeee81d47029fa38eb8cff1a6e2
inspected; each focused pytest exit0 with no mandatory skip.
Storage113987416067 SUCCESS:91passed/0failed/0skipped, exit0, real private
MinIO/owned upload contracts; artifact11640926407/SHA256
5988fd3d89ec338fbae9b43ac829ba76e644b4deaadd7e7357e37cb4b418f708.
Processing113987416318 SUCCESS:62passed/0failed/0skipped, exit0, real private
scanner/non-eager worker; natural0 in315.7s, complete cleanup; artifact
11639918302/SHA25618de3c155995182d8b2006553f890e7030750692ae0553bb58d13bedb3e45674.
Ownership113987416375 SUCCESS: deliberately forced isolated Compose timeout
probe, expected diagnostic failure=true, complete owned cleanup in4.3s;
artifact11640092382/SHA256
1f6a52c71b1e5f54368d4d87690e384248b729cbd54eb4cee660772d53125e5e.
All those jobs executed at this exact final source; no substituted-source
service claim. Foundation is still pending at this checkpoint.

Prior complete failed foundation runs retained: dce19ebd/run37977960616 job
113980907755 had548host unit passes and1175passed/33failed/0skipped in the
installed journal, natural1 in672.4s from the missing finite action. a3e24d7/
run37978323018 job113982148763 had549unit passes and1209passed/4failed/0skipped,
natural1 in504.3s from the observed three review gaps/invalid fixture.
Corrected deccbdc/run37979084358 foundation113984707464 had1253reported
passes/0failed/0skipped but the unchanged900s observation expired at901.9s,
complete cleanup, observed_returncode=null. Artifact11640977385/SHA256
be494fd0efc098d3394f3920567bf4d1693ae949135c0f7aeea3e691e853c983.
It is FAILURE and is not Task7 acceptance or complete inherited gate evidence.
No timeout increase, cutoff success relabel, test skip or service weakening.

Reviewer rechecked the corrected historical same-approval fixture and final
source tree; all Critical/Important/Minor findings resolved. Review is source
inspection only, distinct from hosted acceptance evidence.

## Task 7 COMPLETE — immutable submission and assigned private review intake

Authoritative final Task7 implementation SHA:
`7a6457a7e969393bcc43417f86597340ad0ef613`, tree
`38d1c9173ab32915e9e4c798a2bdd7a2cde4fffb`. NEW hosted GitHub Actions run
[37979891641](https://github.com/alireza-anari/fitlink-v1/actions/runs/37979891641),
attempt1, completed **SUCCESS** at2026-10-09T19:36:30Z. Actual run head/tree,
all five job verdicts, mandatory step inventory, logs and downloaded acceptance
journals inspected before this completion record. No rerun/carried job or
substituted-source acceptance in this final run. No mandatory step/test skip.

- Foundation [113987416252](https://github.com/alireza-anari/fitlink-v1/actions/runs/37979891641/job/113987416252) SUCCESS.549host unit cases passed in19.69s; frozen uv/npm dependencies, CSS/ES modules/hashed static build, Ruff lint/format, inherited/composition mypy, Django test/production checks passed. Complete unchanged immutable exact C01 rehearsal and populated same-database upgrade passed. Current-source complete installed unit/integration suite1216passed, actual C02 browser38passed, browser smoke/Redis/channel/non-eager worker/MinIO restart and final smoke passed. Journals total **1264passed/0failed/0skipped**, all-phase skips0 and all six pytest exits0. Supervisor natural0 in738.9seconds, complete owned host/container cleanup; unchanged900second observation. Downloaded artifact11640768824/SHA256 `ed77f5930f6047ee93f9d9ac6a0a6b8acba3d3f6cdf9edae0d501a76c9efdaa0` is separately retained from every earlier failed artifact.
- PostgreSQL113987416117 SUCCESS; focused Task7 **49passed/0failed/0skipped**, Task6 **67passed/0failed/0skipped**, real concurrency and inherited C02/Task1–6 SQL/service/Redis restart gates GREEN. Processing113987416318 SUCCESS (**62/0/0**), storage113987416067 SUCCESS (**91/0/0**), ownership113987416375 SUCCESS. Exact service artifact IDs/hashes and measured exits are recorded immediately above. All jobs executed at this implementation SHA in attempt1.
- Security/code review complete with separate read-only reviewer; all Critical/Important/Minor findings resolved and subsequent real PostgreSQL tests GREEN. Current active adult normal owner/account authority remains separate from declarations. Immutable independent identity/Coach/Nutritionist snapshots/evidence, current evidence/category matching, target-only withdrawal and coarse owner history, capability-backed assignment/reassignment/start, minimal queue25/cursor, non-self current assigned case detail and audited sanitized derivative reads are installed. Competing draft CAS, submit/edit/assignment/read races, live assignment invalidation, fresh case step-up/reason/current auth/session/owner denial, audit rollback/no evidence release and raw-source denial verified. Production staff verification remains closed pending reviewed provider/config. No source keys/signed URLs/raw hashes in DTOs or audit/outbox values.
- Migration impact **NONE**; installed schema and all guards preserved. No workflow/timeouts/service-gate change, dependency change, User/schema rewrite, approve/reject/revoke command, role restriction, publication_eligibility/verified_roles, public profile/Marketplace, Task8 or C04 work. Tasks1–6 remain COMPLETE; Task7 alone completed. No merge, deployment or force push. Protected main/foundation/c01-cloud/accounts/c02-cloud/profiles/c03-plan refs retained.
- Completion publication is documentation only, retaining this exact validated implementation source and every failed checkpoint. Guarded non-forced fast-forward from actual remote7a6457a7 parent; no synthetic local ancestry is pushed. Legitimate local Task7 commit history preserved. Verify exact remote/documentation tree and protected refs after publication. **TASK_7_COMPLETE — STOP; do not begin Task8.**

## Task 8 recovery and behavioral specification (2026-10-09)

Authorization: C03 Task 8 ONLY; Tasks 1–7 remain COMPLETE. Fresh isolated
checkout starts at b21534918d96300a8812c5b07aca672ebcfafde6, exact tree
ce2bd97fdfd9d712bdb1a202a8ba827fb1e6c512. Initial staged/unstaged/untracked
inspection empty. Protected refs match the approved four immutable baselines.
Task 7 run37979891641 attempt1 verified head7a6457a/tree38d1c91, SUCCESS,
all five required jobs successful. No Task7 documentation-run reopening.
Python3.13.15/frozen dependencies recovered; local PostgreSQL/Docker absent,
hosted real services mandatory. Baseline CI/intake unit selection35passed.
Shell push has no credentials; guarded authenticated GitHub API synchronization
uses real published parent, exact tree/modes and force=false.
Task8 unit RED7failed/0passed: four missing commands, typed eligibility/binding
contracts and missing CI selection. Full focused specification collects71cases
without collection errors. Minimal exact Task8 cumulative selection added,
inherited commands/timeouts/services/workflow unchanged. No migration.
Hosted PostgreSQL behavioral/race RED pending. No Task8 implementation yet.

### Task 8 RED observability follow-up (no production implementation)

Test-specification API commit `fa3d0c9c42e4c987549b7ac7399a38bba5455dd4`,
tree `4f612a25ddddeb5062e82cfe8d45340d90b3832b`, run `37985939065` attempt 1:
Foundation unit check fails on six missing Task 8 contracts (550 passed).
PostgreSQL reaches the four new Task 8 suites and exits naturally with status 1;
inherited C02 has 269 passed and the durable Redis restart probe passes.
Storage, processing, and timeout ownership jobs pass. PostgreSQL artifact
`11643551462` has digest `sha256:aa04ba4ea5b8f84764882cf1b31e79b52cc59d3a2e56194850786deab4f08e6b`.
The artifact reader returns a ZIP reference but materialization returns HTTP 403;
the supervisor intentionally suppresses raw child output. Individual PostgreSQL
RED failures remain unclaimed until their redacted journal can be read.
The permitted minimal workflow adaptation adds an always-run metadata-only
journal report using the incremental script, outside the supervisor. It neither
changes pytest selection nor masks the cumulative gate exit, and adds a bounded
30-second reporting command. Production Task 8 code is still absent.

### Task 8 resumed RED and candidate implementation (2026-10-10)

Fresh checkout inspected clean at published b4f5e6c8f9438ebcfeb0ec40dc693a4f2968e1b6,
exact tree dd679175be3dc05473c02dc90c27ee0d4f265daa. No previous unpublished
implementation is available in this workspace; no claim of local-state recovery.
Protected four refs match the immutable baselines above. Tasks1–7 stay COMPLETE;
Task8 ONLY, no Task9/C04/merge/deploy/force/protected-ref mutation.

Actual run37987556299 attempt1 PostgreSQL114013212963 log inspected. Metadata-only
journal contains86 focused call failures/0passed/0skipped, pytest exit1 at48.837s;
new C02 authority/reassignment interleavings explain the increase from71.
All are AssertionError at missing Task8 commands or assigned binding reader,
after actual submitted/assigned fixtures. Inherited269C02, Redis durable restart,
installed Task1–7 gates passed; storage114013213186, processing114013213041 and
ownership114013212607 succeeded. Foundation114013213115 failed on missing unit
contracts before its regression gate. These are RED evidence, not acceptance.

Installed per-target approve/reject, exact approval-linked revoke, independent
restriction episodes/history, assigned audited review-binding reader and internal
coherent eligibility DTO. Current authority precedes receipt replay; decision
fences include evidence/declaration/decision counters and full restriction history
token, including released episodes. Completed approval evaluation deliberately
does not require old declaration/decision counters to equal current counters.
Only the affected evidence or revoke chain invalidates its approval; current
restriction/declaration predicates separately exclude the role. No public route,
projection, source download, migration or dependency change.

Ruling: extend the current-source Task6 stage guard to permit exactly the now
approved decide_verification_target command, retaining binding helper checks and
generic approve/publication_eligibility absence in the mutation module. Cost if
wrong: explicit Task8 command tests and scope gates still reject generic or public
authority. Original immutable sources remain untouched.

Local Python3.13.15/frozen dev environment, exact C01 fixture, npm frozen install
and CSS build recovered. Focused eligibility/CI/binding35passed. Ruff386 files,
mypy183source files, Django check and diff check passed; migration drift none
(local PostgreSQL unavailable, so not SQL evidence). Complete units545passed/
11failed: ten existing clean-pixel PNG/JPEG cases plus existing process isolation
network/disk/fork/nonroot case cannot run on this restricted host. No relaxation;
exact-head hosted unit/scanner/worker/service acceptance remains mandatory.
Candidate checkpoint is IN_PROGRESS/PENDING_CI, never Task8 COMPLETE.

### Task 8 candidate publication and review regression specification

Candidate local84a1b69503c52a5338d63c2a6d7f3cd8dfb943a6 -> remote
8546825b5e21edb5f5908370cc216082f2f1822d, exact shared tree
26006ad2a3058012b1972b8160c0bad47409d25b, parent b4f5e6c, force=false.
Hosted run38025165827 attempt1 pending. Automatic approval rejected shell push
as unverified/private export; read-only checks proved origin matches public
alireza-anari/fitlink-v1 (private=false), exact execution ref and approved §18
checkpoint synchronization. Limited reviewed source/test/ledger API publication
then succeeded; no runtime fixture, secrets or private user data exported.

Independent read-only review via requesting-code-review identified role-local
malformed current credential propagation as Important and current selected
media safety as a further §7 eligibility gap. New test specifications pin
inconsistent metadata, selected avatar/cover/logo revoke/quarantine/unready
preview, fresh authorized reapproval after revoke and revoke fencing an older
pending review. Expired-evidence decision test renews actual actor/grant/step-up
at the future time and first proves authority so its failure cannot be a stale
session fixture. Shared identity rejection preserves approved role facts.
Production corrections wait for review-specific hosted RED. All prior tests,
CI limits/selections and installed SQL guards remain intact. No COMPLETE claim.

### Task 8 review RED and corrections (2026-10-10)

Candidate remote8546825 exact tree26006ad2 hosted38025165827 attempt1:
PostgreSQL114134360830 naturally exited0 at228.1s, cleanup completed228.3s.
Original Task8 matrix86passed/0failed/0skipped, pytest exit0 at70.626s.
Inherited269C02, Redis durable restart and cumulative Tasks1–7 passed.
Storage114134360918, processing114134361046 and ownership114134360953 succeeded;
foundation114134360971 remains pending at this checkpoint. Not completion.

Review specs local726ab05 -> remote467aa137e7e738806c369190d8af03423823896e,
shared tree0c2ccf6061838a25efb813330d323a4b988db6ca. Actual run38025376489
PostgreSQL114135000215 journal: 15 behavioral call failures (4 malformed
credential cases, 9 selected media safety cases, UTC offset expiry, date.max
OverflowError), 77 observed passes/0skips. The observer ended at240.3s without
natural command exit; incomplete run, not acceptance. Ownership114135000190
failed because owned container never entered running state within probe window;
cleanup and detached-child termination succeeded. No bound or assertion change.

Additional read regression local6b7f3a3 -> remote56057f088f22ebb2f41978962931c2b7f98d85d2,
shared tree54bd706b0cb3eefb95a34a24ccacde212c3fc740. Run38025657690 attempt1
PostgreSQL114135842784 journal observes post-approval assigned derivative read
ProfileNotFound at verification_selectors.py:84 after real authority checks;
16failures/73observed passes/0skips, observer deadline240.3s and no natural exit.
This is actual behavioral RED, not a successful complete test run. Storage,
processing and ownership succeeded; foundation pending.

Corrections isolate malformed current revisions (including missing ORM objects)
to the affected target, retain unrelated immutable approval facts, and revalidate
chosen avatar/cover/logo readiness under the same locked asset set. Typed binding
includes chosen asset identity/version/processing version/current readiness.
UTC date is now used consistently for credential issue/expiry evaluation and
next-expiry boundaries; date.max has no representable later boundary. Ruling:
UTC midnight is the expiry boundary for date-only credentials; cost if wrong is
an explicit policy migration and re-evaluation, never offset-dependent authority.
Terminal assigned evidence reads reconstruct submitted hash counters while still
checking current evidence revision/set/name/source readiness plus fresh case
assignment, capability and step-up. Pending reviews retain current-counter fences.
No source delivery, public route, authority relaxation, migration, dependency,
CI selection, timeout or supervisor change.

Local corrected source: focused35passed; Ruff/format386files; required mypy
selections95 and89sources passed; Django check and diff check passed; drift none
(local service warning means no SQL verification claim). Focused Task8 collection
108 cases. Independent review Important findings await corrected-head hosted
GREEN; Task8 IN_PROGRESS/PENDING_CI, Tasks1–7 COMPLETE, STOP before Task9/C04.

### Task 8 COMPLETE — exact corrected source acceptance (2026-10-10)

Validated implementation local606b1d4ac575bd1eaf8928cc776e8c3599f2450e ->
remote1349e484d3c29b1ad7767fd0840466d9d0bee558; exact shared tree
b4f944dce4df19d7a8a069e330397d8c91795307. Actual remote parent56057f088f22ebb2f41978962931c2b7f98d85d2;
guarded fast-forward publication, force=false. No runtime or private data export.

Run38026094064 attempt2 at this exact SHA is completed/success. Latest job set:

| Gate | Job | Result |
| --- | --- | --- |
| foundation | 114140047055 | SUCCESS, naturally exited0 |
| c02-migrations | 114140048152 | SUCCESS, retained passed same-head execution |
| c03-storage | 114140071494 | SUCCESS, retained passed same-head execution |
| c03-processing | 114140067086 | SUCCESS, retained passed same-head execution |
| c03-timeout-probe | 114140047998 | SUCCESS, retained passed same-head execution |

Only Foundation was rerun. Attempt1 Foundation114137133000 hit the unchanged900s
observer deadline during final MinIO restart/init, after1370 observed passes/
0failures/0skips. Full source unit/integration and C02 browser pytest exits were0,
but final storage/smoke coverage was unfinished, so attempt1 was FAILED and is
preserved as such. Its artifact11660311852 digest
sha256:99bc0e4c8f8ce678ab272e38bc62b625dd7ca953dcf4bbb56422e5fd6e642d57.
The one same-source retry114140047055 naturally exited0 at885.2s and completed
cleanup885.3s, inside the unchanged900s window. Actual Foundation journal1373
passed/0failed/0skipped, all six pytest exits0, no internal error. Complete immutable
C01 rehearsal, exact additive C01→current upgrade, whole unit/integration,
browser sizes, Redis/outbox/worker/channel and MinIO restart/final smoke gates
finished. Host quality556unit tests passed22.35s, frozen JS/CSS/static builds,
required Ruff/format/mypy/Django/production checks passed. Local sanitizer sandbox
limitations remain; exact-source hosted passes supply the required acceptance.

Task8 PostgreSQL114137133005 (retained as114140048152 in attempt2): actual focused
108passed/0failed/0skipped, pytest exit0 at57.139s. Entire cumulative gate natural
exit0 at158.2s, cleanup158.3s; inherited269C02 passed53.79s, actual durable Redis
restart prepare/verify and installed Tasks1–7/SQL/drift/type/race gates passed.
Storage natural exit0 at179.0s/cleanup179.1s;91 selected calls passed, no failures
or skips, actual private MinIO. Processing62passed/0failed/0skipped, pytest exit0
26.644s, natural gate exit0 at313.0s/cleanup313.1s; real scanner and non-eager
durable worker. Ownership probe first reproduces live container after GNU timeout,
then owned container entered running and was removed, detached host child
terminated, supervisor_contract_satisfied=true, cleanup complete. No source,
fixture, assertion, selection, timeout, supervisor or failure verdict changed
between the failed first Foundation attempt and successful retry.

Accepted evidence artifacts (all run38026094064, exact source SHA above):

| Evidence | Artifact | SHA-256 |
| --- | --- | --- |
| Foundation retry | 11660293482 | a23c7c62f1db95e884295a9f901d11a2392e296e556b5bbdd03b32d843ad76d5 |
| PostgreSQL | 11660325718 | 6029f2d1b8d3e8986bed81e3ba5b7a5c533a707226f32c1d041be4ccc1113d19 |
| Storage | 11660830233 | c3033fb64b1070d95a51a171356045fe3c5a3ebb8551b807c8917885d9387e78 |
| Processing | 11660610646 | eb7668cd6c4c0ff49569c02a594489df3ef9e402a557110a1145230c929d2747 |
| Ownership | 11659193977 | a54f0a521f3abecb8ca2dc5ce780616c4ddf833306b4bb7b4883b2beb94a4d73 |

Independent read-only follow-up at corrected local606b1d4 found no remaining
Critical/Important issue in target-local malformed revision denial, media locks/
readiness/binding, UTC expiry/date.max and terminal assigned evidence reads.
Each reproduced review defect now passes in the108-case hosted matrix. Fresh
reapproval after immutable revoke and historical revoke fencing newer pending
reviews are covered. No unresolved Critical/Important finding. Typed eligibility
facts remain internal, retain independent approval history and current role
predicates, and grant no publication/relationship/assistant authority.

Protected refs rechecked after acceptance and remain unchanged:
main8ede9a451db6103f4e3ebf65784ee9f16b96feb2;
foundation/c01-cloud75c551e5b9bbbfb7777ee52b09a1993b681e921a;
accounts/c02-cloud0905be6c6ca608d469fe33e87f514b22591132d1;
profiles/c03-plan79fd62e583cbe81f335bb08fce0eb43ff36b0167.
Exact immutable C01 tree4dff1ebd5a32ed0359552bf29012d9d1ecf09b24 retained.

Tasks1–7 remain COMPLETE. Task8 is COMPLETE. STOP: Task9/C04 not started;
no merge, deployment, force push or protected-ref mutation. This completion
checkpoint modifies only the ledger; acceptance above belongs to the exact
validated implementation SHA, with no claim of re-executing source checks on
this documentation-only descendant.


## Task 9 recovery and lifetime specification (2026-10-10)

Authorization: C03 Task 9 ONLY. Tasks 1–8 remain COMPLETE; Task 10/C04,
merge/deploy/force/protected-ref changes are forbidden. Starting workspace
had no usable Git checkout or unpublished Task 9 work. Fresh isolated clone
at exact 8ce107614ebe78ec7eb183f4874811ffe1e86aca/tree
9f389be42b10b84f4e94fa307330293ea3260593; status/index/diffs/untracked empty.
Remote connector and ls-remote agree. Complete approved plan and ledger read;
existing C02 privacy/hold/outbox and C03 asset/processing/profile evidence inspected.
Task 8 authoritative run38026094064 attempt2 verified SUCCESS at exact1349e484/
b4f944dc. Later documentation run38028083736 is not a reopening criterion.
All protected/unrelated refs match published starting checkpoints; none mutated.

Python3.13.15/frozen dev environment recovered inside scratch; baseline CI/C02
privacy units36passed. Local Docker/PostgreSQL/Redis absent, hosted real services
remain mandatory. New Task9 specification63cases collects without errors.
Initial local unit/CI RED24failed/26passed: missing lifetime APIs/callbacks and
omitted selection; missing interfaces are not misrepresented as behavioral races.
Minimal cumulative selection added; existing report invocation also emits exact
Task9 redacted verdict/counts. Workflow/triggers/services/timeouts unchanged.
Same installed cleanup tests use real private MinIO in the full inherited
Foundation (STORAGE_BACKEND=s3) and deterministic store in PostgreSQL-only CI;
no unavailable-service skip or fake-only overall acceptance is authorized.

Ruling: a committed deletion_pending reservation linearizes cleanup against new
holds, which must deny that already-reserved inventory; long storage I/O remains
outside transactions. Existing valid holds win before reservation. Known source
and derivative tombstones remain discoverable, so a late immutable upload/write
is denied release and erased on subsequent bounded reconciliation. No generic
registry, account erasure pipeline, seeded retention period or schema change.
Cost if wrong: policy/hold review must retain denied/in-progress inventory until
an explicit authorized recovery; no access is granted by retention.
Task9 IN_PROGRESS/PENDING_HOSTED_RED; no Task10 work.

### Task 9 boundary checkpoint and observed RED

- Test checkpoint `e37900f1e6971654ac50cbdbb8407320e47cb70d`, tree
  `f2a3aa93c643d15da92b723bbfbf11fbe38d1eb6`, hosted run `38045752487`:
  PostgreSQL Task 8 remains 108 passed/0 failed/0 skipped. Task 9 reports
  35 failed/2 passed/0 skipped. Missing APIs are contract RED only; the actual
  existing account-security handler fails the deletion/asset/membership state
  assertions. Storage, processing and timeout-probe jobs pass unchanged.
- Local complete unit baseline with the specification checkpoint: 546 passed,
  33 failed; 22 are new missing lifetime interfaces and 11 are the previously
  documented host native-sandbox limitation. No old gate was weakened.
- Closed boundary checkpoint installs typed metadata inventories and trusted
  C03 hold validators/optional governance callbacks. Cleanup deliberately returns
  `denied` until hosted behavioral cleanup evidence is inspected. These are not
  Task 9 completion claims. Local new lifetime+CI contracts: 50 passed; Ruff and
  existing mypy target set pass (95 source files).
- Hold commands lock sorted participants, installed domain anchors, assets, then
  current staff authority and hold rows. C02 default privacy-request validation
  remains exact. Credential holds pin immutable evidence in their assigned case,
  so future credential revisions do not acquire a blanket hold. Existing holds
  remain effective after revocation advances a retained asset's version.

### Task 9 behavioral service RED and implementation candidate

- Boundary checkpoint `6438c670fcdb6babb019c5b74c4a4fe7d76857dd`, tree
  `70a8d045d2633159cae1cd68d8a9c7363363bc12`, run `38046255502`:
  Foundation quality/unit checks pass; its actual PostgreSQL/MinIO complete
  regression reaches Task 9 hold/cleanup race, committed-reservation denial,
  storage failure, policy replacement and late Task 4 upload tests. Behavioral
  RED: 1,335 passed/15 failed/0 skipped. PostgreSQL: Task 8 108/0/0,
  Task 9 48 passed/15 failed/0 skipped. Missing APIs/fixture failures are not
  claimed as cleanup RED. Storage, processing and timeout-probe jobs remain GREEN.
- A closed typed inventory now maps the installed retained classes, classification,
  source/derivative links, explicit policy reference and deletion disposition.
  Immutable non-asset domain records are `retain_only`; C03 does not implement
  their erasure. Inventory overflow denies an incomplete snapshot. It does not
  prevent a record-specific hold or release after 1,001 historical tombstones.
- Independent Superpowers boundary review identified the whole-owner mutation
  cutoff and incomplete inventory mapping. Both were corrected with regressions.
  Hold/release lock only the owner/acting staff and relevant subject/case anchors.
  Case callbacks require the composition's locked-owner context; invoking the
  plain validators through governance cannot bypass the reservation lock protocol.
- Assigned verification-case holds require a live assignment, current named
  `professional_verification` grant, non-self owner/staff, and current
  `privacy_operations` authority with its exact-case recent step-up. Self-assignment
  by an otherwise authorized verifier remains the existing Task 7 behavior; it
  is not a self-review of the owner's records. Credential coverage pins immutable
  case revisions, not later uploads; case holds cover only their linked evidence.
- Cleanup reserves `deletion_pending` under sorted identity/domain/asset locks.
  Effective policy class/purpose, approved positive numeric duration, backup
  approval, asset version, subject binding, active holds, mutable use and the
  complete bounded key inventory are rechecked before each physical deletion
  and completion. Delete/head I/O occurs after commit, outside all transactions.
  Wrong or colliding source/derivative keys deny deletion. Partial storage or
  audit failure leaves a durable reservation and bounded retry; successful
  completion has one transactional `asset.deleted` audit.
- Deleted metadata retains its known source and all processing-generation keys.
  Repeated cleanup and the fair bounded scan remove late stale upload/derivative
  writes without bucket listing or renewed owner/staff access. New holds deny an
  already committed reservation; prior holds prevent it. Expired uploads become
  abandoned without implying a retention duration or immediate erasure.
- Engineering ruling: reuse the installed separate private reconciler's 30-second
  tick with an independently opt-in `ASSET_CLEANUP_ENABLED` (default false) and
  maximum 100 scanned assets. The plan's 300-second cleanup interval is an
  engineering default; adding a second schedule or changing inherited C02 Beat
  contracts is unnecessary. Fair rotation includes held/missing-policy/tombstone
  rows. Actual effective policy durations remain mandatory and unseeded.
- Current account-security effects invalidate up to 100 live assets per event;
  the durable scan reconciles remaining current-state rows after missed delivery.
  Installed self-baseline consent is validated without inventing media consent
  or new C02 events. Retention adds no ordinary read, signing or processing grant.
  Outbox cleanup receipts perform metadata checks only. A new in-memory fake store
  is never treated as a persistent erasure backend; explicit injected stores or
  the installed private S3 adapter provide cleanup I/O authority.
- Focused candidate collection: 77 cases. Local lifetime/CI/C02 privacy/outbox
  contracts: 73 passed. Ruff, formatting, inherited mypy targets and expanded
  domain targets pass; Django test and production checks pass. The 11 existing
  native-image sandbox cases remain host-limited locally and are mandatory hosted
  gates. Task 9 remains **IN PROGRESS / PENDING_CI**, not COMPLETE.

### Task 9 complete-candidate review regressions

- Read-only independent review of candidate `cf07b6a` identified three important
  lifetime gaps: received/unfinalized quarantine after admission expiry,
  terminal rejected processing sources, and an unrelated active-hold inventory
  cutoff. It also requested serialization of the current assigned-verifier grant.
- Test-only checkpoint adds nine cases (86 total Task 9 cases): actual stored
  received/finalized sources, actual scanner rejection/lease exhaustion with and
  without an existing record hold, 1,001 unrelated C02/baseline holds, and an
  independent PostgreSQL grant revocation participant. Candidate production code
  is unchanged in this checkpoint; hosted behavioral RED is pending inspection.
- Ruling for the rejected-source gap: the cleanup reconciler will revoke terminal
  rejected metadata first and begin retention at that transition. Erasure still
  accepts only eligible abandoned/revoked/reserved/tombstoned private inventory;
  no Task 5 processing behavior, admission deadline or production retention
  duration is changed. Accepted retryable quarantine must remain retryable.
- Review findings remain open. Task 9 is **IN PROGRESS**, not COMPLETE.

### Task 9 reviewed fixes and second implementation candidate

- Candidate `cf07b6abd3d94f09cddea1de79ff94f7577a46e4`, tree
  `eb95533ef0db7af19c6ff3a19fd4c74acaa7cb76`, run `38047601785`:
  PostgreSQL Task 9 75 passed/2 failed/0 skipped; Task 8 108/0/0.
  One Task 9 failure is a duplicate effective-policy test fixture (not behavioral
  RED); the other is a real hold/cleanup race. The caller's timestamp could
  precede a hold committed while cleanup waited on the owner lock.
- Review regression checkpoint `3cebf07aca7fdd0e14bccb2d7c55f5a5827cd934`, tree
  `7a9c4022f1d12f3773bf2948c0cc50fa23698784`, run `38048067364`:
  PostgreSQL Task 9 76 passed/10 failed/0 skipped; Task 8 108/0/0. Nine
  concrete behavioral failures confirm the lifetime gaps/races; the separate
  duplicate-policy fixture failure is excluded from behavioral RED claims.
  Unfinalized quarantine is missed, while accepted quarantine preservation
  already passes. Scanner rejection/exhaustion are real processing outcomes.
  Concurrent verifier-grant revocation exposes an unlocked snapshot read.
- Corrected cleanup evaluates current time after identity/domain/asset locks at
  every destructive check. Exact source/case/credential evidence predicates
  filter relevant holds before the inventory bound; 1,001 unrelated active
  privacy-request/baseline holds do not become blanket owner retention.
- The assigned verifier's current grant row is now locked. Expired unaccepted
  quarantine becomes abandoned; accepted retryable quarantine remains intact.
  Terminal rejected sources become revoked first with a conservative retention
  anchor, preserving existing holds and requiring the same effective policy.
  The synthetic policy helper reuses the unique exact effective class/purpose.
- Added a deterministic post-call-timestamp hold regression (87 Task 9 cases).
  Local focused contracts: 73 passed; Ruff/format, expanded mypy (187 source
  files), Django checks pass. Hosted acceptance and repeat review remain pending.
  Task 9 is **IN PROGRESS / PENDING_CI**; no Task 10 work.

- Repeat read-only review of the second implementation candidate identifies no
  remaining Critical/Important finding. It recommends a precise post-lock
  retirement timestamp. Two additional behavioral regressions cover a delayed
  terminal-source tick and a delayed current-owner effect (89 Task 9 cases).
  This test-only checkpoint does not change production code; its hosted results
  must establish the timestamp behavior before the precision fix. No Task 10.

### Task 9 retirement clock RED and final implementation candidate

- Second implementation `cd7d57d29fa8caa5634f454259dfd19f8985d8f7`, tree
  `eedc8130b1a0fb0e02f3f463aff57d098712c0df`, run `38048451978`:
  storage/processing/timeout jobs pass. The PostgreSQL observer reaches its
  unchanged 240-second deadline before completing the Task 8 selection (96
  calls passed, zero failed calls; no Task 9 cases executed). This incomplete
  attempt is neither Task 9 behavioral RED nor a reason to reopen authoritative
  Task 8. No gate/timeout/assertion was weakened to obtain an acceptance result.
- Timestamp regression checkpoint `e3235a85c4c265692b17174cc981f8799358652e`,
  tree `fdb6ebeb47989e70de4bf55cf16a33fbd5fb0400`, run `38048589560`:
  PostgreSQL Task 8 108/0/0; Task 9 87 passed/2 failed/0 skipped, both new
  delayed-retirement behavior assertions. Earlier reviewed fixes pass unchanged.
- New retirement timestamps are now `max(requested tick, current time)` after
  the affected asset locks, for both terminal/admission reconciliation and
  bounded current-owner effects. The policy duration begins at actual retirement;
  existing earlier revocation anchors remain intact. Terminal-source tests use
  the resulting retirement anchor for due time, rather than assuming no lock
  wait. No duration, schema, Task 5 processing, workflow or old gate change.
- Earlier first-candidate actual private MinIO/complete Foundation backend:
  1,402 passed/1 failed/0 skipped; the sole failure was the corrected synthetic
  duplicate-policy fixture. This is supporting recovery evidence, not final
  acceptance. Final exact implementation GREEN/review remain pending.

### Task 9 final source review and acceptance blocker (2026-10-10)

**Authoritative current status: IN PROGRESS / BLOCKED_CI, not COMPLETE.**
Tasks 1–8 remain COMPLETE. Task 9 remains the first incomplete task.
Task 10/C04 have not begun.

Final implementation source:
- Commit `23a4d65a2353f39263cbc73186c6c4255b27d465`
- Tree `55421900ffdf783543e17a7115113e440fbc49ce`
- Exact-source Actions run [38049057652](https://github.com/alireza-anari/fitlink-v1/actions/runs/38049057652),
  attempts 1–3. All three attempts FAILED at aggregate diagnostic observation
  deadlines. They are supporting partial evidence, never authoritative GREEN.

| Attempt | PostgreSQL job | Observed result | Foundation job | Observed result |
| --- | --- | --- | --- | --- |
| 1 | 114204330820 | 240.3s deadline; Task 8 100 passed/0 failed/0 skipped; Task 9 not reached | 114204330661 | 900.7s deadline; 1,417 passed/0 failed/0 skipped; backend pytest exit 0, complete rehearsal unfinished |
| 2 | 114207095197 | 240.2s deadline; Task 8 99 passed/0 failed/0 skipped; Task 9 not reached | 114207095343 | 901.8s deadline; 1,415 passed/0 failed/0 skipped; backend pytest exit 0, complete rehearsal unfinished |
| 3 | 114210539180 | 240.3s deadline; Task 8 96 passed/0 failed/0 skipped; Task 9 not reached | 114210539219 | 902.0s deadline; 1,455 passed/0 failed/0 skipped; three pytest exits 0 (316.161s, 201.237s, 2.110s), complete rehearsal unfinished |

The complete Foundation backend selection includes all four installed Task 9
files against actual PostgreSQL/private MinIO. Its passing backend execution
does not replace the missing final full rehearsal or PostgreSQL cumulative
completion. Counts include whole observed call journals and may differ between
attempts because later rehearsal phases reach different stopping points.

Latest successful same-source service jobs: real scanner/non-eager processing
114210539810; actual Compose timeout/ownership probe 114210540156; private
MinIO/upload/storage 114210540259. All three SUCCESS. No required gate was
skipped, allowed to fail, narrowed or represented as a complete run.

Final read-only independent boundary review found no remaining Critical,
Important or Minor source finding; acceptance is conditional on full exact-head
GREEN. Local pre-disconnection focused checks: 73 passed; Ruff/format, expanded
mypy (187 source files), Django test/production checks and diff checks passed.
These checks are supporting evidence, not substitutes for hosted service gates.

Task 8 authoritative implementation/tree/run remain
`1349e484d3c29b1ad7767fd0840466d9d0bee558` /
`b4f944dce4df19d7a8a069e330397d8c91795307` /
38026094064 attempt 2 GREEN. The later documentation-triggered failed
38028083736 is not implementation evidence. No Task 8 reopening.
The authoritative Task 8 Foundation completion was already 885.3s inside the
900s observer window; Task 9 adds 89 mandatory lifetime/hold/cleanup cases.

**Concrete proposed recovery, NOT implemented or authorized by this entry:**
`docker/c03_gate_diagnostics.py` line 51 currently hard-caps observer windows:
`WINDOWS = {"postgresql": 240, "storage": 600, "foundation": 900}`.
A narrowly scoped exception would change only those aggregate limits to:
`WINDOWS = {"postgresql": 330, "storage": 600, "foundation": 1200}`.
The existing environment override cannot exceed these caps. This file is outside
the approved Task 9 file list; no override, cap change or indirect bypass has
been made. Approval is required before modifying it. Preserve per-suite 180s
guards, incremental child 300s limit, PostgreSQL job 15min/Foundation job 60min,
timeout probe, all Tasks 1–8 assertions/selections/services and literal triggers.
After any approved configuration change, review the bound/negative contracts,
execute all exact-head jobs, and record implementation/tree/actual GREEN before
changing Task 9 status. No production retention period has been seeded.

Final GitHub comparison from starting head `8ce1076` to the implementation
shows only the 17 approved Task 9 source/test/CI-support files and this ledger.
No workflow, migration, dependency, approved plan or other domain file changed.
All eight protected/unrelated branch refs verified unchanged immediately before
this documentation checkpoint:
- `main`: `8ede9a451db6103f4e3ebf65784ee9f16b96feb2`
- `foundation/c01-cloud`: `75c551e5b9bbbfb7777ee52b09a1993b681e921a`
- `accounts/c02-cloud`: `0905be6c6ca608d469fe33e87f514b22591132d1`
- `profiles/c03-plan`: `79fd62e583cbe81f335bb08fce0eb43ff36b0167`
- `diagnostics/c03-task4-foundation-triage`: `5f53cfda706a8bccbe3fad7ca569e9dd607751da`
- `diagnostics/c03-task4-postgresql-slice-a`: `e034e9d2501b2d1e6f4a0689af923e900596bd3b`
- `diagnostics/c03-task4-postgresql-triage`: `977383c4bb4e1b8ec0a79b9749ea0efd8a91375d`
- `diagnostics/c03-task4-storage-slice-b`: `7361d9c8fd6e9db057f3e68988474e2258ee6838`

The execution server disconnected after source publication; GitHub exact-source
readback and branch verification remain available. Last successful local index
was clean at the published implementation; there is no known unpublished Task 9
work to overwrite. This documentation-only checkpoint preserves all final
implementation source blobs. Any workflow triggered by this ledger update is
documentation evidence and cannot substitute for final implementation GREEN.
No reset/clean/stash, merge, deployment, force push or protected-ref modification.

### Task 9 authorized aggregate observer-cap recovery (2026-10-10)

- User explicitly authorized only `docker/c03_gate_diagnostics.py` aggregate
  `WINDOWS`: PostgreSQL 240 -> 330 seconds; Foundation 900 -> 1200 seconds;
  storage remains 600 seconds. This supersedes the approval-pending proposal
  above, without extending authorization to any other timeout or gate change.
- Fresh isolated checkout recovered exact published head
  `e2458ca4522c7e11ec134cb07caabcec18f3c36a`, tree
  `f41072b1dc533d8d6a08094d23c4c296412e7612`. Comparison to final candidate
  `23a4d65` confirms the intervening checkpoint changes only this ledger.
  No unpublished work reconstructed; all published implementation preserved.
- Source diff verified as the exact one-line authorized replacement. Per-suite
  180s guards, incremental child 300s, PostgreSQL job 15min/Foundation 60min,
  timeout probe, all inherited selections/assertions, storage/scanner/worker
  gates, retention durations, triggers, migrations and dependencies unchanged.
- Focused local command: `uv run --frozen pytest
  tests/unit/c03/test_gate_diagnostics.py tests/unit/c03/test_ci_contract.py
  tests/unit/c03/test_privacy_inventory.py tests/unit/test_c03_acceptance.py
  tests/unit/test_c03_foundation_evidence.py
  tests/unit/test_c03_storage_slice.py -q --strict-markers`: exit 0,
  85 passed in 8.36s, zero skipped. Existing deadline/owned-child cleanup,
  natural-success acceptance, unknown-cleanup denial, selection and workflow
  negative contracts retained unchanged.
- One-off local boundary verification: exact new cap map/source replacement
  and 24 invalid/nonfinite/over-cap observations rejected before child launch.
  Ruff check/format for changed source, incremental shell syntax and
  `git diff --check`: exit 0. Frozen Python 3.13.15 environment recovered;
  no lock/dependency edit. Local checks are supporting evidence only.
- Protected main/foundation/accounts/planning refs rechecked unchanged.
  Publish only a guarded non-forced fast-forward on profiles/c03-cloud, then
  require a new exact-implementation hosted run with all five jobs GREEN.
  Task 9 remains IN PROGRESS / PENDING_CI; Tasks 1–8 COMPLETE; no Task 10/C04.

### Task 9 authoritative hosted completion (2026-10-10)

**Current authoritative status: TASK_9_COMPLETE.** Tasks 1–9 COMPLETE;
Task 10/C04 have not started. C03 overall remains IN PROGRESS.

- Final implementation SHA: `27d7916432c26effa9fdf735fd1dffc0ff5a8ec5`.
- Final implementation tree: `571e42ca20df1991dbf4dc93b3b1337a18359003`.
- Parent: `e2458ca4522c7e11ec134cb07caabcec18f3c36a`; guarded
  expected-head update, force=false. Local staged tree and API-created tree
  matched exactly; published readback and clean local index/worktree verified.
- NEW exact-source [Actions run 38053735759](https://github.com/alireza-anari/fitlink-v1/actions/runs/38053735759),
  attempt 1, completed SUCCESS. API run head/tree match the final implementation
  above. All five jobs and every listed step completed SUCCESS, zero mandatory
  step skips. Actual complete job logs and redacted test journals inspected.

| Required job | Exact job evidence | Verified result |
| --- | --- | --- |
| Foundation | [114217876813](https://github.com/alireza-anari/fitlink-v1/actions/runs/38053735759/job/114217876813) | GREEN; 579 current units before rehearsal; complete inherited exact C01 upgrade/current regression command naturally exited 0 in 1021.9s, both host/container cleanup complete |
| c02-migrations / PostgreSQL | [114217876832](https://github.com/alireza-anari/fitlink-v1/actions/runs/38053735759/job/114217876832) | GREEN; 269 inherited cases; real Redis restart/quota gate; cumulative C03 command exited 0 in 219.6s, cleanup complete |
| c03-storage | [114217876999](https://github.com/alireza-anari/fitlink-v1/actions/runs/38053735759/job/114217876999) | GREEN; actual private MinIO/upload slice 91 passed / 0 failed / 0 skipped, complete=true; natural exit 0 in 174.6s, cleanup complete |
| c03-processing | [114217876789](https://github.com/alireza-anari/fitlink-v1/actions/runs/38053735759/job/114217876789) | GREEN; 62 passed / 0 failed / 0 skipped, pytest exit 0; real scanner/non-eager worker/restart/Beat/decoder-parent-death probes; natural exit 0 in 236.8s, cleanup complete |
| c03-timeout-probe | [114217876663](https://github.com/alireza-anari/fitlink-v1/actions/runs/38053735759/job/114217876663) | GREEN; actual Compose timeout probe, owned container removed, detached child terminated, supervisor_contract_satisfied=true |

- Foundation journal totals: 1463 passed / 0 failed / 0 skipped; six pytest
  sessions exit 0. Full current backend 1415; all 38 C02 browser cases; two
  viewport smoke cases before and after service restart; five Redis/Celery/
  Channels recovery cases and one private MinIO recovery case. Backend includes
  all four installed Task 9 files, 89 cases, against PostgreSQL/private MinIO.
  Exact immutable C01 fixture verification, its unchanged full rehearsal and
  populated same-database C01 upgrade remain inside the successful inherited
  command. Unit/quality/static/production steps also SUCCESS.
- PostgreSQL journals: Task 6 67/0/0; Task 7 49/0/0; Task 8 108/0/0;
  Task 9 89/0/0, every selected session exit 0. Task 9 breakdown: inventory
  22, holds 30, deletion effects 23, cleanup races 14. All setup/call/teardown
  reports passed. Full cumulative command completed inside unchanged 300s
  child bound; per-suite 180s guards remain unchanged.
- Foundation artifact 11670379358 SHA256
  `8898d480d9bbb0f1866c9550b3c7592242213d02f7d7c815d4b0fffe72914eb0`;
  PostgreSQL artifact 11670343117 SHA256
  `c178c23b2e55efd1d24f2975c40028cac45f1fad1a22f7eb7ce96a96484b535f`.
  Downloaded ZIP digests and every recorded pytest outcome verified. All five
  artifact metadata records bind to run 38053735759 and implementation SHA.
- Final scope review: only the authorized aggregate observer-cap line and Task 9
  ledger additions differ from preserved candidate `23a4d65`. No behavioral
  failure appeared; no further timeout, assertion, selection, service, workflow,
  migration, dependency or production retention change. Gates remain mandatory.
- Protected main, foundation/c01-cloud, accounts/c02-cloud and profiles/c03-plan
  rechecked unchanged immediately before this documentation checkpoint.
  This ledger-only completion commit preserves the validated implementation
  blobs; its triggered run is documentation evidence, not acceptance authority.
  Prior documentation runs never reopen Tasks 1–8. No merge/deploy/force push.
  STOP after publishing and verifying this Task 9 completion evidence.


## Task 10 recovery and closed-boundary specification (2026-10-10)

Authorization: Task 10 ONLY. Tasks 1–9 remain COMPLETE; no Task 11/C04,
merge/deploy/force or protected-ref changes. Fresh isolated Git clone at exact
b6b07f950a82860fc920a6a1b982fffe19fd526b/tree180a913d43dc0b4ed94d20d814f9cb8b678c5edc.
Initial status/index/staged/unstaged/untracked inspected empty. Remote exact
execution head and all eight protected/unrelated refs verified unchanged.
Approved plan, Task 10/C03-C04 boundary and published ledger inspected. Task 9
run38053735759 attempt1 verified SUCCESS at27d7916432c26effa9fdf735fd1dffc0ff5a8ec5/
571e42ca20df1991dbf4dc93b3b1337a18359003; all five job inventories and actual
complete logs fetched and inspected. Documentation CI is not a reopening criterion.

Frozen Python3.13.15 dev environment recovered; no dependency/lock change.
Local specification RED5failed/57passed (3.60s): missing DTO/private boundaries
and omitted mandatory selections. After minimal same-task cumulative selection
and closed callable boundaries:1failed/61passed (2.06s), missing DTO. Focused
74 cases collect without errors. Real PostgreSQL behavioral RED is still pending;
missing contracts/collection are not race or authorization evidence. Preview
boundary performs existing current actor/owned-profile locks then denies; inert
commands deny until observed hosted positive-command RED. No usable data released.

Ruling: within the explicitly approved Task 10 file surface, assistant changes
use installed professional.profile_changed metadata receipts, advancing only
the ordinary profile version, plus assistant.defined/assistant.revoked audit.
The plan inventories assistant.membership_changed, but its handler is not
installed and handler registry files are outside this task's approved surface.
Do not emit an unhandled event or mutate the registry indirectly. Cost if wrong:
a future approved membership-specific consumer must add explicit handler wiring;
these inert primitives provide no operational/notification/lifecycle effect.

HTTP/native preview adapters and their actual response headers belong to Task11.
Task10 DTO carries private,no-store and noindex,nofollow directives; scope tests
require no preview/public/assistant/future route now. All established service,
workflow, assertions, inherited gates and observer/per-suite/child bounds unchanged.
Task10 IN_PROGRESS/PENDING_HOSTED_RED. No Task11 implementation.

### Task 10 continuation, observed PostgreSQL RED and implementation candidate

- Recovery preserved exact local/remote `c7a0b349f16b2a06340ef4a0aa4ef0db896c472f`,
  tree `9b9a82a354808c77dce6f07e409099597e4dbcde`, and both unpublished
  owner-media/assistant replay test refinements. No reset/clean/stash/overwrite.
  All eight protected/unrelated refs still match the baselines above. Task 9
  authoritative run38053735759 attempt1 reverified SUCCESS at27d7916/tree571e42c.
- Actual test checkpoint run38058891938 attempt1: PostgreSQL114232907724
  naturally exited1 at286.3s with complete cleanup. Task10 **23failed/51passed/
  0skipped**, all failed call frames inspected: owner preview fails at its closed
  ProfileNotFound boundary, assistant positives fail at its closed PermissionError
  boundary, and the missing explicit DTO contract fails. No collection/fixture
  errors counted as behavioral RED. Task8 108/0/0 and Task9 89/0/0 remain GREEN;
  inherited269C02 and real Redis durable quota restart passed. Storage/processing/
  timeout jobs succeeded. Foundation fails on the expected missing DTO unit;
  later skipped rehearsal is not acceptance.
- Implemented explicit frozen private preview/role/media/membership DTOs. Owner
  actor/state/session/auth_version/exact profile are revalidated under locks;
  verification never gates own preview or publishes anything. Query-time identity
  and capability facts reuse Task8 coherent eligibility/binding; preview excludes
  internal binding, identity name, credentials, evidence, keys/hashes and staff
  explanations. Sanitized current private avatar/cover/logo derivative references
  carry only UUIDs/purpose/MIME, no URL or source delivery. HTTP/native adapters
  remain Task11; DTO private/no-store and noindex/nofollow directives are retained.
- Internal define/revoke commands derive owner from current AccountActor, lock
  definition participants in stable User PK order, reject self/unavailable target,
  retain fixed client_support/defined/revoked state, receipts and optimistic CAS.
  Duplicate definitions return current row; old operation replay returns current
  authorized membership including revocation. Audit/outbox/receipt effects are
  transactional; no invitation/activation/operational/client/entitlement behavior
  or fabricated max-two rule. The previously recorded installed metadata-event
  ruling stands; no registry/handler, future-domain, schema or migration change.
- Local supporting checks:62scope/CI cases passed; whole-repo Ruff passed and
  format400files passed; professional mypy41sources and inherited/composition
  mypy95sources passed; Django test/production and diff/shell checks passed.
  Recovery found a truncated ignored Python logging bytecode cache; preserved
  it by renaming only that generated cache, then reran checks successfully.
  No source/dependency/lock workaround. Full local units and exact-source hosted
  gates remain required; Task10 IN_PROGRESS/PENDING_CI, never COMPLETE.
