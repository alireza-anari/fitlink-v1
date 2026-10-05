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
5. COMPLETE — digest-only issuance, ambient boundary fix; Cloud/service gates green.
6. COMPLETE — atomic proof/adult/race/application service gates green.
7. COMPLETE — versioned sessions, rotation/outage findings fixed RED→GREEN.
8. COMPLETE — real recovery/receipt/staff/history/race/rollback/audited-read gates GREEN.
9. COMPLETE — published dual-possession implementation and required CI verified during recovery.
10. COMPLETE — Cloud RED→GREEN; current-source Foundation CI includes all23Consent PostgreSQL cases and full regression gates, inspected genuine success.
11. COMPLETE — Cloud RED→GREEN; retry37369811515 attempt2 both required jobs SUCCESS, actual logs inspected.
12. IN_PROGRESS — Cloud RED→GREEN; real PostgreSQL intake/hold/race and Foundation gates pending.
13–16. UNSTARTED.

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

### Task5 ambient boundary fix
- Initial service47cases passed17.94s plus real Redis restart prepare/verify; full logs inspected.
- Remote sync: local6c42708d0c42e1566e97ddf8c00fb91e18343721 -> GitHuba7bb9d0dcf065ed885ad8dcd48e5c031891a5635; tree9be0dd86b33e63b01b54c8d318850f2a0e6356c8 equality checked before expected-parent non-forced update.
- Actual PostgreSQL RED run37329900652/job111830061966:1 expected DID NOT RAISE OtpUnavailable,47passed10.14s. Restart skipped on RED, not PASS. Logs inspected before fix.
- Added top-level boundary rejection before normalization/admission/generation/audit/provider I/O. Ruling: issuance is a two-phase top-level command; later recovery/phone-change composition commits intent first and revalidates locked authority in issuance, never wraps issuance in an ambient atomic. No on_commit-only security effects. Actual GREEN pendingCI; Task6 remains unstarted.

### Task5 completion boundary
- Remote sync: local94211a1a9c841e0cb057a058aee14f33febcdddc -> GitHub58633c77868da361830d1f3212023b46e97f3525; treed09a61f5e0a21744333b42af24e277c7b8a09e96 equality checked before expected-parent non-forced update.
- Actual GREEN run37330187531/job111831032090:48 PostgreSQL/Redis cases passed10.36s; actual restart prepare/verify passed. Ambient boundary Important fixed RED→GREEN; focused independent review confirms no remaining finding.
- Initial feature run37328982947 full Foundation SUCCESS:138units/203combinedbackend/2+2browser/5Redis-Celery-Channels/1MinIO recovery, completed logs inspected. Current fix Foundation111831032453 Cloud/static step green, Compose ongoing, not yet PASS; wider failures remain mandatory.
- Cloud138units/mypy35files/Django/no migration changes/Ruff/format green; task-done31focused units passed5.23s. Required Task5 service/relevant C01 gates complete. Task6 next.

## Task6 RED preparation
- BASE94211a1; whole Task6 brief read. Cloud2expected missing atomic verification/application and bounded digit input assertions before implementation.
- Real PostgreSQL/Redis tests added for299/300s, wrong1..5/fifthcorrect/locked/replay/resend/dummycompare/purpose/context/generation/missingack/staleversion/malformedshape; separate-connection concurrent first registration; audit rollback; under18/missingattestation/legacy/restricted/suspended; non-login consumed proof/replay/rollback/concurrent application with no sessions. Local collect-only confirms discovery, no service PASS claimed.
- Actual RED pendingCI before implementation.

### Task6 recovery inspection and implementation
- User resumed interrupted run. git status clean, no staged/untracked source or local implementation to preserve. Local HEAD51c906c94c6333ddea04180d05538ea952aabb77 equals remote8fe0323634488841399719cca7fa6316a0c8546f tree9c51e23c9d426c63d9c4d04c4210fbe7a5ef5eae. No reset/checkout/branch recreation/repeated completed tasks. Corrected stale top task summary using recorded completion evidence.
- Remote sync: local51c906c94c6333ddea04180d05538ea952aabb77 -> GitHub8fe0323634488841399719cca7fa6316a0c8546f; exact tree equality verified.
- Actual RED run37330945477/job111833563047:22 expected missing atomic proof assertions,48previous cases passed13.97s. Full failures inspected before implementation; skipped restart is not PASS.
- Task5 final run37330187531 now full SUCCESS; completed Foundation logs inspection remains to be recorded.
- Implemented bounded supported digit input, constant-time real/dummy comparison, quota reservation before proof, sorted anchor/phone/User/challenge locks, committed wrong attempts/audit, adult gate before canonical manager User creation, single consume and rollback-safe one-time non-login application. No session/provider/vendor/model/migration expansion.
- Ruling: explicit internal birth_date/adult_attested keywords and server-owned binding/context callbacks; optional synchronous on_login callback will let Task7 persist session inside this exact proof transaction. No public API until Task14. Internal application effect/context callbacks are server code, not client-selected actions. Adult declaration schema version adult-v1 records a declaration, never verified age or sensitive consent.
- Recovery uv rebuilt ignored stale .venv with frozen unchanged lockfile; no tracked dependency changed. Cloud2focused verification contracts green; type issue for nullable birth date diagnosed and explicit missing-date denial added. Actual GREEN pendingCI.

