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

### Task 1 measured outer-observer budget correction — 2026-10-19 UTC

Published build triage at `cd583d95d5994618f0dd83e51da5a209579e0427`, tree
`c2638774bac91b2d6bd91edd12940127bded655a`; preserved same-tree local authoring
commit `bacd671aad1cc735a6e020a8772abbf65bf737f1` on
`local/c04-task01-build-diagnostic`. New complete run `39201568257` attempt 1
has ten successful jobs: real processing62, owner75, staff67, PostgreSQL44,
plus storage/migrations/restart/native/timeout/evidence-audit. These are actual
current-source executions, not carried-forward results. Processing/owner/staff
have zero failed/skipped cases, natural exit 0 and complete cleanup. The previous
build failures did not repeat; their underlying cause remains undetermined.

Foundation `117895445550` failed at 1,202.1s with observation_deadline,
1,784 passed / 0 failed / 0 skipped, cleanup complete. Earlier diagnostic source
Foundation `117892652519` similarly hit 1,201.8s with 1,776/0/0. Latest source
finished its full backend in 513.739s and C02 browser in 215.438s (exit0 each).
The final 1,198.5s snapshot proves the active command was
`tests/integration/c03/test_c03_failure_recovery.py` inside its existing180s
child timeout, within the appended `--task13-foundation`600s consolidation.
This is progressing nested work cut off by the outer observer, not an observed
assertion failure. Both full original/current rehearsals are still pending.

Engineering ruling under approved §6's prohibition on *blind* timeout growth:
use a FIXED 1,800s current-source Foundation observation budget. The measured
backend/browser alone consumes729.177s; builds, immutable C01 proof, same-DB
upgrade and service restarts precede the independent600s C03 consolidation.
The old1,200s cap repeatedly cuts the latter off before its own bound. Adding
600s gives that EXISTING final stage its budget without changing any test or
inner timeout. This revises the earlier preservation decision using newly
observed phase evidence. It is a current-source CI execution-budget correction,
not a change to permissions, architecture, production behavior or test outcomes.
No further blind budget growth is authorized by this ruling.

Original `.github/workflows/ci.yml`, `verify_c02.sh`, `verify_foundation.sh`,
incremental scripts, all eleven job definitions, 60-minute hosted Foundation
limit, skip rejection, ownership, non-TTY execution, child timeouts, kill/reap,
container cleanup and natural-exit acceptance are preserved. The immutable
C03 fixture retains its exact1200s helper and complete original source tree.
Storage600s/PostgreSQL330s windows are unchanged. Deadline/error/cancellation
still cannot return PASS. This does not permit a diagnostic PASS or partial test
count to become acceptance. A COMPLETE NEW-HEAD manifest remains mandatory.

Behavioral RED: actual observer rejected complete commands configured with
1300s/1800s outer budgets (2 failed; 4 invalid-budget controls passed).
GREEN: 120 C04/observer/inherited-CI controls passed, including actual short
child natural exits; NaN/infinity/negative/>1800 budgets reject. Metadata and
cleanup adapters in those units are explicitly synthetic, not real-service
acceptance. Existing forced-cutoff/ownership/failure tests pass. Ruff all446
files, whitespace and immutable C03 tree verification pass. Durable recovery
JSON validates with state IN_PROGRESS and null hosted acceptance. Task 1 is
not COMPLETE. Tasks 2–11 remain NOT_STARTED.

### Task 1 bootstrap phase and unclassified-browser diagnosis — 2026-10-19 UTC

Budget recovery published as `2ec28171038414fdefc7b86ceccc5dfc00296182`, tree
`5e76a0b86512ec64a62313097ee385a6a1b5edc9`; local same-tree authoring
`59937997d5f998e7689259edc79dbbdaca9dac1c` retained on
`local/c04-task01-foundation-budget`. Full run `39203522167` attempt1 has NOT
accepted Task1. PostgreSQL50 and several inherited gates pass, but Foundation
`117901330238` exits1 naturally after187.8s with0 runtime tests and complete
cleanup; processing `117901330277` exits1 after231.8s; storage `117901330460`
exits1 after200.0s. No new budget success is claimed: Foundation failed before
reaching the revised limit. Last snapshots place Foundation at service startup
and processing/storage at `docker compose run --rm minio-init` before tests.

CORRECTION: earlier “build failure” descriptions exceeded the evidence. A stale
snapshot showed BuildKit active, not the exact failing command. These later
snapshots locate service startup/bootstrap; the original cause remains unknown.
No build/network/credential hypothesis is treated as proven or fixed.

Current c02-migrations `117901330430` additionally exits124 after301.3s: the
existing INNER300s cumulative shell cutoff, not the330s observer limit. Recorded
Task8 108, Task9 89 and Task10 6 cases pass without failures/skips; the final
observed case belongs to source non-delivery controls. This is incomplete
acceptance. No change to that inner timeout, test selection or baseline is made.
Full current/original rehearsals on this head are still pending.

Historical diagnostic run `39200620956` is terminal: both full rehearsals each
have127 zero stage exits, natural final_rehearsal_passed and clean_cleanup0;
overall FAILED because Foundation/startup jobs failed and aggregate denied.
Later `cd583d9` run39201568257 current full job117895445583 failed at
clean_owner_browser:9 passed/1 failed; the SAME owner optional-consent browser
case failed at page.reload line53. Downloaded its REDACTED artifact12164354759
and independently verified SHA256
`5f50d68f80387aa6b775ee51cb715cb4a033bde78276e730fb7dcff08a5053de`.
The artifact records browser_failure_category=other, so navigation-race and HTTP
error hypotheses remain UNPROVEN. No browser assertion or application fix is
made on the basis of that label.

Bounded next diagnosis changes only CURRENT-source instrumentation:
- `docker/minio-init.sh`: finite phase markers on original exit statuses;
  alias/readiness split into an equivalent function with the SAME30 attempts,
 2s sleeps, original mc commands/arguments, bucket ACL and policy. No credentials,
  raw client errors, URLs or policy payload are emitted. Existing immutable
  C01/C02/C03 copies remain unchanged. `progress_lines` recognizes only exact
  finite phase/state/integer-code markers; no arbitrary captures are relayed.
- `failure_data`: six more fixed browser-error categories, never raw message,
  URL, body, token or values. This improves an observed unclassified exception;
  it does not claim the next failure's category in advance.

Behavioral RED: after relocating ONLY the unit's ephemeral policy-file path
(the host lacks /tmp), all7 bootstrap cases failed for missing phase metadata
with correct original exits. The initial /tmp unit-harness failure is NOT claimed
as product RED. Six browser-category cases failed before adding their enums.
GREEN:135 combined C04/observer/inherited-CI controls pass, including successful
bootstrap, all7 failure phases, exact30 attempts, exit1/7 propagation, no secret
output and unknown/tainted/>255 marker rejection. These instrumentation units
use fake mc/sleep only; they cannot substitute for real MinIO/scanner/Celery
acceptance. Ruff all447 files, formatting, shell syntax, whitespace and immutable
C03 tree verification pass. No inherited job or workflow byte is changed here.

This forward diagnostic source requires another complete exact-head hosted
manifest. No same-SHA job retry has been used on cd583d9 or2ec2817; do not use
retries blindly without identifying the causal bootstrap failure. Task1 remains
IN_PROGRESS/BLOCKED on full acceptance; Tasks2–11 remain NOT_STARTED.

### Task 1 pinned-client option-prefix defect reproduced and corrected

Published phase diagnostics at `a52ba33af976b82ad2243e8d872c5cd5430f9c49`, tree
`0aa7c8405b6668f1effabcf48968aa3c672dfb4e`, full run39204677988 attempt1.
Local same-tree authoring55b64ea2eea9d20c1ddf0a06bfaffe6eb5a00cc5 is preserved
on local/c04-task01-bootstrap-diagnostic. All protected/completed/planning refs
were rechecked unchanged before publication; no force update occurred.

A controlled REAL pinned-client experiment now establishes a bootstrap input
handling defect, independently of mocks. Downloaded the EXACT official mc binary
already pinned by docker/Minio.Dockerfile, release2025-08-13T08-35-41Z; verified
SHA256 `01f866e9c5f9b87c2b09116fa5d7c06695b106242d829a8bb32990c00312e891`
BEFORE execution. Only synthetic users/passwords, isolated ignored config and
loopback127.0.0.1:1 were used; MC_/MINIO_/AWS_ environment inputs excluded.
No real credentials, remote private store or health data were read by the probe.

Observed actual client outcomes (exit1 is expected for the absent loopback server):
- Ordinary synthetic alias password: reaches connection attempt.
- Leading `-` and `--` synthetic passwords: argument_rejected before connection.
- `alias set -- ...` with leading-dash password: reaches connection attempt.
- `admin user add ...` with leading-dash password: argument_rejected.
- `admin user add -- ...`: reaches configuration lookup, beyond option parsing.

The existing token_urlsafe generator may legitimately produce a leading hyphen;
both root-password and application-secret positional arguments were passed to
mc without an option delimiter. This is a reproduced causal INPUT defect. It
does NOT prove that every historical initialization failure had this cause,
which remains unclassified where original evidence suppressed the error.

Narrow current-source fix: add standard `--` after `alias set` and `admin user add`
before positional values. No credential alphabet/entropy, access policy, bucket
ACL, retries, expiry, private source protection or other mc command is changed.
No immutable C01/C02/C03 script or generator is mutated. Complete original
baseline verification remains mandatory and may not be patched to hide defects.

Behavioral RED: instrumented shell regression with option-prefixed synthetic
passwords fails at alias (exit1). After alias delimiter alone it fails at user
creation (exit73). Both delimiters produce complete success with unchanged
commands/retry/privacy controls. Fake client units model the independently
observed parser contract; they are NOT real MinIO acceptance. Four extra finite
network error labels also first failed their metadata controls, then passed;
no browser behavior/assertion is changed and previous `other` is not relabeled
retroactively. GREEN:140 C04/observer/inherited-CI controls, zero failed/skipped;
Ruff447 files, format, shell syntax and whitespace pass; immutable C03 tree
verified unchanged. A new complete exact-head hosted manifest, including actual
MinIO/scanner/worker/browser/original baseline, is required before acceptance.
Task1 remains IN_PROGRESS; Tasks2–11 remain NOT_STARTED.

### Task 1 current bootstrap GREEN; browser reload remains unclassified

Published delimiter fix `c9a475741e52459030c100311df01f51f054bb1c`, tree
`4f8ceb525637e65e6d4cfe454a4e1a98859984d0`, run39205168435 attempt1;
local same-tree434d58329d2f69b8cfb1250b49ef784f6bc04ea5 retained on
local/c04-task01-minio-cli-fix. No later task has started.

Current actual hosted evidence: PostgreSQL70; storage91/0/0 with bootstrap
complete0, natural exit and cleanup; processing62/0/0 natural0 and cleanup;
restart natural0 and cleanup; native/timeout/evidence-audit succeed. Migration
job117906314481 passed269 account cases and the unchanged cumulative gate in
285.4s, with Task8 108, Task9 89, Task10 86 all zero failed/skipped. No change to
the cumulative300s cutoff was necessary or made. Owner browser also succeeds.

STAFF FAILURE: job117906314411 reports66 passed/1 failed/0 skipped, natural
command exit1 after458.4s with complete cleanup. The failed case is
`tests/e2e/c03/test_staff_verification.py::test_decision_reload_single_effect`,
line172 at page.reload, exception Error, browser_failure_category=other. This
is an ACTUAL test failure, not infrastructure absence or timeout; do not waive
it or classify it as transient without evidence. Foundation and both full
rehearsals remain active. Task1 cannot be accepted on this manifest.

Further bounded current-source metadata diagnosis: failure_data now emits
network codes ONLY when present in a finite266-code public Chromium allowlist.
The source definition was independently fetched at exact upstream commit
`405665065117459f6a72161b865c8244742b21c7`:
https://github.com/chromium/chromium/blob/405665065117459f6a72161b865c8244742b21c7/net/base/net_error_list.h
No network fetch is performed at application/test runtime. Unknown ERR_* tokens
are omitted; fixed protocol/navigation/frame/connection/lifecycle flags contain
no captures, messages, URLs, query values or private content. Generic protocol
and known-network categories avoid repeated single-code guessing. This is
instrumentation only; no browser helper, assertion, driver version or product
behavior is modified, and previous `other` events are not retroactively assigned
a guessed cause.

Behavioral RED:3 known-code cases and protocol-flags case fail before metadata
implementation; unknown-code privacy negative already passes. GREEN:145 combined
C04/observer/inherited-CI controls pass, zero failed/skipped, plus21 focused
browser-metadata cases. Ruff447/format/whitespace/immutable C03 tree pass.
Attempted a separate local synthetic browser reproduction using the EXISTING
pinned Playwright CLI and official headless-shell archive. Local browser install
is unavailable: download is empty/truncated and cannot extract; initial missing
/tmp was addressed only with an ignored workspace temporary directory. No
unofficial mirror, dependency change, TLS bypass, baseline mutation, browser
assertion fix or fake browser PASS is used. Hosted browser remains mandatory.
The finite diagnostics require a fresh COMPLETE new-head hosted manifest.
Task1 remains IN_PROGRESS/BLOCKED; Tasks2–11 NOT_STARTED.

### Task 1 reload attachment failure — before changing current harness

Latest diagnostic head8cf9b116572c74762a002d1aa7eab19b4133933d /
`ea5da51939e79915cc0006ebae799c79059328a8`, run39206463844 attempt1:
owner job117910270983 failed74/1/0, with browser_failure_category=protocol_error
and flags[protocol,navigation,not_attached] at owner optional-consent line53
page.reload. Actual command exits1 naturally with complete cleanup. This now
locates the failure at DevTools page attachment during navigation; no net:: code
was emitted. Chromium's public content/browser/devtools/protocol/page_handler.cc
was inspected: PageHandler::Reload first calls AssureTopLevelActiveFrame, which
rejects absent/inactive page attachments. This is consistent with reload issued
while the form's redirect changes document/frame attachment, not a demonstrated
application authorization or persistence failure.

Scoped RED is the ACTUAL hosted owner reload failure above and earlier staff
single-effect reload failure117906314411. BEFORE EDITING: only current-source
`test_owner_dual_context_resume_optional_consent` and
`test_decision_reload_single_effect` will explicitly bind their immediately
preceding successful form submission to a completed load navigation and assert
that navigation's final GET/status200 before calling the existing reload(s).
All persisted-value, privacy, layout, no-cache, subsequent preview/athlete
separation and single decision count==1 assertions stay unchanged. No retries,
sleeps, test suppression, browser-version change, application mutation or
immutable fixture edits. This tests the minimal synchronization hypothesis;
only actual hosted GREEN can establish it works.

### Task 1 historical migration preparation — before editing current test

Revisited the initial deferral: approved §6 explicitly assigns migration-selection
preparation to Task1, with new schema proof in Tasks2/4. Finish that preparation
now rather than calling Task1 complete with it outstanding. No C04 schema is added.
Actual behavioral RED: evaluating the CURRENT trusted test's historical-target
expression with future leaves selects accounts9999 and marketplace0001 instead
of exact C02. test_historical_test_selects_c02_even_when_future_apps_depend_on_c03
fails for those wrong selections (not missing infrastructure/imports).

BEFORE EDITING `test_c03_migrations::test_optional_profiles_not_created` only:
replace dynamic non-C03 leaves with the exact five C02 app targets from the
immutable source; explicitly unapply only known post-C02 domains including an
installed marketplace dependent. Run this history rehearsal in a freshly CREATED
owned UUID-named PostgreSQL test database, not the populated parent/acceptance DB.
Django's copied connection and separate test alias keep model operations on that
probe; cleanup closes/removes only its owned alias/database after creation.
Preserve the exact legacy PK/public ID/phone/password/auth-version tuple and
zero automatic Athlete/Professional/auth_user assertions. Strengthen isolation
with a parent DB user/migration-history anchor that must remain unchanged.
Original C03 fixture test is unchanged and still runs on c04-baseline. This
changes test harness selection/isolation, no behavioral permission assertion.
Real PostgreSQL GREEN is mandatory in the next complete hosted manifest.

### Task 1 cumulative PostgreSQL budget — before current-source correction

A second actual inner300s timeout is now proved: run39206463844,
c02-migrations117910270999, natural command exit124 after301.3s, cleanup complete.
Task8 108/0/0 and Task9 89/0/0 completed; Task10 recorded47 passed and no failures
before cutoff (not its full86 cases). Previous current-source run39203522167
similarly cut off301.3s with Task10 only6 passes. In contrast identical inherited
selection on c9a4757 completed285.4s with all86 Task10 cases. These are repeated
total-budget cutoffs of progressing suites, not evidence permitting a skipped
suite or a passing timeout. Individual suite bounds remain180s.

Evidence-based fixed-budget correction: CURRENT cumulative shell wrapper300→450s;
PostgreSQL observer330→480s, leaving the existing10s kill grace and finite cleanup
margin. Both still fit well inside unchanged hosted job limits. No future auto
budget increase, assertions, selections, child-suite deadlines, cleanup ownership
or natural-exit guarantee change. Immutable original C03 retains300/330 and exact
source. Behavioral RED: actual observer rejects configured460/480s (2 failed,
6 existing controls pass). As with Foundation, only complete hosted natural
success on the new source can accept this correction. This is not another blind
same-SHA retry or permission to relax runtime verdicts.

### Current-source pin reconciliation for the measured cumulative budget

The focused regression correctly caught the sanctioned shell-budget change:
`test_existing_c02_gates_not_removed` and `test_every_incremental_gate_still_installed`
fail because task13_installed hashes the complete inherited entry prefix. BEFORE
EDITING that helper: retain original TASK13_ENTRY_SHA256 and every block/job pin;
require exactly ONE current450s wrapper line and zero old300s wrapper lines,
then normalize ONLY that exact literal back to300s for the original prefix hash.
Any other command/selection/timeout/cleanup mutation remains rejected. Add
negative controls for300/900/true replacements and changed individual180s suite
limits. The original immutable C03 test/helper is unchanged and validates its
actual300s source. This is explicit current-stage reconciliation, not a new digest
that blesses arbitrary changed behavior.

### Task 1 combined recovery candidate — local verification only

Current recovery candidate includes the two explicit successful-navigation
barriers, fixed450/480 cumulative budgets with strict original-prefix
normalization, and the approved historical C02 migration-harness preparation.
Local focused GREEN:162 C04/observer/current inherited-CI/final-rehearsal controls,
zero failed/skipped. Ruff449 files and formatting, shell syntax and whitespace
pass. Individual runtime suites still use their original180s bounds; restart,
scanner/native, staff/owner job deadlines and test counts stay intact.

Dedicated history helper has a UUID-only freshly CREATED database name, refuses
non-PostgreSQL/atomic/non-autocommit administration, and drops only that exact
owned database after closing/removing its separate alias. It does not modify
parent connection settings or migrate parent data backwards. Existing historical
RunPython migrations were inspected: both account-state mapping and flag seeding
explicitly use schema_editor.connection.alias. All original legacy-user and
zero-profile assertions remain, with an additional unchanged parent user/history
anchor. Pure selection/guard units pass; REAL PostgreSQL proof is PENDING_CI.
No fake DB or local browser result is claimed. The browser archive remains
unavailable locally; actual hosted failing cases are the RED evidence and hosted
successful navigation/reload/single-effect/privacy cases are required GREEN.

Earlier a52ba33 Foundation job117904827509 completed NATURALLY after1404.9s,
1,853 passed/0 failed/0 skipped, host/container cleanup complete. This proves
that head's1200s cutoff would truncate otherwise successful existing work and
supports the fixed1800s correction; it does not accept another SHA or all Task1.
Latest source/complete manifest still controls advancement. Task1 remains
IN_PROGRESS; Tasks2–11 remain NOT_STARTED.

### Task 1 focused historical probe and private failure evidence

Published combined recovery351db4b1b1c82d6bd42f277167449a8c9b5cc24a / tree
`c88f3286566e60486a850b733becccff51e55632`, run39208190000 attempt1;
local same-treefde455fb9e1eafdc9c29b70f279ee1520032c438 preserved on
local/c04-task01-rehearsal-fix. Real owner117915510439 now75/0/0 and
staff117915510343 now67/0/0; both natural0 and complete cleanup. Thus the first
focused real-browser GREEN supports the explicit form-load barrier hypothesis;
all broader latest-source browser repetitions and full manifest remain required.

Migration job117915510192 now fails naturally after63.9s with ValueError and
cleanup, not a timeout. It occurs before later Task8/9/10 selections. The new
history harness is NOT claimed GREEN or complete: existing inherited output
redaction lacks its failing line. No fixture assertion is waived. Add the EXACT
historical test node to C04's real PostgreSQL gate so it is directly required and
can report its static traceback through the existing redacted reporter.

Distinct author review of C04 required runner found Important gaps (no separate
reviewer claimed): raw pytest failure payload could reach CI output, and
collect-only/filtered execution could return0. Actual RED controls demonstrated
synthetic-private-health-token in old runner output, --collect-only returning0
with0 passed, and -k selecting only one of two cases returning0. The initial
absolute --deselect probe did not deselect anything and is NOT claimed as RED;
it was corrected to an actual -k deselection before implementation.

Current-source correction reuses docker.c03_pytest_triage as a pytest plugin.
Raw stdout/stderr (including low-level FD writes) stays in an unlinked mode600
TemporaryFile; only finite failure metadata and actual counts/exit are printed.
Fail on zero passes, errors/failures, skipped/xfailed/xpassed/deselected cases,
including a final post-pytest guard; no failure can be hidden by output redaction.
Every run owns a fresh UUID runtime folder and fresh --basetemp underneath it.
Local default-temp artifacts from a host without/tmp were moved INTACT under
.runtime/c04-task1/runner-default-temp-20261019; no legitimate work deleted.
No app authorization, original baseline, inherited job or service substitute added.

GREEN:165 C04/current inherited-CI/observer/final-rehearsal controls pass, zero
failed/skipped; direct required runner executes86 C04 units with all error,
skip, expected-failure and deselection counts zero and actual exit0. Privacy and
incomplete-selection negatives pass. Ruff450 files, format, shell syntax and
whitespace pass. Real PostgreSQL history probe GREEN is PENDING_CI. No new
acceptance or Task2 start is recorded.

