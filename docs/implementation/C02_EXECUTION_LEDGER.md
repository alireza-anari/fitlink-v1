# C02 execution ledger — plan: docs/superpowers/plans/2026-10-05-c02-accounts-authentication.md

## Immutable baseline and authorization
- Remote C01 SHA: 75c551e5b9bbbfb7777ee52b09a1993b681e921a.
- Local C01 SHA: 5881a2792beca2dbd56cfb9ec6cecf910879d6ab.
- Verified exact C01 tree: 4dff1ebd5a32ed0359552bf29012d9d1ecf09b24.
- Private repository verified via authenticated GitHub API; push permission present.
- C01 branch/head verified; final Actions run 37296846443 job111719979967 completed success, all listed steps success.
- C01 execution ledger inspected; final exit supersedes historical blocked entries.
- Isolated C02 worktree: /workspace/scratch/431fd37d49de/fitlink-c02.
- Local and remote branch: accounts/c02-cloud; remote created from immutable C01 SHA.
- Plan materialized byte-for-byte from corrected attachment; SHA256 60cf2adadb323f303203638c0493914c7d37e941f0a69881f6927f9de40bba83.
- Environment: Linux Cloud, Node24.19.0, uv; existing workspace CPython3.13.15 and locked C01 environment available. Docker integration belongs to GitHub Actions.
- User authorized implementation/sequential16 tasks, API synchronization and CI only on C02. No Foundation/main edits, merge, deployment, SMS vendor or C03.

## Task states
1. COMPLETE — input/configuration contracts; Cloud and actual CI green.
2. COMPLETE — additive schema/upgrade; Cloud, PostgreSQL and full Foundation CI green.
3. IN_PROGRESS — audit/outbox/staff authority RED preparation.
4–16. UNSTARTED.

## Pre-flight shared interfaces
- 1→2/4/5/6: typed policy, canonical identity, HMAC domains/key IDs; all quota versions must aggregate retained keys.
- 2→4/5/6/7: durable anchors, challenge generation/delivery/proof state and session controls.
- 3→5–14: required audit callback and outbox in same connection/transaction; accounts cannot import governance.
- 4→5/6/8/9: conservative failure reservations precede proof comparison; successful cleanup required before session issue.
- 5→6→8/9: code consume is separate from one-time application of context-bound proof.
- 7→8/9/12/14: mutation locks current User and rechecks auth version/state; middleware alone insufficient.
- 3/13→16: explicit durable effects/retry scan; C01 empty Beat allowlist evolves only when scan implemented.
- 2/15/16: preserve immutable C01 fixture for populated migration and original Foundation browser/scope evidence.
- Ruling: use isolated git worktree with matching local C01 tree and different local ancestry — exact tree equality was verified before branching; preserve Foundation history and refs.

## Evidence and findings
No C02 implementation test or migration has run yet. No C02 PASS claim.

## Task 1 evidence
- First RED had test helper import failure, not behavior; corrected pytest pythonpath to preserve existing shared subprocess fixtures when selecting nested test paths.
- Behavioral RED: 37 failed /1 passed; missing named phone/date/IP/config contracts and production missing-key rejection. Log: .superpowers/task1-red.log.
- GREEN:38 input/config cases passed, including exhaustive supported-calendar daily roundtrip and published vectors.
- Full Cloud regression:108 passed after building CSS/hashed static and adding synthetic production key fixtures. No existing security assertion weakened.
- Ruff lint/format, mypy15 files, Django check, JS syntax and offline production deploy check exit0. Lockfiles/schema/User/initial migration unchanged.
- Calendar source/license reviewed through authenticated read-only GitHub API; MIT source blob14309485f93dd8eff2e30d7ba20ba38115457a74. UI only accepts1200..1500; no approximation beyond range.
- Security review: no persistent codes or production vendor, redacted immutable key ring; production accepts only disabled providers and entry/recovery remain closed.
- Ruling: move C02 workflow trigger enablement forward from Task16 — Task1 and Task2 require actual CI before advancing; existing Foundation gates run unweakened on C02 only — final upgrade/full auth gates are still added in Task16.
- Ruling: explicitly set pytest pythonpath=tests/unit for existing fixture helpers — nested selected tests otherwise fail before contract execution — production module paths unchanged.
- Task1 Cloud GREEN; required CI PENDING_CI. Do not advance to Task2 until CI succeeds.
- Task1 commit: ff143e247452e658a1b39f7c0788dc523e93c8d8.
- Remote sync: local ff143e247452e658a1b39f7c0788dc523e93c8d8 -> GitHub 1916ce2f221a982e08afe9d0c2429ffeb6a888b9.
- Verified local/remote tree equality: ad7c42b4694e0e01f89f8f7a8edbc3f2848138f6; expected remote parent was75c551e; non-forced update of C02 ref only.
- Actions https://github.com/alireza-anari/fitlink-v1/actions/runs/37316186738 on remote1916ce2, job111783407022: frozen dependencies, static, Ruff/format/mypy/Django/108-unit/production step success. Compose/Playwright in progress; not PASS yet.
- Workspace environments copied into independent ignored directories after bootstrap; no tracked Foundation branch file changed. TMPDIR points to ignored .superpowers/tmp to contain test outputs.

