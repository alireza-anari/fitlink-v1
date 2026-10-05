# ADR-005: AI assists; humans authorize domain changes

Date: 2026-10-03. Status: Accepted; amended by locked Stage 2 default exclusions/Mirror Beta policy. Vendor integration and threshold calibration remain later-stage gates.

## Context

AI professional summaries/suggestions and Mirror can add value but cannot become autonomous coaches, diagnoses or silent sources of authoritative nutrition/plan data. Sensitive inputs and vendor failure require explicit boundaries.

## Decision

Intelligence owns provider adapters, AIJob, AIInsight, AISuggestion and AIMirrorSession, not workout/nutrition publication. AI adapters return typed validated output with provider/model metadata, input period/source IDs, missingness, uncertainty and errors. Queue jobs with minimized authorized data; recheck scope/consent/entitlement at execution and release. Sensitive provider transfer needs a distinct informed grant and reviewed retention policy. Malformed outputs, prompt-injection text and provider failures cannot invoke domain commands.

Insights include weekly summaries, adherence/trends, attention signals and follow-up drafts, private to the responsible professional. Suggestions include draft training/nutrition changes, constrained to professional capabilities. Present exact changes, diff and explanation; require explicit professional confirmation against the expected current base revision. Normal domain services validate capability, relationship, consent, entitlement and version inside the transaction, create an immutable revision and record actor/time/diff/AI involvement. Stale drafts require new review, never automatic rebasing and approval. Rejection/failure leaves the plan unchanged. Rollback creates a new revision.

Food images yield nonauthoritative candidates/approximate portions; only athlete confirmation/correction creates actual FoodLog values. Unknown nutrients stay unknown. AI output cannot silently update the food library or client intake.

Mirror uses an existing browser/on-device pose library where practical, exactly Squat/Biceps Curl/Shoulder Press. Count repetitions, estimate joint-angle ROM and phase tempo, and show a small exercise-specific set of validated observations with confidence/camera constraints. Raw video and durable keypoint streams are not stored/uploaded by default; V1 need not implement any video-upload mode. Derived session data is private; sharing with the professional's workout report requires explicit current athlete permission. Insufficient confidence gives unavailable/uncertain output, not diagnosis.

## Alternatives rejected

- Provider directly editing plan models or background auto-publish: violates explicit human approval/history and domain authorization.
- One AI vendor embedded in domain logic: violates adapter boundary and impedes testing/provider replacement.
- Accepting food estimates as logged intake automatically: conflates an estimate with the athlete's confirmed record.
- Training a proprietary pose model or uploading all footage: unnecessary V1 complexity and privacy exposure.
- Medical/injury diagnosis or confident form judgments without validated camera geometry: outside the product and evidence boundary.

## Stage 2 refinement

Default external-AI allowlist excludes progress photos, health documents, identity documents, arbitrary private files and raw Mirror video. Prefer minimized/derived signals; sensitive transfer needs a specifically designed feature, required explicit consent, provider/privacy review and auditability. A food-image feature is a reviewed exception path, not a general file-access permission. No production AI/SMS/payment vendor is selected here; fake adapters support tests.

Mirror is Beta and FeatureFlag-protected, with versioned exercise-specific confidence/visibility thresholds. Below threshold return insufficient_confidence/insufficient_visibility, explain unreliable analysis and suppress unavailable observations rather than inventing feedback. Nutrition suggestions require Nutritionist capability; Coach adherence discussion/grants confer no structured nutrition editing.

## Consequences and validation

Approval orchestration lives in composition wiring and leaves activity apps independent of intelligence. Keep protected model/output provenance without sensitive general logs. Later tests must cover rejected/stale/concurrent/unauthorized approval, provider retries/failure, withdrawn input consent, image confirmation and Mirror sharing. Owner must approve provider handling and validated three-exercise observations before live release; Mirror can remain feature-disabled during validation.