Historical complete evidence kept separate: run39204677988/a52ba33 exact source
and tree pass validate_completed_task_evidence for all14 jobs, attempt1. Both full
rehearsals have127 zero stages, clean_cleanup0/final_rehearsal_passed; original
backend1692, current1757, no failed/skipped phases; final C04 job117913426045
executes65 cases and drift check successfully. This is historical authority only,
not acceptance of later legitimate recovery source changes.

### Task 1 OTP-only parent-anchor fixture correction

Private-evidence checkpoint52ac877dddfb261185b0355eb87cd9124a49cd44 /
`be0450f29273ef5b8b0f62b4b8e111aeb645fd33`, run39210185737 attempt1,
C04 PostgreSQL117921604583 now exposes the exact static cause safely:
C03 historical test line33 → apps/accounts/managers.py create_user line22,
ValueError. Actual runner counts87 passed/1 failed, no error/skip/xfail/xpass/
deselection, actual exit1. No private exception payload is emitted.

The new parent anchor incorrectly supplied a password to create_user. This was
an implementation mistake in the new TEST FIXTURE: C01 deliberately rejects
password provisioning for OTP-only accounts. Correct ONLY the fixture call to
create_user(phone), preserving its generated unusable-password value in the
unchanged anchor comparison. No manager, account policy, legacy historical
password preservation, SQL assertion or privacy boundary is weakened. Hosted
RED above independently confirms the identified call/guard.

Focused GREEN after correction:86 C04 units and the separate10 user-contract/
runner-privacy controls pass, zero failed/skipped. Existing C01 password rejection
stays tested. REAL PostgreSQL probe and complete new-head manifest remain PENDING.
Task1 is not accepted; no Task2 code has started.

### Task 1 non-root evidence-directory compatibility review

OTP-anchor correction published87be4460b54fddbdfe41244d43c379ee0b793177 /
`359ead16855a2c5f0132733627bbbffc09ba9542`, run39210570676 attempt1.
REAL focused PostgreSQL117922788459 now88 passed/0 errors/0 failed/0 skipped/
0 xfailed/0 xpassed/0 deselected, actual exit0, including the dedicated historical
migration flow and unchanged parent anchor. Ten jobs currently succeed; Foundation
and both full rehearsals remain active. No complete latest-source acceptance yet.

Review-discovered compatibility issue, not claimed as an observed Docker failure:
the inherited checks container runs app UID1000 against the host checkout bind
mount. The new reporter initially required writes below that checkout's.runtime,
which can be owned by the host runner with nonwritable permissions. Do not chmod
the checkout or weaken source permissions. Extracted the existing folder creation
unchanged; behavioral RED then injects PermissionError for the checkout and the
actual creation helper fails rather than providing writable evidence storage.

Correction: retain preferred fresh UUID runtime folder when writable; on ONLY
permission/read-only-filesystem errors use standard atomically-created private
system temp (0700) under the executing user. Other errors/collisions still fail.
Fresh basetemp/raw unlinked file/finite JSON rules remain. A collision control
proves existing legitimate evidence work is neither reused nor overwritten.
No public storage, environment/credential bypass, original fixture mutation or
broader filesystem permission change. Standard container/tmp is used only when
checkout writes are denied; local allowed-workspace output remains preferred.

GREEN:167 C04/current inherited-CI/observer/final-rehearsal controls, zero failed/
skipped, including all5 runner privacy/selection/unwritable-root/collision controls.
Ruff450 files/format/whitespace and immutable C03 exact tree pass. Full non-root
Docker/current/original browser/service acceptance still belongs to the complete
next exact-head hosted manifest. Task1 IN_PROGRESS; Tasks2–11 NOT_STARTED.

### Task 1 workspace recovery and bounded original-C02 phase diagnosis

Live refs rechecked on 2026-10-19: execution head remains
058c51599ce3155bdc58a6e876e77fab03f57273, tree
0a77382cd2d4dd980bdfe69d0070f6dc85380d68; approved planning ref/tree and
all completed-stage/diagnostic refs remain unchanged. Run39212222210 attempt1
finished with12/14 successes: c03-final117927953855 failed at
exact_original_c02 exit1; c04-final117942482298 failed its upstream guard.
No test exception, test name, count or infrastructure cause was recorded in the
failed stage's finite diagnostic. Artifact12167199899 ZIP SHA256
3c9431ec34f48cc1eaeee5a460ac269afed17b911bd6188e3401543853e2e979
contains only upgrade.jsonl with that single failure. The cause is UNKNOWN.
Do not infer a transient network, runner, MinIO or application defect.

Same-head immutable baseline117927953860 completed its full rehearsal, including
exact_original_c02 exit0, clean_cleanup0 and final_rehearsal_passed. Foundation
117927953856 completed naturally with1877 passed/0 failed/0 skipped and complete
cleanup; C04 PostgreSQL117927953991 completed90/0. Parallel baseline success
alone does not satisfy the approved transient-failure retry condition. No
same-SHA retry was requested for058c515; Task1 is still not accepted.

Automated workspace maintenance left a partial source directory without Git
metadata or the usable Python3.13 environment. Preserved that directory. Rebuilt
a separate checkout from the GitHub connector: all511 original file blobs and
modes independently match their Git object hashes; git write-tree exactly equals
0a77382cd2d4dd980bdfe69d0070f6dc85380d68. Recovered the exact hash-matching head
commit and13 ancestor commit objects through the C03 handoff; the repository is
explicitly shallow at that handoff. Approved planning ancestry was checked with
git merge-base. This recovers published state, not any deleted unpublished bytes.
No claim of byte-for-byte recovery of missing local-only state is made.

Ruling: add finite prerequisite results to the CURRENT C03 replay wrapper under
Task1 diagnostics authority, without changing any immutable C02/C03 fixture —
the existing single aggregate cannot locate this failure — cost if wrong: the
extra wrapper could change command failure propagation, requiring RED/GREEN
subprocess controls and complete new-head hosted acceptance before advancement.

Behavioral RED: simulated failures in commands1,3,11,13 retain only the aggregate
result; all four phase-evidence assertions fail, and the successful-chain control
also fails its expected per-command evidence. GREEN: current wrapper records each
constant original_c02_* stage and actual exit in the existing metadata-only JSONL.
All13 original commands, argument order, working directory, umask, environment,
frozen dependencies and immutable verifier remain. No command is skipped/retried,
no raw stdout/stderr/argv is exported and an early nonzero command stops the chain.

Verification in recovered environment: Python3.12 stdlib unittest runs both new
tests (four failure subcases plus successful-chain control), zero failures/skips;
three existing final-rehearsal source-contract functions execute successfully via
stdlib AST extraction. Shell syntax and git diff --check pass. These are bounded
harness checks, NOT the required Python3.13/Django/PostgreSQL/browser suite.
Python3.13, pytest and Docker are unavailable locally after maintenance; full
locked-runtime verification remains mandatory in the complete hosted manifest.
No full local regression or Ruff pass is claimed. New-head CI must independently
execute these tests and every inherited/current/baseline job. Task1 IN_PROGRESS;
Tasks2–11 NOT_STARTED. No public functionality, C05 work, merge or release.

### Task 1 COMPLETE — exact-source hosted acceptance

Accepted implementation: f2cebc3a08352eafeab84dff4470970161c45bc2, tree
8acd1b9a83c88d423a9672baebc5f8fdde157bfd. Hosted run39252751752 attempt1
completed SUCCESS on that exact head/tree, branch marketplace/c04-cloud,
push event and .github/workflows/c04.yml. All14 mandatory jobs SUCCESS;
every job and step was inspected, with zero skipped steps. The actual
validate_completed_task_evidence call accepts freshly retrieved provider metadata.
No retry or cancellation was requested for this SHA.

| Mandatory job | Exact job ID | Runtime evidence inspected |
|---|---:|---|
| foundation | 118060342226 | Natural command0 in1345.5s, reported1883 passed/0 failed/0 skipped, complete host/container cleanup; locked quality/static/unit/production checks also pass |
| c02-migrations | 118060342037 | Account269, focused38, cumulative C03 task8/9/10:108/89/86; natural0 in291.5s, complete cleanup, no skips |
| c03-final | 118060342516 |127 outer stages all0, backend1783 passed, no failed/skipped phases, final_rehearsal_passed and clean_cleanup0 |
| c03-owner | 118060341978 |75 passed/0 failed/0 skipped, natural0 in485.8s, complete cleanup |
| c03-staff | 118060342287 |67 passed/0 failed/0 skipped, natural0 in534.6s, complete cleanup |
| c03-storage | 118060342414 |91 actual passed call reports/0 failed/0 skipped, natural0 in182.2s, complete cleanup |
| c03-processing | 118060342292 |62 actual passed call reports/0 failed/0 skipped, natural0 in297.7s, complete cleanup |
| c03-restart | 118060342164 |Actual owned worker SIGKILL and scanner/storage/broker outage/recovery, durable receipt, single effect and stale-delivery denial; natural0 in351.4s and cleanup |
| c03-timeout-probe | 118060342327 |Expected deadline negative control; owned container removed, detached child terminated, supervisor_contract_satisfied true; the intentional child exit1 is not represented as a successful service execution |
| c03-task14-native | 118060342184 |Actual native runtime/decoder/isolation checks and diagnostic_cleanup all exit0 |
| c03-evidence-audit | 118060341660 |All12 earlier C03 task records verify their real hosted selections, provenance, positive counts, exit0 and zero skips; read-only audit, not new execution of those historical tests |
| c04-baseline | 118060342190 |Exact immutable handoff full verifier:127 stages all0, backend1692 passed, no failed/skipped phases, clean_cleanup0/final_rehearsal_passed |
| c04-postgresql | 118060342111 |92 passed, zero error/failed/skipped/xfail/xpass/deselected, actual0; hosted service cleanup succeeds |
| c04-final | 118079191777 |Exact upstream manifest accepted,92 passed with all non-pass counts0, actual0, no migration drift; hosted service cleanup succeeds |

Foundation count1883 is the existing reporter's aggregate, not a claim of1883
distinct test functions. Its host unit phase separately reports800 passed and4
successful subtests. Preserve the observed counts without deduplicating or
relabeling executions. Intentional timeout/native fault controls remain clearly
separate from natural successful service gates.

Current final artifact12189070584 was downloaded and its provider SHA256
0a7a16278906382486ecdac762bd0029775bcf3e0574b11a7c69d089fded2d76 independently
matched. Its142 metadata rows all have exit0, including all13 original_c02_*
prerequisites and final clean_cleanup0. The original058 failure remains
historical/unexplained; it did not recur here. No unsupported root cause or
successful retry is claimed. Original baseline logs independently establish the
unchanged full verifier's positive execution; that job has no artifact upload
step and none is invented.

Distinct author manual Task1 review completed after the runtime inspections:
verified approved plan blob f1225196c95a203e440afc4da362b74806e84f20, exact
baseline trees, inherited ci.yml, all11 current job counterparts, missing/fake/
wrong-head/skip rejection controls, diagnostic privacy/failure propagation,
isolated historical migration ownership and absence of C04 application/schema
changes. No unresolved Critical or Important Task1 finding. No independent
reviewer or whole-C04 final review is claimed. Retained limitation: local
Python3.13/Docker remained unavailable after maintenance; the locked real-service
and browser proofs above were actually executed on hosted runners instead.

Rechecked all live refs: main, C01/C02/C03 completed/planning/diagnostic refs and
approved C04 planning ref remain unchanged. validate_checkpoint accepts the new
task01-complete.json with exact14-job metadata and per-job runtime evidence.
task01-start.json remains the original historical start record. This completion
checkpoint changes documentation only and preserves f2cebc3 as the tested
implementation authority separately. Task1 COMPLETE; next Task2, in strict order.

### Task 2 RED — deliberate source-domain publication

Task1 prerequisite is COMPLETE at tested f2cebc3/source8acd1b9, run39252751752
attempt1 all14 mandatory jobs green. Its documentation-only completion886cc5c
contains the validated task01-complete record and preserves the tested SHA.
Task2 starts from886cc5cd42b020f15315876df3197bda22526764.

Read the Task2 brief and exact interfaces, existing C03 eligibility evidence
bindings/role revisions, owner/session policies, receipts/privacy inventory and
governance metadata/migration contracts before choosing interfaces. No parallel
authorization or new Consent purpose is introduced.

Initial behavioral RED: Python stdlib unittest on test_public_fields.py executes
4 assertions and all4 fail because the explicit safe-field publication boundary
does not exist. Tests demand immutable selection, reject private credential and
identity media, reject private/fictional snapshot keys and limit qualification
summary fields. PostgreSQL tests additionally use the actual C03 approved-role
fixture to prove verification never publishes and false confirmation cannot
activate a revision; hosted RED execution is pending. No production code or
migration has yet been written for Task2. Remaining Task2 matrix will be added
and demonstrated RED before the corresponding behavior is implemented.

Task2 hosted RED independently observed: published a9ee450cbf8a4fe4a86062e6bd08060f4956777e,
tree fe95e6f1def26fc01327a6e0601c071e1e776afe, run39259243564 attempt1,
C04 PostgreSQL118082293031 executes real C03 approved-role fixtures and reports
92 passed/6 expected missing-feature assertion failures,0 error/skipped/xfail/
xpass/deselected, actual exit1. Failures are the four field-boundary unit tests
and both deliberate-publication integration cases. No missing service is used
as RED. Foundation118082292686 also fails the intended missing-contract tests.
Task2 is not accepted; full next-head acceptance remains mandatory.

Additional local RED: both planned public contract files execute9 tests and all9
fail before publication_contracts exists. Initial GREEN after implementing only
the safe immutable selection/summary/slug/snapshot contract:9 tests pass using
stdlib Python3.12, no skips. This is not a complete Task2 or real-service GREEN.

Task2 Ruling: restore the existing locked development toolchain through a
temporary auxiliary CI workflow because maintenance removed Python3.13, Django,
pytest and Ruff locally — generating/reviewing additive migrations and running
focused controls requires those same existing tools — cost if wrong: extra CI
compute/artifact bytes; the auxiliary workflow is not acceptance and is removed
after recovery. The14 mandatory acceptance jobs and immutable fixtures remain
unchanged. Only clean interpreter/public site-packages are exported, before
services, environment generation or tests; no source/credentials/test inputs.
Artifact digests and the original uv.lock hash must match before local use.
No dependency version or production infrastructure is added.

Locked toolchain recovery run39260416591/job118086286813 succeeded; artifact
12189966981 SHA25645a586780b28f2a7f0d9c4ae18d8c9a3a5e51db1f77141a58bb9f465def54df7
matched independently, its internal archive digest and original uv.lock hash
also matched. Extracted only20364 regular files/directories under controlled
python/packages paths after bounded archive checks. Local interpreter3.13.15,
Django5.2.17 and pytest9.1.1 execute successfully. This is tool recovery, not
application acceptance. Packaging initially omitted venv/bin/ruff; one forward
auxiliary workflow adjustment exports ONLY that locked public executable and
its digest/version manifest, avoiding another full toolchain transfer. No
application source, generated environment or test inputs are exported.

Ruff recovery run39261286147 succeeded; artifact12191861109/provider SHA256
82ec354cee6c73b86b583507b2839b78b3a688b2fec55fec42d8cdcc7a7d794b matched, as
did the native executable digest, Ruff0.16.10 version and original uv.lock hash.
Temporary auxiliary workflow is now removed; no recovery job is acceptance.

Current locked local runtime3.13.15 executes both contract files:10 passed plus33
subtests, no failures/skips. Review found mutable/unhashable malformed media/role
values raised TypeError rather than bounded ValueError. New behavioral assertion
RED observes that exact TypeError, then strict string guards GREEN it. Ruff
format/check passes after correction. Full installed C04 unit selection now100
passed plus37 successful subtests,0 failed/skipped in6.37s. PostgreSQL ownership,
source-edit/reconfirmation, exact summaries, revocation ordering, private-media
pending and direct-SQL immutability tests were written before model/service/SQL
implementation; no Task2 schema or command implementation is present yet.

Ruling: source-domain release disclosure is absent by default, with only explicit
versioned synthetic wording injected by tests — the plan defers real informed
wording to release sign-off — cost if wrong: publication stays unavailable until
trusted configuration supplies an approved version/text. No real legal policy,
new consent purpose or implicit publication is invented. C03 stored type_code
is used verbatim as the selected qualification type label; there is no approved
credential-label catalogue to invent.

Task2 test-harness correction: matrix checkpointb5d2ae706fb267ae12e838714116bb8f5180968f,
run39262148010/PostgreSQL118092294156 had3 collection errors and0 executed tests.
This is NOT accepted as behavioral RED. Local locked-runtime collection reproduces
exactly3 ImportError instances: attempted relative import with no known parent
package. C04 tests use namespace directories without __init__.py; replaced the
three files' relative helper imports with existing project-style absolute imports.
GREEN collect-only finds all17 intended PostgreSQL cases with exit0 and no
collection errors; this is collection proof, not a real DB test pass. Re-run the
real PostgreSQL matrix before crediting additional feature RED. Initial6 actual
hosted behavior failures from a9ee450 remain valid separately.

New models and generated0018 migration are currently local drafts; no database
migration or SQL guard has been executed locally. Django5.2.17 generation and
state drift check pass with the explicit expected local PostgreSQL connection
warning. Do not describe that as an applied/validated real migration.

Task2 full matrix behavioral RED:4efe4ae736171051a89732eb2aace8cf477f7963,
tree d4a5e7e67900b47c2108962caa0b64050710df06, run39263037610 attempt1,
PostgreSQL118095380415 executes102 passed/17 intended missing-feature assertion
failures,0 error/skipped/xfail/xpass/deselected, actual exit1. All17 matrix cases
were collected and executed against real PostgreSQL before source-domain command
and SQL guard implementation; collection errors from the previous head are not
credited. Task2 remains IN_PROGRESS, Tasks3–11 NOT_STARTED.

Implemented draft source-domain intent, exact immutable revision/qualification
and private-branding selection, current-owner/version confirmation, withdrawal,
receipts, fresh C03 eligibility and atomic UUID-only governance metadata. No
public route, public blob, search, new consent purpose or production disclosure
is added. Selected media stays requested with no current pointer until Task3.
Current verified role loss filters that role; identity loss hides everything.

Task2 Ruling: keep the request-selection bound16KiB but permit its derived public
snapshot up to1MiB within unchanged individual C03 field limits —20 valid selected
qualifications expand beyond16KiB, observed by a failing unit assertion before
the correction — cost if wrong: bounded additional storage, never extra public
fields. Explicit selection remains finite and private references never enter
snapshots. A non-UTC aware expiry also produced a failing canonical-binding test;
canonical UTC serialization now preserves equality with PostgreSQL timestamps.

Task2 Ruling: extend CURRENT source stage-absence tests by exactly the four named
publication models, their protected UUID relations and one confirmation reverse
relation; retain exact legacy model sets/field exclusions everywhere else — C04
adds approved schema while immutable C03 fixtures must remain byte-identical —
cost if wrong: a narrowly added model could be overlooked, so UUID/FK/timestamp
checks cover the new rows as well. Only ProfessionalPublication may have slug.
Current C03 SQL-rendering coverage delegates only0018/0015 to the cumulative C04
runner; original historical SQL commands and all11 inherited job counterparts
remain mandatory. No native-decoder or CSS-build assertion is relaxed.

Task2 Ruling: register a finite publication metadata outbox handler now — committed
source-domain commands must not enqueue unknown events before Task4 — cost if
wrong: no projection until Task4 initial reconciliation; handler performs only
current owner/version checks and no publication or external delivery.

Cumulative C04 runners and checkpoint validation advance to task2. New controls
first failed with the prior task1 runner and with prior-stage runtime accepted;
now exact integer executed_task must match each post-Task1 checkpoint, with bool,
float, string and prior-stage values rejected. Task1 historical record is intact.
Local locked-runtime checks:212 passed plus37 subtests across C04, current C03
schema/scope/CI and foundation scope; Ruff check/format pass, required mypy97
source files pass, Django check0 issues, migration state no changes detected.
Local migration consistency probe warns PostgreSQL unavailable: no real migration
or PostgreSQL GREEN is claimed. Full local unit run also encounters sandbox
native-isolation and absent built CSS; mandatory hosted jobs retain those checks.
New PostgreSQL tests additionally require role degradation, audit/outbox rollback
and immutable deletion after withdrawal, so FK protection alone cannot mask a
missing revision-delete guard. Hosted GREEN on the implementation SHA is pending.

Task2 first implementation e8e13edb7835c951790b04793888ac42a92dd560,
tree0829114428be91345d0202159c278e6065c15176, run39269877496 attempt1.
Real PostgreSQL118119048987 applies both new migrations and executes127 cases:
118 passed/9 failed/0 error/skipped/xfail/xpass/deselected. Every failure is
NotSupportedError at effective_publication's nullable current_revision join;
PostgreSQL reports FOR UPDATE cannot be applied to nullable side of outer join.
Direct SQL immutability, owner binding, explicit confirmation and rollback cases
otherwise run; this is not Task2 GREEN. Restrict the read lock to publication
itself with select_for_update(of=("self",)); existing User/profile/verification
and asset locks from C03 eligibility remain, confirmed revisions are immutable.
The same actual nine behavioral failures must pass on the next hosted head.

Historical audit118119048635 independently fails after verifying Tasks1–4.
Artifact12195121528 SHA256e8f60c0a8e3b51e23a865015f9dcf5ab5ca803b5b0350b5ddc1de9134dc65997
matches and shows HTTPError, without status or endpoint. Do not infer transient,
expired evidence or permission cause, and do not rerun/bless missing evidence.
Add finite HTTP status/endpoint-family diagnostics only, preserving original
exception/fatal exit, token-stripping redirect, bounds, timeout and audit checks.
Six synthetic HTTP failures first RED because metadata absent, then GREEN;
no URL, header, response body or token emitted and no retry added. Immutable
C03 baseline file unchanged. Need next hosted diagnostic before root-cause ruling.

Task2 correction5a159a57e08fd799591b1a85e967e6fa4065070c,
tree d17054e91ed2b572f78bfa48f17160de217fdc24, run39270379482 attempt1:
PostgreSQL118120779600 SUCCESS133 passed,0 failed/error/skipped/xfail/xpass/
deselected, actual exit0, C04_TASK_ACCEPTANCE task2. Both additive migrations and
all installed SQL/source/ownership/rollback/revocation race contracts run for
real; the nullable-lock defect is GREEN. No complete Task2 acceptance yet.

