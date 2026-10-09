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
