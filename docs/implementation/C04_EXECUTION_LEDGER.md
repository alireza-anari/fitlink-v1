# C04 execution ledger — approved plan: docs/superpowers/plans/2026-10-18-c04-marketplace-search-public-profiles.md

## Authority and initial checkpoint — 2026-10-18

User explicitly approved all eleven tasks at planning commit
`ba82967cb2e21920076c5a0d25ed1988f777e943`, tree
`1478d691b2a60d95f6c0d2ce5e561d34f59a61c0`, and separately authorized
sequential autonomous execution. No merge, production release, deployment,
force update, completed-stage ref mutation or C05 implementation is authorized.

Live refs and Git objects were independently read before creation. Planning
parent is C03 handoff `0a867328a6d8ee8c71ec9bd9eeb8910221d1b270`, tree
`5c294cb330cf08b297cc01c8baa27adb1e6b93b7`; its parent is tested C03
`97fb92a2f074e3d13795670246636fad1a822055`, tree
`451faaac7c3ffbf6235b7e666db47e46a75fa528`.

`marketplace/c04-cloud` was absent, then created from the exact reviewed planning
commit. A fresh isolated local clone has the same HEAD/tree and both C03 anchors
as actual Git ancestors; no synthetic ancestry or prior unpublished work exists
in this new clone. Other session files were preserved.

Protected-by-instruction heads at start:
- main: `8ede9a451db6103f4e3ebf65784ee9f16b96feb2`
- foundation/c01-cloud: `75c551e5b9bbbfb7777ee52b09a1993b681e921a`
- accounts/c02-cloud: `0905be6c6ca608d469fe33e87f514b22591132d1`
- profiles/c03-plan: `79fd62e583cbe81f335bb08fce0eb43ff36b0167`
- profiles/c03-cloud: `0a867328a6d8ee8c71ec9bd9eeb8910221d1b270`
- marketplace/c04-plan: `ba82967cb2e21920076c5a0d25ed1988f777e943`
All four diagnostic refs were also read and preserved. No administrative branch
protection is inferred from instructions; live GitHub reported protected=false.

Pre-flight shared interfaces:
- Tasks 2→3→4: confirmed immutable professional release authorizes copies; final
  source/generation fences precede public projection release. No conflict.
- Tasks 4→5→6→8→9: one fresh public reader supplies search, selections, HTML and SEO.
  Current verified-role intersection remains authoritative. No conflict.
- Tasks 3+7→8: new educational-image purpose is added only in Task 7; old source
  and preview purposes remain private. No conflict.
- Tasks 1→all→11: immutable original C03 full runtime and eleven inherited
  current-source jobs plus cumulative C04 gates are required at each checkpoint.
  Full hosted evidence, not a local focused PASS, controls advancement.

## Task 1 — IN_PROGRESS, no acceptance or advancement

BASE: approved planning commit above. No production code or migration changed.
New scope: explicit isolated C04 workflow; unchanged inherited workflow bytes and
executable job counterparts; immutable C03 manifest/verifier; exact-head job
manifest validator; fail-on-skip C04 runner and cumulative Task 1 PostgreSQL tests.
Original C03 verifier, privacy/eligibility/source guards and all inherited tests
remain unchanged in this checkpoint. Historical migration-target adaptation is
not needed until dependent C04 schema arrives; it remains required before Task 2/4
migration acceptance. No security assertion is removed preemptively.

Behavioral RED: existing workflow has only accounts/c02-cloud and profiles/c03-cloud
push triggers. `pytest tests/unit/c04/test_ci_contract.py::test_c04_ref_runs_every_inherited_gate`
actually failed: C04 execution ref has no isolated hosted trigger (1 failed).
No import/infrastructure error was counted as this RED.

Focused GREEN: 24 passed, zero failed/skipped in new C04 unit controls, including
all eleven executable-job fake-command mutations, missing/skipped/wrong-head/
wrong-attempt/duplicate/extra-job evidence, exact immutable-source mutation and
unchanged inherited workflow blob. Source verifier independently reconstructed
C03 tree `5c294cb330cf08b297cc01c8baa27adb1e6b93b7` from the actual fixture.
Ruff format/check and shell parse passed on new files. Frozen Python dependencies
installed at approved Python 3.13.15; lockfiles unchanged. Frontend npm ci,
Tailwind build and ES syntax checks passed.