Historical audit118120779431 reports finite HTTP503/actions after verifying
Tasks1–4. Artifact12195531263 SHA25676f60c88ddb68ed6c5a0824e5ce698ec8da6f2eb78abfb66a0698adb352a10bd
independently matched. This is evidence of external HTTP service failure. One
same-SHA job rerun was requested under the approved policy; GitHub rejected the
request403 because the containing workflow is still running. NO retry actually
started, no permission failure inferred, no accepted evidence replaced.

Separately immutable baseline118120779815 fails exact_original_c02 exit1;
its original diagnostic has no exception/test/count/infrastructure category.
The first causal command remains UNKNOWN. Do not label that failure transient
or rerun it blindly. Original C03 source remains exactly0a/5c294; all original
C01/C02/C03 source verifiers pass locally. Additional outer observation is needed.

Task2 Ruling: add a C04-owned observer around the unchanged original command
sh docker/verify_c03.sh with its exact original cwd/environment/timeout — the
original private log survives but cannot safely be published — cost if wrong:
extra finite metadata, never an altered baseline verdict. Verify the original
source before launching, preserve its actual exit, read only the last bounded
4MB of a known stage log, emit static categories/allowlisted npm error codes,
and upload only newly generated finite metadata outside the baseline. No source,
private log, URL, token, arbitrary message or baseline file is exported/modified.
Three tests first RED for missing observer then GREEN, including exact child
command/cwd/nonzero exit and unknown-error non-inference/privacy controls.
Focused C04/current C03 CI174 passed+37 subtests, no failures/skips. All14 gates
remain mandatory on the next exact head. No retry, timeout growth, baseline
mutation, failed-job suppression or Task3 advancement is authorized by this change.

### Task 2 COMPLETE — exact-head full hosted acceptance

Tested implementation86b354b63cd042f94712b9dfb9d9cf8cd71577da,
tree8ca53644566aab5ca48f639abe827b420dfc3de9, run39271586772 attempt2,
all14 mandatory jobs SUCCESS, zero selected skipped jobs/steps. Provider exact
head/tree/ref/path/push metadata freshly inspected; validate_checkpoint accepts
new task02-complete.json. Historical task02-start.json stays unchanged.

Attempt1 had12 green, historical audit118125000107 HTTP503/actions and final
118147302398 correctly denied failed upstream. Its artifact12194868611 digest
36f67832e018a7ce431716d4dd82cd32bad8641c0506434e0e4a17c9588581c4 independently
matched. Once the run completed, the one permitted same-SHA audit retry actually
started:118267274381, attempt2. All12 earlier completed C03 tasks' exact-source
execution evidence verifies real executions/exit0/zero skipped. The retry succeeds;
no second retry, audit bypass or invented transient explanation is used. Provider
attempt2 job logs were inspected for all14 jobs. Unaffected inherited runtime
records retain their original execution times; no new execution of unchanged
successful jobs or original historical tests is claimed merely from retry IDs.

| Mandatory job | Attempt2 job ID | Actual runtime evidence |
| --- | --- | --- |
| c03-evidence-audit | 118267274381 | 12 historical tasks verified, all real/exit0/zero skips |
| c03-owner | 118267275738 | 75/0/0, natural0, elapsed430.8s, owned cleanup true |
| c03-processing | 118267276179 | 62 passed call reports, natural0,302.0s, cleanup true |
| c03-staff | 118267276877 | 67/0/0, natural0,542.2s, cleanup true |
| c04-baseline | 118267322558 | immutable0a/5c294,127 stages0, backend1692, final cleanup0 |
| c03-timeout-probe | 118267324107 | intentional deadline child1, positive supervisor/owned cleanup contract |
| c03-storage | 118267327503 | 91 passed call reports, natural0,151.4s, cleanup true |
| c03-final | 118267328729 | 129 stage markers0, backend1827, clean_cleanup0/final_rehearsal_passed |
| c03-restart | 118267340581 | actual crash/service restart contract, natural0,332.9s, cleanup true |
| c03-task14-native | 118267343616 | all10 native/isolation/runtime/cleanup stages0 |
| c02-migrations | 118267343926 | inherited real PostgreSQL/Redis; Tasks8/9/10 counts108/89/86, natural0/cleanup true |
| foundation | 118267351752 | host823 passed+37 subtests; aggregate1960/0/0, natural0,1463.5s, cleanup true |
| c04-postgresql | 118267352485 | 136 passed,0 failed/error/skip/xfail/xpass/deselected, actual0, task2 |
| c04-final | 118268335346 | upstream accepted,136 passed/all other counts0, actual0, task2, no migration drift |

All full-service cleanup verdicts and final service Stop containers steps succeed.
Foundation aggregate1960 is reporter aggregation, not1960 distinct test functions.
Artifact12198456239 SHA256a36e7a999fb67f4705bbeb117a47792340b30b2c641228b967def7db9b6f2807
independently matched:11583 finite rows,144 stage rows all0,13 original C02
subphases all0, no failed/skipped/xfail/xpass reports. Baseline artifact12199965729
SHA25608d9210edd4f031dcaffdc0dd5bc43b6c7a8677902b604e462edb0d1aa5e42ef
matched and confirms exact original tree/exit0/empty failure categories. Retry
audit artifact12216373876 SHA25613bee5a2fa78aaf26d50dce2ce17d2a5bac3d86cb8aa4d35f6fb51fe67b406e9
matched with12 verified task rows. Prior5a159 baseline failure's causal command
remains unknown; current immutable baseline success is fresh acceptance, not an
invented diagnosis or a change to that historical failure record.

Distinct author manual Task2 review after runtime inspection: exact frozen owner
selection/confirmation, C03 User-first locks/fresh eligibility, partial role loss,
source version reconfirmation, expiry/withdrawal, exact approved qualification
membership, credential/identity/private media exclusions, disclosure default-deny,
SQL immutability and cross-owner guards, receipt/audit/outbox atomicity, protected
slug identity, privacy inventory, additive migrations, bounded diagnostic output
and current-stage scope-test extensions checked against approved Task2/§3/§5.
No unresolved Critical or Important Task2 finding. No independent reviewer or
whole-C04 final review is claimed. Public delivery/search/posts remain absent;
selected media remains pending until Task3. Real production disclosure and media
rights wording remain the approved later release gate, not invented policy.

Live main/C01/C02/C03 completed/planning heads and approved C04 plan/blob remain
unchanged. New completion is documentation-only and preserves the tested SHA/tree
above separately. Task2 COMPLETE. Next Task3 in strict order; no further approval
needed for that already approved task.

### Task 3 RED — separate sanitized publication copies

Task2 prerequisite COMPLETE at tested86b354b63cd042f94712b9dfb9d9cf8cd71577da,
tree8ca53644566aab5ca48f639abe827b420dfc3de9, run39271586772 attempt2 all14.
Documentation-only35e6b7920b46177bd093c490e663fae0baebfcea/treeb42b7bd132ed03f5225ec5af1d90dd64ac46f58b
preserves that acceptance separately; Task3 starts from35e6b79. Read exact Task3
brief/§3/§5 and current assets processing/scanner/isolated sanitizer/store,
privacy/cleanup/worker composition and professional source-selection contracts.

Local behavioral RED:15 actual assertions in test_public_copy_contract fail for
missing frozen release/copy DTO and separate publication namespace. No Task3
production code exists. New five PostgreSQL tests collect without errors and
exercise real C03 verified/confirmed branding fixtures before missing copy
command assertions; real hosted RED is pending, never inferred from collection.
Remaining scan/re-encode/crash/revocation/hold/real-service cases must be written
and fail behaviorally before their corresponding implementation. No Task3 service
or complete acceptance is claimed. Tasks4–11 remain NOT_STARTED.

Task3 engineering direction follows approved boundaries: reuse private origin
ACL and existing bucket through an exact isolated publication namespace adapter,
never change Asset/AssetDerivative classification or URLs; reuse isolated pixel
decoder, actual scanner, existing Celery worker and private reconciliation Beat.
Assets receives server-validated typed release callbacks; it must not import
professional models. Source holds and the existing profile_media/purpose policy
retain descendant copy bytes but never authorize a withdrawn copy's delivery.
No new Consent purpose, legal wording, public bucket, image format or scheduler
is introduced. Task3 has no public route; its final internal buffered-read
callback is later composed with Task4's public authority.

Task3 initial hosted RED independently observed at
f8b1f5297e71ef35a1870c66637d1ad605f90fe7/treec4bd68b0f0335ffdab1113d1e14ff5924406a46a,
run39314340099/PostgreSQL118271816278:136 prior tests pass,20 expected
missing-copy-boundary assertion failures,0 error/skipped/xfail/xpass/deselected,
actual exit1. Five failures use actual verified/confirmed C03 fixtures before
calling the missing composition. Foundation118271816197 fails intended missing
contract assertions too. No runtime absence/collection error is credited as RED.

Expanded pure contract tests20/20 first fail before implementation, then20/20
GREEN after frozen typed release/public DTO and exact publication-key adapter.
This adds no model, migration, processor, public URL, signer or source ACL change.
New fake-I/O/PostgreSQL tests for separate-object effect, withdrawal during write,
crash inventory/new-generation recovery, scanner faults, final buffered release
and direct-SQL cross-binding are written before those services/models exist;
collection succeeds for the eight race/failure cases, real DB RED still pending.
Fake adapters assert I/O occurs outside transactions; actual MinIO/scanner/worker
and SIGKILL evidence remains independently mandatory, never replaced by them.

Task3 Ruling: record a separate protected PublicCopyAttempt for each generation
alongside PublicAssetCopy — an old writer can finish after a lease expires, so
all prewritten generation keys must stay inventoried for policy cleanup — cost
if wrong: bounded extra rows (existing eight-attempt ceiling), never a private
source reference becoming public. The unique release/source/purpose/processing
effect remains one copy row; each generation gets a distinct publication key.
This follows the approved generation/crash/idempotence/cleanup contract and C03's
existing attempt pattern, without another infrastructure or authorization system.

Task3 expanded hosted matrix at275a4cefbe2064eb0b5fc6602b744613235abbe9,
treea70cc669669156599ff96fe66a37ca189fb8ed79, run39315118465,
PostgreSQL118274449849:156 passed/16 expected missing-inventory/command assertion
failures,0 error/skipped/xfail/xpass/deselected, actual exit1. All16 failure
nodes/phases/classes inspected. Only then source-bound copy schema and prepare
command were written. Worker result contract additionally first fails with
missing CopyResult, then all21 pure tests pass with its frozen finite metadata.

Current partial implementation adds copy/attempt tables and frozen SQL identity/
source guards in unpublished assets0010, depending on accepted professionals0018.
No existing migration is edited. Copy source includes exact private derivative
identity/version, and each generation's immutable key/output metadata is retained.
Preparation validates current owner/account, exact confirmation, C03 eligibility,
private branding purpose and source generation through mandatory trusted
composition, then commits inventory without I/O. A shared professional selector
handles confirmed media preparation; the existing effective_publication default
still only returns an activated current revision, so pending copies do not become
public. No assets Python import of professionals is added.

Local partial verification: whole-tree Ruff/format478 files clean,134 C04 tests
plus37 subtests pass, required mypy98 source files pass, Django check0 issues.
Django-generated migration state check says no changes detected, with the expected
local PostgreSQL-unavailable warning. SQL has NOT been compiled/applied on a real
service yet; hosted migration/source-binding results are required. Scan/process/
read/activation/cleanup and actual media gate/probe are still unimplemented, and
Task3 is not accepted. A further SQL test now requires publication promotion to
fail before selected copy outputs exist; its actual negative behavior must be
observed before adding the new readiness guard. No public route/release exists.

Held-copy and buffered-read tests are present before cleanup/read implementation.
Source holds inherit existing profile_media/avatar-cover-logo retention policy;
no new hold kind or consent purpose is introduced. Cleanup must reuse committed
reservation semantics outside I/O and prove a hold-vs-copy-deletion race, including
new holds during reservation and late old writer cleanup, before acceptance.

Task3 partial schema/prepare head72f2d4c0048a38576d774795399e61b5bcd9f80d,
treeb086002c3a78f024d0723fa85de32ecafbc621b7, run39317673095,
PostgreSQL118283271209 applies assets0010 and reports162 passed/13 failures,
0 error/skipped/xfail/xpass/deselected, actual exit1. Initial five source/prepare
cases now pass. Twelve cases stop at the intentionally missing durable scanner
interface; three of those SQL cases were unnecessarily coupled to claiming a
worker lease. Split their fixture into prepare-only versus claim paths so the
SQL identity/readiness probes exercise the actual guards independently.

The thirteenth failure is decisive additional behavioral RED: direct SQL can
promote a media-selected publication while outputs are absent; pytest's expected
DatabaseError does not occur. Add a supplementary readiness trigger in Task3's
initial migration: every selected media binding needs an exact ready copy/current
ready attempt before a new current revision/state can activate. All Task2 guards
remain installed unchanged; text-only publication and withdrawal retain their
existing behavior. This new guard still requires real PostgreSQL GREEN.

Ruling: evolve only the not-yet-accepted C04 initial0010 schema through forward
commits before any deployment — its newly demonstrated readiness invariant must
be present on a clean install — cost if wrong: replay this unaccepted initial
schema in disposable CI. No C01/C02/C03 or accepted Task2 migration changes, no
history rewrite, and each prior published SHA/tree/runtime record stays intact.

Task3 readiness correction9a56476578fca972304aa45a4e13a0d2d012e6db,
tree0eaf3944ebc2c4978b887edb68f236fef6e7ab3d, run39319110775,
PostgreSQL118288212579:166 passed/9 expected missing scanner/worker command
failures,0 error/skipped/xfail/xpass/deselected, actual exit1. All initial prepare,
three direct-SQL copy binding and direct publication readiness probes now pass;
all remaining failures stop at scan_due_public_copies, which is not implemented.
The earlier unauthorized SQL promotion is behavioral RED→real PostgreSQL GREEN.

Task3 mandatory real-service wiring test first RED because c04-public-media is
absent. Add that exact already-planned required_jobs(3) job with pinned tooling,
real private MinIO/ClamAV/isolated decoder and actual worker/crash/Beat/scanner
outage probe commands; cumulative and aggregate runners advance to task3. The
PostgreSQL-only selection explicitly ignores ONLY the real media service file;
that file is mandatory in c04-public-media, not skipped/deselected or replaced
with fake providers. Three actual-service cases collect locally; they have NOT
run locally and no service GREEN is claimed. The new service job must establish
its own real RED before production processing is implemented.

Extend current schema scope by exactly assets.PublicAssetCopy/PublicCopyAttempt
and the one User reverse relation; unchanged UUID/PROTECT/timestamp/forbidden-field
checks still cover every old and new model. Current C03 migration coverage first
fails for assets0010, then delegates only that exact new leaf to C04's real SQL
rendering, preserving all historical commands. Immutable fixtures/pins are intact.

Task3 Ruling: reuse the inherited observer's fitlink-c03-private-processing
Compose label on the new job's separate fresh hosted runner — this keeps exact
owned-process/cleanup supervision without modifying C03 observer infrastructure
or sharing data between runners — cost if wrong: a preexisting project/volume
causes non-destructive refusal before ownership; never cleanup another run's data.
No scheduler process is added; the probe requires the existing asset-beat to
find a copy with no explicit prompt. Worker SIGKILL and scanner outages are actual
commands in the mandatory script; their successful execution is still pending.
Probe diagnostics first RED for missing metadata boundary, then GREEN with only
allowlisted phase/error class; exception text and private state never leave it.

### Task 03 — first required real-media job diagnostic boundary

- Published source `d141fc711c48287e9f29fa1340a8b38591b73011`, tree `53a3bb4b47af0d32e5b32cfb05df4cd6c0b7ab20`, run `39322305205`, media job `118299166893`: exit 1 at 155.1 seconds, natural exit and complete owned cleanup. PostgreSQL, MinIO, Redis and scanner bootstrap completed; new migration appeared in finite progress. No test case reports were produced. This is **not** credited as missing-feature RED: the exact shell boundary is not yet observable. Add finite static stage/exit metadata only; preserve all verification and timeout bounds. No raw output, environment, private identifiers or image bytes are exported.
- The same run's staff job `118299166838` exited at 13.9 seconds before any test report (all counts zero); first cause remains unknown. It is not acceptance and no speculative retry or diagnosis is asserted.

### Task 03 — durable claim and observable real-service RED continuation

- Diagnostic source `739b507e7dcfab6336929d03223e335e9977aa82`, tree `71663122429816b360f66280253d28b015361deb`, run `39323212080`, media job `118302295168`: finite shell verdict identifies **behavioral_tests**, exit 1 at 131.3 seconds after successful migration and scanner health; complete owned cleanup. Earlier uncertainty is narrowed, not retroactively relabeled.
- Inspection found the outer supervisor intentionally discards arbitrary child stdout. `c04_gate.py` emits finite reports on stdout but its private temporary evidence directory is not the outer media artifact directory. Persist those same sanitized report records and aggregate counts to a fixed dedicated path only when the media gate explicitly opts in. No raw pytest output is persisted/exported. Local direct gate proved 21 passed / every non-pass category zero, exit 0, and exactly 63 finite phase reports plus one aggregate record.
- Hypothesis that PYTEST_PLUGINS caused duplicate plugin registration was tested locally with the exact plugin setting: 21 passed, exit 0. Rejected; no plugin-registration workaround added.
- Implement metadata-only due scanning/claiming after the nine real-PostgreSQL missing-scan failures already observed at `9a56476578fca972304aa45a4e13a0d2d012e6db`. User anchor and existing source authority precede copy/attempt locks; 60-second leases, eight generations, distinct preinventoried keys, broker I/O after commit. Recovery recomputes authority after generation change. Unknown programming/database failures propagate; broker failure retains a recoverable lease. No processing, read, activation, cleanup or production worker implementation in this checkpoint.
- Current C04 unit suite: 136 passed + 37 subtests; focused contracts: 21 passed; mypy two modified domain/composition files: success; Ruff: success. These local checks are not real-service or full hosted acceptance. PostgreSQL job `118302295260` on the diagnostic source still reports the expected missing scan boundary. Task 03 remains IN_PROGRESS.
- Live protected heads checked again: main `8ede9a451db6103f4e3ebf65784ee9f16b96feb2`, C01 `75c551e5b9bbbfb7777ee52b09a1993b681e921a`, C02 `0905be6c6ca608d469fe33e87f514b22591132d1`, C03 handoff `0a867328a6d8ee8c71ec9bd9eeb8910221d1b270`, C03 plan `79fd62e583cbe81f335bb08fce0eb43ff36b0167`, approved C04 plan `ba82967cb2e21920076c5a0d25ed1988f777e943`; unchanged.

### Task 03 — claim PostgreSQL evidence and real-service settings correction

- Source `9c0b837ac4bc1c4774cb57ea9d9dc7f63fb7ed1a`, tree `ca8795c752d6f055bc6ce70b2ec2f81255951119`, run `39323692894`, PostgreSQL job `118303952236`: **168 passed, nine failed, zero errors/skips/xfail/xpass/deselections**, exit 1. All nine call traces now pass real source preparation/claim and reach `process` at copy_helpers.py:108, where the intentionally absent processor raises AttributeError. Metadata claim is exercised on actual PostgreSQL; this is not whole-task acceptance.
- Same source media job `118303952060`: finite export now works, **21 passed / three failed / all other categories zero**, exit 1. All three stop at prepared_real line46, the explicit real-storage-settings assertion. The failure is harness configuration, **not** processing RED. Root cause: pyproject.toml pytest addopts forcibly select `config.settings.test`, whose STORAGE_BACKEND is hard-coded fake, overriding the Compose development environment. Preserve the real-provider assertions and explicitly select `--ds=config.settings.development` for this required isolated real-service command; no production settings, mocks, skips or timeout changes. This proves the default composition rather than injecting a fake backend. Processing implementation remains deferred until the actual service preconditions reach the missing processor.

### Task 03 — real processing RED and two-phase implementation checkpoint

- Source `eaede780e5d94ccf74c2eecfa9e12b93444eefb5`, tree `98dc8f9fe03d2031ccb14b270fa5d8df7924cf43`, run `39324315619`, media job `118306083143`: **21 passed, three expected missing-processor assertion failures, zero other categories**, exit 1. All three pass real S3 settings, enabled processing, actual clean ClamAV scan, actual MinIO write/head and PostgreSQL source/confirmation/claim; call failures are precisely test lines115/140 requiring `process_public_copy`. This is valid real-service RED. No worker recovery success is yet claimed.
- Implement source/checksum bounded reads, existing scanner and isolated decoder, prewrite output inventory, separate private publication object write/verification, fresh owner/source/hash/generation/lease fences, complete-revision activation and UUID-only outbox, and buffered internal read with a second fresh authorization after object I/O. Provider calls stay outside database transactions. Retry output metadata is immutable; old generations never share keys. No public route.
- Local C04 unit suite 136 passed +37 subtests, Ruff and two-file mypy successful; actual PostgreSQL/service GREEN still pending publication. Production Celery task, atomic confirmation scheduling, lifecycle/physical erasure and hold reservation composition remain to finish Task03.
- Review concern to reproduce: C03's private derivative checksum constraint validates format but does not require a version increment on checksum mutation. Public copy currently binds derivative ID/version, while the stored processing authority vector also contains mutable publication/account state; it cannot simply be reused unchanged after activation. Add an end-to-end checksum mutation regression before choosing the narrow binding fix. This new test is not yet executed and no RED or resolution is asserted.

### Task 03 — observed processing results and remaining security boundaries

