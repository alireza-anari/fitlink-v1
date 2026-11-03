# C04 Task 7 residual-cost decision

Task 7 remains **IN_PROGRESS / NOT ACCEPTED**. The single authorized residual-cost diagnostic completed successfully; it does not satisfy acceptance. No product, test, migration, lockfile or protected-branch changes were made. The private-draft fixture correction remains isolated. Task 8 was not started.

## Execution and source identity

- Diagnostic commit: `081e508fd2dfedc7a7726f5bd68e24fae10c716c`.
- Diagnostic tree: `91889314f7cdd18e5ad8b0dd512d50525dd48ee6`.
- Branch: `diagnostics/c04-task07-residual-cost-101`.
- [Workflow run 41604151542](https://github.com/alireza-anari/fitlink-v1/actions/runs/41604151542), attempt 1, exactly one job (`125809727336`), conclusion **success**.
- Task 6 runtime: `0787d7880f9fd27006bf76ae0f16e31536ef4503`, tree `b207a0a8e946750a0dd1213f5460e51f67dd3000`.
- Task 7 runtime/protected branch: `2b2790cdf9019338ddeb09f9df2fdfb1fa0dd331`, tree `f4a49666111ce27d6c12cc6aff89f3430c7ea243`.
- Previous report checkpoint: `924dba7933c6fecde53380d8eae138bfb34d7493`; its fixture correction was not included.

The complete diagnostic diff adds four diagnostic-control files only. The report/evidence publication changes documentation only, outside every workflow trigger path. The user-confirmed writer shutdown remains the ownership basis; no positive competing-writer evidence or active workflow was observed at preflight. Workflow inactivity alone is not proof of writer shutdown. The inaccessible Windows/WSL checkout was not accessed or independently verified.

## Collection and complete five-pass results

All six authorized functions and complete parameter sets were collected before any test execution. Inherited collection was 12 evidence-authority cases, one crash/recovery case, four cleanup-replay cases and seven broker/Beat-denial cases. New collection was four stale-derivative cases and one report-quota case. Inherited parameter/order digests match across sources. Runtime collection matched preflight on every pass. Exactly **101 executions and 303 passing phase records** were independently validated; no failure, skip, xfail, missing phase, observer error, truncation or unfinished child was present.

Seconds below are measured pytest session and phase wall times. Session time also contains collection/reporting work; command time additionally includes interpreter/uv startup and shutdown.

| Pass | Source | Observer | Cases passed | Session | Setup | Call | Teardown | Entire command |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 1 | Task 6 | Minimal | 24/24 | 22.170 | 3.068 | 16.263 | 2.286 | 24.264 |
| 2 | Task 7 | Detailed | 24/24 | 144.037 | 35.356 | 100.047 | 8.013 | 146.223 |
| 3 | Task 7 | Minimal | 24/24 | 24.403 | 4.866 | 16.339 | 2.589 | 26.522 |
| 4 | Task 6 | Detailed | 24/24 | 136.997 | 24.146 | 104.659 | 7.585 | 139.159 |
| 5 | Task 7 | Detailed | 5/5 | 118.445 | 35.609 | 80.524 | 1.754 | 120.728 |

Preparation took **27.406 seconds** against 600. Combined measurement took **457.523 seconds** against 600, including Redis resets, command overhead and evidence validation. The longest pytest command took **146.223 seconds**, below 180. Final cleanup verification completed within **0.690 seconds** of the original cleanup start, below 120. The single job finished in approximately eight minutes, below 25 minutes. No deadline was extended and no workflow was retried or rerun.

## Measured source comparison and observer effect

With minimal observation, Task 7's inherited session was **2.233 seconds longer (+10.07%)**. Its phase differences were setup **+1.799**, call **+0.076 (+0.47%)**, teardown **+0.303** seconds. The aggregate call phase was nearly unchanged in this selected sample.

| Inherited function, complete parameter set | Task 6 minimal call | Task 7 minimal call |
|---|---:|---:|
| Evidence authority | 5.980 | 5.966 |
| Process crash/recovery | 1.282 | 1.412 |
| Cleanup replay | 4.407 | 4.505 |
| Broker/Beat denial | 4.594 | 4.455 |

Detailed versus minimal session differences were **+114.827 seconds (6.179x)** for Task 6 and **+119.633 seconds (5.902x)** for Task 7. The profiler's callback-body CPU lower bounds alone were **62.461** and **65.840 seconds**, across 54.858 and 59.841 million callbacks. These are observed source-matched contrasts, confounded by pass order and host variation; they are not a pure randomized overhead estimate. Minimal hook overhead was not independently isolated; its sampler CPU was approximately 0.010 seconds per inherited pass.

**The detailed observer substantially perturbed execution.** Do not treat detailed wall time as natural test cost, subtract callback CPU to manufacture an unobserved baseline, or extrapolate these differences to the full suite. The original acceptance observer `docker/c03_pytest_triage.py` has no `sys.setprofile`/`sys.settrace` instrumentation; this new profiler overhead is not evidence that it caused the historical acceptance timeouts.

## Lifecycle, SQL, child and teardown observations

| Detailed pass | Main-thread SQL statements | SQL execute seconds | Approval lifecycle calls | Approval inclusive seconds | DB flush calls / inclusive seconds |
|---|---:|---:|---:|---:|---:|
| Task 7 inherited | 35,355 | 16.956 | 23 | 68.829 | 24 / 7.527 |
| Task 6 inherited | 35,250 | 17.585 | 23 | 70.682 | 24 / 7.251 |
| Task 7 new | 24,204 | 11.335 | 5 | 15.747 | 5 / 1.638 |

The inherited **call phases executed exactly 33,113 primary-thread statements on each source**; teardown executed 1,344 on each. The 105-statement difference occurs in setup (898 versus 793). This supports equal selected call workload, not a new selected call-query explosion. Setup includes first-test database/schema preparation; this observation does not repeat or replace previous migration-rendering attribution.

The approval lifecycle contains nested profile construction, credential, reviewer, verification command and decision timings. Its inclusive times overlap those nested labels and SQL execute time. The evidence also provides self time excluding labelled descendants; that is not total Python self time. Never add overlapping categories.

Each detailed inherited pass observed exactly one child process, the intended crash-boundary subprocess, with exit status **17**, parent-observed lifetime **1.325 seconds** (Task 7) or **1.355 seconds** (Task 6). Pytest itself passed. No children were observed in the new-case pass. SQL in child/worker threads and child CPU are not measured; no argv or child output was exported. This sample does not support subprocess lifetime as the leading inherited cost.

## New Task 7 cases

Only detailed observation was authorized for these cases, so their natural wall time and observer-specific inflation are **unknown**.

| Function | Cases | Detailed call seconds | Call SQL statements | Approval calls | Post-publication calls |
|---|---:|---:|---:|---:|---:|
| Assigned-media stale derivative binding | 4 | 40.866 | 12,104 | 4 | 2 |
| Account-serialized report quota/duplicate | 1 | 39.658 | 10,922 | 1 | 6 |

Post publication accumulated 35.144 inclusive detailed seconds across eight calls, including 26.221 seconds across six calls in the quota test. The new pass's profiler callback-body CPU lower bound was **55.243 seconds**, across 49.276 million callbacks. Those numbers localize repeated work under profiling; they are not measured removable or natural costs.

## Host resources, privacy and integrity

The hosted runner had **4 logical CPUs and 15,983.910 MiB memory**. Logs identify Ubuntu **24.04.5**, image `ubuntu24/20261025.353.1`, and installed uv **0.12.19**. Controller Python was **3.12.3**. Frozen environments requested Python **3.13.15**; per-pytest artifacts do not export the executing interpreter version, a reporting limitation. Dependencies were installed frozen and both sources retained identical lock hashes before and after.

Only owned PostgreSQL and Redis services ran. Selected storage paths used their unchanged in-memory test stores. This excludes Foundation's scanner, MinIO, worker and Beat background load and cannot reproduce its pressure or full-suite test ordering. Minimum observed available memory was **14,725.707 MiB**; sampled memory PSI was zero. Maximum sampled load per CPU was **0.599**; CPU PSI some avg10 peaked at **0.83**, I/O PSI some avg10 at **4.59**. One-second samples cannot rule out brief contention. These observations provide no evidence of sustained memory exhaustion in this diagnostic.

The exported evidence contains fixed function/lifecycle labels, occurrence ordinals and aggregate numeric metrics only. No account identities, credentials, SQL text/parameters, subprocess arguments/output, business rows or raw logs were published. Private credentials and pytest temporary files were removed. Both cleanup inventories verified **zero owned containers, networks and volumes**. A prior cleanup failure would remain a failed verdict even after later cleanup.

- Artifact ID: `13216266338`, ZIP size 35,552 bytes.
- Independently downloaded ZIP SHA-256: `fd8896f1fb77dc1f9de0d00a6180b59be78ab1211ef6e3e6f4e6fae5ee96abc3`, matching GitHub's artifact digest.
- Internal `SHA256SUMS.txt` SHA-256: `38b010ee10147c2e7f3f0a07e27aaec8841e2b35c7e2a69424e7de22d5a88fb1`.
- All seven internal JSON checksums and the exact eight-entry ZIP manifest were independently checked. All 101 observations were revalidated separately from the hosted verdict.
- Sanitized evidence is preserved alongside this report, including the original internal manifest. GitHub's hosted artifact expires 2026-11-17; the committed evidence remains available.

## Technical decision and next authority

**No additional removable fixture cost is established.** The inherited authority, public-read and erasure tests need real lifecycle state; the new stale-binding tests need public media, and the quota test needs distinct reportable public targets. Removing setup without additional characterization could remove the condition being asserted. No new fixture or product correction is justified by these timings alone.

Retain the previously validated private-draft correction on its isolated branch for eventual separately authorized integration. Its approximately 3.005-second measured saving belongs to its prior three-test experiment; this run neither repeated it nor measured a full-suite saving.

Ranked next actions:

1. Establish natural cost and localized publication cost for the **two new Task 7 functions**, using a minimal control and fixed-callsite wrappers instead of the global profiler. This resolves the explicit pass-5 measurement blind spot. Expected value is better attribution, not a promised runtime saving; product risk is low, hosted cost is bounded.
2. Separately authorize eventual integration of the characterized private-draft correction. It is already supported but has too little measured impact to justify an acceptance retry by itself.

**Single next authorization requested:** one new, Task-7-only, low-overhead diagnostic on a new isolated branch, attempt 1, one Ubuntu 24.04 job, unchanged pinned source and both complete parameter sets (5 minimal + 5 fixed-callsite executions = 10). It would replace `sys.setprofile` with exactly-once, return/exception-preserving wrappers at the existing approval, publication and post-publication helper callsites; retain phase/CPU/SQL counts and fixed labels; record actual pytest interpreter version; and measure the same original assertions. Require exact collection, local delegation/privacy/failure/cleanup checks, preparation <=600 seconds, each invocation <=180, combined measurement <=180, cleanup <=120 and job <=20 minutes. Use the same owned two-service topology, privacy allowlist, independent checksum verification and cleanup controls. No action under that proposed authority has been taken.

The complete Backend 900-second failure and Foundation 1,800-second cumulative deadline remain unresolved. This sample does not reproduce full-suite ordering, database growth or Foundation stage overlap and cannot assign a whole-suite bottleneck. Historical immutable-C03 MinIO initialization remains **unclassified**; it was not executed here, and prior isolated initialization success did not classify the original failure. Do not repeat isolated MinIO initialization; preserve failure-only subcommand evidence when its original context is independently authorized.

Acceptance still requires all **15 mandatory jobs** to pass on one authorized implementation source with unchanged assertions and original limits. No acceptance rerun, fixture integration, deployment or Task 8 work was performed.