- Task5 final Foundation37330187531/job111831032453 completed logs inspected:138units/204combinedbackend/2+2browser/5Redis-Celery-Channels/1MinIO, all SUCCESS.
- Task6 Cloud GREEN140units13.35s, mypy36files/Ruff/format126files/Django/no migration drift all pass. History warning due absent Cloud PG is not real migration evidence. Actual proof/race/adult GREEN and focused independent review PENDING; do not advance Task7.

### Task6 completion boundary
- Remote sync: local6ba95bcb3b48e3abd3e5bff849d168b2618e62fb -> GitHube41ed5d4d8eb72116d9f9d200cb45e19f91c950d; tree3041b3a0590405175eb9a46507abb7439e1cdb19 equality verified before non-forced expected-parent update.
- Actual GREEN run37346206791/job111885284381 SUCCESS:70 PostgreSQL/Redis cases passed14.36s, actual restart prepare/verify passed. Separate DB connections/barriers establish exactly one login consume/User and one non-login application; rollback leaves proof unapplied. Logs inspected.
- Focused independent security review: no concrete Critical/Important/Minor finding. Production check green. Task6 required service/relevant C01 regression gates complete; Foundation111885284711 static/unit step green, Compose pending, not yet PASS. Any wider failure remains mandatory. Task7 next.

## Task7 RED preparation
- BASE6ba95bc; whole Task7 brief read. Cloud12expected missing current-action policy failures. Real PostgreSQL tests cover rotation/payload/oldkey/missingrevokedstalescope/control/single-global logout/session-audit rollback/owned detail-list-count/current-state mutation recheck/login-suspension serializations plus actual cookie CSRF and dependency failure closed with liveness available.
- State re-entry fixture resets only cooldown to enable second approved attempt; quota/generation/session invariants remain real, no substituted concurrency. Actual RED pendingCI before implementation.

### Mandatory Foundation failure diagnosis
- Task6 run37346206791/Foundation111885284711 failed:227combined tests passed, only C01 test_private_minio_signed_roundtrip failed with httpx.ReadError connection reset on expired URL request after valid GET200 and anonymous GET403. No storage/test_minio/transport changes in Task6. This is not proof of authorization bypass; required expired403/recovery/browser gates remain unsatisfied.
- Inspected full traceback/source. Ruling: rerun only failed Foundation job at identical Task6 head to determine whether isolated connection reset persists, preserving all assertions and already-green service job. This is a diagnosed retry, not blind rerun of RED. Task7 RED tests authored/synced, but implementation paused until required wider regression resolved.

### Task7 required RED and Foundation resolution
- Remote sync: localfef7a5217b0fd8523b1811e8f1917c9a3a5d13b3 -> GitHubed30db9d60742581c8cf04e42799a0076ef5a802; tree2d1e0f5a74d8fc548f911c19acc11e41ab1543dd equality checked before expected-parent non-forced update.
- Actual Task7 RED run37347031963/job111888319977:16 expected missing versioned-session failures,70previous cases passed22.79s. Logs inspected before implementation.
- Diagnosed Task6 Foundation retry37346206791/job111888247694 SUCCESS:140units/228combinedbackend/2+2browser/5Redis-Celery-Channels/1MinIO recovery. Expired URL403 passed without source/assertion changes; transient connection reset did not reproduce. Full completed logs inspected; wider Task6 gate resolved before Task7 implementation.
- Strengthened Task7 tests before implementation: account.login audit failure occurs after actual session/control save (not earlier proof audit); second real saved session survives current logout and is revoked by all logout. Revocation command owns phone-before-User locks, test no longer pre-locks User in reverse order.
- Implemented synchronous session/control save inside proof transaction, rollback clearing in-memory request state, current version/scope/control resolver and mutation recheck, owned selectors, unknown-action denial, post-auth account middleware and Session+CSRF DRF adapters. Internal state changes/global logout lock phone/User, invalidate challenges/version/controls synchronously. No new model/migration/API/vendor.
- Ruling: account_control session TTL bounded by approved recent-auth600s (normal retains Django cookie lifetime), limited self/privacy/logout allowlist. No stock staff permission bypass. State command is internal server-owned, no generic state-edit route.