- Tested processor source `6e98efb817f8d8076beab737bc622e0ae06bc400`, tree `9b085ee1248e3efc864eeb612df78202a8924bdb`, run `39325358272`: PostgreSQL job `118309667376` **175 passed / three failed / zero errors, skips, xfail, xpass, deselections**, exit 1. New-object output, withdrawal during I/O, crash/reclaim and all four scanner failures now pass. Remaining cases: buffered read TypeError at race test110 (implementation used `store`, existing contract tests use `publication_store`); held copy reaches the absent lifecycle command at131; checksum mutation regression at165 **Failed: expected exception not raised**, demonstrating the reviewed stale source binding.
- Same run real media job `118309666948`: **23 passed / one failed / zero other categories**. The actual MinIO/ClamAV/isolated-decoder clean case passes EXIF/GPS/XMP removal, new namespace, unchanged private derivative, no source read/signer and both unsigned origin 403 checks. Wrong MIME rejection passes. The first parameter's EICAR text embedded inside PNG metadata was not classified malicious; the real service accepted it and the sanitizer removed metadata. Do not invent a production malware detector or claim arbitrary embedded-text detection. Use the same complete standard EICAR byte fixture as inherited real ClamAV tests, and add an explicit actual scanner malicious precondition before this rejection case. Metadata removal remains separately tested with a real PNG. No scanner mocks, skipped cases or relaxed processor behavior. Worker probe has not yet run past the behavioral command.
- Fix read keyword to the existing `publication_store` interface. Add immutable private `source_derivative_sha256` to the not-yet-accepted C04 copy schema, regex constraint, SQL source/promotion checks, prepare and mandatory composition validation. No C03 or accepted Task02 migration changes. This closes the actual checksum RED without reusing a processing digest that legitimately changes after publication activation.
- Ruling: extend the private copy binding with its source derivative checksum — approved exact-source authorization cannot rely solely on a mutable C03 checksum plus unchanged version — cost if wrong: one extra private fixed-length field/constraint; no public field, format or publication category added.
- Implement lifecycle metadata revocation after the actual missing-command RED; it uses the same source policy with only the Marketplace flag check disabled, so flag-off does not erase intent but withdrawal/expiry/source loss revokes delivery. No storage I/O or new authorization system. Physical cleanup remains absent for its next explicit RED.
- Add (not yet executed) positive-authorizer, source-hold-after-copy-delete-reservation and private copy inventory regressions. These must establish their own first causal outcomes before changes to the C03 hold composition or inventory.
- Local verification: C04 units **136 passed +37 subtests**; two-file mypy successful; Ruff successful; Django migration drift reports **No changes detected** with expected unavailable-local-PostgreSQL history warning. No local real migration or hosted acceptance asserted.

### Task 03 — positive source fences and observed remaining boundaries

- Source `e86d6dbfc398e19cbc1d9b7ebea3446a0cb98c7f`, tree `7d5592a54c4cf514a7de3bdb49f67b2ecfe0b7f1`, run `39326313942`, PostgreSQL job `118312979710`: **177 passed / four failed / all other categories zero**, exit 1. Checksum mutation and buffered-withdrawal races now GREEN. Exact remaining RED: missing cleanup composition at race134; positive-authorizer test180 expected exception not raised; source-hold-after-committed-copy-reservation test201 expected denial not raised; owner-copy inventory test211 missing record. All cases are actual PostgreSQL and first causes inspected.
- Media job `118312979730`: **24 passed / zero failed, errors, skips, xfail, xpass, deselections / actual behavioral command exit0**. This includes actual clean pixel sanitization and both real scanner/MIME rejection cases. The following real worker probe fails in `worker-prepare`, matching absent `tasks.process_public_asset_copy` in this exact source. No SIGKILL/Beat/recovery success is yet claimed. Add finite shell stage labels for every subsequent probe boundary so shell metadata cannot continue labeling a worker failure as behavioral_tests.
- Fix positive digest validation; add owned/bounded private copy and attempt inventory records without keys, hashes or URLs. Extend only the existing C03 hold composition's final owner-serialized reservation predicate to recognize C04 copy/attempt deletion_pending descendants. No new hold kind, purpose, capability or retention policy.
- Implement per-generation reservation → recheck → private publication namespace delete/head outside locks → final recheck/audit, with missing-policy/hold retention, audit/provider retry, preserved tombstones and no source/derivative deletion. Old inactive generations can be erased while the current ready generation stays visible. Add immutable attempt retired_at so retention is measured from retirement, not restarted by retries; deletion_pending fits the new C04 attempt state column (20 chars). These are edits to the still-unaccepted initial C04 migration, never accepted C03/Task02 history.
- Add the real ID-only late-ack/reject-lost public task and atomic confirmation inventory hook. Existing private Beat/process/schedule remains the only scheduler: extend its reconciliation body while preserving its return/result and isolating C04 retry failure. Reuse current attempt next_attempt_at for bounded ready-lifetime/cleanup due work, at most100, so successive ticks do not repeatedly inspect only the first100 permanently-ready profiles. Ready output metadata remains immutable; SQL readiness checks apply to entering ready, while advancing its due timestamp never becomes authorization. Source/account/flag request checks remain fresh.
- Ruling: use the existing attempt due field for ready lifecycle checks and cleanup — preserves bounded progress without another cursor table/scheduler; cost if wrong: due work may lag, while request-time authorization still denies stale delivery. Attempt retirement timestamp remains fixed across cleanup retries/late writers.
- Synthetic fixtures now finalize private checksum/body **before** real publication confirmation; the new atomic hook correctly freezes that binding at confirmation. No production source mutation or bypass of the checksum regression. Add verification of policy erase/late writer, audit failure/retry, old-generation cleanup/current visibility, no deletion under atomic locks, and real MinIO copy deletion with original derivative bytes preserved. These added verifications have not yet run on PostgreSQL/MinIO; no GREEN assertion.
- Local checks: 158 unit tests +37 subtests (C04 and C03 privacy), 108 inherited schema/scope/CI/foundation units; seven-file mypy successful; Ruff/format/diff checks successful; migration drift No changes detected with expected unavailable-local-PostgreSQL history warning. Full fifteen-job hosted acceptance remains mandatory and pending. Task03 IN_PROGRESS; Task04 not started.

### Task 03 — October 20 source recovery and remaining harness failures

- Resume found the local workspace at old accepted implementation `86b354b63cd042f94712b9dfb9d9cf8cd71577da`; live execution head remained `d8d7c73423641b4fdbd9d9e2b22a21840828d7ac`, tree `aa8d3a8be342909fd188761e5bfb8b64b2eba052`. Preserve the old local branch as `local/c04-pre-resume-20261020`. Recover 34 changed/new blobs from GitHub, verify every blob hash, reconstruct the exact full tree, and reconstruct all twelve intervening unsigned commit objects with exact SHA encodings. The recovered branch is clean and C03 handoff ancestry verifies. This is recovery of published objects, not byte-for-byte recovery of missing unpublished files. Four earlier local-only harness edits and local diagnostic logs were absent after rollback; reimplement the two evidenced boundaries and independently rerun RED/GREEN, without claiming recovery of their original bytes.
- Protected live heads independently match the previously recorded main, C01, C02, C03 implementation/planning and approved C04 plan heads. No protected branch updated.
- Run `39327898085` at exact d8 source: PostgreSQL `118318368095` **184 passed / every non-pass category zero / exit0 / task3 accepted by that focused gate**. New source checksum SQL, positive-authorizer, owner inventory, hold reservation, lifecycle, physical-generation erasure, audit retry, late-writer and current-generation preservation cases are GREEN on real PostgreSQL. This does not complete the task.
- Media `118318367842`: **24 passed / every non-pass category zero** including actual MinIO generation deletion and original private derivative preservation, followed by `worker-prepare` **PermissionError**, shell exit1. Existing finite diagnostic lacks source frames, so the exact cause remains unproven. Add only bounded existing repository Python source paths/function/line, excluding exception text, locals, environment, private paths and external frames. Do not yet guess a production fix or claim worker/SIGKILL success.
- Foundation `118318367621`: 1912 pass /3 fail /0 skipped; all failures are the new real-media cases at prepared_real line46 (STORAGE_BACKEND assertion). Current C03 final `118318367924` complete_backend:1875 pass /3 fail /0 skipped, same new real-media file. The dedicated real job uses development settings, while inherited pytest addopts uses test settings with hard-coded fake storage. Preserve all inherited tests and select the actual S3/processing fixture settings only after asserting the Compose environment explicitly provisions S3 and enabled processing; actual MinIO, scanner and default runtime providers still execute. No skip, ignore or mock substitution added.
- Immutable baseline `118318367750`: original complete_backend1692 pass, clean owner browser10 pass, then clean_staff_browser27 pass/1 fail at `tests/e2e/c03/test_staff_verification.py::test_decision_reload_single_effect`; exit1. Precise exception/root cause is not exposed by its unchanged diagnostics. No claim of a transient fault, no baseline mutation, no baseline-only speculative retry. The next implementation acceptance still requires an unchanged original baseline run to pass.
- Ten jobs succeeded and five failed in this run, including C04 final `118333426091` correctly rejecting failed upstream jobs before its installed acceptance (selected dependent steps skipped). No complete hosted acceptance or Task03 completion.
- Fresh local TDD after recovery: six missing-boundary failures plus one passing privacy test → seven focused tests pass. Full C04 unit suite **142 passed +37 subtests**; Ruff/format/diff checks pass. An extra nonmandatory mypy invocation on the diagnostic script exposed an existing unannotated deque in imported `docker/c03_gate_diagnostics.py`; it is not a runtime failure, and no unrelated code or typing gate is weakened. The configured mandatory mypy command is rerun separately.

### Task 03 — exact worker failure located; private atomic probe journal

- Source `c829a7dc75fd8ed155a57eadafadd42255d2ccbd`, tree `4cf2342250a243e7e3442c2fe18c4d8796ad02a7`, run `39348451849`: PostgreSQL `118386651252` **190 passed / all non-pass categories zero / exit0 / task3 focused acceptance**. The configured mandatory mypy command also passed locally for98 source files. These do not replace the full hosted manifest.
- Real media `118386652213`: **24 passed / all non-pass categories zero**, then worker-prepare PermissionError. Newly bounded source frames identify `worker_prepare` line182 → `save` line115, exactly `STATE.open("w")`. The journal was directly beneath host-owned `.runtime`, while the checks image runs as non-root `app` (Dockerfile UID1000). This is a test-harness journal permission defect, not evidence of a publication authorization defect or unavailable actual media service.
- Move only this synthetic fixture journal to the probe's already-explicitly-writable `.runtime/c04-media-evidence/checkpoint-private.json`. Artifact patterns select only *.jsonl, so neither that JSON nor private temporary files is uploaded. Do not broaden workspace permissions or change the production container user.
- Two additional independently observed REDs: initial file creation was not0600 before JSON serialization, and a serialization failure truncated the previous journal. Both tests failed (2fail/2pass) before the change. Create an exclusive/no-follow random temporary file with0600 at open, serialize/flush/fsync, then atomic replace; remove failed temporary writes while retaining the previous checkpoint. Both cases GREEN, plus a regression checks private checkpoint and temporary paths against the actual artifact upload patterns. No actual identity, upload bytes, tokens, object keys or session secrets enter these fixtures/artifacts.
- Current local C04 suite **145 passed +37 subtests**, Ruff/format/diff checks successful. No production code, schema, required job, assertion or service changed in this patch. No worker/SIGKILL/Beat success is claimed until the following actual hosted run executes them. Task03 remains IN_PROGRESS; Tasks04–11 not started.


### Task 03 — real worker GREEN; exact derivative-version review regression

- Source `70a3d3d40ca9bac7f091d52dadf897bd060c414f`, tree `140d0c9a95c70e8d99b503a2824a9f69eaa38ab5`, run `39349264499` attempt1: PostgreSQL `118389314507` **193 passed / all non-pass categories zero / exit0 / task3 focused acceptance**. Media `118389314460` **24 passed / all non-pass categories zero**, followed by actual non-eager worker queue, real output before commit, SIGKILL/recovery into generation2 exactly once, existing Beat discovery without a prompt, actual ClamAV outage denying readiness and scanner restoration recovery. Shell complete/exit0 and owned host/container cleanup complete. First actual worker/Beat/crash GREEN is now observed; earlier checkpoints did not prove it.
- Downloaded actual media artifact `12232252997`; ZIP SHA256 `eb470e07df9c8817a8624bc4d3774108a1932c1690859857d88636830c2c59a6` matches provider digest. All four members are finite JSONL; checkpoint-private.json and temporary journals absent. Inherited current owner/staff, migration, processing/storage/restart, timeout ownership and historical evidence gates also succeeded. Full foundation, original baseline, C03 final and final C04 acceptance remain pending; **not task acceptance**.
- Author review found a possible exact-source read/lifecycle gap: processing compares private derivative ID/version/checksum, but composition `_binding` currently compares an existing copy only by checksum. An incremented derivative version with identical bytes may therefore reauthorize an old copy, including after buffered I/O. Add three real-PostgreSQL regression cases (before read, during read, lifecycle reconciliation), without production changes. Their RED is not yet observed; no speculative fix or GREEN claim. Full new-head hosted acceptance remains required after any correction.
- Live approved plan commit/tree and C03 handoff/parent independently reverified; main, C01/C02/C03 and both plan heads unchanged. No protected ref updated. Task03 IN_PROGRESS; Task04 not started.


### Task 03 — exact derivative binding RED and relocated diagnostic source RED

- Regression source `e0f50b76df5eca913cd25bdefd4793ea3fa8e9c7`, tree `81d0adca4d44c835448eff093d15562d8188115a`, run `39350647622`, PostgreSQL job `118393764897`: **193 passed / three failed / errors, skips, xfail, xpass, deselections zero / exit1**. Before-read and after-buffered-I/O cases reached test204 with expected AssetNotFound not raised; lifecycle case reached test201 and remained ready instead of revoked. Real PostgreSQL confirmed the hypothesis. `_binding` now compares the inventoried private derivative ID, version and checksum together, matching processing/SQL identity. The same mandatory validator governs both read fences and lifecycle; no new policy, DTO field, schema or authorization system. Actual PostgreSQL GREEN remains pending.
- On prior source70a, foundation job `118389314495` **1923 passed / one failed / zero skips**: `test_probe_failure_metadata_reports_bounded_source_frames_only`, test21, frames absent. Investigation found the existing inherited triage already documents pytest rewritten bytecode retaining host compile-time co_filename inside container mounts. Reproduced this exact boundary locally with a compiled external checkout filename and the loaded module's actual repository __file__: **one failed/five passed**, missing relocated source frame.
- Fix only the C04 diagnostic normalizer: walk runtime traceback frames; direct repository filenames remain preferred. An outside compile filename can map only to its loaded module's existing, allowlisted repository Python file with an identical relative filename suffix. Emit only bounded relative file/function/line, never external path, exception text, locals or environment. No immutable baseline, assertion, observer deadline or required job changed.
- Local C04 units **146 passed +37 subtests** after both fixes; Ruff/format/diff checks pass; mandatory mypy command **98 source files success**. This is unit/typing GREEN, not PostgreSQL/media/full-hosted acceptance. Task03 stays IN_PROGRESS, Task04 not started; require a complete fifteen-job new-head manifest.


### Task 03 — derivative fences GREEN; prerequisite build cause still unknown

- Source `e71ee5fb703afff5e43774006fe91fcaca7d3e27`, tree `2d60bb26ecbd29492b59005d21e470eb177fc65f`, run `39351021742`, PostgreSQL `118394952543`: **197 passed / every non-pass category zero / exit0 / task3 focused acceptance**. All three derivative-version regressions are now GREEN on actual PostgreSQL. Real media `118394942728` **24 passed / every non-pass category zero**, all six worker/write/SIGKILL/Beat/scanner outage/recovery markers, complete shell exit0 and owned cleanup. No production/media regression observed.
- Same source foundation `118394942753` fails its exact C01/C02 runtime prerequisite after152.9seconds, before test reports; finite process snapshots reach the original C01 production Docker build. C03 final `118394942770` fails `exact_original_c02` after approximately242seconds; no test counts/exceptions/known infrastructure markers. Selected post-action cache steps skip after upstream failure; this is not acceptance. Exact first causal build/dependency error remains **unknown**, not proven transient. Do not attribute it to npm, rerun blindly or mark the task complete.
- Add bounded diagnosis for the already-existing strict npm error-code classifier to both current-source streaming supervisor and private prerequisite-log metadata. Only its finite allowlisted codes may appear as npm_E503 etc.; arbitrary codes, exception messages, private URLs/paths/content remain absent. Existing immutable C01/C02/C03 trees and their commands are untouched; original failures/return codes remain authoritative. No dependency retry, timeout growth, skips or weakened assertions. This extension is evidence collection, not a claimed production fix or a known failure cause.
- Three local diagnostic REDs (two streaming-code cases, one private-log code case): **3failed/8passed**. After wiring the shared classifier, **193 units passed +37 subtests**, including C04, inherited triage/privacy, supervisor and final-rehearsal contracts. Ruff/format/diff checks pass. Actual hosted cause must be inspected on the next source; zero complete fifteen-job manifest so far. Task03 IN_PROGRESS; Task04 not started.


### Task 03 — cleanup replay review and hosted-only continuation

- Source `6910845e7178cd155fbec390ab2c90c1beede4c4`, tree `f7d2114827dd6d327d488c471761de9b28243dfd`, run `39351977101`: PostgreSQL `118398017707` **200 passed / all non-pass categories zero / exit0**; real media `118398017716` **24 passed / all non-pass categories zero**, all six actual worker/write/SIGKILL/Beat/scanner outage/recovery markers and complete/exit0. Downloaded artifact `12233504062`, SHA256 `e78afe47bf38ff056ae4bc85e30a82ab9d8bd15eee8bde5e0e78df6179018895`, matches provider; four finite JSONL members, no private journal. Current foundation `118398017561` now SUCCESS; exact runtime counts remain to inspect. C03 final and immutable baseline still pending; not task acceptance.
- Author review identified a possible cleanup replay defect: every successful public-copy cleanup overwrites attempt.deleted_at and emits a new asset.deleted audit even if already erased. The inherited private cleanup instead guards its first deletion effect. Reconciliation repeatedly visits retained tombstones, so duplicating metadata/audit would misstate erasure history and accumulate audit effects. Add four actual-PostgreSQL cases for preserved first deletion time and one audit effect, both with and without a late writer; retain actual object removal on every replay. RED not yet observed; production cleanup is unchanged in this checkpoint.
- Local read commands stopped responding; a bounded retry of pwd returned explicit `environment_offline: Environment is not connected` from exec-server capabilities. No unpublished modifications existed: last local/provider head was6910845 and clean. Preserve its local branches/files. Continue via the already-authorized GitHub connector, reading exact current blobs and publishing forward non-forced commits, with actual hosted PostgreSQL RED/GREEN and the complete hosted manifest. Do not claim local checks for changes made while offline. No verification is replaced by mocks/skips; stop if mandatory hosted verification becomes unavailable. Task03 IN_PROGRESS, Task04 not started.


### Task 03 — actual cleanup replay RED; first-erasure fix

- Regression source `07d888a41458b9d08a45c8cd24441ad7d636cf2a`, tree `66d50fd931c3a24b97fe8dd61dedea3a917493db`, run `39354437479`, PostgreSQL job `118405873584`: **200 passed / four failed / errors, skips, xfail, xpass, deselections zero / exit1**. Both before/after-late-writer deletion-time cases fail at test350; both single-audit cases fail at test352. They reach completed actual PostgreSQL cleanup, not a fixture/import failure. This confirms the review finding: successful replay rewrites deleted_at and duplicates the asset.deleted event.
- In the existing final owner/attempt-locked transaction, retain the first non-null deleted_at and append asset.deleted only on first completed erasure, following the inherited private cleanup guard. Repeated cleanup still commits a fresh reservation, checks current policy/hold, deletes/verifies the inventoried generation outside locks and removes late writes. No retention duration, due schedule, policy, hold semantics, schema or public interface changed. An audit failure on first erasure still rolls the completion transaction back and remains retryable.
- The test-only regression source's foundation `118405873281` additionally reports exactly one Ruff formatting correction at test331 (collapse the AuditEvent filter expression); apply that exact formatter output without changing assertions. No local lint/test command can run while the execution environment is offline, so no local GREEN is claimed for this forward fix. Required PostgreSQL GREEN, media replay/cleanup and complete fifteen-job hosted acceptance remain pending.
- Prior source691 foundation `118398017561` independently inspected: **2027 passed / zero failed/skipped**, supervised command exit0 and complete owned cleanup. The earlier prerequisite-build failures remain unclassified historical failures, not a proven transient cause or a same-SHA retry. Task03 remains IN_PROGRESS; Task04 not started.

### Task 3 COMPLETE — independently recovered exact-source acceptance

- Recovery read live execution HEAD `c4ea69fd84c8a9dae37f4101ec651755f2084701`, tree `2a0bd56f12325aaed042d45aa0b33b3bf586a6eb`. Approved plan commit/tree/blob exactly match the authorized values; actual Git merge-base/ancestry verifies. All eighteen commits since accepted Task2 documentation checkpoint `35e6b7920b46177bd093c490e663fae0baebfcea` were inventoried and their source/test/CI changes examined against Task3. A fresh clone matches the full published HEAD/tree and is otherwise clean. No earlier unpublished files exist in this conversation workspace; none are claimed recovered. No existing checkout was reset or overwritten.
- Run `39354826027`, attempt1, exact c4ea69f/tree2a0bd56, push on marketplace/c04-cloud through `.github/workflows/c04.yml`: **all15 mandatory jobs SUCCESS**, every listed step SUCCESS, no mandatory job/step skips. Raw attempt-specific provider metadata confirms every job head and attempt. All fifteen job logs independently retrieved and inspected. New `task03-complete.json` passes the existing exact-source checkpoint validator, with finite runtime evidence and log digests.
- PostgreSQL `118407110990`: **204 passed**, failed/error/skipped/xfail/xpass/deselected all0, actual exit0, task3. Final `118420896394`: complete upstream accepted, **204 passed/all other categories0**, actual exit0, task3, No changes detected, services cleaned up.
- Real media `118407111203`: **24 passed/all other categories0**, actual non-eager worker queued; output written before commit; actual SIGKILL recovered exactly once into a new generation; existing Beat discovers an unprompted copy; actual scanner outage denies readiness; restored scanner recovers current copy. Shell complete/exit0; owned host/container cleanup complete. Actual MinIO checks prove distinct publication namespace/object, private-origin anonymous403, original private derivative retained, no source reads/signing, sanitization removes GPS/EXIF/active metadata, malicious/mismatched MIME denied, and policy-controlled copy deletion.
- Downloaded media artifact `12234204059`; independently computed SHA256 `caf6b1e9c5ad67f64a931249eca95d14bd3b79e26ae31438f4cde4dcdc72fea4` matches provider. Exactly four finite JSONL members,150 total rows; all six probe markers/counts/complete shell verified. Private journal and temporary files absent.
- Inherited Foundation `118407110914`: host859 tests+37 subtests; runtime reporter aggregate2031/0failed/0skipped, natural0, owned cleanup complete. Original immutable C03 baseline `118407111103`:127 stages all0, backend1692, final_rehearsal_passed/cleanup0. Current C03 final `118407111007`:130 stages all0, backend1898, final_rehearsal_passed/cleanup0. Failure/skip diagnostic arrays empty; deliberate timeout/service fault probes remain identified as probes, not ordinary service success.
- Owner `118407110680`:75/0/0; staff `118407111077`:67/0/0; PostgreSQL inherited `118407110929`:Tasks8/9/10 counts108/89/86, natural0; private storage `118407110979`, processing `118407111037`, restart `118407110950`:natural0/owned cleanup complete. Native `118407111100`:10 stages all0. Timeout `118407111080`:intentional deadline with supervisor ownership contract satisfied. Historical audit `118407110910`:all12 tasks, actual executions/exit0/zero skips. No immutable fixture or inherited mandatory service was replaced.
- Distinct recovery author source/security review checked server-issued own-branding authority, selected confirmed immutable revision, exact source/derivative ID/version/checksum, current identity/role/account/hold/withdrawal checks, SQL cross-owner/immutability/readiness guards, bounded I/O outside domain locks, final buffered read fences, leases/generations and late writers, retained inventory, policy/hold serialization, first-erasure timestamp/single audit effect, and metadata-only diagnostics. No unresolved Critical/Important Task3 finding. This is author review, not an independent reviewer or final whole-C04 review. No public route yet; no C05/merge/deployment/production publication.
- Live main, C01, C02, C03 implementation/planning and approved C04 plan heads independently match recorded protected-by-instruction values. Repeated live execution-head reads throughout recovery show c4ea69f with no subsequent publication. Future updates require a nonforced expected-head lease; any competing change must be inspected first. Task3 COMPLETE at the tested implementation above; completion documentation is separate from the tested source. Next Task4, already authorized, in strict order.

