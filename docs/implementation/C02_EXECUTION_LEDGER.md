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
3. COMPLETE — audit/outbox/staff; payload findings fixed with real PostgreSQL GREEN.
4. COMPLETE — real dual-store quotas, races, outage/reset/process/restart; one deferred retry hint minor.
5. IN_PROGRESS — digest-only OTP issuance RED preparation.
6–16. UNSTARTED.

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

### Task3 payload security fix
- Run37322212998/job111803867632 actual audit insertion RED:1 expected missing IntegrityError,23 passed (4.45s).
- Remote sync: local7a7158d8d17c40010042b6e3969ae460a41d4537 -> GitHub ba32553f1c41d3c7b1dcfc3cdeebbb6746347dac; treeefb29af95d0f91553f2f7100b49950269207f365 matched before expected-parent non-forced update.
- Run37322448447/job111804671208 actual PostgreSQL RED:2 expected missing IntegrityError in audit/outbox insertion guards,23 passed(3.26s), logs inspected before fix.
- Fixed original audit JSON shape validation and OutboxEvent model validation. Governance0003 adds IMMUTABLE metadata check functions + DB constraints: audit is bounded array of allowed names, outbox object has event-specific UUID string keys/values only. Bulk/direct insertion cannot retain arbitrary private JSON. No caller flag/retention bypass.

- Payload fix Cloud GREEN:13 audit/provider/model contracts; full123 units pass. Ruff/format110 files, mypy30 files, Django/production/drift pass. Real SQL insertion fix and full current-head regression remain PENDING_CI.

### Task3 completion boundary
- Remote sync: local9df9fd2bf612b1d4f5d539e2f5b2599bfe393b57 -> GitHub bfdeea8aff171eddef588d5ad8103ae6c5570750; treeefb0bb7275d51c252695994ba6e196c562813612 equality verified before non-forced update.
- Run37323034017/job111806661619 SUCCESS:25 actual PostgreSQL cases passed4.65s; emitted0003SQL inspected. Both Important payload findings fixed RED→GREEN; no remaining focused review finding.
- Current Foundation job111806661280 static/config/123units passed, Compose ongoing, not yet claimed PASS. Relevant C01 migration regression passed in25-case gate. Task3 required PostgreSQL transaction/SQL/role gates complete. Wider regression remains mandatory; any failure must be fixed.
- Task3 task-done14 focused units pass; Task4 next.

## Task4 RED preparation
- BASE9df9fd2, whole Task4 brief read. Cloud RED6missing atomic limiter contract assertions; before implementation.
- Actual PostgreSQL/Redis fixture gates cover exact phone/IP send/failure quotas, boundaries, normalized identity, first-anchor/PG-only guard races with24separate DB connections, successful failure-slot release, Redis unavailable/NOSCRIPT/key reset, retained-key aggregation, crashed process after real Redis reservation, aborted DB admission and cleanup failure. Required actual RED pendingCI.
- Ruling: recovery intake separately configurable engineering defaults3phone/10IP/hour — plan requires separately configured limits but specifies no numeric values — keeps conservative abuse bound and does not change ADR OTP quotas; operational tuning remains release review.

### Task4 CI RED discovery correction
- Remote sync: local4307a3eafd8e0e20d3629782917a6b7cf1e4bad4 -> GitHub ff273bef40d1d46533cd8d95a2eb97ceabb73aca; treec023682b9fe05976bd0847d2ec683148444669c7 matched, expected-parent non-forced update.
- Task3 run37323034017 full SUCCESS, logs inspected:123units,166 combined backend,2+2 browser,5 Redis/Celery/Channels recovery,1 MinIO recovery. Task3 all wider gates green.
- Task4 run37324103261/job111810306064:25 previous gates passed but13fixture-not-found errors. This is NOT behavioral RED. Started local uncommitted limiter draft after reading summary, then inspected full traceback and stopped further implementation; no draft published.
- Root cause reproduced locally by --fixtures-per-test: mixed individual file selection loses nested limiter fixture; C02 directory selection loads it for all13cases. Ruling: select tests/integration/c02 directory plus C01 initial migration file — complete suite, robust nested discovery, no test weakening.
- Corrected new production test helper use to production_env() dict union; helper has no keyword arguments. No implementation behavior adjusted. Actual corrected RED pendingCI before resuming draft/GREEN.

