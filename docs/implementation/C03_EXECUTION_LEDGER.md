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

Task 1: STARTED — CI bootstrap only; schema implementation not started.
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