### Task 4 IN_PROGRESS — current read/projection RED

- BASE `5458a2a2df6f19c6c9efbed2348ce6fdd0ca3532`, Task3 completion; accepted runtime remains c4ea69f/tree2a0bd56/run39354826027. No Task1/2 work restarted. Local Task3 contracts/privacy verification:27 passed; no local real-service success claimed.
- Added public DTO allowlist/defensive-copy, missing fresh authority and bounded reconciliation unit contracts; actual local run:3 failed at explicit missing marketplace contract/reader/composition assertions, zero errors. Added real PostgreSQL current-read matrix for damaged projection, withdrawal, already-receipted initial scan, flag off/missing, source edit, account inactivity, expiry without counter change, identity revocation, staff hide and repository failure. Hosted RED remains pending; no Task4 production code or schema in this checkpoint.
- Current managed environment has no Docker; mandatory real-service evidence continues through authorized hosted Actions. A separate workspace-local Python3.13.15 environment avoids the default interpreter path becoming unavailable; dependencies remain frozen and lockfiles unchanged. No mock substitutes for PostgreSQL/MinIO/scanner/worker acceptance.

### Task 4 — initial current reader and durable projection candidate, not accepted

- Hosted RED source `91adce6c011d83fc988d127382dc213af344ba72`, run `39377389046`, PostgreSQL `118478481357`:204 passed/13 failed, errors/skips/xfail/xpass/deselected0, exit1. Ten failures are explicit missing-boundary assertions after actual C03 publication setup; three are absent model/module imports, recorded separately rather than called behavioral assertions. The published existing implementation did not supply the new reader/DTO/scan.
- Added marketplace derived projection/location tables and separate restricted refresh hash/due state; leased UUID-keyset initial scan plus bounded dirty work; no private backfill or public route. Current reads construct only from the exact current confirmed source, C03 verified-role intersection and validated selected ready media, independent of projection JSON. Sorted User anchors precede per-profile/source locks; buffered serialization/render callbacks run under those locks with a fresh final source/expiry recheck. No decoder/scanner/store/broker I/O under these read/refresh locks.
- Composed existing account/profile/verification/cleanup/publication metadata handlers with ID-only durable due writes, preserving inherited effects/results/receipts. Extend the existing private Beat with a projection task; C02 outbox Beat stays exact. Privacy inventory includes owned finite projection/due/location records without content or private digests. False flag keeps scanning/purging. No domain imports from marketplace into private source authority or reverse imports into upstream domains.
- Actual unit RED: a swallowed flag repository OperationalError returned disabled instead of propagating unavailability (1failed). Extend the existing fresh governance flag reader with an opt-in raise_unavailable argument; defaults preserve inherited fail-closed behavior, while the public composition maps repository failures to content-free MarketplaceUnavailable. No parallel flag cache/policy. Four additional actual DTO REDs admitted nested biography/specialty/location data or boolean experience; finite typed public DTO validation now rejects them. Focused projection contract run8 passed.
- Added real PostgreSQL tests for fresh roles/restriction removal, stale derivative copy, final timestamp recheck, refresh/revoke commit orders, opposite multi-owner requests and privacy inventory. Extended actual service probe with production projection worker, real broker stop/withdrawal/current-read denial and restored broker/Beat purge. These new real-service paths have NOT yet run; no worker/recovery GREEN claimed for Task4.
- Added three direct SQL tests for private snapshot fields, foreign publication binding and generation rollback. Their real PostgreSQL RED is pending; this initial Task4 migration deliberately has not yet implemented those guards. Public reads never authorize through these rows. Task4 cannot complete until the SQL probes, required race/expiry matrix, actual worker/broker checks, full exact-SHA hosted manifest and source/security review pass.
- Ruling: extend only current-stage scope/schema/schedule allowlists with the four exact approved marketplace models and one exact additional Beat task, retaining all upstream negative import mutations, absent C05+ surfaces and immutable original C03 acceptance. Add a separate mandatory marketplace mypy step; normalize only that exact additive step in the inherited-job equality test, keeping every original executable command unchanged. Cost if wrong: inherited/current full CI fails, so no task advancement. No immutable baseline bytes or original ci.yml changed.
- Local validation so far:256 focused units+37 subtests pass; mandated existing mypy succeeds for100 files. New marketplace mypy initially flagged the same unstubbed Celery import already handled explicitly elsewhere; use the identical import-untyped annotation, with a separate mandatory ten-file marketplace check. Django system check and generated migration drift check pass (no local PostgreSQL history availability is claimed); frozen npm install, Tailwind and ES syntax commands pass. Full local unit attempt:839 passed/28 failed/37 subtests;17 were missing initial C01/C02 fixture probes, then exact fixtures were restored and20 relevant fixture tests passed;11 are inherited native decoder/isolation unavailable cases. They remain unchanged and must pass on hosted nonroot/native services. Further full validation is pending.
- Task4 IN_PROGRESS. Tasks5–11 not started. No SQL/service/full-hosted acceptance or task completion is inferred from these local checks.

### Task 4 — three actual PostgreSQL guard REDs and account fixture diagnosis

- Candidate `8edaaaf7bf31307dc661b55286ceacab311bc784`, tree `546c9b653d6e5e18cdaecec20b5b44a980cb2ac5`, run `39378882587`, PostgreSQL `118483144184`:231 passed/4 failed, all error/skip/xfail/xpass/deselection categories0, exit1. Three failures reach the direct SQL rejection assertion at test177: unknown private snapshot field, unrelated publication UUID, generation rollback all accepted. This is actual behavioral SQL RED, not an import/fixture error. The fourth failure reaches User.save at test112 before the read assertion; its IntegrityError is explained by existing account_state_active_consistency: active state cannot carry is_active=false.
- Add a guard in still-unaccepted marketplace migration0001, reusing the existing exact public-snapshot SQL validator, requiring profile/publication/revision/source-version/slug bindings and nondecreasing refresh generation. No index row authorizes release; damaged but allowlisted public text remains a tested input which the current source reader ignores. No accepted migration edited. Actual SQL GREEN remains pending.
- Correct only the failing account scenario to use the existing internal transition_account_state command with suspended state and synchronous session invalidation, preserving its current-read/tombstone assertions. Add pending_deletion through the same actual command; no account constraint is relaxed. This is fixture correction, not evidence that the initial account denial assertion executed.
- Added explicit credential-date expiry without any profile counter change, old publication event delivery after staff hide, and read/revoke barriers which verify actual pg_blocking_pids on independent PostgreSQL connections in both orders. Added a review regression for rebuilding a disposable projection while retaining its durable generation; its PostgreSQL RED is not yet observed and no speculative generation fix is included.
- After exact C01/C02 fixture setup and normal CSS build, complete local unit command reports856 passed/11 failed/37 subtests. Every remaining failure is in inherited test_image_sanitization:ten clean-pixel purpose/format cases and the isolation probe report unavailable in this managed host. No test was skipped/ignored/modified; hosted native acceptance is still mandatory. Focused CI/projection/media privacy45 passed; all ten new marketplace modules pass mypy; original mandatory command passes100 files. The complete hosted source/security/service manifest remains pending. Task4 IN_PROGRESS, Task5 not started.

### Task 4 — guard GREEN, actual rebuild RED and bounded-source review

- Source `238ea692bcdf13993d6c08439ab87a2e82f5209f`, tree `a0368c5fd3a2307263b112872bb7b8d1ddcaa2ff`, run `39379406335`, PostgreSQL `118484801065`:239 passed/one failed; errors/skips/xfail/xpass/deselected0, exit1. All three SQL guards, actual account transitions, role/date expiry, old-event latch, privacy and actual pg_blocking_pids read/revoke tests passed. Sole failing test is rebuilt disposable index generation at test218: public row deletion loses its generation even though retained refresh state still holds the prior value. Actual RED now observed. Refresh now locks that retained metadata under the existing owner anchor and advances from max(index generation, durable generation), with no caller-provided generation or stale snapshot authority. Actual PostgreSQL GREEN still pending.
- Source8ed actual media job `118483144257` also independently inspected:24 passed/all non-pass categories0; all original six media/worker/SIGKILL/scanner markers plus real_worker_refreshes_current_projection, real_broker_outage_withdrawal_denies_current_read, existing_beat_and_restored_broker_purge_withdrawn_projection; shell complete/exit0, natural supervisor0 and host/container cleanup complete. This focused older-source success cannot accept a later source change or the whole task.
- Review reproduced two more local REDs: the batch reader consumed beyond101 identifiers before rejecting a >100 batch, and the global scan cursor used a character primary key despite the approved UUID schema convention (2failed). Bound iterable consumption with islice101; use UUID primary key and unique finite cursor name in still-unaccepted migration0001. Projection unit contracts10 passed afterward; no migration drift reported, with unavailable local PostgreSQL history warning. No historical schema edited.
- Added actual PostgreSQL rejection tests for zero durable generation, zero cursor version and refresh-state identity rebinding. Their RED is pending; no speculative guards for those new cases included yet. New schema-valid task04-start.json preserves exact prerequisite, RED and SQL evidence; it explicitly claims no hosted acceptance and next_task4.
- A later local focused inherited run reports257 passed/one failure/37 subtests: unchanged test_required_service_unavailable_is_failure reached its20-second subprocess deadline before the inherited readiness verdict. Earlier exact local case passed after the explicit environment path setup; this later cutoff is not a demonstrated application defect or a proven transient cause. Do not change its bound/assertions; require its unchanged hosted execution to pass. Task4 remains IN_PROGRESS; Task5 not started.

### Task 4 — durable metadata RED and finite operations counters

- Source `59e5fe419189f978e3c7243ba0e3c071436ecd6d`, tree `b66bfd93cc210f016674eaeb39f71739dc8721d5`, run `39379947171`, PostgreSQL `118486539327`:242 passed/three failed, all non-failure non-pass categories0, exit1. Rebuilt projection generation now passes. All three failures reach test239's expected SQL rejection: zero refresh generation, zero cursor version and refresh profile UUID rebinding were accepted. Add explicit positive CHECKs and immutable/existing profile plus nondecreasing generation trigger on refresh state in the still-unaccepted initial migration. No pointer, counter or owner constraint was waived.
- Review found the required finite operational counters absent: actual local metric-contract RED1failed, then add content-free backlog (including missing projections), oldest due age, current failure, outbox exhaustion and per-scan purge counters. Another actual RED1failed for missing finite exhaustion alert; add only a constant warning event/dependency when exhausted work exists. Counts contain no profile IDs, content, hashes, provider errors or search criteria. Existing eight-attempt outbox exhaustion and audited staff retry authority stay unchanged. Local projection contracts12 passed; marketplace/composition mypy12 files success. Actual PostgreSQL metrics fixture and new-head worker execution remain pending.
- Added a direct flag-event delivery test requiring bounded global rescan intent while retaining the inherited flag effect/result. Initial/due scanning already purges with flag off, but explicit flag-event cursor invalidation has not yet been implemented or proven; its actual PostgreSQL RED is pending. Do not claim that test passed or task acceptance before implementing and verifying the event composition.
- Task4 remains IN_PROGRESS; require metadata SQL GREEN, current worker/broker recovery, all15 exact-SHA jobs, zero mandatory skips and final Task4 review before Task5. No public adapters, C05, merge or deployment.

### Task 4 — metadata and metrics GREEN; flag-event RED corrected

- Source `a1f5f677b6a3430cfc62d5e556995e47a2cfb68e`, tree `6f4bbcf317eeb4b3029bbd2dd1f7615aa0bc18ad`, run `39380769858`, PostgreSQL `118489135221`:248 passed/one failed, errors/skips/xfail/xpass/deselections0, exit1. All durable metadata guards and finite metric checks now pass. Only failure is test314: inherited feature_flag.changed returns applied but leaves the source-scan cursor advanced, proving the explicit C04 event effect is missing.
- Compose that existing handler with the same C04 due wrapper. For the marketplace flag only, persist a one-row cursor restart, increment its version and invalidate any earlier scan lease. The earlier scan's final cursor write requires its original lease and therefore cannot erase the new due intent; its per-owner work still reads current source. No unbounded projection update, User lock sweep, object I/O, changed flag authority or receipt rewrite. Other flags retain their independent behavior. Actual PostgreSQL GREEN remains pending.
- Strengthened initial-scan acceptance: a constraint-valid leased C03 profile event goes through the actual dispatcher and unchanged C03 metadata handler, producing an actual sent event and durable receipt; restore current handlers, then require C04 initial scan to discover the deliberately published profile without rewriting that receipt. This exercises the pre-C04 receipt boundary, not a fake broker/service acceptance. The actual worker/broker probe remains a separate mandatory gate.
- Local new-source checks: all C04 units161 passed+37 subtests; whole-tree Ruff/format500 files clean, Django system check clean, no generated migration drift, new marketplace/composition mypy12 files and original mandatory mypy100 files successful. Native/service/full exact-head hosted acceptance remains required. Task4 IN_PROGRESS, Task5 not started; no ordinary in-scope permission request is needed.

### Task 4 — close the post-restart broker proof gap before acceptance

- Source `ef9f0f01d0b990cc07c7101d826e9e6c21f52ff0`, tree `0e6784ddc20770139bac24afc739920a80e69350`, run `39381427186`, PostgreSQL `118491183827`:249 passed/all non-pass categories0/exit0/task4. Stronger actual C03 receipt dispatch/initial-scan test passes. Source media `118491183683`:24/all other counts0, all nine markers and complete/exit0, supervisor natural0 and owned cleanup complete; owner/staff/migrations/native/processing/storage/restart/history/timeout jobs also SUCCESS. Foundation and full current/immutable rehearsals still pending; not task acceptance.
- Distinct source review identified an Important evidence gap: projection_restored could see a tombstone produced by a task already in flight before the Redis restart. That proves fresh denial but does not prove delivery of a fresh post-restart broker message. Do not retrospectively claim the older marker proves that stronger condition.
- Strengthen only the real-service harness. After the shell restarts actual Redis, remove only the synthetic disposable projection and mark its durable source due; require unprompted worker reconstruction as a tombstone, without direct refresh. Then publish a newly generated task UUID through the actual broker, and require a worker task_postrun witness for that exact projection task UUID, SUCCESS state and zero failure result. The witness writes only an expiring UUID-keyed fixture marker to actual Redis; arbitrary/earlier/wrong/failed tasks cannot satisfy it. No application task/provider is replaced and no task content enters artifacts. Add constant restored_broker_delivers_unique_projection_task marker.
- Actual local witness RED:1failed at missing unique witness assertion. Unit adapter verifies absent proof key, failed result, wrong sender and wrong UUID do not mark completion; matching fresh successful task does. Seven focused harness/privacy tests pass; complete C04 unit suite162 passed+37 subtests afterward. This unit adapter is not real broker acceptance: the new actual hosted phase must execute. Existing90-second phase and900-second overall shell bounds stay unchanged; two bounded35-second observations fit within that existing phase.
- Application implementation remains unchanged. A complete new-head15-job manifest, including this stronger actual service proof, is still mandatory before Task4 COMPLETE. Task5 remains not started.

### Task 4 — final immutable-release SQL regression, RED pending

- Unique broker witness source is published as `655e7ac83b243eef5191bd2ebcd6e12173609d1a`, tree `a566f9e90a0069324476787a12b9d23f77beb67e`; actual hosted proof is pending, not inferred from its local162-pass unit result.
- Final source review noticed that the SQL projection guard verifies publication/profile/revision/source-version/slug ownership and typed public fields, but does not explicitly require the bound revision's owner confirmation. Application refresh already consumes only effective confirmed releases and direct reads ignore the index, so this is a storage-invariant probe, not a demonstrated public exposure. Add an actual PostgreSQL test attempting to bind an active projection to a new unconfirmed own draft, with all other source fields valid. Its RED is pending; no speculative SQL correction in this test checkpoint. Task4 cannot complete before this source invariant is proven.

### Task 4 — complete selection/filter SQL probes before final guard correction

- Extend the same final SQL review with confirmed-selection negative cases: adding an unselected public field, advertising a role not selected in that release, or adding a qualification summary absent from the confirmed revision. Also exercise actual PublicLocation rows with arbitrary private JSON modes, a broad city absent from the parent snapshot, and rebinding to another professional's nonpublic projection. Services already construct these rows solely from current confirmed snapshots; these tests check the approved database supplements and do not claim an existing public read leak. All six new actual PostgreSQL REDs are pending; no SQL implementation for them is present in this test checkpoint. Task4 remains IN_PROGRESS and no later task has started.

### Task 4 — seven actual selection/filter SQL REDs; final guard candidate

- Source `516ad12951f66375e3e712dad5c728f30d96f898`, run `39383706348`, PostgreSQL `118498461653`:250 passed/one failed/all other categories0/exit1; unconfirmed-revision binding reaches expected SQL rejection at test263 and fails because no exception occurred. No fixture/import error counted as RED.
- Extended source `4f58d247f1612a98f07aa3e88cb2d86645860a2d`, tree `75cad80d434eda43a370900d1aa111cfc2cdd77a`, run `39384381262`, PostgreSQL `118500595232`:250 passed/seven failed/all other categories0/exit1. The confirmation case reaches test263, all three selection cases test302 and all three actual owned broad-filter cases test345; every failure is the expected rejection not occurring after valid PostgreSQL setup.
- In still-unaccepted migration0001, require exact owner confirmation on the bound immutable release, identical selected field keys, role and qualification-summary subsets of that release. Permit harmless/stale selected text damage so the existing current-reader corruption tests remain meaningful; these rows never authorize release. Constrain filter rows to an active parent and the exact already-sanitized broad tuple in its snapshot, with immutable filter ID/parent/creation identity. No public field, claim, grant or consent category added. Actual PostgreSQL GREEN remains pending.
- Strong broker witness source `655e7ac83b243eef5191bd2ebcd6e12173609d1a`, run `39383337753`: PostgreSQL `118497273168`250 passed/all other counts0/exit0/task4; actual media `118497273575`24 passed/all other counts0, all original media/scanner/SIGKILL/Beat markers plus actual fresh UUID projection-task delivery after Redis restart, complete shell/exit0 and owned cleanup complete. This is actual provider/worker evidence, not its unit adapter. Later source still needs the complete exact-SHA15-job acceptance; no older-source green is substituted.
- No remaining Task4 source-review correction is planned beyond resolving actual new-head failures. Task4 IN_PROGRESS; Task5 not started.

### Task 4 — inherited populated-preservation metadata RED and bounded correction

- Run `39381427186`, job `118491183934`, failed at `populated_preservation` after SQL rendering, migration, no-op migration, drift and migration-list checks passed. Its mandatory aggregate rejected acceptance. This was not waived or classified as transient.
- Inspection found the current preservation checker derived expected added content types only from C03 apps. A focused behavioral test reproduced `AssertionError: preservation exact C03 content types` when the four actual marketplace models and their exact default permissions were added.
- Current-stage checker now enumerates precisely `publicprofessionalprojection`, `publiclocation`, `projectionrefreshstate`, `publicationscancursor` alongside existing C03 models. Added marketplace business rows are explicitly forbidden during upgrade. Original table OIDs, row values/counts, catalog identities, migration records and preserved sessions remain checked; immutable C02/C03 fixtures are unchanged.
- Focused GREEN: 12 tests, including rejection of future content types, altered permissions and automatic marketplace business rows. This diagnoses a reproducible mismatch; the actual hosted populated upgrade remains mandatory on the corrected implementation SHA.
- Task 4 remains IN_PROGRESS. No Task 5 work or acceptance claim.

## Task 4 — COMPLETE — exact hosted acceptance 2026-10-20

