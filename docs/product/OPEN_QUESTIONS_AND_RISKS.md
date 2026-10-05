# Open questions and material risks

Updated in Stage 2, 2026-10-03. The resolutions below are locked and closed; do not reopen them. Remaining items are implementation/integration or legal-operational release gates, not blockers to writing/executing the bounded Foundation plan after authorization. No production provider is chosen in this stage.

## Closed Stage 1 questions

| Former ID | Locked resolution | Remaining detail, if any |
|---|---|---|
| Q1 — closed | Owner-only private preview and private management before verification; no public page/search/discovery/indexing until approval. | Operational credential evidence standards only. |
| Q2 — nutrition authority closed | Explicit Nutritionist authorization for structured plans; Coach can view granted adherence/discuss it and make non-prescriptive notes, never implied editing. | Optional contest-preparation responsibility definition; omit separate scope until nonoverlap is specified. |
| Q3 — closed | End operational/new-data access; narrowly manifested read-only delivered-service history obeys current archive consent; holds/evidence distinct from ordinary archives. | Numeric archive retention and informed archive-consent text. |
| Q4 — workflow closed | Verified request, normal-access restriction, pending deletion, hold evaluation, delete/anonymize, completion; central configurable durations; affected-record holds; restore markers and backup aging. | Actual retention periods/legal bases/operational deadlines and backup retention values before launch. |
| Q5 — client limits closed | Free maximum five; beta Pro default 100, Admin configurable through central service without deployment; lowering limits never deletes clients. | Remaining feature catalog/prices/assistant/Mirror tier details below. |
| AI boundary — closed | Default external-provider exclusions for progress photos, health/identity documents, arbitrary private files and raw Mirror video; reviewed designed feature + required consent + audit for sensitive exception. | Provider review/consent implementation in later integration. |
| Mirror — closed | Beta, feature-flag protected, versioned exercise-specific gates, insufficient-confidence/visibility states, no diagnosis. | Device benchmarks/library choice/threshold calibration. |
| Recovery — closed | Manual Admin process with explicit request/verification/authorization/audit/phone history and prior-auth invalidation; no questions/bypass. | Evidence checklist/staff MFA and support procedure. |
| Vendors — deferred by decision | Adapters and fake/mock tests now; no production SMS/payment/AI vendor selection in Stage 2. | Selection in subsequent integration stages. |

The former contradictions/tensions are resolved at policy level. Numeric/legal/vendor details do not reopen these decisions.

## Launch risks requiring owner review

| ID | Risk | Required review / release gate |
|---|---|---|
| R1 | Provider reachability/contracts and hosting jurisdiction are unvalidated. | Intentionally select SMS/payment/AI only in later integration; test reachability/delivery/verification and approve storage/privacy handling. Foundation uses MinIO/local services/fakes and needs no production vendor. |
| R2 | Health declarations, food-image processing and private photos could be transmitted to AI without meaningful informed consent. | Approve exact consent text/purposes/provider retention. Until approved, omit sensitive provider inputs or disable affected AI paths. Private share consent alone does not authorize external AI transfer. |
| R3 | Mirror camera estimates could be mistaken for medical advice; accuracy across devices/body types/camera angles is unproven. | Approve observation vocabulary, benchmark three exercises on target devices, confidence cutoffs and clear limitations. Release only validated observations; feature flag allows withholding Mirror without blocking core management. |
| R4 | Real-beta breadth creates operational and delivery load, particularly concurrent offline edits, Persian PDF exports, verification/moderation and support. | Approve launch sequence within the locked scope, operating staff responsibilities, backup/restore and provider incident procedures. Do not silently drop required V1 features to meet a date. |
| R5 | Age/credential/recovery evidence and staff authentication operational standards need sign-off. | Keep manual Admin recovery locked; define evidence verification, authorized staff/MFA and incident procedure before live recovery. No automatic alternative or consumer security questions. |
| R6 | Verified reviews/case studies can overstate payment, outcomes or authenticity; off-platform package disputes have no platform settlement evidence. | Approve labels defining relationship/progress verification and complaint workflow; define external payment evidence standards without implying escrow, verified revenue or automatic external refunds. |

## Remaining implementation/catalog items

- Central retention periods, hold review deadlines and infrastructure backup expiry need privacy/operations approval before live data. No hard-coded forever retention.
- Remaining Pro feature catalog (assistant/groups/bulk tools, advanced branding/report boundaries, Mirror tier), prices/annual discount need approval before paid rollout. Until configured, preserve previously specified core Free tools; do not silently paywall them. Pro client limit 100 is already locked.
- Optional contest-preparation scope requires nonoverlapping responsibilities before enabling that label; training/nutrition scopes suffice for the base V1.
- Exact compatible dependency versions, container digests, system fonts and tool availability are checked during authorized Foundation execution and recorded in lockfiles; this is an engineering gate, not another product-policy question.

## Contradictions found

None remain among the locked Stage 2 resolutions. Archive retention must not be interpreted as permission for live/new data, and preservation/holds must not imply unrestricted normal access.

## Review handoff

Policy resolutions were applied on 2026-10-03. Later integration/release owners resolve only the remaining period/catalog/evidence/vendor/validation details in their assigned roadmap stage. No unresolved item blocks planning Foundation. Stage 2 completion authorizes no execution; do not begin coding without a subsequent request.
