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