### Task1 completion boundary
- Task1 required CI input/subprocess tests actually passed within job111783407022 step7. Task1 complete; wider unchanged Foundation Compose regression still pending.
- Ruling: apply the plan's per-task gate precisely — Task1 requires input/config CI tests, not live-service tests; proceed after that successful step rather than treating the longer Foundation rehearsal as a Task1 gate — any later Foundation failure remains mandatory to fix. This corrects the overly broad earlier note requiring whole-run completion.

## Task2 RED preparation
- BASE ff143e2. Read whole Task2; schema implementation not started.
- Added Cloud schema contract and actual PostgreSQL migration/constraint tests before models.
- Add dedicated real PostgreSQL CI job to observe RED before schema implementation; no SQLite or mocked migration.
- Ruling: per-commit workflow concurrency — independent CI runners use isolated service DBs, so allow a new RED-contract run alongside the previous Foundation rehearsal — final head must still pass every mandatory job.

- Task2 Cloud RED:2 expected assertion failures: missing additive User fields and registered security models; .superpowers/task2-red.log. No schema implementation yet.

## Task1 actual Foundation regression exit
- Run37316186738/job111783407022 SUCCESS. Full logs inspected:108 units,128 combined backend,2 browser viewports before restart,5 Redis/Celery/Channels recovery,1 private MinIO recovery,2 browser viewports after restart. Clean accounts0001 migration applied; no mandatory skip claimed.

## Task2 implementation checkpoint
- Remote sync: local c68ed17ded960c11754a1ee9562022c2b33a31ab -> GitHub f91e0d30bc18a613648d568b6e544001086e1c5c, tree245b6d66f780928413bf8527deb0f36fe9140b09.
- Actual RED: run37317650640/job111788351652 PostgreSQL17:5 failed with expected missing C02 durable security schema,2 original Foundation migration tests passed,4.13s. Logs inspected. Foundation quality job also failed on2 intentionally RED schema tests; Compose skipped is not a pass.
- Additive migrations:0002_account_security,0003_map_legacy_account_state,0004_account_state_constraints,0005_target_binding_constraint. Initial0001 unchanged.
- Nullable birth date/attestation preserved. Inactive legacy rows mapped to suspended before active/state constraints. New inactive manager creation also maps to suspended while retaining canonical-only/unusable-password boundary and historical-model support.
- Cloud GREEN:10 focused schema/User/scope cases and110 complete unit tests pass. Ruff/format, mypy20 files, deploy check pass. Drift check reports no changes with expected unavailable-PostgreSQL history warning, not real migration evidence.
- Security inspection strengthened bound-user/version SQL NULL consistency before live use;0005 closes three-valued-check ambiguity. Actual constraints and emitted SQL remain PENDING_CI.
- Ruling: add minimal inactive-state manager default — the new state/is_active constraint would reject legitimate create_user(is_active=False), including Foundation callers — explicit inconsistent state remains rejected, no account is reactivated.
- Task2 IN_PROGRESS until actual PostgreSQL upgrade/constraints and Foundation regression gates pass. Tasks3–16 UNSTARTED.
- Task2 implementation commit65ecc97529db6a7cf2fddf93649a6140eb2690f9.
- Remote sync: local 65ecc97529db6a7cf2fddf93649a6140eb2690f9 -> GitHub ebc1770c5e1fea90eecd70b1203de7f187935fdb; tree333a08a0f8f4ac825bb5e3f0c84cf08a642c7d37 matched before non-forced C02 ref advance.

### Task2 CI diagnosis and correction
- Run37318536132/job111791364501: migration SQL step succeeded; actual tests6 passed/1 failed. The populated C01 upgrade and no-auth_user cases passed.
- Root cause from full traceback: enum fixture 'arbitrary' exceeds SecurityRateAnchor.kind varchar(5), so PostgreSQL correctly raises DataError before the expected CHECK/IntegrityError. Model/security behavior is correct.
- Fix preserves the overlength denial assertion as DataError and adds bounded unknown 'other' to exercise the CHECK/IntegrityError. No production constraint relaxed.
- Emitted SQL inspected: additive columns/tables, unique indexes, PROTECT FKs, no User replacement, inactive data mapping precedes consistency check, explicit non-NULL bound auth version.
- Wider Foundation job on the previous implementation head still in progress; current task not complete until corrected real PostgreSQL tests pass.
- Remote sync: local 848115c523fec0d482129f0fda6ce1767649a104 -> GitHub b9c835febe635af26b728602d8a1f7a6c1d36a8e; verified tree equality e5c327b7a0bb4d08bf44f8011eca45ba1dbf1f48, non-forced expected-parent update.