- Cloud GREEN152units16.04s, mypy42files/Django/productioncheck pass. Nullable current control ID now denied explicitly before query; third-party DRF imports lack stubs, narrowly annotated import-untyped only, typed account core remains checked. CI mypy scope expanded to composition/middleware/adapters. Actual Task7 services and focused security review PENDING.

### Task7 focused review RED fixes
- Remote sync: local27cf5efbc8fc79982b5146cc3404b3b4b6db5266 -> GitHubce07f114c7e3e108f26a003168a89d624df9e894; tree1e1890cf5fe0d707e83ca07045ac0c0f275699bf equality checked before expected-parent non-forced update.
- Initial service run37348954456/job111894634840 SUCCESS:86actual PostgreSQL/Redis cases16.14s plus restart prepare/verify. Foundation111894634380 failed solely I001 inner-test import order after last test strengthening; no Compose gate executed. Corrected formatting, no assertion weakened.
- Independent review Important accepted: Django login retains same-User/hash authenticated key; second OTP entry can collide with session-control digest or retain cookie after key rotation. Require explicit every-login rotation and old control revocation. Added existing authenticated-key regression before fix.
- Minor accepted for Task7 contract alignment: authority query outage after middleware returns500 instead of generic503; fail-closed but specified status wrong. Added later-query real DB execute-wrapper failure injection before fix. Actual RED pendingCI; Task7 not complete.

### Task7 rotation/outage fix
- Remote sync: local6d6253ac1dca0770b8f48b2fc4c487c748a436b3 -> GitHub904de351c314f9a6b77127f560298824f4dac3c0; tree6e3acdbda6666682f9ab864706f225c6a083ff1b equality checked before expected-parent non-forced update.
- Actual RED run37349401287/job111896136180:2 expected failures (late permission-query OperationalError and same-User session_control_digest IntegrityError),85passed17.11s. Tracebacks inspected before fix.
- Explicitly revoke the old cookie's retained-key controls, flush old Django key/payload and persist a fresh key each login. This also prevents cached prior request store from retaining control authority. Cookie-based old-control revocation changes no other User identity/state; only login User row is involved in this effect. Proof callback now saves controls before verification audit append, honoring control-before-audit ordering.
- Fresh DRF authority DB failure now raises a503 APIException with only status=unavailable; no exception text/data reflected. Existing middleware outage/liveness checks retained. Actual GREEN pendingCI.

### Task7 completion boundary
- Remote sync: localb392f88de10088b48273a43a05265b404b5442c7 -> GitHub7769602dce07e4edeb32d1c5bc0f2a52f268c6be; treef0ca5ab6e37dc5c0e89d975aecb043a534bf05f8 equality checked before expected-parent non-forced update.
- Actual final service run37349888522/job111897773416 SUCCESS; full logs inspected. Both review findings fixed RED→GREEN; focused independent rereview confirms no remaining finding or concrete lock-order cycle.
- Foundation111897773033 full SUCCESS:152units/257combinedbackend/2+2browser/5Redis-Celery-Channels/1MinIO. Completed logs inspected. Final service87passed20.76s plus actual Redis restart. Task7 complete.

## Task8 RED preparation
- BASEb392f88; whole Task8 brief read. Cloud3 expected missing recovery/schema/metadata failures; real receipt/staff/self-approval/evidence/apply/rollback/history/uniqueness/suspension race contracts authored. Actual RED pendingCI before implementation. No completed work reset or repeated.

### Task8 required RED
- Remote sync: locald068b9a9b46bb1ec095f174895470b61a2b6895b -> GitHub275c108734127be899264aa71225f1de3a942ece; tree3c55ac6b90b8424919cb9233991edfd01bf912fc exact equality. Actual RED37351949493/job111904704304:24 expected missing recovery failures,87previous cases passed23.08s; full failure output inspected. Foundation RED is expected missing3unitcontracts, Compose skipped not PASS.
- Ruling: NULL-target recovery proof permits uniform proposed-phone possession verification for unresolved existing/unknown cases, with server-owned receipt/case validator; it never applies an identity effect or issues a session. Staff resolution requires a new target/version-bound proof for application — prevents enumeration at intake and preserves case ownership — if wrong, recovery transport leaks membership.
- Ruling: recovery OTP allows suspended/inactive target while preserving its state, unlike login/normal change — Task8 expressly forbids reactivation and permits recovery for suspended users — if wrong, legitimate suspended recovery is blocked. Terminal identity states remain denied.