- Tested implementation: `0353c16bd8a4712134d27f19e3478ac9b385586c`, tree `88f5ab8e53f21caa90d923b645d6e21b3bf92bea`. Run `39385613444`, attempt 1: completed SUCCESS, all 15 mandatory jobs SUCCESS on that exact SHA. The completion documentation is not a separately tested implementation.
- Actual PostgreSQL and final cumulative gate: **261 passed each**, zero failures/errors/skips/xfails/xpasses/deselections, exit 0, `C04_TASK_ACCEPTANCE task=4`. This includes the seven real SQL rejection regressions, rebuild-generation continuity, flag rescan fencing, immutable DTO/source selection, ownership, timestamp expiry and actual independent-connection blocking/race proofs. Earlier REDs and all correction commits are retained above.
- Media job `118504613347`: 24 passed, all other outcome categories zero; all ten actual-worker/ClamAV/isolated decoder/SIGKILL/Beat/broker recovery markers, including unique post-restart task delivery. Natural return 0 and complete host/container cleanup. Artifact `12246774691`, SHA-256 `446c35a56686b1d75d196fec8687dcf0d99bef14fb3f59c19dcbe57b2f452c64`, independently downloaded/digest matched; four JSONL members/132 finite records, private journal absent.
- Current C03 final `118504613032`: all **130 stages exit 0**, including `populated_preservation`; full backend 1,955 passed, no failure/skip diagnostics, final rehearsal marker and cleanup. The earlier reproduced metadata mismatch is resolved by actual populated same-database verification, not a waiver.
- Immutable C03 baseline `118504612756`: all **127 original stages exit 0**, final marker and cleanup. Foundation `118504612959`: 876 unit tests + 37 subtests; static/type/build/production checks; 2,088 inherited runtime records, zero failures/skips, natural exit/cleanup. Owner/staff browser/API jobs: 75/67 passes, zero failures/skips. Migration/backend diagnostic counts 108/86/89 all zero failures/skips; original 269-test source controls passed. Storage, native (10 stages), processing, restart and intentional timeout ownership contracts all passed and cleaned up. Historical audit independently verified all 12 original tasks; it is not relabeled new C04 execution.
- Distinct inline source/security review inspected Task 4 diff, immutable source/confirmation boundaries, strict flag outage behavior, sorted owner locks and final time fences, absence of I/O under domain locks, DTO/hash separation, durable initial/due scan/lease invalidation, metadata-only handlers/tasks/metrics, privacy inventory, additive SQL guards and unchanged inherited executable CI invocations. No unresolved Critical/Important findings. This was an author review, not an independent reviewer or production audit; final whole-branch review remains mandatory in Task 11.
- Local focused verification: 235 tests + 37 subtests passed; Ruff/format and mypy passed. Host-only native/environment limitations were not substituted for required hosted services. All protected/completed-stage refs were independently re-read unchanged; live execution HEAD matched the tested candidate with approved plan and C03 handoff as actual ancestors. No merge, deployment, production publication or C05 change.
- Durable finite evidence: `docs/implementation/c04/checkpoints/task04-complete.json`; actual attempt-specific workflow/job identity, all runtime log digests, counts/stages/cleanup and media artifact binding pass `docker.c04_acceptance.validate_checkpoint`.

**Current durable state:** Tasks 1–4 COMPLETE. Tasks 5–11 pending, strict order. **Next action:** Task 5 behavioral RED for bounded Persian PostgreSQL search/filters and exact signed visible-only pagination; do not restart earlier accepted tasks.

## Task 5 — IN_PROGRESS — behavioral RED checkpoint

- Prerequisite Task 4 accepted implementation `0353c16bd8a4712134d27f19e3478ac9b385586c`, tree `88f5ab8e53f21caa90d923b645d6e21b3bf92bea`, run `39385613444` attempt 1; docs checkpoint `277b2f848b8269a2b861aa4d9fad1f0cd71c51eb`, tree `809fda9259f3beb10f807380c53196d166ada494`.
- New behavioral RED: 31 actual assertion failures in Persian normalization and bounded search-input tests against the unchanged Task 4 production behavior. Assertions explicitly identify missing normalization/search contracts; no import or infrastructure error is counted. Added real PostgreSQL tests require actual pg_trgm/two GIN indexes, fresh empty browse and denial of withdrawn stale candidates. The inherited cumulative gate still identifies installed Task 4 until Task 5 implementation wiring arrives; this bounded RED is not acceptance or a Task 4 regression waiver.
- Scope is exactly approved Task 5 normalization/FTS/trigram/filter/keyset/quota work. No public adapters/UI or Task 6 work. No new production dependency. PostgreSQL extension availability and realistic measured query plans remain mandatory; no local service substitution.

### Task 5 — hosted RED inspected; first bounded implementation candidate

- RED `edd25dbbaaf3b26347014c008e779932e642fd46`, tree `5ca4fa141a9497e00fee2549237f5c773791464d`; run `39391863193`, PostgreSQL job `118525050430`: 261 passed/34 failed, zero errors/skips/xfails/xpasses/deselections, exit 1. Exactly 33 missing-behavior assertions (31 unit plus absent actual pg_trgm and browse boundary); one withdrawal fixture used the pre-confirmation version and raised ProfileConflict. That fixture is corrected to read the actual current publication version and is not counted as behavioral RED.
- Additional observed local REDs: malformed unhashable role/mode + missing signed cursor (3); missing separate limiter (3); missing finite actual-plan evidence validator (1); query compilation failed because the inherited app list does not globally register the trigram field lookup (1). Fixed using explicit Django TrigramSimilar expression and parameter binding, without a new app/dependency or a string SQL substitute.
- Candidate implements `fa-search-v1`, immutable bounded SearchCriteria/PublicPage and 15-minute signed/hash-bound public-key cursors; current released-only indexed fields and filter rows; additive `marketplace/0002_persian_search` with actual TrigramExtension, frozen v1 populated projection backfill, weighted simple tsvector/trigram/filter/location indexes and SQL filter/version/experience checks. Accepted `0001` and all historical migrations are unchanged.
- Search selects at most 100 parameterized candidates, orders exact native quantized ts_rank_cd/similarity tiers/UUID, then renders only through sorted owner-locked fresh public readers. Current role/location/filter facts are checked again; stale/damaged normalized text cannot rank on facts absent from the current public DTO. No totals/facets or invisible cursor keys. Exhaustion persists bounded rescan intent and raises content-free retryable `projection_refresh_required`. SQL statement/lock timeouts are 2s/1s. Flag off has a distinct closed boundary for future uniform-404 adapters; repository failures stay content-free unavailable.
- Separate atomic Redis TTL/HMAC admission has 60 search/120 cheap-origin defaults, retained key material and existing canonical/trusted-proxy IP extraction; OTP quotas/schema remain untouched. This is the trusted internal search service plus request admission utility; public HTTP adapters and mandatory admission wiring are Task 8, not invented early routes. Real Redis race/TTL/subsecond/missing-TTL/unreachable-connection/recovery checks are installed, awaiting hosted execution.
- Actual PostgreSQL corpus/order/location/current-role/expiry/private-field/cursor/100-stale-candidate recovery and populated Task4→Task5 backfill probes are installed. The realistic 30,000-document EXPLAIN ANALYZE/BUFFERS probe uses a transaction-local candidate-index relation solely for planner measurement; it does not replace source authorization or supply any public output. Real domain-service corpus tests separately establish authority and expected order. It records measured cardinality, returned rows, index nodes, timings and buffer blocks through a finite numeric-only evidence hook; no SQL/queries/snapshots/plans are exported. No planner result is claimed before actual hosted execution.
- Local GREEN: 318 focused/current-stage tests + 37 subtests, mypy (17 source files), Django checks and no migration drift. Whole-tree Ruff/format passed. One earlier local inherited readiness subprocess hit its unchanged 20s deadline because uv was invoked without the recovered isolated environment variables and tried replacing the default environment; rerun with the correct existing isolated environment passed (317 +37 before the added compile regression, then 318 +37). No assertion, timeout or hosted gate was weakened. PostgreSQL is unavailable locally; schema/service/query-plan proof remains mandatory in hosted CI.
- Full 15-job manifest and inherited executable blocks remain intact; C04 cumulative entrypoints select installed Task 5 and require exactly one passing finite actual-plan measurement in PostgreSQL/final gates. Task 5 remains IN_PROGRESS, all hosted candidate evidence pending. Tasks 6–11 are not started.

### Task 5 — collection harness correction and retained ownership refusal

- First implementation candidate `4dca2b50da9b33bcddca5efab9debeee1edde1a6`, tree `953ad54c23ca0ad1604d150b35099fc0f8854b0e`, run `39394356100`: PostgreSQL `118533271788` stopped in collection (0 passes/0 failures/1 error, no skips); it is not a behavioral service result or acceptance. Reproduced locally: the new unit and integration `test_search_limiter.py` basenames collide under the inherited pytest import mode. Renamed only the new unit file to `test_search_limiter_contract.py`. Combined C04 collection now discovers 335 tests without error; no test was omitted, deselected or relaxed.
- Inherited restart `118533271529` refused before starting its child with `fresh_runner_ownership_unavailable` after 2s. Artifact `12251091240`, SHA-256 `03882912e83598ab1b67994bd8b70710dabe6878e84f57efb64e2965a0a43fb8`, retains that original evidence. Existing output cannot distinguish failed bounded Docker inventory from a pre-existing owned-project collision; no retrospective cause or transient classification is claimed, no foreign resource was touched, and the gate was not waived.
- Three observed diagnostic REDs proved missing baseline-availability/conflict distinction and missing timeout metadata. Current-source diagnostics now add only finite baseline availability, enumerated conflicting owned-project names and existing sanitized metadata-query failure records; metadata timeout/unavailable categories contain no raw command/error content. Refusal, 2s query deadline, observation windows, child ownership and cleanup behavior are unchanged. Immutable C03 source remains unchanged. Focused GREEN: 13 tests, including existing ownership/cleanup/privacy tests. A new hosted exact-SHA run must execute the restart contract naturally and the complete PostgreSQL corpus/actual-plan checks before acceptance.
- Task 5 remains IN_PROGRESS. First real-service/query-plan execution of the corrected cumulative selection is the next pending requirement. No Task 6 work.

### Task 5 — first actual service/query-plan GREEN; surviving-role expiry review RED

- Corrected source `9e64983c6c7fc76021a70d461e5e249708c08acf`, tree `63619713299c17ba83037a70c715a310f6cc0010`, run `39395186979`: PostgreSQL `118536059174` executed 333 passed, zero failed/errors/skips/xfails/xpasses/deselections, exit 0. Actual 30,000-row EXPLAIN ANALYZE/BUFFERS measurement: 10 returned, 2 index nodes, planning 0.641 ms, execution 4.814 ms, 441 buffer blocks. This is real measured planner evidence, not an authorization substitute.
- Restart `118536059898` on that same source exited naturally 0, full host/container cleanup. This independently proves the current restart gate; it does not retroactively identify or waive the earlier refused inventory/collision.
- Source review found one further mandatory freshness case to prove: the candidate query excludes rows at cached earliest `next_expiry`, which may suppress an unchanged still-current Coach when only the Nutritionist credential expires and the worker has not run. New real PostgreSQL test first establishes current C03/Task4 Coach-only authority, then requires Coach discovery and Nutritionist denial at the same UTC boundary with unchanged profile version. Production search is unchanged in this RED checkpoint; no result is assumed before hosted execution.
- Local executor transport disconnected before the attempted test-edit result and did not recover on a bounded read-only probe. No unpublished edit is claimed recovered or applied. All previously verified implementation is published. Continuing via user-authorized GitHub source writes and real hosted verification; new test source was reconstructed from exact published files. Local formatting/compilation is not claimed for this checkpoint; hosted quality/collection remains mandatory.
- Task 5 remains IN_PROGRESS. Tasks 6–11 are not started.

### Task 5 — real surviving-role expiry RED and bounded source correction

- Test-only `c7b8944dddc655852d66d1267fa9dbc80d6e3937`, tree `fab53895507e95a41176a02f7eb8d2da9a867031`, run `39396025416`, PostgreSQL `118538855244`: 333 passed, exactly 1 assertion failed, zero errors/skips/xfails/xpasses/deselections, exit 1. The failure is `test_expiring_one_role_without_worker_preserves_other_current_search` at the Coach result assertion, after the actual current C03/Task4 reader already proved Coach-only authority at the unchanged-version UTC expiry boundary. Fixture setup and all other search/service/plan cases passed.
- Diagnosis: `next_expiry` is the earliest selected-role boundary, not whole-profile authorization. The query's cached row-level cutoff dropped the still-eligible Coach before fresh revalidation. Removed only that coarse cutoff. Active/version/criteria prefilters, native deterministic ordering, parameterization, 100-candidate maximum, 2s/1s SQL/lock limits, current per-role/source/flag checks, visible-only cursors and bounded refresh-required behavior remain intact. Current authority decides expiry for every candidate; due scanning still uses the retained boundary to refresh.
- No acceptance is borrowed from the previous 333-pass source or the RED run. The corrected source requires fresh hosted surviving-role GREEN, actual measured query plan, real media/restart/cleanup and all 15 mandatory exact-SHA jobs. Local executor remains unavailable, so local execution/formatting is not claimed; authorized hosted quality and service gates control this candidate.
- Task 5 remains IN_PROGRESS. No Task 6 work.

### Task 5 — mandatory immutable-browser failure; diagnostic RED

- Candidate `5040ec5052b6ce064e7306f82f4ad9fb0d250966`, tree `15027a986697a0daa565f79b7e911dbc0b522dd3`, run `39396940944`: corrected PostgreSQL `118541884214` passed all 334 with zero failure/error/skip/xfail/xpass/deselection and Task 5 marker. Actual plan: 30,000 rows, 10 returned, 2 indexes, 0.603 ms planning, 4.566 ms execution, 441 blocks. Media `118541883929` passed 24/all other categories zero, all ten real worker/scan/SIGKILL/Beat/broker markers, natural exit/cleanup; restart `118541883899` and migrations `118541883478` passed naturally with cleanup. These focused results do not authorize completion.
- Mandatory immutable C03 baseline `118541883751` FAILED at `clean_staff_browser`: 27 passed/1 failed/no skips, node `tests/e2e/c03/test_staff_verification.py::test_decision_reload_single_effect`. Prior original stages passed, including full backend 1,692, focused 38 and owner browser 10. Original fixture remains exact C03 `0a867328a6d8ee8c71ec9bd9eeb8910221d1b270`, tree `5c294cb330cf08b297cc01c8baa27adb1e6b93b7`. Baseline metadata artifact `12253842855`, GitHub-reported SHA-256 `a334b8fe91d68e653bfdba263913486ed48260e4169687c5dbb1b0396090a2a7`, preserves the failure.
- The published original finite diagnostic has no assertion location or underlying exception detail for this browser failure. Private raw stage logs are not available after that runner ended; no detail is invented or claimed recovered. No transient classification, retry-to-pass, fixture edit, skipped case or waiver is accepted.
- New diagnostic RED tests require the current outer observer to extract bounded known repository source locations and finite browser operation/error/network enums, rejecting payloads/locators/private paths. After their hosted RED, the observer can inspect only the existing known private browser stage logs before the next runner ends, without printing/uploading those logs or altering the original verifier invocation, tests, assertions, timing or single execution. A fresh exact-source complete original baseline remains mandatory.
- Local executor remains unavailable; use the already-authorized GitHub/hosted verification path. Task 5 remains IN_PROGRESS; Task 4 remains the last accepted task. Tasks 6–11 are not started.

### Task 5 — outer browser-diagnostic RED inspected; bounded observer installed

- Diagnostic RED `9ffe8efb30cab33152b0616ae7e30d9d6dd42fd1`, tree `73f0c00c58278267212c8df8deedb03aaf883757`, run `39401186561`, Foundation `118556008893`: 924 passed +37 subtests; exactly two AssertionErrors in the new observer tests, explicitly `Missing finite immutable-browser failure metadata`. No import/infrastructure error is counted as that RED.
- Current outer observer now reads only four existing known private browser stage logs, at most 4 MB tail each, after the original verifier exits. It emits at most 12 source locations per stage from known original-repository Python paths, fixed error/browser-operation/network enums, or an explicit metadata-unavailable boolean. Raw logs, locators, messages, credentials, captures, URLs, private paths and payloads are never printed/uploaded. The two RED cases cover unknown/private text rejection and location-count bounds.
- The immutable fixture and original tests/assertions are untouched. The exact `subprocess.run(["sh", "docker/verify_c03.sh"], cwd=baseline)` invocation, single execution, source pin, exit propagation, timeouts, service selection, screenshots/tracing prohibition and cleanup remain unchanged. Existing exact-command/exit tests remain mandatory and unchanged. This is diagnosis, not a retry-to-pass or acceptance waiver.
- Historical failure `118541883751` remains preserved and its underlying detail remains unknown. This candidate must pass new diagnostic checks and every original baseline case naturally; if failure recurs, inspect the newly available finite source/operation metadata before any further action. Full exact-SHA 15-job acceptance remains mandatory. No local execution is claimed while the local executor is unavailable.
- Task 5 remains IN_PROGRESS; no Task 6 work.


### Task 5 COMPLETE — exclusive takeover acceptance — 2026-10-20

User confirmed the previous executor stopped and authorized this session as sole
writer. Independently fetched live HEAD9609f7a009a416100b67e1fde985b227900ecb7e,
tree9bcda8c22f9880bcb591cd49952e645145cd225f, approved unchanged plan/blob and
actual ancestry; no later publication on repeated live reads. Separate recovery
clone preserves published history. Automated pruning removed the earlier scratch
checkout; no absent unpublished state is claimed recovered. Tasks1–4 checkpoints
are preserved and were not restarted. Protected completed/planning refs match the
recorded values. Further publication uses nonforced expected-head leases.

Run39402163393 attempt1 independently read: exact push/ref/path/head/tree,
all15 mandatory jobs and every listed step SUCCESS. All fifteen logs inspected,
with log SHA256 and exact identities retained in task05-complete.json.
- PostgreSQL118559260758 and final118579216470: each336 passed; failure/error/
  skip/xfail/xpass/deselection all0, actual0, installed Task5 marker, no migration
  drift. Real pg_trgm/Gin, corpus expected order/variants/weights, paired location,
  OR/AND filters, private field denial, role restriction and unchanged-counter
  expiry (including surviving Coach), visible cursor pagination and stale100-row
  budget/catch-up, populated0001→0002 backfill and real Redis concurrency/TTL/
  connection-loss/recovery cases executed.
- Actual EXPLAIN ANALYZE/BUFFERS over30000 candidate index documents:
  PostgreSQL10 returned/2 index nodes/0.601ms planning/4.131ms execution/441 blocks;
  final10/2/0.633ms/5.025ms/441 blocks. These measure the indexed candidate query
  on the documented temporary index relation, not30000 independently authorized
  professionals or Task10 end-to-end load. Separate real-domain corpus proves
  publication authority and expected ranking; no privacy substitute.
- Real media118559260803:24 passing, all other counts0, ten actual media/projection/
  broker/Beat/scanner/SIGKILL recovery markers, natural0/complete cleanup.
- Foundation118559260812:host926+37 subtests, runtime aggregate2163/0/0,
  natural0/owned cleanup. Counts are reporter aggregates, not distinct functions.
- Original immutable baseline118559260364:127 stages all0, backend1692,
  final_rehearsal_passed after cleanup. Current full118559260904:130 stages0,
  backend2030, final_rehearsal_passed/cleanup. Original source/tests unchanged.
- Owner118559261000:75; staff118559260925:67; inherited PostgreSQL118559260783
  Tasks8/9/10 counts108/89/86; storage118559260898, processing118559261050,
  restart118559260829 all natural0/cleanup. Native118559260942 recorded stages0.
  Timeout118559260762 preserves intentional child deadline with successful
  supervisor ownership/cleanup. Historical118559260864 verifies12 prior tasks.

All13 available artifacts downloaded; every SHA256 independently matched provider.
Finite reports contain no nonpassed test reports or nonzero pytest exits.
Baseline12258052330 digest1052aacdddc573aa16646940ecb670afc310316eaadcdf00af55e7f6281a48ff;
full12257669493 digestde0260593a576c1a64348f92cdbd6e9c048ed7b905f949650e98015e2c8923c3;
media12255536160 digest9c5dfc5f98f20c7032baa8e526638126019b85f84c113169470eb312fdf4e0b1.
Full artifact bindings are in the checkpoint. Historical baseline failure and
ownership refusal remain unknown-cause failures as recorded; fresh complete
current-head success does not retrospectively classify or erase them.

Distinct takeover author source/security review of the seven Task5 commits and
current implementation checked frozen normalization/versioned additive backfill,
weighted simple/parameterized FTS+trigram/quantized deterministic keysets, bounded
criteria and signed criteria/time/page-size cursor, current sorted owner-locked
revalidation/role intersection/final time fence, no counts/private keys in paging,
100-candidate/2s statement/1s lock bounds, committed refresh-required recovery,
HMAC/atomic TTL/closed quota behavior, preserved OTP semantics, no I/O under domain
locks, migration guards and narrow finite diagnostics. No unresolved Critical or
Important Task5 finding; author review, not independent final whole-branch review.
HTTP admission integration remains approved Task8 scope, no early adapter added.

Local focused C04 unit recheck216 passed+37 subtests, zero failed/skipped,
9.23s with exact immutable C03 fixture. Installed validate_checkpoint accepts the
complete exact-source record. Docker unavailable locally: all mandatory real
services are the independently inspected hosted executions above. No mock/skipped
service substitutes or new implementation changes made during takeover acceptance.

Task5 COMPLETE at tested9609f7a/tree9bcda8c above. Completion docs are separate
from accepted implementation authority. Next Task6 already authorized, strict
order; no Task7+ start before preceding acceptance, no merge/deploy/C05/live flag.


## Task 6 — IN_PROGRESS — selection behavioral RED

BASE edd6b30081a7b62ef1a38ec06721ccdba7829588; prerequisite Task5 accepted at
9609f7a/tree9bcda8c, run39402163393 attempt1. No prior task restarted.

Actual local behavioral RED:17 assertion failures in test_selection_inputs.py,
all explicitly Missing bounded selection contracts, not import/fixture/service
errors. No production selection implementation exists in this checkpoint.
New PostgreSQL/session tests cover current owned-athlete favorites, idempotent
receipts, unrelated/revoked users, invisible favorites, three-item cap, duplicate
entries/replay, separate visitor sessions, flush revocation, authenticated-session
denial without visitor fallback, and flag-off private clear. Additional actual
concurrency/SQL/session-switch proofs remain required before acceptance.

Ruff/format pass on these four new test files. Existing cumulative runner still
identifies installed Task5; its collection of these missing Task6 behaviors is
RED, not Task6 acceptance. Full hosted Task6 acceptance will require installed
Task6 entrypoints, real PostgreSQL concurrency and all fifteen mandatory jobs.
Next implement only approved owned/session selection boundaries after RED.
No Task7, public adapters, merge, deployment or production enablement.


### Task 6 — hosted behavioral RED; first bounded owned-selection candidate

