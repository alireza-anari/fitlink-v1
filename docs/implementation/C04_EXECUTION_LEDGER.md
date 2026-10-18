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
