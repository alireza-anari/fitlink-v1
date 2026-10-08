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