### Task8 implementation checkpoint
- Added confidential RecoveryRequest/EvidenceMetadata/immutable PhoneChangeHistory and additive accounts0006..0010 migrations. All new schema/protected FKs/checks; no accounts0001/User replacement/auth_user/profile tables. History owner SQL trigger has no caller-settable bypass, PUBLIC mutation privileges revoked; restricted runtime INSERT/SELECT test added.
- Receipt-only intake does not query User. Uniform unresolved new-phone proof can consume only in server-owned case; staff resolution clears earlier proof references, application requires approved case and proof issued after decision, target/User/version/phone/context/current generation unchanged. Suspended recovery preserves inactive/state/password/DOB/UUID, no session. Both phone anchors sorted before involved sorted Users/case/proof/staff grants; current authority rechecked before conflict/effect details.
- Synchronous phone/history/authversion/control/challenge invalidation/proof application/case effect/audit/ID-only outbox share one PostgreSQL transaction. Required recorder/authority/emitter callbacks cannot be no-op defaults; root imports governance, accounts does not.
- Schema regression allowlists expanded precisely for these3models and5User reverse relations. Direct history SQL test corrected to DatabaseError (PostgreSQL42501 insufficient privilege), matching existing audit trigger contract, not weakening a mutation assertion. Added history write failure and restricted-role append/read/deny tests before GREEN service run.
- Cloud GREEN155units15.44s, mypy53files, Ruff/format146files, Django/no migration drift/production config/Tailwind/JS pass. Cloud PG unavailable is not migration verification. Actual GREEN pendingCI; Task8 remains IN_PROGRESS.
- Focused author security review: no new session or reactivation; NULL-target proof cannot apply; protected identity/version and staff self-case checks fail closed; proof/date/generation and old/new uniqueness rechecked under locks; private metadata/code/receipt absent from audit/outbox. Required real rollback/race/SQL-role gates pending; no PASS claimed yet.

- Remote sync: local56b9b5cd9099c2ca10b403c461ef213a10a89e6b -> GitHub4122424192003cdadb3d68ab8eb0df7dd3a281f6; treef93ddb5b733b576cdf2855b85ef029a05919ac21 equality checked before expected-parent non-forced update. Current CI37353277690 service step success, restart ongoing; full completed logs required before PASS. Strengthened planned rejection/outbox rollback/expiry/purpose/version/generation contracts; no implementation or assertion weakened.

### Task8 sensitive-read review finding
- Remote sync: localc85a9aaaf0319cf33be19bacfb9bfe2c75785f65 -> GitHub321ab1e8592c3ea687ec93f2563033af995ad694; exact treecb5bc884175602805e5622d56e5706e8dd3d3c61. Initial real GREEN37353277690/job111909202057:113passed26.20s and actual Redis restart prepare/verify; full SQL/migration/role/race/rollback output inspected. Extra planned regression run37353539025 pending.
- Important author review accepted: PERMISSIONS_MATRIX line12 requires audit on sensitive/evidence access; Task8 detail/evidence selectors checked staff authority but lacked synchronous read audit. Added required-recorder Cloud contract (actual1expected failure/3pass) and actual read-count/audit-outage denial test before fix. Task8 remains IN_PROGRESS.

- Remote sync: local9b02b21e9475c584b4443fc2e4cf820355636105 -> GitHub8eb541128ede5f4773d187cfbe5c38ed09f813fb; exact tree8d0bb17994a83c240f54c3cf923d591f89fa817b. Extra regression37353539025/job111910077958:118passed28.13s,2rejected-evidence cases failed actualDB varchar15 truncation for allowlisted16-character ownership_review. Diagnosed model bound, not a test weakness; additive widening required. Task8 not complete.

- Actual sensitive-read RED37353760288/job111910840559: missing2read-audit rows assertion,2known classification truncations;118passed21.60s. Full tracebacks inspected before fixes. Required read recorder now runs before any sensitive metadata return inside same authority transaction; audit outage denies read. Additive accounts0011 widens classification15→16, no earlier migration edited. Five recovery unit contracts now GREEN0.09s. Actual final GREEN pendingCI.

- Final fix Cloud GREEN157units13.70s, Ruff/format147files/no migration drift; mypy identified omitted root detail-recorder argument during verification, corrected before sync and rechecked. Actual service/migration/focused-read GREEN still pending.

### Task8 completion boundary
- Remote sync: local164a42a60f5f7c5a6e0b68a9f78e52fbc5067cda -> GitHub11d4888abb6907a7df65fe39dd558bc5a4dd99f7; exact tree3a16a617a1efcc1ae4818d445573e542b39fa59b checked before expected-parent non-forced update. Actual final GREEN37354148073/job111912166344:122passed28.84s, actual Redis restart prepare/verify. Full SQL/migration/race/rollback/role/audited-read output inspected. Both focused findings fixed RED→GREEN; no remaining concrete author-review finding. Task8 complete; Foundation111912166676 static/unit/config step GREEN, Compose ongoing not yet PASS. Any later wider regression remains mandatory. Task9 next.