Initial complete unit run: 710 passed, 12 failed, zero selected skips. Eleven
failures were the inherited native decoder clean-pixel/isolation cases; one was
missing unbuilt dist/app.css in the inherited manifest test. CSS was then built
through the original npm commands; the static test is rerun separately. Native
isolation probe returns unavailable in this managed local host; a bounded direct
probe shows PermissionError errno=1 in the unchanged isolation boundary. This
is an unsupported local isolation runtime, not accepted native GREEN and not a
reason to relax decoder isolation. Required hosted nonroot/Docker/native gates
remain mandatory. Local Docker is not installed; real-service evidence will be
obtained on hosted Actions. No service PASS is claimed locally.

Ruling: keep original ci.yml and all inherited executable commands byte/semantically
unchanged, porting only explicit C04 ref guards in a separate workflow and adding
exact immutable C03 fixtures to full-unit jobs — required by the approved CI
contract; cost if wrong: Task 1 fails hosted acceptance and cannot advance.

Ruling: defer current-stage C03 absence/historical-target assertion adaptation
until the schema/route task first needs it, with immutable original tests retained
— no C04 schema exists in Task 1, so no behavioral conflict yet; cost if wrong:
first dependent task is blocked until its explicit harness correction passes.

Next: publish this Task 1 candidate non-forced; inspect every mandatory hosted job,
actual skip/failure/cleanup evidence and first causal failure. Correct ordinary
in-scope problems and rerun the complete exact-head manifest. Task 2 is NOT_STARTED.

Additional Task 1 checks: inherited static-page tests plus C04 controls now
26 passed / zero failures/skips after the original static build. Complete-tree
Ruff/format (443 Python files), Django system check, and shell syntax pass.
Focused mypy for the three new helper modules passes with imported historical
modules treated as external; a broader exploratory invocation reported existing
historical verifier Path/PurePosixPath annotation errors, so no historical code
was edited to satisfy an unrelated expanded typing scope. Task-generated mutated
fixture copies were moved into ignored .runtime before whole-tree lint, without
changing their bytes. Original baseline sources were not modified.

### Task 1 forward source-binding correction — still IN_PROGRESS

Shell push had no GitHub credentials; the authorized GitHub connector published
identical source tree `9398bb402f37e9e8682a21acbcddbfb1ced4d9be` as remote
`b0ac843fc32366a001f7601e922670e9bb9daa0d`, parent exactly the approved planning
commit. Local source commit `6cf2780a610f2fb9de2b95864e3267f19174b6d1` was preserved
on local/c04-task01-source; actual remote ancestry was fetched and checked out
without overwrite or synthetic history. No completed/planning ref changed.

Hosted run `39158759787`, attempt 1, is the first candidate run on b0ac843/tree
9398bb4. At review time c04-postgresql, c03-timeout-probe and c03-evidence-audit
were SUCCESS; remaining required jobs were still running. No task acceptance
is inferred from these partial results.

Distinct Task 1 review found an Important evidence-validation gap: a successful
job set could match SHA/branch but not the intended workflow path/event/tree.
Actual RED `test_acceptance_binds_workflow_path_event_and_source_tree` showed the
wrong workflow path was accepted. Fix binds the official run path, push event,
head_commit.id and tree_id to the exact implementation SHA/tree. Added negative
wrong-event/tree/commit tests. Actual GitHub run metadata confirms all fields
exist; no fabricated API shape was assumed. Checkpoint schema validation also
rejects COMPLETE with absent hosted/runtime/cleanup evidence; initial missing
schema-validator RED was observed before its implementation.

Corrected focused GREEN: 29 C04 controls plus 2 inherited static tests = 31
passed, zero failed/skipped. Whole-tree Ruff, focused new-helper mypy and format
pass. A fresh complete hosted manifest is required on the corrected source;
previous-run PASS cannot accept this change. Task 2 remains NOT_STARTED.

### Task 1 hosted acceptance blocked — 2026-10-18 UTC

