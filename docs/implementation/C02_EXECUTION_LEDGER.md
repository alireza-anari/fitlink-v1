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
1. IN_PROGRESS — input/configuration contracts, no schema.
2–16. UNSTARTED.

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