### Task2 required gate evidence
- Corrected run37318999983/job111792948986 SUCCESS: actual PostgreSQL17 emitted SQL and seven migration/constraint cases passed (7 passed in1.33s), logs inspected.
- Independent read-only security review of C01..848115c: no Critical/Important/Minor finding in Tasks1–2. Reviewed SQL NULL checks, ordering, inactive/DOB preservation, manager historical models, keys/errors, proxy trust and adult/calendar boundaries. Tasks3+ excluded.
- Previous Foundation run37318536132/job111791364069 failed on the same corrected overlength test fixture:134 passed/1 failed. Not a regression in implementation. Current head Foundation remains pending; Task2 not yet marked complete.

### Task2 completion
- Run37318999983 SUCCESS, Foundation job111792948381 logs inspected:110 units,135 combined backend,2 browser before restart,5 Redis/Celery/Channels recovery,1 MinIO recovery,2 browser after restart. Dedicated PostgreSQL job7 cases passed. All required gates green, no skips.
- Task2 COMPLETE. Skill task-done rerun:10 focused unit cases passed. Task3 is next, no later implementation started.

## Task3 RED preparation
- BASE848115c, whole Task3 brief read. Cloud RED9 expected failures: missing governance audit contract. No governance implementation exists.
- Added real PostgreSQL transaction/dedup, ORM/SQL immutable audit and restricted NOLOGIN role tests;12 staff cases cover bare superuser, forgery, stale/version/case/user/capability/self-issue/current state. Required actual RED pending CI.

- Remote sync: local2de9ba9f987b7b04ebfdd3d85e36754e5e8d0355 -> GitHub c366aa923f87e72f29e8846321026d04014aa1e0; tree496cfa14323fc808f6bb4b0b441a4cf3cb695aa4 verified, expected-parent non-forced ref update.
- Actual Task3 RED run37320527330/job111798131005:15 expected governance/staff missing-contract failures,7 migration regression cases passed,2.37s; logs inspected before implementation.

### Task3 implementation checkpoint
- Added governance0001_initial (explicit accounts0005 + swappable dependency) and0002_audit_append_only. SQL owner UPDATE/DELETE denied; runtime SELECT/INSERT only audit probe, no retention bypass flag. Runtime TRUNCATE also denied by privileges; migrator retains DDL privileges for migrations, not ordinary staff.
- Audit action/result/reason/changed-field allowlists; no unstructured private payload. Audit and ID-only outbox require existing domain atomic transaction; dedup conflict rejected.
- Named capabilities/current account+version+case-bound fresh step-up; self-issued grants and bare staff/superuser denied. Private bounded single-use memory Mock step-up has no web route, is blocked outside development/test. No production adapter or grant CRUD installed.
- Additional Mock contract RED2missing-provider/9passed then GREEN11; full Cloud121 units pass, mypy29 files/Django/production/drift green. Drift history unavailable locally is not PG proof. Real transaction/immutability/staff GREEN pendingCI.

### Task3 security finding and RED fix preparation
- Remote sync: local10ef0807c27eedeac97534dc88b0a5edf0566bb0 -> GitHub f3a734301d38e6ce765fd4252c925133c2b6fed2; tree331adb05605bd86cd5dbcf8f0d954c1e39a39961 matched, non-forced expected-parent update.
- Initial PostgreSQL run37321714246/job111802165945 SUCCESS (initial23 cases); SQL immutability/role denials inspected. Wider Foundation in progress.
- Independent review Important accepted: model save coerced changed_fields dict to tuple(keys), allowing private values to remain in original persisted JSON; bulk/direct insert had no JSON-shape guard. No other concrete finding. Task3 remains IN_PROGRESS.
- Cloud reproducer RED1: original dict passes model validator; expected ValueError not raised. Added real bulk/SQL insertion reproducer before schema fix; actual RED pending CI.

- Remote sync: local57be071fdfb444b08c4329cd1bae4b20d0324680 -> GitHub0507e5071800ce37d2cc8d76afc2b4b1548094f0; treedd91e4ffd2c8e9b831d3fa6e26553611637e302d matched before expected-parent non-forced update.
- Additional security inspection identified analogous direct OutboxEvent model/bulk insertion payload validation gap, despite safe append_outbox. New model RED reproducer1fails expected ValueError not raised; DB bulk insertion reproducer added before fix. Treat as Important within same Task3 fix pass, not scope expansion.