- Remote sync: local0056efd1404afa30d416700459c8cdb2c509e0e2 -> GitHub45a78ca518bfbed151b610f0dc46af481f22471c; tree3fc1f079ba4a7c9141523fbb0e2f4af24f043ae8 matched, expected-parent non-forced update.
- Corrected actual RED run37324882314/job111812955568:13 expected missing real dual-store limiter assertions,25 previous gates passed5.12s. Full traceback inspected. Resume unpublished draft after this required behavior RED.

### Task4 implementation checkpoint
- Lua reserves both dimensions atomically using HMAC ZSET keys and UUID members. PostgreSQL sorted unique anchors serialize durable rolling-window counts across retained key IDs. No refund on aborted send admission; proven-success failure reservations release through actual Redis before durable success, exceptions fail closed.
- Dedicated logical DB4 config; production TLS certificate/hostname/query/db checks retained; Mock/recovery disabled production. Cloud6limiter and129full unit cases passed, mypy32files/productioncheck green.
- Security inspection adds explicit removed-key RED case before guard: absence of retained key could otherwise make old anchors undiscoverable; require uniform unavailable while any recent event references a removed key. Actual RED pendingCI.
- Ruling: add isolated host-CI Redis restart probe in Task4 — plan requires actual restart failure injection; checks image has no Docker daemon, so host runner restarts only its service container and verifies real PostgreSQL main scratch DB, then discards counters too. No production credentials or persistent application data.

### Task4 focused review and pending fix
- Remote sync: localba5ae276e73fc1833bc41882b1944f5ef2e46020 -> GitHub3d5644e2a81ca6b3523f0b0bb5533dff4605a11f; treea2754d3a11f86085975363d26b2f88b5b4b1161c verified before non-forced expected-parent update.
- Run37325626913/job111815509657:38 actual PostgreSQL/Redis cases passed,1 expected removed-key guard RED (LimiterUnavailable not raised),9.60s. Restart step skipped due RED, not PASS.
- Independent review Important accepted: plan §2 line114 explicitly3phone/day and10IP/day, not hour. Previous ruling claimed unspecified numeric defaults and hourly window incorrectly; superseded by this correction to exact approved daily limits. No scope redesign or approved override.
- New Cloud RED1missing separate window contract; real daily-boundary RED pendingCI before fix.
- Task4 minor (deferred): retry_after can reflect an earlier event in an unsaturated dimension; repeated denials possible but no over-admission. Keep metadata limitation for handoff; no scope expansion to polish now.

### Task4 guard and daily-window fix
- Remote sync: localf286018b11110dc5b74adfb899f9093fa4867274 -> GitHub1f88a814d6bfb2c11207340e736532bf1976d705; tree8cf59c345f1ef4f2668bfbc500ef075543eefa31 equality verified before expected-parent non-forced update.
- Actual RED run37326108079/job111817147270:2 expected failures (daily recovery boundary and removed-key unavailability),37passed9.14s; logs inspected before fix.
- Separate approved recovery86400s window now applies both Lua and PG guard; OTP3600s unchanged. Added global closed admission when any still-counting event references removed material, including daily recovery/pending failure quotas, rather than silently forgetting undiscoverable anchors. Audited closed maintenance/warm-up remains required before key removal.
- Focused Cloud GREEN7contracts passed. Task4 stays IN_PROGRESS pending actual races/outage/reset/process/restart gates and current Foundation CI.

