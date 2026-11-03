# C04 Task 7 — four-function ABBA diagnostic: stopped at offline harness

**Status:** `BLOCKED_DIAGNOSTIC_CONTROL`. Task 7 is **IN_PROGRESS / NOT ACCEPTED**. This report records one consumed workflow authorization. **No original pytest test executed** and no acceptance result was produced.

## Authority and immutable source pins

- Execution branch: `marketplace/c04-cloud`, commit `2b2790cdf9019338ddeb09f9df2fdfb1fa0dd331`, tree `f4a49666111ce27d6c12cc6aff89f3430c7ea243`.
- Accepted Task 6: commit `0787d7880f9fd27006bf76ae0f16e31536ef4503`, tree `b207a0a8e946750a0dd1213f5460e51f67dd3000`.
- Isolated control branch: `diagnostics/c04-task07-abba-four`.
- Trigger/control commit: `f151fd699ca81d728dc99da7d88a8617700e9941`.
- Hosted workflow: [41703990982](https://github.com/alireza-anari/fitlink-v1/actions/runs/41703990982), attempt **1**, exactly **one job**, job ID `126154342644`, **failure**.
- Preflight: branch did not previously exist; protected HEAD and both source trees checked; zero active/queued GitHub workflows; no evidence of a competing GitHub workflow writer. Unavailable local Windows/WSL checkout was not inspected or modified.

## What ran

The authorized diagnostic was designed to run a fixed four-function manifest on Task 6 / Task 7 / Task 7 / Task 6 (A-B-B-A), with 16 total original pytest executions, fresh pytest databases, exact collection checks, and class/SQL/fixture timers. It was **not started** because the offline harness failed. The full original selections, code and assertions remain unmodified.

| Hosted step | Outcome |
|---|---|
| Start preparation clock | success |
| Checkout diagnostic controls | success |
| Pin interpreter and uv | success |
| Checkout immutable Task 6 | success |
| Checkout immutable Task 7 | success |
| Offline Harness | **failure: 13 of 14 checks passed; one error** |
| Four original pytest functions, four passes | **skipped, zero tests executed** |
| Unconditional cleanup | success |
| Sanitized evidence artifact upload | success |

### Root cause: first observed failure

The Harness case `test_exact_two_pass_manifest` was updated to the four-function manifest in its positive check but three negative checks continued passing the old group key `'new'` to `collection_record`. The new plugin defines only `SELECTIONS['four']`; the first negative check raised `KeyError: 'new'`. The error is deterministic in the offline Harness. The validator did not complete and therefore correctly prevented application pytest, Docker service startup, and any observation from being represented as successful.

The exact stale references are in `docker/test_task07_abba_harness.py`, lines **50–52** of the trigger commit. They must all be `'four'` before any separately authorized run.

### Second static control defect, not reached in hosted execution

The workflow preparation-clock command contains `+"\\\\n"` at the Python source level (two literal backslashes before the letter n). That Python expression writes a literal backslash-plus-n rather than a newline to `GITHUB_ENV`. The controller subsequently expects `float(FITLINK_PREPARATION_START)`. This combination risks rejecting the preparation timestamp even if the Harness is corrected. This is **static code review**, not an observed runtime failure: the controller step was skipped. The workflow clock writer must emit an actual newline (one source-level backslash in `"\\n"`) and be checked with a dedicated offline test before any future authorization.

Other controller/observer code has **not been validated by original pytest**. No assumptions about migration/query timing or background load may be drawn from this run.

## Independently verified cleanup and evidence

- Hosted artifact ID: `13265336610`, ZIP size **462 bytes**, GitHub digest `sha256:f5e378623459afda4bc674ca12c667a1c2f67fc0260f8a3c726fa496c5b0e033`.
- Independent download SHA-256 matched exactly: `f5e378623459afda4bc674ca12c667fc0260f8a3c726fa496c5b0e033`.
- ZIP has exactly `cleanup.json` and `SHA256SUMS.txt`; internal cleanup digest matches: `e04a8f577a0f344801132c56ca0b46b9e0167d642358c384e0668f60c9836370`.
- Cleanup: `verified=true`, `owned_resources_created=false`, `private_files_removed=true`, zero owned containers/networks/volumes. Cleanup wall **0.179512 seconds**.
- No private application logs or database values were published. No product source, migration, test fixture, lockfile or protected branch changes occurred.

## Decision and authorization

**STOP**. The sole authorized hosted workflow run was consumed. Do **not** rerun it, commit a changed workflow to trigger another run, retry acceptance, or start Task 8. An isolated control correction could be prepared only under a separately approved next diagnostic; before rerunning, fix both independently identified control defects, run offline validation against the complete manifest, and reverify that source pins and test assertions remain unchanged.

The historical 900-second Backend, 1800-second Foundation, and immutable-C03 MinIO gates remain unresolved. This failed infrastructure/control probe provides **no new performance attribution** and no Task 7 acceptance.