## Task9 RED preparation
- BASE164a42a; whole Task9 brief read. Cloud2expected missing owned intent/dual-proof command failures0.07s. Real tests cover owner/foreign/stale/expiry/purpose/context/same proof/unique owner/current-global logout/replaced intent/rollback/audit/outbox/history/new-login replay and independent-connection competing change/recovery serialization. Actual RED pendingCI before implementation. No Task10+ work.

### Task9 required RED
- Remote sync: local3a5ad48910c730749e2c8776b904359c975fb170 -> GitHubf1f541be021a38da40c48ecc657234f73da08cdf; exact tree04efeb15f4a9f942875d157d191f888e145f3fb0. Actual RED37354820117/job111914439885:17expected missing owned command failures,122prior cases passed30.97s; full named failures inspected before implementation.
- Task8 initial full Foundation37353277690/job111909202560 SUCCESS:155units/286combinedbackend/2+2browser/5Redis-Celery-Channels/1MinIO; completed logs inspected. Final fix Foundation37354148073 still pending, not claimed PASS.
- Ruling: intent validity uses existing recent_auth_seconds600s, while each proof retains300s expiry/freshness — bounded secure context without another unapproved policy constant — if wrong, user must restart expired intent more often. Applied effect replay requires a fresh current normal actor; revoked original cookie cannot replay.

### Mandatory Foundation transport diagnosis during Task9
- Task8 final Foundation37354148073/job111912166676 failed only expired MinIO signed-read request:296combinedbackend passed93.15s; accepted200 and anonymous403 already passed. Full traceback shows third request reused HTTP11connection then EOF/RemoteProtocolError before any authorization response. Same keepalive-close class occurred Task6; no accounts change touches storage.
- Ruling: disable keepalive reuse in this real-MinIO three-response fixture only, preserving accepted/private/anonymous403/expired403 assertions and production S3 adapter — separate signature authorization from anonymous-403 connection-close race, avoiding repeated blind reruns — if wrong, the unchanged expiry403 assertion still fails on a fresh actual connection. No production behavior weakened or Foundation branch edited. Actual MinIO GREEN is mandatory before Task10.
- Task9 Cloud159units13.23s/mypy56files/Django/no migration drift/production checks GREEN. Additive accounts0012 PhoneChangeIntent enforces one live context/User and distinct proof roles. Ownership/current actor version/state, both context/purpose/User/version/generation/expiry/unapplied proofs and destination uniqueness rechecked under sorted phone/User/intent/proof locks. History/auth revocation/proof/application/audit/ID-only outbox atomic; rollback callbacks required. Focused author review: no recovery/staff shortcut, no account reactivation, original cookie revoked, completed replay requires fresh current owned actor. Actual service GREEN pending.


## Recovery inspection — 2026-10-05
- Authoritative remote branch accounts/c02-cloud inspected via authenticated GitHub connector. Head b7fdcea278fd3d9ad8538a4af32cb90c48bb005d, exact tree 7742c7ca6c5feed3ba6dd48818047fb2f7540c4a; recent RED and implementation commits inspected. No completed Task recreated; no main/Foundation ref changed.
- Task9 COMPLETE. Existing published RED evidence remains run37354820117. Inspected committed apps/accounts/phone_change.py, config/use_cases/identity.py, tests/unit/c02/test_phone_change_contract.py, tests/integration/c02/test_phone_change.py and ci.yml. Focused recovery author review confirms owned current actor, distinct bound old/new proofs, purpose/context/User/version/generation/expiry/unapplied checks, sorted phone/User locks, unique destination, atomic history/proof/auth invalidation/audit/outbox, rollback and one-effect replay contracts. No new concrete finding from this review.
- Genuine final GREEN run37355592772 is push-triggered on b7fdcea278fd3d9ad8538a4af32cb90c48bb005d; conclusion SUCCESS. Both jobs and complete decoded logs inspected: c02-migrations111917066160 has141passed34.80s and actual Redis restart prepare/verify; Foundation111917066513 has159units11.51s, mypy56files,318combinedbackend111.00s,2+2browser,5Redis/Celery/Channels and1private-MinIO restart test. Additive accounts0012 SQL inspected in log. Previous wider MinIO gate is now resolved at this exact implementation head.
- Recovered host is Windows rather than the former Linux Cloud workspace. Current workspace contains no repository checkout. Python/py/uv/bash/wsl command discovery returned none; CODEX_PRIMARY_RUNTIME variables absent; codex_app/load_workspace_dependencies returned tool-request failure. Git Schannel credential acquisition failed; OpenSSL transport reached authentication but Git Credential Manager could not persist credentials and could not obtain password. Authenticated connector read/write remains available, so shell Git failure alone is not the blocker. Docker daemon pipe absent; Docker absence alone is also not the blocker because actual-service CI remains available.
- Task10 BLOCKED_BEFORE_RED: approved per-task local/cloud Python unit/static/TDD gates cannot execute on the recovered host without a usable Python3.13/uv runtime or restored Cloud executor. No Task10 implementation/test source has been written or claimed verified; do not skip RED or substitute unexecuted source review for GREEN. Resume at Task10 once execution runtime is available.
- C02 remains BLOCKED, not PASS. Tasks11–16 unstarted; exact populated C01-to-C02 rehearsal and full final security/CI review still mandatory in Task16. STOP before C03; no merge/deploy/vendor/C18 work.