### Task4 completion boundary
- Remote sync: localec5ccee56f23a883cbb168003abd47302da58d5b -> GitHub d90009fe9077f4ef4415c57f91129b8d317db86b; treeabd1c9bf98d0726f8df8ceef742bba589d2726ba matched before non-forced expected-parent update.
- Run37326556611/job111818684769 SUCCESS:39actual PostgreSQL/Redis cases passed11.40s, including24connection real races, exact daily/rolling boundaries, correct-slot release, outage/NOSCRIPT/key reset/retained rotation/removed key refusal and process exit.
- Host runner genuinely restarted its Redis service container; both prepare/verify durable quota probes passed, including deleting saved counters. Fresh main scratch DB applied accounts0001..0005/governance0001..0003. No skipped gate claimed.
- Cloud130units/Ruff/format/mypy32files/Django/drift/production all green. Focused task-done23units pass. Important review finding fixed RED→GREEN, retry metadata minor deferred.
- Current Foundation job111818684950 static/130unit step passed; Compose ongoing, not yet PASS. As prior task boundaries, required Task4 service/relevant C01 migration gates passed; current wider Foundation failure, if any, remains mandatory to resolve. Task5 next.

## Task5 RED preparation
- BASEec5ccee, whole Task5 brief read. Cloud RED7 named missing bounded SMS/digest-only OTP contracts before implementation; added actual1-second hanging provider bound test before code.
- Added true PostgreSQL/Redis issuance/cooldown/resend, retired late-ack race with separate DB connection/thread barrier, failed/unknown/crash-pending, audit rollback-before-IO, private sentinel persistence/log and existing/restricted/suspended uniform-result contracts. Production provider remains unselected/disabled. Actual RED pendingCI.

- Remote sync: local6d8fe04a89b0db79d4b9ac7383b77f28614b62ba -> GitHub cb3beba783ea050b24a717282b7e123455fac061; tree9b4f2b075107a46dfd0f0877d55b07a2bc91a1a5 verified before non-forced expected-parent update.
- Actual Task5 RED run37327549360/job111822024462:8 expected missing durable digest-only issuance failures,39 previous service cases passed11.04s. Full traceback inspected before implementation.

### Task5 implementation checkpoint
- Transient cryptographic6digit generator/HMAC context includes challenge UUID/generation/purpose/context/User+auth version/key ID; compare uses hmac.compare_digest, removed key never validates. No plaintext durable column or SMS Celery payload.
- Bounded8-worker/no-queue transport capacity holds slot until timed-out I/O actually completes; timeout/exception/unknown becomes unverifiable, no raw provider error logging. Private bounded threadsafe Mock collector, production refuses Mock/entry.
- Digest/pending/generation/cooldown/audit commit before provider I/O; late acknowledgement re-locks phone/User/context/challenge and marks sent only if generation/current expiry/terminal state still valid. Request does not query/create User for login. Audit failures roll back before send; conservative admission remains spent.
- Ruling: extend request_otp with required keyword provider and optional server-only OtpBinding + context validator for non-login purposes — composition must supply purpose/phone/User/version/case authority rather than accepting client IDs — Task8/9 install their owned validators; unbound non-login issuance denies now. Costs one explicit callable interface, no future-domain model/import.
- Cloud GREEN8provider/digest contracts; full138unit cases, Ruff/format122files/mypy35files/Django/drift/production checks pass. Real request/resend/late-ack gates PENDING_CI, Task5 not complete.

### Task5 ambient transaction security RED
- Task4 full Foundation run37326556611/job111818684950 SUCCESS:130units/187combined backend/2+2 browser/5Redis-Celery-Channels/1MinIO recovery, completed logs inspected.
- Remote sync: local951435fec24d5528122c8d3fa38bf1ca1e495c94 -> GitHub76276f2ae610155186dae16a170877b18062681a; tree2afa40537419c0002ac90cd29ba8736414026964 equality verified before non-forced expected-parent update.
- Initial Task5 service run37328982947/job111826892712 SUCCESS; full logs inspection pending. Foundation111826892801 ongoing, not PASS.
- Independent review Important accepted: nested atomic exits only a savepoint; SMS can occur before outer challenge/audit commit and with locks retained, then rollback loses all evidence. Required top-level command boundary before admission/I/O. No other concrete Task5 finding.
- Added actual PostgreSQL ambient transaction rejection regression before fix; expected OtpUnavailable absent. Actual RED pending CI, no Task6 started.
