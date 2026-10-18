# C04 architecture and execution-readiness summary

Date: 2026-10-18. Status: **complete planning proposal for user review; no implementation authorization**.

Detailed plan: [`2026-10-18-c04-marketplace-search-public-profiles.md`](../superpowers/plans/2026-10-18-c04-marketplace-search-public-profiles.md).

## Verified repository authority

Repository: [alireza-anari/fitlink-v1](https://github.com/alireza-anari/fitlink-v1).

| Item | Verified value |
|---|---|
| Current C03 engineering/handoff branch | `profiles/c03-cloud` → `0a867328a6d8ee8c71ec9bd9eeb8910221d1b270` |
| Handoff tree | `5c294cb330cf08b297cc01c8baa27adb1e6b93b7` |
| Sole parent / tested implementation | `97fb92a2f074e3d13795670246636fad1a822055` |
| Implementation tree | `451faaac7c3ffbf6235b7e666db47e46a75fa528` |
| Hosted CI | [39145562365, attempt 2](https://github.com/alireza-anari/fitlink-v1/actions/runs/39145562365/attempts/2), all 11 jobs SUCCESS on that implementation SHA |
| Handoff compare | One commit ahead, zero behind; only C03 ledger and handoff documentation changed |
| `main` | `8ede9a451db6103f4e3ebf65784ee9f16b96feb2` |
| C01 / C02 | `75c551e5b9bbbfb7777ee52b09a1993b681e921a` / `0905be6c6ca608d469fe33e87f514b22591132d1` |
| C03 planning | `79fd62e583cbe81f335bb08fce0eb43ff36b0167` |

Current GitHub refs and job metadata were read independently. Handoff documentation is not the tested implementation commit. No new application tests/services were run during planning. The listed branches report no administrative protection flag; the instruction to preserve them remains binding.

## Proposed architecture

- **Professionals** owns explicit publication intent, immutable selected public revisions, qualification summaries and educational posts. Its existing `private_ready` state, owner preview and independent identity/role verification are preserved.
- **Marketplace** owns minimal derived PostgreSQL public/search projections, favorites and comparison. Its single public reader uses current `publication_eligibility` and exact source-publication checks; no stored index eligibility bit grants access.
- **Assets** owns separately sanitized publication copies in a distinct namespace. Existing credential sources and owner/staff derivatives remain private. An isolated gated media origin rechecks current public eligibility and release bindings; no anonymous bucket/source URL or cached stale copy.
- **Governance** keeps existing audit/outbox/flags/retention/staff authority and adds bounded C04 profile/post moderation. Composition supplies validated source callbacks and preserves dependency direction.

Public capabilities are release-selected roles intersected with fresh `verified_roles`. Shared identity/account failure hides the profile; restriction or expiry of one capability cannot advertise that role or erase the other role's valid authority. Timestamp expiry is checked without relying on counter changes or Beat.

An owner explicitly confirms the exact public field/media revision and public audience. Private edits do not automatically publish. Selected source changes suppress old output pending reconfirmation; owner withdrawal and staff hide cannot be reversed by stale events/reconciliation. This source-domain release record implements the deliberate publication authority required by the approved product/ADR; it does not invent a public User/grantee or reuse athlete Consent.

Only intentionally selected qualification **summaries** may appear, bound to current approved revisions. No credential or identity document publication is planned. Own avatar/cover/logo and new own educational-image uploads can yield separate sanitized copies after confirmation; evidence/athlete/health assets cannot. Exact informed wording and third-party-image/rights procedures remain explicit live-release sign-offs.

Search uses versioned Persian normalization, PostgreSQL `simple` FTS and pg_trgm, deterministic quantized rank with UUID tie-breaker, bounded keyset pagination and current authorization before results leave the server. Supported criteria: current capability, mode, broad city/region, selected specialty, stored language and declared experience. No health personalization, invented ratings/capacity/availability, package filters, prices or matching percentages. Broad location filters must match the same location tuple.

Favorites require current owned athlete context and confer no professional access. Comparison is athlete/session scoped, uses locked collections and unique SQL slots 1–3, rejects a fourth item, and rotates visitor scope at account transitions. Every displayed target is freshly public-authorized.

Posts are plain text with at most four separately sanitized images and alt text, with immutable revisions, explicit publication, private drafts and reasoned staff hide/report controls. No feed, followers, reviews, case studies or C18 disputes.

SEO is server-rendered from the same public DTO: trusted-origin canonical URLs, conservative factual ProfilePage/Person JSON-LD and eligibility-filtered sitemap. No ratings, offers, medical claims or unavailable CTAs. Public content responses use no-store and bypass no authorization on HEAD/conditional requests; static assets may cache normally. Controlled-origin removal cannot recall downloaded third-party copies or search-engine caches.

## Eleven strictly ordered tasks

| Task | Independently verifiable deliverable |
|---|---|
| 1 | Isolated execution authority, immutable C03 baseline and complete inherited C04-hosted CI wiring |
| 2 | Explicit professional publication revisions, public allowlist and selected qualification summaries |
| 3 | Separate sanitized publication media copies with real-service and stale-job fences |
| 4 | Public projections, fresh reads, privacy/flag effects and durable refresh/reconciliation |
| 5 | Persian PostgreSQL FTS/trigram search, filters, deterministic pagination and abuse bounds |
| 6 | Owned favorites and concurrency-safe three-professional comparison |
| 7 | Safe educational posts, publication history and bounded profile/post moderation |
| 8 | Responsive accessible RTL server-rendered pages, owner controls, APIs and real-browser journeys |
| 9 | Truthful canonical metadata/structured data and current-eligibility sitemap |
| 10 | Real fault/recovery, privacy/security, accessibility and measured performance acceptance |
| 11 | Populated same-database C03→C04 upgrade, independent clean full regression and handoff |

Each task in the full plan includes exact proposed files/interfaces, schema impact, scope/exclusions, prerequisites, named behavioral RED/GREEN assertions, real-service/browser evidence, hosted acceptance, commit boundary and stop criteria. New schema lives in forward migrations; existing User, verification evidence/history and private storage contracts remain unchanged. No C05+ work is included.

## Required execution and CI strategy

Proposed planning branch: `marketplace/c04-plan`, based exactly on the verified C03 handoff. Proposed execution branch: `marketplace/c04-cloud`, based on the exact reviewed planning commit only after explicit execution authorization. Both names were unused at initial inspection; recheck before creation. Preserve all existing refs and use expected-head/nonforce publication with parent/tree verification.

The current workflow triggers only C02/C03 pushes and most C03 jobs have literal branch guards. A new C04 branch would not inherit those gates automatically. Task 1 proposes a separate explicit `c04.yml` for only the C04 execution branch; planning changes neither workflow nor tests.

Mandatory C04 manifest retains all eleven inherited current-source job counterparts: `foundation`, `c02-migrations`, `c03-final`, `c03-owner`, `c03-staff`, `c03-storage`, `c03-processing`, `c03-restart`, `c03-timeout-probe`, `c03-task14-native`, `c03-evidence-audit`. Add `c04-baseline` (full immutable original C03 verifier), `c04-postgresql` and cumulative `c04-final` from Task 1; `c04-public-media` from Task 3 and `c04-browser` from Task 8. Every task must pass its complete installed manifest on its exact implementation SHA/tree. A focused or diagnostic test never substitutes for it.

Original C03 stage-absence/source-pin tests run unchanged against the immutable handoff checkout. Current-stage tests receive only recorded phase-aware assertion changes; privacy, role, expiry, ownership, immutable evidence and future-stage exclusions remain. A specifically identified C03 migration test derives C02 targets from current app leaves and needs a narrow historical-target/isolation correction once C04 dependencies exist. No digest update may simply bless changed security behavior.

Real PostgreSQL/pg_trgm, Redis, private MinIO plus separate publication storage, real ClamAV/isolated decoder, non-eager Celery, broker/worker restart and actual browser/HTTP gates are required. Final acceptance executes the original C03 verifier, populates original C03 by actual commands, upgrades the **same** database preserving IDs/OIDs/history/privacy, then independently verifies clean C04 with all inherited/current tests, faults, browsers and measured performance.

Each task follows behavioral RED → scoped implementation → focused GREEN → complete same-head hosted acceptance → review → normal forward commit and documentation-only completion checkpoint. The execution ledger records exact approved plan/source/fixture SHA/tree, commands, failures/skips, run/attempt/job IDs, cleanup, findings and next task. Only one evidence-supported same-SHA transient CI retry is permitted; recurring failures require diagnosis, never weakened gates. Interrupted sessions resume from verified published checkpoints and preserve unpublished work; they do not restart completed stages or fabricate lost evidence.

## Critical review outcome

Review method: a distinct manual author pass, not a separately delegated reviewer or additional test execution. The full plan records findings by severity and maps resolutions to assertions.

Critical issues resolved in the proposal: index/expiry staleness; private media/evidence exposure; dual-role overclaiming; missing C04 CI triggers and incompatible C03 stage-absence checks; stale copy/publication resurrection after withdrawal/edit/hide.

Important issues resolved: public consent/grantee confusion; count/cursor leakage; comparison/session races; already-receipted events; expensive lock-heavy eligibility reads; moderation/cleanup omissions; fake upgrades; CDN/flag-off purge gaps; deferred service wiring; historical migration-target dependency errors.

Retained minor limitations: normalization is not Persian stemming; source edits can temporarily hide profiles pending confirmation; controlled public-copy removal cannot erase third-party downloads; synthetic performance/accessibility evidence is not a field audit. No unresolved Critical/Important planning defect is knowingly left as an implementation choice.

## Decisions and next action

No unresolved source-policy decision blocks this bounded engineering proposal. User approval of the **complete plan** must adopt the proposed exact-publication mechanics, conservative stale-source behavior, search/abuse bounds, gated media, immutable slug and bounded moderation choices. This approval is not implied by publication of the planning documents.

Before live release: approve exact informed public-disclosure wording and third-party rights handling, identity/credential evidence standards and staff/MFA procedures, scanner/storage/origin/network/secrets maintenance, quotas/capacity/incident operations and central retention/hold/backup/restore privacy policy. Any requirement to publish documents, athlete/health media or another unapproved category is a blocking new decision; no agent may infer that authority.

**Exact next action:** review the published planning commit and approve the complete plan, then separately authorize sequential C04 execution. The later agent must reverify refs, exact plan SHA/tree and ancestry before creating the execution branch and starting Task 1. Stop after this planning publication; no implementation, merge or deployment.