- Test-only9b6779a0fff06282150b9e74f576228ddc07e6fe, run39433356334,
  PostgreSQL118663865773:336 passed/26 failed, error/skip/xfail/xpass/deselection0,
  exit1. Seventeen contract assertions and nine owned/session-boundary assertions
  identify missing behavior; actual PostgreSQL existing cases and fixtures pass.
  Foundation expected missing-contract failures are not an inherited waiver.
  Native job failure in the RED run still needs finite evidence classification;
  no cause or transient classification is inferred.
- Candidate introduces private Favorite/ComparisonCollection/ComparisonEntry and
  separate immutable operation receipts, no stored public names/media. SQL enforces
  unique favorite, collection owner XOR session digest, unique target/slot and
  slot1..3, immutable ownership/receipt/entry identity, positive collection version.
  New0003 additive migration only; historical migrations unchanged.
- Marketplace services receive trusted composition callbacks. Current AccountActor
  and existing own-athlete selector are required, without profile activation.
  Visitor scope derives from server DB session secret plus HMAC bound to session
  key/key-id; every read/write checks current unexpired DB session. Invalid
  authenticated sessions cannot become anonymous. Existing login/logout/session
  flush separates visitor/account selections; no merge/client scope IDs.
- Sorted caller/target User anchors precede collection locks; visitor session lock
  precedes collection lock. Changed entry hints deny rather than lock a new owner
  out of order. Collection row lock plus SQL slots enforce concurrency cap.
  Current public readers revalidate every returned target; inactive targets
  contribute no name/media/hidden count. Current caller/session authority is
  checked again after buffered render to enforce timestamp expiry.
- Remove/clear remain account/session-authorized with flag off; additions require
  current public eligibility. Replayed receipts do not grant stale target content.
  Anonymous CSRF enforcement and 30/min selection HTTP admission are installed
  with actual adapters in approved Task8; no public route exists here.
- Added actual PostgreSQL final-slot concurrency, direct SQL cap/XOR/ownership/
  receipt tests and real DB-session expiry/login/account-switch tests. These are
  awaiting first real-service execution, not claimed GREEN locally.
- Local contract GREEN17; combined C04/current-scope/account-policy246+37 subtests,
  no failures/skips. Whole-tree Ruff/format, Django check and mypy22 sources pass;
  no migration drift. Local PostgreSQL/Docker unavailable, so no SQL/concurrency
  GREEN claimed. Existing exact-scope/upgrade metadata controls initially failed
  on precisely the five new models; narrowly extended their current-stage allowed
  names only. All preservation/future-domain negatives and original baseline stay.
- Installed cumulative runner/workflow now select Task6, render0003 SQL and retain
  all15 inherited/media/full jobs. Full hosted exact-source proof, remaining
  adversarial/privacy inventory and security review are mandatory before COMPLETE.
- Ruling: private favorites listing bounds candidates to100 and fails closed on
  larger lists, preserving private removal access — uses approved shared bounded
  public-reader maximum; cost if wrong: paging must be added before large-list UX
  acceptance. No record/content is silently truncated or deleted.
Task6 IN_PROGRESS; Task7+ not started. No merge/deploy/production publication.


### Task 6 — adversarial ownership/inventory review RED checkpoint

Author review identified two further cases to prove before acceptance: all five
new owned selection record kinds must appear in the private owner inventory
without any visitor-session capability; a forged AccountActor must be rejected
before a hidden favorite-candidate count can affect the response. Added actual
PostgreSQL cases establishing these states through real selection commands/direct
bounded synthetic rows. Production implementation is unchanged in this test-only
checkpoint; neither defect is assumed proven before actual hosted execution.

First implementation sourcee4d94129ad5796293960b5994bb365687e8cefdf,
tree d2637fdb2c5b7396463ac64ef0c86909c177c2e8, run39434763002:
owner118668746573 refused before child startup after2.0s; finite metadata proves
baseline_available=false with docker ps -aq metadata_command_timeout, no reported
conflicting project. No application/browser test ran. This is a mandatory failed
gate, not a transient classification, retry-to-pass or waiver. PostgreSQL/full
other candidate results remain pending at this checkpoint. No service assertion,
ownership refusal, deadline or cleanup contract changed.

Both review cases require actual behavioral RED then a bounded source correction
and complete new-head acceptance; Task6 remains IN_PROGRESS. No Task7 start.


### Task 6 — read-only selection contract review probe

Added test_read_of_empty_comparison_does_not_create_selection_collection.
Approved Task8 adapters cannot let GET mutate selections; the core reader must
therefore return an empty version1 view without allocating a selection collection.
This test-only checkpoint leaves production unchanged and requires actual hosted
RED before correction. Earlier ownership/inventory review probes remain selected.
Task6 stays IN_PROGRESS; no Task7. Local static build succeeds; full local unit
suite is being inspected, and cannot substitute for real service evidence.


### Task 6 — actual review REDs and bounded corrections

- Coree4d9412 run39434763002 PostgreSQL118668746868:368 passed, all non-pass
  categories0, exit0, actual Task6 marker; measured30000-row plan10 results,
  2 indexes,4.042ms execution/441 blocks. This proves initial SQL/session/
  concurrency cases, not task acceptance: owner118668746573 failed its2s
  Docker inventory boundary before application tests, as recorded.
- Review-onlyac675a3fba61e786b8f07465680b675777b3c69b run39435124778,
  PostgreSQL118670016882:368 passed/exactly2 failed, errors/skips/xfails/
  xpasses/deselections0, exit1. Inventory test reaches real owned selection
  creation and fails missing five selection kinds. Forged actor test reaches
  _favorite_ids and raises MarketplaceUnavailable on101 private hints instead
  of PermissionError, confirming authorization happened too late.
- Read-onlydd3606497ac09bb77e0cfb34a4a356f438c67568 run39435506219,
  PostgreSQL118671325597:368 passed/exactly3 failed, other categories0, exit1.
  Same two defects plus empty comparison reader creates selection collections
  (test_comparison.py135). These are actual behavior failures after successful
  fixtures/current owned commands, not missing services or import errors.
- Corrected inventory to include all five account-owned selection kinds through
  bounded exact-owner queries, cumulative existing1000-record ceiling, no target
  snapshots/session secrets/digests. Classified as private account-selection
  metadata with existing retain-only default; no legal duration, new hold
  authority or destructive erasure policy is invented.
- Added nonlocking current AccountActor preflight before favorite hint inspection.
  It grants nothing: sorted locks and current account/athlete checks still repeat
  inside the authoritative domain transaction. Invalid actors now deny before
  hidden hint bounds can affect output.
- Reader no longer creates ComparisonCollection: an absent authorized collection
  yields empty version1. It rechecks after owner/session locks; a concurrently
  changed hinted set conflicts instead of rendering unlocked targets. Only
  commands create/mutate selection records. Server session scope metadata is
  separate from selection state. Existing final current-session/time checks stay.
- Added characterization negatives for forged visitor digest/no collection
  allocation, changed favorite payload/operation conflict and duplicate SQL target.
  All assertions retained; new real-service GREEN is required on this source.
- Local final focused246+37 subtests passes, zero failures/skips8.49s; whole-tree
  Ruff/format531 files, mypy22 source files, Django checks pass. Full local unit
  run additionally observed931+37 passed/12 failed: one inherited readiness
  subprocess exceeded20s because uv lacked this isolated environment's path
  variables; exact same test with correct environment passed1/0 in0.65s.
  Eleven inherited native decoder/isolation cases remain unavailable locally
  (ten clean raster parameter cases and isolation probe); images/decoder bytes
  equal original C03. No local full GREEN or isolation PASS is claimed, and no
  assertion/isolation/deadline was weakened. Mandatory hosted isolation remains.
- Task6 IN_PROGRESS until these corrections pass real PostgreSQL and the complete
  new-head15-job manifest, cleanup and distinct source/security review. Task7+
  remain NOT_STARTED. No merge, deployment, production enablement or C05 work.


### Task 6 — real review GREEN; narrow current-stage schema correction

- f5c903bdd5b96d319feeb5173dbe001a21e5154d/tree58842c727283757f8bc6141ee8f2aa791e8cbd73,
  run39437434939 PostgreSQL118678080183:373 passed, failed/error/skip/xfail/
  xpass/deselection0, actualexit0, Task6 marker. All three reproduced review
  defects and additional scope/receipt/SQL negatives now GREEN on real PostgreSQL.
  Actual plan30000 documents/10 returned/2 indexes/4.669ms execution/441 blocks.
- Mandatory inherited migrations118678080091 failed naturally1 with cleanup.
  Actual first assertion: current-stage test_no_c04_or_c09_database_surface,
  test_c03_dependency_direction.py48. Its four-table Task4 exact set rejects
  the five approved Task6 selection tables. Task8=108/0/0, Task9=89/0/0,
  Task10=85passed/1failed/0skipped, focused38 pass. No service outage or product
  selection failure is inferred; this is not complete task acceptance.
- Ruling: extend only the current-stage marketplace table set by the exact five
  approved Task6 names, retaining exact equality and every future-domain/import/
  professional-index/no-auto-copy assertion — matches installed0003 schema and
  approved narrow current-stage adaptation contract; cost if wrong: full inherited
  migrations and immutable baseline gates must reject the candidate.
- Added a pure schema-guard mutation control: actual local RED1 explicit
  Missing exact current-stage selection schema guard assertion; GREEN accepts
  exactly nine approved tables and rejects each missing member or an extra
  marketplace_private_directory table. Existing actual PostgreSQL assertion still
  introspects the real installed schema. Original immutable C03 bytes/tests and
  inherited workflow commands are unchanged. No assertion was removed or skipped.
- Local focused247+37 subtests passed, zero failures/skips8.06s; whole-tree
  Ruff/format532 files pass. No migration or production code changes in this
  correction. New-head inherited SQL and all15 hosted gates remain mandatory.
Task6 IN_PROGRESS; no Task7 or later implementation. No merge/deploy/C05/live release.


### Task 6 — schema GREEN; mandatory immutable prerequisite failure diagnostics

- Source5b9d4c638dc5076d0fca381150cd3363e9bfdfc8/tree66ec32d3a29025df7ce03a762e2cfaf474874c63,
  run39439640428: PostgreSQL118685792325 **374 passed**, all other categories0,
  exit0/Task6. Measured30000-row plan10 results/2 indexes/4.86ms/441 blocks.
  Inherited migrations118685792113 naturally0/cleanup, Tasks8/9/10 counts
  108/89/86 all0failed/0skipped; exact nine-table correction is real SQL GREEN.
- Mandatory historical audit118685792206 verified ten earlier tasks then recorded
  historical_http_error HTTP502, endpoint_family=actions, and HTTPError failure.
  Artifact12272969991 digestc55ba26edc416bbeb00925e6e638519fbd127546a5f1af48792a65ceaefe4d25
  independently downloaded/matched. This is observed external API failure, not
  acceptance. No same-SHA retry used; policy would allow one evidence-backed retry
  after terminal status, but the separate unknown baseline failure does not
  justify a retry-to-pass of the whole run.
- Mandatory immutable baseline118685792403 failed exact_original_c02 exit1.
  Original C03 tree5c294cb330cf08b297cc01c8baa27adb1e6b93b7 verifies; its finite
  original diagnostic has no exception/count/location/infrastructure detail.
  Outer original-C02 metadata also has empty npm/categories. Artifact12274616510
  digestaab4dfc7a7aeb2d09e32a1be480c4b0e2ac32c2483ad432658fd248239ff6bda
  independently downloaded/matched. Private raw logs ended with that runner;
  none are recovered or invented. No transient classification, blind retry,
  assertion waiver or claim of original-baseline success.
- Actual local diagnostic RED7 asserts missing finite prerequisite classifier.
  GREEN12 includes those privacy/category/location bounds plus unchanged observer
  exact-invocation/single-execution/exit17 propagation and browser privacy tests.
  Current outer observer now inspects only the existing exact_original_c02 private
  log, bounded4MB tail, with fixed infrastructure categories/last-phase enums and
  twelve known-original-repository source locations/finite error/browser enums.
  It prints no provider text, commands, locators, URLs, credentials, payloads,
  private paths or raw logs. Marker presence is diagnostic evidence, not a causal
  verdict or success condition. Existing npm classifier semantics are unchanged.
- The original subprocess.run(["sh", "docker/verify_c03.sh"], cwd=baseline),
  one execution, return code, immutable source, tests/assertions, timeouts, service
  list and cleanup remain unchanged. No fixture or original verifier was edited.
  This is an authorized bounded observability correction after a mandatory
  evidence failure; new-head full original acceptance remains required.
- Local focused254+37 subtests passes with zero failures/skips7.78s; whole-tree
  Ruff/format533 files pass. No production selection/schema changes in this
  diagnostic checkpoint. If the prerequisite fails again, inspect its finite
  evidence before any further action; no automatic retry of an unclassified cause.
Task6 IN_PROGRESS. Task7+ NOT_STARTED. No merge/deploy/C05/production publication.

### Task 6 — immutable baseline GREEN; measured full-backend deadline RED

Exact source e750f26807c17d371a813cc776cda6514a344e6c,
tree7ffa943e290791d1d760a78fce4a2753c5545acc, run39442164342 attempt1:
13 jobs GREEN; c03-final118694553646 FAILED and aggregate118716425907
correctly FAILED. No retry/waiver or COMPLETE checkpoint.
- C04 PostgreSQL118694553788:381 passed, failed/error/skipped/xfailed/xpassed/
  deselected0, natural exit0. Real plan30000 documents/10 returned/2 index nodes,
  5.103ms execution,0.586ms planning,441 buffers.
- Foundation118694553810:951 unit+37 subtests, inherited2208 passed, zero skips/
  failures. Owner75, staff67, migration108/89/86, all real media/restart/native/
  private-storage/timeout/history gates naturally GREEN.
- Immutable C03 baseline118694553938:127 stages, every exit0, exact tree
  5c294cb330cf08b297cc01c8baa27adb1e6b93b7. Original backend1692 and all original
  browser/service/cleanup stages GREEN. Metadata artifact12277512119 SHA256
  8c674d66f684bb501fbfc21430de020888a61fec4d771884b7f8c5bf2a86c47b verified.
- Current complete_backend reached the inherited900s deadline, exit124. Its
  verified artifact12276713196 SHA256
  b564705e27ce4355015e1fa76e4ffa00c7588269ac4254572df2301fa4ff72e0 already
  contained the nonterminating Foundation observer:1948 completed cases,
  889.530 cumulative case seconds, no nonpassing reports before termination.
  Last started test_foundation_reporter_loads_after_console_bootstrap at895.039s.
  Slowest case test_candidate_budget_fails_without_partial_output_and_recovers
  completed in124.730s; query-plan case23.719s. Cause is cumulative deadline,
  not a proven hung case or an external/transient failure; no same-SHA rerun.
- Initial inspection missed those existing journals; an unpublished redundant
  observer proposal/local RED1 was discarded after reading the verified ZIP.
  No observer/manifest/deadline change is being published.
- Bounded fixture performance correction: batch only the100 synthetic corpus
  setup/publication/withdrawal operations in one actual PostgreSQL transaction,
  committed before tested search/reconciliation. Every account/verification/
  release/withdrawal still uses real commands and SQL guards. Keep100 distinct
  candidates, all stale-budget503/no-partial-output/cursor/reconcile assertions,
  original full test selections,900s deadline and all15 jobs unchanged. Emit
  finite setup row/time metadata. This is not product behavior or fake service
  acceptance. Actual observed900s timeout is the performance RED.
- Local whole-tree Ruff/format533 and diff checks pass. No local PostgreSQL/Docker
  exists, so fixture GREEN and full regression require fresh hosted proof.
  The52+4 local diagnostic tests passed for the discarded observer proposal;
  that result is not claimed as proof of this fixture correction.
Task6 remains IN_PROGRESS; Task7+ not started. No production enablement.

### Task 6 — batched fixture PostgreSQL GREEN; current prerequisite diagnosis

Source2e8d23c834c646dbfaa109abf5b63fc28249e3e4,
tree6b9c68123e86a71745e4ca42f9fd7744b8e7dad4,
run39449624858 attempt1 (remaining jobs still running at this checkpoint):
- PostgreSQL118720654346:381 passed; failed/error/skipped/xfailed/xpassed/
  deselected0, natural0. The batched100-candidate test and all unchanged budget/
  recovery assertions pass on real PostgreSQL. Full900s regression proof remains
  pending; no performance success inferred from this focused gate.
- Current c03-final118720654354 failed earlier, before full backend:
  original_c02_lock/sync/npm/css/js/static/lint/format/types/check/units/production
  all exit0, original_c02_runtime exit1; exact_original_c02 exit1. Cause unproven.
  Verified artifact12277806760 SHA256
  f201834739a13a35ed625958100c56c021f33798a075da6da6c8f5d7951f5036.
  No classification as transient and no blind retry.
- Audit118720654450 independently verified historical tasks1–7, then Actions
  HTTP502/HTTPError. Verified artifact12278550294 SHA256
  217eb763deb8079c60ba9739d6eb0f41bd8855cd8eb6942ee0fc3c6283aa4b3b.
  A bounded evidence-backed same-SHA retry would be permitted for this external
  failure, but no retry was used while another mandatory cause is unknown.
- Current upgrade metadata still used only the old npm-focused classifier,
  unlike the immutable baseline observer added at e750f26. Local RED2+7 passed
  cases proves TLS/daemon category observations are absent at this current path.
  Add the same reviewed finite classifier only for exact_original_c02.log,
  using existing64KiB tail and known test paths. No raw text/values/URLs export,
  no changes to original sources, test commands, services, timeouts or exits.
- Local execution server disconnected during the correction. The attempted
  source-file write failed; no local GREEN/static result claimed for this new
  diagnostic. Reconstructed the intended small patch from exact fetched GitHub
  source with unique-match checks, preserving all published content. Hosted
  verification is authoritative. Accessible published work and all prior
  evidence remain preserved; no claim of recovering lost unpublished files.
Task6 IN_PROGRESS; Task7+ not started. Fresh exact-source all15 jobs remain
mandatory. No production publication, merge, deployment or C05.

### Task 6 — repeated full-regression deadline; bounded hosted artifact diagnosis

Exact48eb911a9cd499649b39c0b4bab73d9b4fe6cba8,
treeceb8c63c8251946ac7ab75ea1d9a5f07fec5c0e4,
run39451304085 attempt1:13 GREEN, c03-final118726524934 FAILED,
c04-final118747460960 correctly FAILED on its failed upstream.
- PostgreSQL118726524613:383 passed, all failed/error/skipped/xfail/xpass/
  deselected0. New finite prerequisite diagnostic tests pass on real hosted
  source. Actual30000-row plan2.869ms execution/0.453ms planning/441 blocks,
  two index nodes and10 returned.
- Foundation118726525152:953 unit+37 subtests;2210 inherited regressions,
  failed/skipped0. Immutable C03 baseline118726524608:all127 stage exits0,
  exact approved C03 tree and original backend1692. Owner75/staff67 and
  migration108/89/86 GREEN. Real scanner/store/non-eager worker/SIGKILL/
  restart/withdrawal/purge probes and cleanup pass.
- All12 earlier artifacts' API digests match actual upload-log SHA256 records.
  Method is metadata/upload-log cross-check, not an independent local ZIP
  rehash: local execution server remains unavailable.
- Current original C02 prerequisite and exact source/preservation/zero-state
  controls passed this run. complete_backend again reached900s and exited124,
  before any full-backend PASS/count. No same-SHA retry or timeout increase.
  Failure artifact12281581780 SHA256
  b12ff7e5d3b6fb8a90477b5853b60b400acb759ce9ca8ea1b99846e6f258f597.
  Its stage logs prove the repeated budget failure. The full safe case journal
  needs inspection to locate remaining costs; do not claim a hung case or a
  successful fixture performance correction from focused GREEN.
- Add a bounded hosted metadata reader, pinned to this exact artifact/run/SHA/
  digest. It checks provenance and archive SHA256; accepts only bounded known
  journal members; exports fixed counters/known static test names/finite timing
  and known failed-stage exits. Parameters, stacks, payloads and arbitrary text
  never leave it. No extraction or private-log upload. GitHub token is not
  forwarded across the artifact redirect. Every result says acceptance:false.
- Add only an after-tests C04 PostgreSQL metadata step,90s bounded, with scoped
  contents/actions READ permissions. All15 required jobs, inherited executable
  jobs, real test selections/services, deadlines and cleanup stay unchanged.
  This is a diagnostic, not acceptance; a fresh complete manifest is still
  required after the actual performance correction.
- Three focused parser privacy/bounds tests accompany the reader. Existing
  hosted900s failure is the performance RED. Local execution is unavailable:
  no local syntax/static/GREEN claim for this diagnostic; actual hosted source
  verification must run. Task6 remains IN_PROGRESS; Task7+ not started.

### Task 6 — exclusive Work Cloud handoff and bounded timing probe — 2026-10-23

The C04 Phase Manager explicitly confirmed the previous local executor and all
background/Git writers stopped, and appointed this session sole Task6 writer.
Local-only laptop ledger changes remain unavailable/unpublished; no recovery is
claimed. Live branch independently matches7fad19eae808c781585f24d47c84470a835846bc,
tree3b0cc18f4af58c08b25c087035f7e6c697617520. Approved plan blob f1225196c95a203e440afc4da362b74806e84f20
and tree1478d691b2a60d95f6c0d2ce5e561d34f59a61c0 match; actual compare proves
approved planning ancestor (zero behind). Fresh dedicated clone is clean at base.

Run39458472046 attempt1 independently reports13 successful jobs and failed
c03-final118751407841/aggregate118771461003. Downloaded artifact12284825254
was independently SHA256-rehashed to
ee7b69fb25596a9664bd14ff9c318c537d7e3b6556c96b749bb21d0803aeca34.
Complete-backend journal has1107 completed cases, no nonpassing reports;
candidate-budget call178.573s, teardown0.181s; last query-plan setup at874.842s.
The older pinned hosted diagnostic independently reports180.311s on the earlier
source. Transaction batching alone has not established full-budget recovery.
No hung query, service failure or product root cause is inferred.

Ruling: add one360s hosted cProfile probe of the two exact existing candidate/
query-plan tests after the unchanged cumulative PostgreSQL gate. Export only
fixed repository-function labels, bounded numeric counts/timings, exact GITHUB_SHA
and exit code; no SQL, parameters, locals, call graphs, arbitrary filenames or
profile dumps. Publish one identifiable timing.json artifact. Preserve all15 jobs,
original900s complete-backend deadline, test selections/assertions, immutable C03,
services and lockfiles. Cost if wrong: diagnostic fails or remains insufficient;
it never grants acceptance. Full manifest still runs on this diagnostic source.