## Verified Cloud continuation — Tasks10–16
- User continuation attachment authorizes only Tasks10–16, coherent local commits and authenticated Git Data sync on accounts/c02-cloud. No main/Foundation change, merge, deployment or C03.
- Recovery mapping: local a53d37678c9f5cc94669a08e74fdabae969ba8dd -> remote 4664e4123529c3c25bad3575b2797b5311a60c8a. Exact tree13beede47e6be7a822303a9ac6709b18da590d4b reverified clean before edits. Linux Python3.13.15/uv0.12.19 baseline159units passed9.66s; CI37361681677 completedSUCCESS. Synthetic ancestry must not be published.
- Immutable protected refs observed: main8ede9a451db6103f4e3ebf65784ee9f16b96feb2; foundation/c01-cloud75c551e5b9bbbfb7777ee52b09a1993b681e921a.
- Ruling: continue in user-selected recovered isolated checkout, retaining this authoritative ledger instead of reconstructing Tasks1–9 or new worktrees — preserves verified state and explicit recovery authorization — cost if wrong: this checkout is the single local recovery copy.

## Task10 — Consent Cloud checkpoint
- BASEa53d376. Full approved Task10 brief read; linked domain/permissions/storage/AI requirements inspected. Tasks1–9 intact;11–16unstarted.
- Cloud RED9expected missing validated core assertions0.08s before implementation; additional grant-event behavioral RED1expected ValueError/9passed before event extension. Logs recovery-runtime/task10-red.log.
- Added Consent/normalized ConsentScope, subject/grantee/purpose/text hash+version/expiry, required synchronous recorder, current User/session authority, exact scope revision, owner-only list/count, optimistic one-way revoke. Grant and revoke audit/outbox share the domain transaction. Sorted User participant locks serialize grant against identity restrictions. Unknown/uninstalled validators deny; dataclass values are revalidated at mutation/query. No object permission API or future domain objects.
- Ruling: the sole C02 validator is account_metadata for the existing own User/state_version, never sensitive data — permits real nonsensitive core tests without inventing health/photo objects; all future purposes remain closed until reviewed validators exist — cost if wrong: account metadata purpose would need narrower policy before a future public adapter.
- Ruling: add explicit ID-only consent.granted event alongside consent.revoked — user requires outbox on grant as well as revoke; existing event allowlist only named revoke — cost if wrong: Task13 must handle this additional bounded metadata event.
- Additive governance0004Consent schema,0005grant event+DB payload guard,0006immutable scope/terminal consent SQL guards. Earlier migrations unchanged; accounts0001/User unchanged. Exact Foundation model allowlist extends by Consent/ConsentScope only; no User reverse fields added.
- Cloud GREEN169units9.09s; Ruff/format159files, mypy62files, Django/production checks, no migration drift, diff check exit0. Local PostgreSQL history unavailable is not real migration evidence.
- Authored required real PostgreSQL tests before implementation: exact predicate/expiry/version/foreign actor/stale state/guessed ID/list/count/future scope, SQL terminal denial, grant/revoke audit+outbox rollback and independent-connection competing revoke. Real integration GREEN pendingCI; Task10 remains IN_PROGRESS and Task11 must wait.
- Focused author review: consent only predicate, no profile/health/relationship/AI provider; scope/text are not arbitrary audit payloads; UUID-only outbox; actor rechecked under locks; terminal SQL revocation and scope immutability; no generic web grant endpoint. Required SQL/race evidence remains pendingCI.
- Remote sync: local 38b8fdc772bda2fa9dc6b2c9ab8d1f19747b45ab -> GitHub a65436927d116d14698b572d42aa0f0a31880917. Verified exact treee4f73b77607cbb640c756d83351ab111fb6b79f6; actual remote parent4664e4123529c3c25bad3575b2797b5311a60c8a reread before non-forced C02-only ref update. Synthetic baseline not published. Required real CI pending; Task11 not begun.
- During required CI queue wait, completed two specifically planned contracts: independent-connection new grant vs revoke (old row stays terminal; new explicit revision is a new grant), and test-only server validator proving AI/archive/publication independence without live sensitive records. 23integration cases collect successfully;10focusedunits pass0.04s. Collection is not actual PostgreSQL evidence. No Task11 work. These test additions require a new head CI, not a blind rerun of an unexplained failure.
- First Task10 run37365997159 remains queued; neither job has executed a step or produced logs yet. No CI PASS or failure diagnosis claimed.
- Remote sync: local 1b4af970272bec5f68353deae6858501d2bc11bf -> GitHub a127df0dc6ac519ae5973aad609832a0dd7ce37a; verified tree3e4ec667e9d7083269fc926234be1879340371c5 and actual remote parenta65436927d116d14698b572d42aa0f0a31880917 before non-forced C02-only advance. Task10 pending required current-head service CI;11–16 unstarted.