Corrected remote implementation: `76160937b81186f7c0f6b5f6cf00ddec62599576`,
tree `3a21a2469898febaabb41ffa37dc5f7dd41832cd`, actual parent b0ac843.
Local matching source commit cbdef158e66bfc8529499d962a82fd2a25084cf2 was
preserved on local/c04-task01-binding-source. The actual remote branch and exact
matching tree were fetched and checked out without replacing legitimate work.
Hosted run `39159006853`, attempt 1, executes the full installed manifest.

First causal failure on this head: Foundation job `117768128292`, step
“Exact C01 upgrade and complete isolated C02 regression”, reached the unchanged
1,200-second observation deadline. Earlier hosted quality/unit phase passed
739 tests. Runtime observer recorded 1,748 passed / zero failed / zero skipped,
but C02 browser command was still active at cutoff. Observed return code was
not natural success; reason observation_deadline, cleanup complete. This is
INCOMPLETE/FAILED acceptance, not a test PASS, waiver or behavioral RED.

Superseded run 39158759787 at b0ac843 had the same observation cutoff after
1,763 passing checks and no failed/skipped checks, with its final Foundation
smoke still active. Its processing job also exited during MinIO initialization
before application/scanner tests; that startup failure did not recur on corrected
head, whose real processing and native jobs are SUCCESS. No unproven underlying
MinIO network/credential cause is asserted and no source/ACL control was relaxed.

Corrected-head successful jobs already observed: c02-migrations, c03-owner,
c03-staff, c03-storage, c03-processing, c03-restart, c03-timeout-probe,
c03-task14-native, c03-evidence-audit, c04-postgresql. Public artifact/log metadata
confirms C04 30 passed, owner 75 passed, staff 67 passed, private storage 91 passed,
all zero failed/skipped. These partial job successes do not complete Task 1.

Full c03-final job `117768128404` and immutable c04-baseline job `117768128528`
were still active at this observation. The c04-final aggregate cannot accept
failed Foundation or incomplete upstream work. Request to rerun only Foundation
through the authorized connector was rejected by GitHub: HTTP 403, workflow run
containing the job is already running. This is a provider state restriction,
not an automatic approval-review rejection or a missing user authorization.

Next recovery: obtain both full rehearsals' terminal stage/cleanup evidence;
then use at most one evidence-supported same-SHA failed-job retry under the
approved policy. Preserve the original observer bound, immutable baseline and
all assertions. Repeated failure stops advancement for diagnosis; no blind
window increase, mock substitution or Task 2 start. Task 1 remains BLOCKED on
mandatory hosted acceptance; Tasks 2–11 remain NOT_STARTED. This local observation
will be synchronized in a normal forward checkpoint, without using a docs push
to evade GitHub's active-run retry restriction.

### Task 1 full rehearsals GREEN; single retry used — 2026-10-18 UTC

Terminal first-attempt full-source evidence was inspected, not inferred:
- Current-source c03-final `117768128404`: all 127 stage exits zero, natural
  final_rehearsal_passed after cleanup; complete backend 1,722 passed, focused
  Task14 38, clean owner browser 10, staff browser 28, C02/Foundation browser 40,
  upgraded C02 browser 38 and real-service integrations 10; no failed/skipped
  tests in any recorded phase. Populated upgrade, source fences, native/service
  failures/recovery, independent clean migration and cleanup all passed.
- Immutable original c04-baseline `117768128528`: all 127 stage exits zero,
  original backend 1,692 passed with the original focused/browser/service gates,
  natural final_rehearsal_passed and cleanup. No immutable fixture was changed.

The first-attempt aggregate correctly failed upstream acceptance because
Foundation remained failed. After the workflow became terminal, the connector
successfully reran ONLY Foundation and its dependent aggregate on the SAME
implementation SHA. Run `39159006853` is now attempt 2; Foundation retry job
`117778573606` is active. GitHub lists carried-forward successful jobs under
attempt 2; their actual first-attempt runtime evidence above remains recorded.
This is the ONE permitted same-SHA retry. Do not request another blind retry if
it fails. No timeout, test assertion, selection or baseline was relaxed.

Task 1 is still IN_PROGRESS/BLOCKED pending that retry's natural complete success,
all fourteen required job results, actual zero-skip/runtime/cleanup evidence and
final exact-head manifest validation. Tasks 2–11 remain NOT_STARTED.

### Task 1 retry terminal; bounded browser diagnosis — 2026-10-19 UTC

