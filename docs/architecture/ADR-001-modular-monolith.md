# ADR-001: Modular Django monolith

Date: 2026-10-03. Status: Accepted for Stage 1; locked by product brief. Scope: architecture only, no implementation authorization.

## Context

FitLink must coordinate client capacity, responsibility scopes, plans, sensitive consent and subscription limits in one trustworthy beta. Independently deployable services would add cross-system consistency and operational costs before a proven scaling need. Django and a server-rendered frontend are locked.

## Decision

Use Python 3.13/Django 5.2 LTS/DRF and PostgreSQL as one modular monolith, with Redis, Celery/Beat, Channels/channels_redis and S3-compatible storage. Frontend uses Django Templates, HTML, Tailwind and Vanilla JavaScript ES Modules, Persian RTL and PWA enhancement. API contracts are versioned under `/api/v1/`, exposed resources use UUIDs and future native clients reuse services/API without forcing a browser SPA.

Sixteen cohesive apps: accounts, governance, assets, billing, athletes, professionals, coaching, workouts, nutrition, progress, scheduling, messaging, marketplace, analytics, intelligence and notifications. CRM is a coaching submodule; check-ins belong to progress; Mirror belongs to intelligence; moderation/audit/privacy belong to governance. A project composition root wires multi-domain workflows/events without becoming a business-logic app. See [dependency rules](V1_ARCHITECTURE.md#3-dependency-direction-and-coupling-rules).

Domain services own state transitions; object-scoped selectors/policies own reads. Templates, views, serializers, admin actions and sockets call the same rules. Cross-domain side effects use explicit committed outbox events. Complex activation/version/payment decisions remain single PostgreSQL transactions. Separate web/worker/scheduler processes share the release and domain model.

## Alternatives rejected

- Microservices: conflicts with locked choice and makes capacity/consent/activation distributed workflows without beta evidence.
- One giant app: obscures ownership and promotes god models/views.
- An app for each entity: unnecessary coupling/boilerplate, especially for CRM, check-in and audit records.
- React/Vue/Next.js or SPA: explicitly excluded; ES Modules supply needed interactive islands and offline workflow.
- Elasticsearch/OpenSearch: unnecessary V1 operations; use PostgreSQL full-text/trigram and verify Persian behavior first.

## Consequences and invariants

The team must enforce one-way dependencies through reviews and later import checks; Django permits coupling that the design rejects. Composition wiring is explicit, not a generic workflow/event framework. Public views are projections, not full model serialization. PostgreSQL constraints/transactions remain authoritative when Redis or workers fail. History survives library edits and incremental schema migrations. Monolith scaling/queue isolation is allowed; a new distributed architecture requires a later approved requirement.

## Stage 2 refinement

Foundation creates only infrastructure and the minimal Custom User needed for migration safety; the sixteen domains are not all scaffolded at once. Central entitlements in billing serve all admissions/Pro checks (Free five, beta Pro configurable default 100); admin changes are data/configuration, not deployment. Foundation plan and V1 roadmap are separate documents, and only Foundation receives executable task detail in Stage 2.

## Validation for later stages

Confirm locked runtime compatibility; inspect app import direction; verify concurrent request activation and private read selectors; test real Persian rendering/search. No scaffold or dependency installation in Stage 1.