### Task10 external CI blocker
- Current source head GitHuba127df0dc6ac519ae5973aad609832a0dd7ce37a, exact tree3e4ec667e9d7083269fc926234be1879340371c5. Required current-source run37366520349 queued; earlier37365997159 likewise queued. No job step or log has executed; neither is a failed run or PASS. Do not rerun blindly or advance Task11.
- Verified official GitHub Status unresolved incident3q1yb5m7ltvb (https://www.githubstatus.com/api/v2/incidents/unresolved.json): investigating hosted-runner assignment delays since2026-10-05T19:11:58Z, latest update19:50:50Z still investigating across runner configurations. This corroborates an external CI-start blocker; it does not prove an application defect.
- STOP at required Task10 PostgreSQL/Foundation CI boundary. Tasks1–9 remain COMPLETE; Task10 implementation is Cloud-verified but NOT COMPLETE;11–16 UNSTARTED. Full C02 review/upgrade/clean final migration gates remain unexecuted and mandatory. Resume by inspecting current-source run37366520349 exact job/step/log when runners execute; no repository rematerialization or Task1–9 repetition.

## Task10 CI reconciliation — 2026-10-05
- Remote accounts/c02-cloud80fe1218b7604c4d50610661eb0190194b44ebf8/tree819d070027f307bfede8f2165fb36891652ef9f9 verified against clean localb3eaae6. Only ledger documentation differs from source heada127df0dc6ac519ae5973aad609832a0dd7ce37a. No Task10 source was rewritten or repeated.
- Current-source run37366520349 Foundation111952925131 SUCCESS. Full decoded logs inspected: checkouta127df0;169units9.19s, Ruff/format159files/mypy62files/Django/production, fresh PostgreSQL migration governance0004..0006OK/no drift,351combinedbackend79.53s,2browser before restart,5actualRedis/Celery/Channels recovery,1privateMinIO recovery,2browser after restart. docker/verify_foundation.sh runs all tests/unit+tests/integration against actual PostgreSQL with fresh test DB and no reuse; all23Consent cases are selected within351. Root conftest fails any selected skip; no skips reported.
- Earlier run37365997159 Foundation111951190151 SUCCESS:169units11.63s/349combinedbackend114.77s (before2extraConsent cases),2+2browser/5transport/1MinIO; complete logs inspected.
- Dedicated migration jobs111951190437 and111952924987 CANCELLED before runner assignment, no steps; raw current-source job runner_id0, runner_nameempty. Log fetch404BlobNotFound confirms no executed log. Documentation run37366672604 both jobs CANCELLED before execution. Workflow conclusions FAILURE from cancelled jobs, not a demonstrated implementation/test failure. No blind rerun or production fix.
- Ruling: apply existing per-task gate precisely: Task10 requires real PostgreSQL Consent scope/version/expiry/rollback/cross-user/race tests, all executed successfully in current-source Foundation351suite — standalone duplicate migration-job cancellation does not erase that actual evidence; explicit emitted-SQL/durable limiter restart job remains mandatory at final fullCI — cost if wrong: finalTask16must reconcile every workflow job, not claim globalC02PASS from Task10.
- Task10 COMPLETE;Task11next;12–16unstarted. No whole-workflow PASS claimed;C02notPASS.


## Task11 Cloud implementation checkpoint
- Resumed existing recovered checkout; Task10 actual CI reconciled before any Task11 code. Existing Task10 implementation/commits preserved.
- Cloud behavioral RED:14 expected missing flag/referral contract failures before implementation. GREEN:14 focused contracts and183 full unit cases (9.51s).
- Four exact FeatureFlag keys, disabled data migration defaults, current authoritative reads with database failure disabled, optimistic row version and named feature_flags capability plus flag-bound fresh staff step-up. Same transaction audited ID-only feature_flag.changed outbox; no object authority or profile/capability creation.
- Digest-only256-bit opaque referrals with retained key lookup, expiry/revocation, anonymous link-UUID-only descriptor and no private identity. Current active adult issuer/recipient checks and ordered identity locks serialize unique first attribution; no future-domain FKs, rewards or lead conversion.
- Canonical first-party /i/<str:token>/ landing redirects to constant /, no-referrer/no-store, Secure HttpOnly SameSite=Strict signed UUID attribution cookie. Later cookie binding rechecks current issuer/recipient and link expiry/revocation; no raw token persistence/audit.
- Ruling: referral engineering lifetime30days, bounded signed-cookie lifetime matches; plan specifies expiry but no duration. This is acquisition metadata expiry, not a legal retention period.
- Ruling: explicit composition root config/use_cases/referral.py preserves accounts→governance import boundary; professional entry service reads only professional_registration, full entry UX remains sequential Task15.
- PostgreSQL tests cover four independent switches, bare staff/superuser denial, case-bound/stale authority, same-version race, fresh read outage, data seed defaults, digest/expiry/revocation/entropy, anonymous landing/cookie forgery, current restrictions/adult/self denials, first-attribution race, idempotence and audit rollback. They have not run on a real database yet; no Task11 PASS claim.
- Cloud Ruff/format171files, required mypy69files, Django check, migration drift (unavailable local PG history warning only), production deploy check and JS syntax pass. An over-broad exploratory mypy apps/config invocation reported existing out-of-scope Foundation stub/type errors; exact mandatory CI mypy target set passes unchanged.
- Task11 remains IN_PROGRESS until actual required PostgreSQL races/failure/current-source CI logs pass. Tasks12–16 unstarted.

## Task11 CI completion — 2026-10-05
- Runner health: official GitHub incident update21:54:23Z declares Actions operating normally. On inspection, existing run37369811515 was already executing attempt2 started21:58:50Z; no duplicate rerun or trigger commit created. Original zero-step cancelled attempt remains infrastructure fallout, not implementation RED.
- Remote f9c9bccffe07e3dc782c7fa7276623c9fd28342d/treec0b0c9172eb5c138319530f05024da8ccaf538d9 matches clean localef96111d482bbc51933c645367c9d194c7304cd0. Both retry logs confirm checkout of the authoritative remote commit.
- c02-migrations job111997366271 SUCCESS: additive SQL inspected including accounts0013/governance0007..0008;185 real PostgreSQL cases passed28.41s including all21 flag/referral cases, independent-connection flag-version and first-attribution races, disabled seeds, fail-closed reads and authority/rollback/cookie contracts. Redis durable quota prepare/restart/verify passed.
- foundation job111997366742 SUCCESS:183units11.94s, Ruff/format171files/mypy70files/Django/production and frozen/static checks passed; fresh migrations including new flag/referral schema applied, no drift;386combinedbackend132.36s,2browser before restart,5Redis/Celery/Channels recovery,1MinIO recovery,2browser after restart. No selected skips. Full required regression evidence inspected.
- Task11 COMPLETE. Tasks1–10 preserved. Task12 next;13–16 unstarted. No merge/deploy/C03.

## Task12 Cloud checkpoint
- BASEd46347e43904f7444cef8d9b89ef49457ee50e41 maps to ledger-only remote2f0007027ba03f656fbfa4f98cf4eafc19b7c89c/tree20b759d59ece6ac3ddb30985f9980992b6bf83bc. Task11 completed before Task12 edits; all prior rulings preserved.
- Cloud RED9expected missing privacy/hold contracts; GREEN9focused and192fullunits9.06s. Real PostgreSQL tests authored before implementation;28intake/hold cases cover owned status/list/count, confirmation and authoritative600s authentication, open-request idempotence, deletion invalidation/consent revocation, failure rollback, independent-connection intake/delete/logout/grant/recovery races, bounded holds and policy authority. Collection is not service execution.
- Governance PrivacyRequest/RetentionPolicy/RecordHold additive0009; no User/initial migration replacement or future domains. Composition supplies account restriction callback, synchronous audit/outbox and existing Consent revocations in the same transaction. Old session/OTP controls become unusable before return; no file generation/purge/provider/C18 execution.
- Ruling: expose explicit confirmed=True keyword on the server-owned intake command; default denies — plan requires explicit confirmation though its listed signature omits it — cost if wrong: later adapters must forward validated confirmation explicitly.
- Ruling: only installed record/case hold validator is privacy_request with exact owner/version/case UUID; no account-wide or future sensitive subjects — avoids inventing absent feature records — cost if wrong: future stages need reviewed validators before applying holds.
- Ruling: overdue review never silently releases retained evidence; expiry or authorized release ends this bounded hold — review is a staff obligation, not implicit erasure authorization — cost if wrong: policy owners must define escalation before C18.
- Retention policies start draft with duration unset; approval requires explicit positive duration and versioned backup reference, named privacy_operations capability plus policy/case-bound fresh step-up. Test durations are synthetic only; no live policy seeded. Existing effective policy is preserved; supersession remains denied until a reviewed command exists.
- Cloud Ruff/format179files, mypy75files, Django/production, frozen lock, JS and drift checks pass. Local unavailable PostgreSQL history warning is not migration execution evidence. Required actual PostgreSQL and full Foundation CI PENDING; Task12 NOT COMPLETE,13–16unstarted.