Recovered live run `39159006853` attempt 2 on unchanged implementation
`76160937b81186f7c0f6b5f6cf00ddec62599576` / tree
`3a21a2469898febaabb41ffa37dc5f7dd41832cd`: completed FAILURE.
Twelve required jobs succeeded; Foundation `117778573606` failed and dependent
aggregate `117783181582` correctly denied upstream acceptance. Carried-forward
success metadata is not a claim that successful jobs re-executed in attempt 2.

Foundation retry reached natural command exit 1 after 1,144.8 seconds, with
host/container cleanup complete. It reported 1,789 passed, ONE failed, zero
skipped. The first causal failing assertion/call is the inherited browser test
`tests/e2e/c03/test_owner_setup.py::test_owner_dual_context_resume_optional_consent`
at line 53 (`page.reload()`), exception class Error. This differs from the first
attempt's observation deadline. The existing metadata deliberately excludes
exception messages; the underlying browser error category is NOT yet established.
No navigation-race, server outage or product defect is asserted as root cause.

Approved §6 permits bounded metadata-only diagnostics. Current-source
`docker/c03_pytest_triage.py::failure_data` now classifies Playwright exceptions
into a finite static enum, without emitting messages, URLs, values, call logs,
locals, traces, screenshots or page content. No test assertion, timing bound,
selection, runner exit, workflow job or application behavior changes. The
immutable original C03 fixture remains byte-identical. Behavioral RED: five
category/privacy cases failed (one non-browser control passed) before the helper
change. GREEN: all 35 C04 unit controls pass, Ruff check/format pass. A fresh
forward diagnostic commit requires the COMPLETE new-head hosted manifest;
passing diagnostics alone cannot accept Task 1. This is not another same-SHA
blind retry. Task 1 remains unaccepted; Tasks 2–11 remain NOT_STARTED.

### Task 1 diagnostic checkpoint and build boundary — 2026-10-19 UTC

Published bounded browser triage as nonforced forward commit
`4a1a3f113ff516ca08740429b77ce54815eb1be8`, exact tree
`3c3a65c2f76731ed6b4e6a2638c005737282216b`, parent `76160937...`.
Local authoring commit `a619e0d27ef32a193eae3b01cd0567ed9c9b18be` has the same tree
and is preserved on `local/c04-task01-browser-diagnostic`. Local focused current
C03 CI/scope plus C04 controls: 133 passed, zero failed/skipped. Full hosted run
`39200620956` attempt 1 is bound to this source. All completed-stage, planning
and diagnostics branch heads were rechecked unchanged before publication.
Immutable C03 verifier independently returned the exact `5c294cb3...` tree.

Two terminal inherited jobs fail before tests/services: restart `117892652554`
exits 1 after 130.9 seconds; processing `117892652598` exits 1 after 218.3 seconds.
Their snapshots show `docker compose build`/BuildKit active and no service
containers; command exits naturally and host/container cleanup is complete.
The actual build error is suppressed by the original metadata-only observer.
Do not label this a proved network failure or retry blindly. Other current-head
jobs successfully build/run; that alone cannot establish these failures' cause.

A second bounded metadata change adds only finite infrastructure categories to
`docker/c03_gate_diagnostics.py::progress_lines`, emitted to the existing journal
through `watch::read_progress::record`. No raw child output or interpolated
capture is emitted. Categories never authorize success or change child exits.
Behavioral RED: six category/privacy cases failed before implementation, one
unrecognized-output control passed. GREEN: 53 combined C04/observer controls
pass, including an actual failing subprocess whose exit 17 is preserved and
whose secret-bearing build message is absent from journal/stdout. Local host
cleanup observability is unknown in this restricted environment; the subprocess
unit does not claim Docker cleanup. Hosted real-service cleanup remains mandatory.
Ruff check/format and git whitespace checks pass. No immutable fixture, original
CI, gate selection/deadline or production code changed.

Latest observed current-head results: storage, evidence audit, migrations,
timeout ownership, PostgreSQL, native, owner and staff GREEN. Owner actual
runtime: 75 passed, zero failed/skipped, command exit 0 and complete cleanup.
Foundation and both full rehearsals remain active; their results are not inferred.
These diagnostics are not Task 1 acceptance. Tasks 2–11 remain NOT_STARTED.
