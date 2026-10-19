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
