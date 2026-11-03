# C04 Task 7 — low-overhead new-case decision

Task 7 remains **IN_PROGRESS / NOT ACCEPTED**. The authorized two-pass diagnostic finished: **5/5 minimal + 5/5 fixed-callsite executions passed**. Source, locks and cleanup were preserved. Helper-level attribution has a specific alias-coverage limitation described below; it is not a complete call census. No fixture or product correction was implemented.

## Authority and execution

| Reference | Verified identity |
|---|---|
| Protected/runtime Task 7 commit | `2b2790cdf9019338ddeb09f9df2fdfb1fa0dd331` |
| Runtime tree | `f4a49666111ce27d6c12cc6aff89f3430c7ea243` |
| Diagnostic branch | `diagnostics/c04-task07-new-callsites-minimal` |
| Diagnostic control commit | `697816b8f6ea300f6508e0ebc37b1da05b50e340` |
| Diagnostic control tree | `6d99f2ba65e3659bffe94e3b5f273bd3cb3f41d9` |
| Previous evidence commit/tree | `ab136b9e99a9aed3844d036525482d1c13fa6748` / `5c73cc9a08407312c710f12fb3870e019720ba4e` |
| Workflow | [41688653353](https://github.com/alireza-anari/fitlink-v1/actions/runs/41688653353), attempt **1** |
| Hosted job | `126101060648`, exactly **one**, conclusion **success** |

Preflight verified the protected pins and previous report, no active/queued/pending/waiting/requested workflows, an absent new branch and zero prior new-branch runs. The user's writer-shutdown confirmation was the ownership handoff; no evidence contradicted it. Inactivity alone is not proof of writer shutdown. The original Windows/WSL checkout was untouched and was not independently verified.

The branch starts from pinned Task 7, not the private-draft correction or previous diagnostic. Its control commit adds only one workflow, one probe, one observer and one control-harness file. Twelve harness checks passed locally and on the hosted job. No original test was run locally. The earlier 101-execution run was not repeated.

## 1–3. Natural-runtime reference and remaining inflation

The same complete five-case manifest was collected before testing and matched in both passes. Its digest is `68bc0e0cef1eecc1a71195a7d3560e49db174347b9302381c668d37960d31207`. Both passes used **CPython 3.13.15**, **pytest 9.1.1**, and frozen locks with verified **uv 0.12.19**. All ten call outcomes and thirty phase outcomes passed, with no skip, xfail, observer error, truncation or collection mismatch.

| Function / complete cases | Minimal setup | Minimal call | Minimal teardown | Minimal phase sum | Fixed call |
|---|---:|---:|---:|---:|---:|
| Assigned-media stale derivative binding / 4 | 6.987 s | **8.921 s** | 0.576 s | **16.484 s** | 9.064 s |
| Account-serialized report quota/duplicate / 1 | 0.001 s | **8.555 s** | 0.211 s | **8.768 s** | 8.617 s |

The first function bears the session's first-test database/schema setup; do not interpret its 6.987-second setup as four independent fixture costs. Minimal stale-binding call occurrences, in unchanged collection order, were **2.105, 2.402, 2.003 and 2.410 seconds**.

| Whole pytest session / phase | Minimal | Fixed-callsite | Fixed minus minimal |
|---|---:|---:|---:|
| Collection wall | 0.637 s | 0.694 s | +0.057 s |
| Setup wall | 6.989 s | 6.963 s | -0.025 s |
| Call wall | 17.476 s | 17.681 s | +0.206 s |
| Teardown wall | 0.788 s | 0.788 s | +0.001 s |
| Session wall | **25.897 s** | **26.136 s** | **+0.239 s / +0.921%** |
| Session process CPU | 19.694 s | 19.918 s | +0.224 s |
| Session main-thread CPU | 19.694 s | 19.904 s | +0.210 s |
| Entire pytest command | 28.728 s | 28.978 s | +0.250 s |

The fixed call-phase increases were **0.144 seconds / 1.611%** for stale-binding and **0.062 seconds / 0.724%** for quota. These are two sequential observations, not a randomized causal overhead estimate. Order, cache and host variation remain confounded. Minimal observation still has phase/session hooks; its hook cost was not independently isolated. The fixed pass is not pure natural time.

Fixed-wrapper bookkeeping CPU measured **0.000546 seconds**, a lower bound excluding dispatch, SQL-wrapper and timer overhead. Alias installation took **0.049771 seconds**, restoration **0.000027 seconds**, and resource-sampler CPU **0.013332 seconds**. The whole-session contrast is the useful observed combined observer effect. No global profiling or tracing mechanism was used.

## 4. Observed lifecycle, publication and SQL work

Ten exact helper functions were wrapped; 25 qualified-module aliases were rebound and restored. All ten labels recorded activity. The following are **observed fixed-wrapper counts and inclusive seconds**, not complete whole-program totals:

| Helper label | Calls observed | Inclusive seconds |
|---|---:|---:|
| Full approval | 5 | 3.696 |
| Verification review | 5 | 2.324 |
| Verification target decision | 15 | 1.045 |
| Professional publication preparation | 5 | 0.335 |
| Professional publication confirmation | 5 | 0.535 |
| Profile-media pending setup | 2 | 2.523 |
| Post pending setup | 8 | 4.015 |
| Post-publication outer helper | 6 | 5.654 |
| Post-image metadata/PNG construction | 8 | 0.023 |
| Public-copy processing helper | 8 | 3.565 |

Approval contains verification review/decisions; post-publication contains pending setup and media processing; pending setup contains image construction. **Do not add nested inclusive values.** Exported self time subtracts labelled child intervals only, not every Python descendant, and remains conditional on the observed wrapper coverage.

For the quota case, all six post-publication helper calls were observed: **5.654 seconds**, including **2.986 seconds** in pending setup and **2.667 seconds** in public-copy processing. Its six image-construction calls totaled just **0.017 seconds**. These locate real repeated publication work; they do not establish removable work.

| Fixed pass SQL scope | Statements | Execute seconds |
|---|---:|---:|
| Setup | 898 | 0.534 |
| Call — stale-binding | 12,104 | 3.851 |
| Call — quota | 10,922 | 3.521 |
| Teardown | 280 | 0.462 |
| Total | **24,204** | **8.369** |

SQL covers the primary thread's default Django connection only. It does not include every database-creation connection, worker-thread SQL or child-process SQL. SQL execute time overlaps helper/phase timers; no exclusive SQL-versus-Python subtraction is warranted. SQL contents and parameters were never retained.

### Attribution limitation discovered during independent validation

The measured helper counts do not cover two direct profile-media processing calls and two stale-binding outer `published` calls indicated by the unchanged source. The observer rebound qualified module aliases only. Source-based inference: pytest's separately collected top-level module references retained the original functions; `tests/integration` and `tests/integration/c04` lack package initializers, and the harness did not bind aliases through each actual collected item's module object. No runtime module inventory was exported to independently prove that import-path explanation. Consequently, the stale-binding subset records **two of four** source-indicated media-processing calls and **zero of two** outer post-publication calls. Nested post-pending/image calls and other wrapped helpers remain observed; all phase/session and main-thread SQL measurements cover the unchanged test execution.

This was an observer alias-coverage gap. The hosted validator required activity for each allowlisted label across the pass, which did not catch missing occurrences in one function when another function exercised that label. The hosted success/valid verdict and original artifact are preserved verbatim; the independent engineering classification is **COMPLETE_TEST_RESULTS / PARTIAL_HELPER_ATTRIBUTION**. No missing helper time is reconstructed or asserted. No rerun or post-run control correction was performed. Future reuse would need to include actual collected-item module objects in identity-based alias binding and characterize per-function coverage; this report does not request a rerun merely to repair that gap.

## 5–6. Necessary repetition and correction decision

**No avoidable setup or new narrow fixture correction is established.**

- The four stale-binding cases cover both profile/post targets and before/during-I/O mutation. Real confirmed media binding is the condition under test; approval/publication cannot simply be omitted.
- The quota case requires six distinct, actually public post targets so that the sixth report fails on quota rather than unavailable content. Duplicate-report receipt equality is also checked for the first five targets.
- Pinned `apps/governance/moderation.py::report_public_content` calls `target_source` before the quota check. Replacing the sixth public target with an invalid draft would change the denial being exercised.
- Pinned `PostInput.validate_publication()` requires at least one image, `posts.publish_post()` invokes that validation, and `test_post_publish_requires_explicit_confirmation_and_images` characterizes draft/text-only denial. Replacing image posts with text-only posts would not preserve the actual publication contract.
- The current helper uses one image per post, already the minimum. PNG construction is a measured small component; removal would not demonstrate a meaningful deadline saving.

Thus no exact fixture edit is proposed under this evidence. Natural runtime savings from any counterfactual correction remain **unmeasured**. Do not extrapolate five cases to the complete backend.

## Resources, limits, preservation and artifact integrity

The runner had **4 logical CPUs**, **15,983.910 MiB RAM**, Ubuntu **24.04.5**, image `ubuntu24/20261025.353.1`. Controller Python was 3.12.3; actual pytest Python was separately recorded as 3.13.15 in both passes. Only real PostgreSQL and Redis ran in the unique owned Compose project. Test storage fixtures were unchanged. The topology does not reproduce Foundation's scanner, MinIO, worker, Beat or full-suite ordering/load.

The fixed pass took 26 resource samples: minimum available memory **14,789.852 MiB**, maximum normalized load **0.246**, CPU PSI some avg10 **0.80**, I/O PSI some/full avg10 **0.06**, memory PSI zero. No sustained memory pressure was observed; one-second samples cannot exclude brief contention. Minimal mode did not start the sampler. Child-process and worker-thread CPU/lifecycles were not instrumented.

| Limit | Observed | Ceiling |
|---|---:|---:|
| Preparation, including earlier workflow setup | 32.731 s | 600 s |
| Longest pytest invocation | 28.978 s | 180 s |
| Combined controlled measurement | 58.037 s | 180 s |
| Cleanup through unconditional verification | 0.897 s | 120 s |
| Job | under 2 minutes | 20 minutes |

The runtime HEAD/tree remained exact and clean. Lock hashes before/after were unchanged: uv.lock `36671286a414ab75c37aa7fc1ec76aa06d6a788ac7b047e78d70b212207425a2`; package-lock.json `1d7c6cc4ed2cb7bf1553f1ec4fe9ea6744bb7a82880363cee51b2a4db5c029c1`. Cleanup verified zero owned containers, networks and volumes, and removal of the private environment and pytest temporary files. No private raw logs were exported. Sanitized metrics contain fixed function/helper labels and numeric aggregates, with no identities, phone numbers, credentials, object keys, SQL/parameters or subprocess arguments/output.

- Artifact ID `13257645286`, original ZIP size **6,580 bytes**.
- Independently downloaded ZIP SHA-256: `fbd246ff27a59732d7b6e52910a1be256a57fa9dda2efd3e2e7d0573ad127246`, matching GitHub's digest.
- Internal `SHA256SUMS.txt` SHA-256: `d148445fd955cf0dee53d64704cc5ad3be06412811332c81f3230199aff61275`.
- Exact six-entry ZIP manifest and all four internal JSON checksums independently verified. Ten passing executions/thirty passing phases, actual versions, fixed-label privacy and source/cleanup claims were independently rechecked. Original artifact bytes are committed alongside this report; the hosted ZIP expires 2026-11-17.
- Failure classification: none for test execution, infrastructure, source preservation or cleanup; helper attribution limitation is recorded explicitly above.

## 7–10. Next decision, retained correction and unresolved acceptance

**The highest-value remaining acceptance investigation is the uncharacterized full-suite execution-context cost, not another benchmark of these five cases.** This sample's natural call total is 17.476 seconds and provides no demonstrated removable cost. It does not explain the historical complete-backend shortfall, the observed slowdown of other inherited cases, cumulative teardown/order effects or the work remaining after Foundation's browser stages.

**Exact next authorization requested:** one read-only residual full-suite cost audit using already published evidence—original acceptance `40084769140`, its completed Foundation backend phase artifact, the accepted Task 6 timing checkpoint and the published three-gate/timing reports. Exclude the completed private-draft, candidate-budget, migration-rendering and both residual/new-case experiments from remeasurement. Reconcile timing coverage for the *remaining* inherited/new families, distinguish startup/call/teardown and execution-context differences, inspect the highest remaining fixture call graphs, and return one specific correction candidate or one concrete causal verification proposal. **No repository writes, hosted workflow execution, test reruns or acceptance rerun** are requested for that audit. Do not spend another hosted run merely to fill this observer's alias gap.

Retain the characterized private-draft correction on its existing isolated branch for separately authorized future integration. Its prior approximately 3.005-second saving was not repeated here and is not a complete-backend saving.

The **900-second complete Backend deadline** remains unresolved. The **1,800-second Foundation deadline** remains unresolved; its prior complete backend/browser/consolidation evidence is not replaced by this two-service subset. The historical **immutable-C03 MinIO initialization failure remains unclassified**; no MinIO service or initialization diagnostic ran here. Prior isolated success does not classify that historical failure.

No protected branch update, original test/fixture change, production/migration/lock edit, private-draft integration, acceptance run, merge, deployment or Task 8 work was performed. Acceptance still requires all **15 mandatory jobs** to pass on the same authorized implementation source with original assertions and limits. This diagnostic is complete within its stated attribution limitation; **Task 7 remains IN_PROGRESS / NOT ACCEPTED**.
