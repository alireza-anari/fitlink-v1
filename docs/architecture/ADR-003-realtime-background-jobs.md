# ADR-003: Durable writes, transient real-time delivery and idempotent jobs

Date: 2026-10-03. Status: Accepted for Stage 1. Runtime choices locked; reliability mechanics are engineering decisions.

## Context

Chat/notifications should feel responsive, but network/socket/broker failures cannot lose messages or duplicate relationship/payment effects. Report generation, AI and file processing must not block ordinary requests. Revoked access must apply to queued work as well as pages.

## Decision

Persist messages, notifications and business state in PostgreSQL. Use HTTP domain commands for canonical message writes; Channels/channels_redis delivers authenticated ephemeral events and cursor-based reconnect/backfill via HTTP. Validate origin/hosts and session on connect, object permission on every action/subscription/outbound dispatch, and close revoked memberships. Redis delivery is not a message history source.

Keep OTP verification, relationship acceptance/end, reservation, consent change, log sync, plan/AI approval and verified payment activation synchronous and transactional. They return a definite authoritative result rather than optimistic eventual success. Worker generation/delivery occurs afterward.

Use Celery for exports, notifications/push, AI, scanning/derivatives, check-in occurrence scheduling, reminders, projection updates and privacy processing. Celery Beat performs recurring due-row scans with one active scheduler. Timestamp-derived entitlement/security predicates remain valid if Beat is delayed. Queue task IDs/references rather than sensitive bodies.

Use a transactional OutboxEvent written with domain state/audit. Dispatch after commit plus scanner recovery; consumers are at-least-once and use unique effect keys. Bound retries/backoff/timeouts, track exhausted jobs and provide operator recovery. Check current relationship/consent/entitlement at execution and output release. A task whose input rights were revoked is cancelled/skipped and its stale private artifacts are removed. Offline sync has separate PostgreSQL receipts and foreground retry; optional Background Sync cannot be its sole trigger.

## Alternatives rejected

- WebSocket-only durable business writes/history: difficult replay/CSRF/error contracts and no offline delivery guarantee; HTTP is the V1 canonical command interface.
- Doing AI/exports/scans in web requests: latency, timeouts and resource contention.
- Asynchronous capacity/payment/approval decisions: permits overbooking, optimistic payment access or plan edits without a definite decision.
- `on_commit` enqueue alone: a crash after database commit/before broker delivery can lose the task.
- Exactly-once assumptions: brokers/network retries duplicate deliveries; idempotent effects and reconciliation are required.
- General notification SMS or in-app calling: explicitly outside V1.

## Stage 2 refinement

Foundation boots ASGI, Redis channel layer, worker and one Beat using its built-in persistent scheduler with no product schedules. Channels runs in the web ASGI process; no separate socket service. Later jobs must distinguish closed operational access from narrow consent-filtered finalized service archives. Ended episodes receive no new-data notification or broadcast. Deletion/hold tasks use central retention policies and do not expose held evidence as ordinary archives.

## Consequences and validation

An outbox, reconciliation scanners and delivery logs add a small explicit reliability surface. Test post-commit broker failure, duplicate consumers/callbacks, stale permissions, reconnect replay and duplicate recurring jobs. Queue-age/backlog/failed-provider metrics are operational release checks. Primary references: [Channels origin security](https://channels.readthedocs.io/en/stable/topics/security.html) and [Celery task behavior](https://docs.celeryq.dev/en/stable/userguide/tasks.html).