Profiler export control: actual local missing-profiler assertion RED, then
stdlib unittest GREEN1; focused installed controls/static checks recorded below.
Task6 remains IN_PROGRESS; Task7+ prohibited. GitHub-hosted real services remain
the only runtime acceptance environment; no local Docker qualification repeated.
Local frozen C04 unit controls:247 passed+37 subtests, zero failures/skips7.88s.
Ruff check/format and whitespace checks pass for the probe. This is not runtime
acceptance or evidence of fixture performance improvement.

### Task 6 — measured fixture specialization candidate, not acceptance

Diagnostic4054dd7e71e66c0d24b8bc1c5d6aa9ba1c1809c9/
85e764f6d84e6f637e9b58f09ce32d17b3fb52a4, run39902905443 attempt1,
PostgreSQL120248252482: unchanged cumulative Task6 gate naturally passed,
30000-row query plan4.645ms/441 blocks/two indexes/10 returned. The separately
bounded two-test profile naturally passed2/0 in227.13s. Fixed-symbol profile:
101 corpus calls160.039s; dual-role approvals124.984s;173959 database executions
85.724s; publication prepare10.138s/confirm9.981s; withdrawal2.973s;
reconciliation17.158s/search12.526s. Artifact12480161568 digest
1f5ad44050084d8183c075d74b9bbe6fc207dd40a8b74e714e3518f614edd3ca.
These are overlapping cumulative times under cProfile, not additive wall times.
The30k planner is not established as the cause; repeated full fixture construction
is the measured dominant probe cost.

Ruling: specialize ONLY the100-candidate test to an actual identity+coach source
lifecycle. Each distinct professional still uses real account/session/setup,
private evidence/credential, prepare/submit/assignment/case-bound step-up/review/
terminal approval, publication prepare/confirmation, projection and withdrawal
commands with all SQL guards. Eliminate unrelated nutritionist declaration,
third evidence/revision and third review decision from this bulk fixture only.
All mixed-role, expiry, private-field, media, SQL, isolation and concurrency tests
retain their original dual-role corpus. Preserve100 unique real profiles, stale
budget/no-partial-output/cursor/four reconciliation calls/recovery assertions,
all15 jobs, lockfiles, original900s deadline and immutable C03. Add a real SQL
fixture characterization proving exactly the two approved targets, current
identity/coach eligibility, declared coach-only role and effective coach release.
Cost if wrong: the characterization or full hosted gate rejects this candidate;
no fixture or performance GREEN is assumed before actual hosted measurement.
This changes test construction only; no production behavior/schema is changed.

Independent fresh-context read-only security/privacy/architecture review of
accepted Task5edd6b300..4054dd7e found no Critical/Important/Minor findings.
Runtime concurrency/migrations/full15 were explicitly not inferred by review;
actual hosted gates remain authoritative. Task8 HTTP adapters/CSRF/browser work
were set aside because no routes are introduced at Task6; existing CSRF/session
middleware must remain unchanged. The profiler was not treated as acceptance.

A distinct mandatory job120248252465 failed its historical HTTP audit with
URLError at c03_upgrade_probe_impl.py1266. Earlier supervised decoder checks,
native real credential processing and diagnostic_cleanup all naturally0;
expected direct-PID1 diagnostic isolation failure is not relabeled as runtime
acceptance. No blind retry used and no transport/DNS/TLS cause invented. Other
current-head completed gates are successful; full run remains active/unaccepted.
A new correction head must obtain every gate naturally GREEN; no waiver.
Task6 IN_PROGRESS. Task7+ prohibited.
The timing ZIP was independently downloaded/rehashed to the digest above.
Local frozen C04 unit controls247+37 subtests pass7.96s, zero failures/skips.
Whole-source Ruff check and format537 files pass after preserving generated
pytest temp copies under ignored .runtime; whitespace clean. No local real-service
GREEN or fixture timing improvement is claimed. Fresh hosted proof required.

### Task 6 — fixture characterization adapter correction, still IN_PROGRESS

Correction92b80a0a7bd98d48ed2c1540a261b25793b9812b/tree
b912acb3ef33e372a7ef0c31797faa1d450cf016, run39904239921 attempt1,
PostgreSQL120252405589 naturally failed1:387 passed/exactly1 failed;
errors/skips/xfails/xpasses/deselections0. The new characterization reaches
eligible identity+coach and exact coach-only verified-role assertions, then raises
AttributeError at test_search_eligibility.py126. The returned subject.case is a
VerificationDTO, not an ORM Verification instance, so it has no targets manager.
Fix ONLY that test adapter to inspect persisted VerificationTarget rows by the
exact case.id, retaining the same exact two approved-target assertion. This is an
author test defect, not a permission/SQL failure, fixture GREEN, or acceptance.
All existing budget/recovery tests passed; query-plan30000/10/two indexes/441
blocks/2.9ms. Subsequent profile was correctly not run after the failed cumulative
gate; no timing artifact or performance GREEN is invented.
No same-SHA retry; forward source correction requires a fresh full15 manifest.
Native job120252405715 on this candidate independently succeeded (including the
historical audit which failed with URLError on earlier diagnostic source).
No external root cause is inferred from this later success. Task7+ not started.
Local Ruff/format/whitespace pass; real fixture characterization requires hosted
proof. All original assertions/services/deadlines/security guards remain.

### Task 6 — controlled immutable clean_minio diagnostics — 2026-10-23 UTC

Phase Manager authorizes continued sole-writer Task6 recovery. Existing explicit
stopped-executor handoff persists; branch independently remains6fa56e89567a7414602752c5882e5a6995c38dc6,
treeb569d4eaa0c18af0bad0fb7b10e783a447bdfd95, local tracked/index state clean
before this change, no other active implementation agent or competing remote
advance observed. The fresh diagnostic reviewer is read-only. Laptop-only
ledger changes remain unavailable/unpublished and are not reconstructed.

Re-fetched run39904837930 attempt1 is terminal FAILURE. Thirteen jobs actually
succeeded: c04-postgresql120254272507, foundation120254272404,
c02-migrations120254272365, c03-owner120254272369, c03-staff120254272414,
c03-storage120254272609, c03-processing120254272436,
c03-restart120254272180, c03-timeout-probe120254272460,
c03-task14-native120254272559, c03-evidence-audit120254272474,
c04-public-media120254273473, c03-final120254272635.
Failed c04-baseline120254272520 at original clean_minio exit1; c04-final120266713385
correctly failed its upstream guard. No skipped/cancelled job is accepted.

Separate c03-final now proves complete_backend natural0, original900s bound
unchanged, final_rehearsal_passed and clean_cleanup0. This is actual current-source
success, not inferred from the focused388 result. Baseline metadata artifact
12481720290 digest28d798471454ea8feccfb3467bb6db8252ec051ad5814825f1ca94d88578477f
remains insufficient for MinIO's failing subcommand. The C04 wrapper did not read
clean_minio.log. That omission caused missing evidence, not the MinIO failure.

Inspected immutable C03 minio-init.sh, Compose dependency/entrypoint and pinned mc
release RELEASE.2025-08-13T08-35-41Z command source. Alias/readiness errors are
explicitly redirected away in the unchanged original loop. Empty or Compose-only
logs cannot prove which loop command failed; duration/last-active marker alone
is not a cause. No original source, Compose behavior, init command, bucket/ACL/
policy/user requirement, dependency, source guard or deadline is changed.

Ruling: add ONLY a C04 outer reader for the exact generated clean_minio.log,
64KiB maximum, reject links/nonregular files, explicit missing/empty/oversized/
malformed/unreadable outcomes. Match fixed pinned-mc error prefixes or explicit
Docker startup/daemon errors; export finite classifications/evidence tokens only.
No raw logs, captures, credentials, environment values, endpoints, policy text,
identifiers, paths or exception messages leave the reader. Unknown/admin-only or
conflicting operation evidence stays unknown_or_insufficient_evidence. Diagnostics
always say acceptance:false; original one subprocess execution/exit is preserved.
Cost if insufficient: the failing subcommand remains unclassified; no success,
external-transient label, initialization bypass or blind same-SHA retry follows.

Actual local RED21 missing-reader assertions. Initial focused GREEN33, then
additional directory and prefix-collision RED2 were corrected. Independent static
security/privacy/correctness review found an Important descriptor-close error
could override the original exit; reproduced actual RED. Its order-dependent
conflicting-daemon finding was regraded as diagnostic correctness, reproduced
RED, and fixed in the same pass. Both negatives now pass. No unresolved review
finding remains; runtime/actual MinIO cause were explicitly not inferred by review.
Final frozen C04 unit controls275 passed+37 subtests, failed/skipped0 in6.69s;
whole-source Ruff/format538 files, whitespace and immutable source verification
(5c294cb330cf08b297cc01c8baa27adb1e6b93b7) pass. The unchanged original subprocess
one-call/exit17 control passes. No local Docker qualification or service PASS.
New exact-source hosted full15 and actual sanitized MinIO observations required.
Task6 remains IN_PROGRESS; completion checkpoint absent; Task7+ prohibited.
Prior successful full-current rehearsal artifact12482016987 independently
rehashed82b9f337407fe71590fc4647d4b5aea52cb09923c7974ea4bd3f08f2ec3303a6;
all145 recorded stage exits0. This separate success does not waive the failed
immutable MinIO baseline or aggregate.
Its complete-backend journal proves2082 completed cases, pytest exit0 in692.474s,
zero nonpassing reports; no deadline increase or selected-test suppression.


### Task 6 full-regression comparative recovery diagnostic — 2026-10-23 UTC

Task 6 remains IN_PROGRESS and unaccepted. No Task 7 authorization.
The Phase Manager renewed this session's exclusive writer authority. Only the
root implementation agent is a writer; a separate reviewer is read-only.
Execution ref independently remains 0787d7880f9fd27006bf76ae0f16e31536ef4503,
tree b207a0a8e946750a0dd1213f5460e51f67dd3000; working checkout is clean.

Read-only evidence:
- Run 39904837930 attempt 1, source 6fa56e89567a7414602752c5882e5a6995c38dc6:
  c03-final succeeded. Artifact 12482016987 independently rehashed to
  82b9f337407fe71590fc4647d4b5aea52cb09923c7974ea4bd3f08f2ec3303a6.
  Complete-backend journal: 2082 completed cases, pytest exit 0, 692.474 seconds.
- Run 39913564638 attempt 1, source 0787d7880f9fd27006bf76ae0f16e31536ef4503:
  13 mandatory jobs succeeded, c03-final failed complete_backend exit 124 at
  the unchanged 900-second bound, c04-final correctly rejected upstream failure.
  Artifact 12486980090 independently rehashed to
  beaa7f2d68fc93169d3994446de0e136480dee1c85013d49441ee00618632e40.
  Complete-backend journal: 1332 completed cases, no nonpassing phase reports,
  1333rd case active at termination; this is NOT complete acceptance.
- Match sanitized node identity PLUS occurrence ordinal, preserving parameterized
  repetitions instead of collapsing repeated identities into a dictionary.
  First 1333 started identities have identical order. No newly added MinIO test
  was reached before timeout. Their collection impact remains a separate question.
- The 1332 common completed cases: setup 7.814 -> 11.316 seconds;
  call 508.553 -> 696.943; teardown 104.681 -> 180.519.
  Shared case #100 ended at 28.573 -> 42.935; #500 at156.427 ->236.498;
  #1000 at376.245 ->555.344; #1332 at626.218 ->896.503 seconds.
  Broad slowdown predates C04 and is not explained by the last active test.
- Candidate-budget case total85.248 ->110.916; query-plan case17.752 ->27.508.
  Existing focused profiles record SQL counts/timing only for their separate
  diagnostic runs, not for the full-regression process. Do not equate them.
- Current immutable C03 baseline succeeded, clean_minio exit0 and natural final
  rehearsal completion. Its finite MinIO classifier returned
  unknown_or_insufficient_evidence (log read; no recognized error).
  Historical MinIO failure cause remains unknown, not classified as transient.
- c03-final logs/journals do not contain sufficient CPU/memory/I/O utilization or
  aggregate database-wait measurements to distinguish host from service contention.
  A source defect, service contention, and runner variability are not established
  root causes by these comparisons.

Justified next execution is diagnostic only, not a same-SHA acceptance retry:
- New diagnostics/c04-task06-performance branch, parent anchored to0787d788.
  Execution branch, mandatory c04.yml and ci.yml, original full test selection,
  900-second deadline, immutable C03, dependencies and lockfiles stay unchanged.
- Two ubuntu-24.04 runners, same pinned PostgreSQL/Redis images as acceptance.
  Both compare exact checked-out 6fa56e8 and0787d788 sources; ABBA and BAAB
  sequences balance source order and cache/warmup effects within each runner.
- Full collection-only measurements for both sources; current MinIO tests measured
  separately; four bounded representative real-database samples on each runner.
  Samples cover existing CPU-only exhaustive calendar case, C02 staff authority,
  Task6 comparison fixtures, and100-real-professional candidate-budget lifecycle.
  Diagnostic selections do NOT replace, deselect or modify acceptance selections.
- Each process bounded120s(collection/MinIO) or240s(sample), job25min.
  Record phase durations, SQL execute/executemany count and elapsed time without
  SQL text, numeric host CPU/memory/pressure/disk-free snapshots, aggregate sampled
  active database wait-type maxima. Wait samples2s can miss short contention.
  Real-services backend is GitHub service containers, not the full C03 multi-service
  rehearsal; results cannot prove full-regression acceptance or reproduce every
  full-rehearsal contention source.
- Framework stdout/stderr and arbitrary exceptions are discarded, not uploaded.
  No locals, credentials, environment dumps, query text, IDs, query parameters or
  pytest parameter values are exported. Output nodes are unparameterized known
  selected source symbols; unknown paths become other.
- Local non-service controls: collection2110, exit0; all28 MinIO tests passed
  (84 phase reports), total phase duration0.031990s, whole diagnostic0.568513s.
  These local timings do not substitute for hosted measurements.
  Initial local harness run exposed missing temp-parent setup; corrected before
  publication. Ruff and explicit redaction/exceptional-SQL-count controls pass.
- Artifacts are finite JSON files identified by runner lane; acceptance:false.
  No completion checkpoint is authorized by a diagnostic success.

Distinct read-only diagnostic review: no unresolved Critical/Important findings.
Reviewer limitations above remain explicit; historical cause and acceptance remain unproven.


### Task 6 paired performance diagnostic results — 2026-10-23 UTC

Diagnostic-only run39926412693 attempt1 completed successfully on
e67ec1c1bbe464fca2d9d6b7fc353367b5701c71,
tree9e8c9c8e3c5c2966bfd5053f7d36f5f3e7863d14.
Jobs120323789052 and120323789420 both succeeded; all eight24-case samples
and both collection/MinIO measurements exited0. This is NOT acceptance.
Artifact12490460430 SHA256
f47ac8e9c610b32946e9af2794b7c027d4367f0f87c1f568aa82f600f1fe7ff0
and artifact12490181632 SHA256
7a0ca2162b45e3e2a9c438ae9eeec3bf0b78f2e9a6a4aa76ab17391d50290474
were independently downloaded and rehashed; both matched GitHub digests.

ABBA lane0: prior118.089, current132.986, current121.970, prior126.938 seconds.
BAAB lane1: current108.404, prior116.663, prior113.624, current108.823 seconds.
Current/prior mean ratios1.0405 and0.9433 reverse direction. No repeatable
current-source regression is demonstrated by this diagnostic.
The fixed CPU calendar case averaged3.783s on lane0 vs2.920s on lane1.
This demonstrates present diagnostic host performance differences, not the cause
of either historical full-rehearsal run.

Both sources collected2082/2110 tests as expected. Prior collection6.433-7.072s;
current3.864-4.540s. Prior was collected first, so cold/warm ordering prevents
interpreting the difference as a source speedup. Actual full journals' first
test starts4.165 ->6.153s: this recorded startup difference cannot explain the
270.285s shared-prefix difference. Newly added MinIO cases were never executed
before that timeout. Separate hosted28-case MinIO execution0.606-0.703s, no SQL.

Representative samples executed156499-157027 SQL calls, elapsed SQL43.665-66.471s.
These small call-count differences do not establish an application defect.
All lane staff samples had1654 calls, comparison samples20824 calls. Most total
count/timing variation was in the100-professional candidate lifecycle/reconciliation.
Sampled active database waits observed Client/Timeout/running-or-other;
no Lock or IO wait was observed. Two-second sampling cannot exclude shorter
waits, nor establish anything about the historical full-rehearsal database.

No source/fixture correction is justified by these results.
Historical PostgreSQL/service contention vs runner resources vs full Compose
topology remains unresolved: original c03-final has no matching synchronized
resource/wait telemetry, and this focused host-Python service-container experiment
does not recreate that topology or its background services.
The next defensible execution, if continuing recovery, is one separately bounded
diagnostic of the exact full complete_backend selection in original Compose
topology with synchronized finite CPU/I/O/container/database-wait and phase SQL
telemetry. Keep the exact source and inherited900s deadline. It must remain
diagnostic-only; it is not an authorized same-SHA acceptance retry.

Execution branch still0787d7880f9fd27006bf76ae0f16e31536ef4503.
All existing refs remain unchanged; results are published on a separate
diagnostics/c04-task06-performance-evidence branch to avoid triggering another
performance run merely to record evidence.
Task6 IN_PROGRESS. No completion checkpoint. Task7 NOT_AUTHORIZED.


### Task 6 single full-topology diagnostic outcome — 2026-10-23 UTC

Exactly one authorized diagnostic executed: run39931454829 attempt1,
job120340462413 succeeded; diagnostic SHA
f853186e1079239a43fc615a090d74f3eaad4690, tree
15cc97029841d1e6cc621431fec1948f2bb19cd0.
Application checkout before/after verified clean and unchanged at
0787d7880f9fd27006bf76ae0f16e31536ef4503,
treeb207a0a8e946750a0dd1213f5460e51f67dd3000.
The original acceptance workflows and execution branch remain unchanged.

Artifact12491729575 task06-full-topology-numeric-evidence downloaded and
independently SHA256 verified:
51b544718b81cb76af7b9db9c0bf182b4271504277dadd9a0e5cc3271a4e3b0d.
Only summary.json,host.jsonl,pytest.jsonl; no unrestricted logs/stacks/SQL/data.

Actual original-selection complete backend:
- Command elapsed629.038631s, natural exit0, unchanged900s bound.
- Pytest observer624.549194s;2110 started/completed/passed cases.
  Zero failed,error,skipped,xfailed,xpassed,deselected. No observer fault/truncation.
-2147 call reports include37 additional subtest reports; they are not2147 cases.
- First1333 case identities/order match historical timed-out source. Shared1332
  completion: historical success626.218s, historical timeout896.503s,
  current diagnostic572.850616s on pytest monotonic reference.
- Current28 MinIO tests total phase time0.037023s; no basis to blame their execution.
- Candidate-budget call67.823317s vs prior85.085/110.731s.
  Fixed CPU calendar call3.089160s vs prior3.097/5.358s.
- All15 recorded setup/preflight stages exited0: immutableC03/C02/C01 identity,
  original build/services/MinIO/scanner, migrate/clean/no-op/drift and isolated
  exact-baseline. Original clean worker override and all required services used.
- Cleanup complete, no post-window records, sampler stopped. No unrelated
  persistent resources deleted; execution source remains unchanged.

Correlated numeric observations:
-126 total host samples,125 within window,620.121s coverage, zero sampler errors,
  no missing PostgreSQL samples. Common host/container monotonic origin verified.
- Four reported/affinity CPUs. Host idle55.015%,iowait0.531%,steal0%.
  CPU some pressure cumulative2.736%, peak10s average19.81%.
  No observed container CPU throttling deltas. Root quota unavailable;
  checks/db/worker/beat quotas reported unlimited; scanner retains1CPU quota.
- Memory available minimum12685380KiB; no observed high/max/OOM/kill deltas.
  Memory pressure10s averages0; no evidence of sustained memory pressure here.
- Mean container cores: checks0.699,db0.310,worker0.266,beat0.245,
  web0.085,minio0.081,redis0.011,scanner0.008.
- Whole-cluster PostgreSQL active max1; no sampled Lock/LWLock/ungranted-lock
  waits; one IO-wait sample and five Client-wait samples. IO-wait sample aligned
  with public-copy cleanup replay, not the candidate-budget case.
  Five-second sampling cannot exclude short waits or historical contention.
- Host IO some pressure cumulative0.561%,peak10s1.52%; supported-device mean
  writes3.576MiB/s,write_ms/completed_op3.061ms. These are whole-host indicators,
  not application query latency. PostgreSQL track_io_timing=false; its0 timing
  fields are unavailable measurements, not measured zero latency.
- Wrapped Django739164 execute/executemany calls,233.300331s aggregate elapsed.
  Other process/service SQL is outside this wrapper counter.
- Observed SQL-counter bookkeeping1.083771s,hook/AST/write observation0.403702s;
 10000-no-op calibration0.005601s. Host controllerCPU0.618273s,
  host childCPU7.003853s; cumulative collection wall16.275330s ran concurrently.
  None is causally subtracted from runtime; uninstrumented same-host full control
  was not authorized. Instrumentation overhead is measured/estimated, not eliminated.

Decision:
No repeatable current-source regression or authorized application/fixture defect
is established. Unchanged full source passes comfortably despite telemetry.
Earlier paired-source direction reversal, independent CPU benchmark variation,
cross-stage historical slowdown and current full-topology result support runtime/
host performance variability as a recovery hypothesis; they do not prove the exact
historical mechanism. This experiment did not replay preceding populated-upgrade/
browser workload history, and earlier runs lack synchronized resource telemetry.
No speculative source,fixture,DB tuning or deadline change is justified.

Recommended final recovery action: ONE full15-job acceptance retry on unchanged
0787d7880f9fd27006bf76ae0f16e31536ef4503, only after separate Phase Manager
authorization as required by the diagnostic-only instruction. None triggered.
This diagnostic GREEN is NOT acceptance GREEN. Latest mandatory acceptance stays
run39913564638 attempt1,13/15, c03-final124 and c04-final upstream rejection.
Task6 IN_PROGRESS. No completion checkpoint. Task7+ NOT_AUTHORIZED.
