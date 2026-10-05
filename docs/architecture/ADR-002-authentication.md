# ADR-002: One phone-based User and browser sessions

Date: 2026-10-03. Status: Accepted for Stage 1; locked authentication with labeled implementation defaults. No migrations generated.

## Context

Iranian users authenticate by phone OTP without required email/password. Coaches and nutritionists may share one professional profile and need consistent account restrictions, ownership and assistant identity. Browser sessions/CSRF are locked; native authentication is a future decision.

## Decision

Define a Custom User from the first future migration, normalized unique Iranian mobile phone as login identifier, opaque public UUID and optional AthleteProfile/ProfessionalProfile. ProfessionalRole records Coach/Nutritionist capabilities; assistants are User memberships. Record adult birth-date declaration/attestation; account profile status and professional verification are distinct.

OTP defaults: cryptographic six-digit code, five-minute expiry, 60-second resend cooldown, five attempts/challenge, five sends/phone/hour, twenty sends/IP/hour, ten failed verifications/phone/hour and sixty failed verifications/IP/hour. Normalize Persian/Arabic digits and E.164 before rate keys and uniqueness checks. Defaults are configurable and require operational validation. Challenge uses keyed digest and atomic single-use consume; resend invalidates older code. Uniform send/verify errors limit enumeration. Trusted proxy IP extraction, atomic Redis counters and fail-closed behavior avoid unauthenticated limiter outages. Audit metadata only; never log codes.

SMS service interface shields vendor details; mock provider is development-only and production configuration rejects it. SMS is for OTP only. Failed delivery/timeouts do not issue sessions or reuse expired challenges. Login rotates Django session. Production cookie flags/TLS and CSRF apply to OTP/session/API state changes; no bearer token in browser storage. Object permissions use current User/account/profile/relationship/consent, not session-cached roles.

V1 lost-phone recovery is manual Admin-mediated only: explicit RecoveryRequest, identity/account evidence verification, authorized decision, new-phone OTP, unique phone update with PhoneChangeHistory/audit and invalidation of all previous authentication state. No security questions or unaudited bypass. Staff evidence/MFA procedures require operational review, but the recovery mechanism is closed. Normal authenticated changes verify old/new possession; consumer password login remains unnecessary.

Foundation must create minimal `apps.accounts.User` in `accounts/0001_initial` and set AUTH_USER_MODEL before any migration/database-backed test. No default-User database may be created as a temporary step. Foundation adds canonical phone, UUID/auth flags and unusable-password default only; OTP/recovery/adult onboarding/domain profiles arrive later through additive migrations. [Django custom-user guidance](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/) requires the swapped model in its app's first migration.

## Alternatives rejected

- Separate Coach/Nutritionist user models: explicitly forbidden and splits one person's identity.
- Mandatory password/email login: unnecessary V1 burden and conflicts with scope.
- JWT/localStorage browser authentication: conflicts with locked session/CSRF approach and introduces another browser credential lifecycle.
- OTP solely in memory or without phone/IP attempt bounds: replays, inconsistent workers and brute force.
- Trusting phone possession as credential/age verification: proves neither qualification nor age.

## Consequences and validation

Future native apps need an explicitly chosen authentication adapter while using the same domain API. Test OTP expiry/resend/replay, concurrent consume, normalized phone uniqueness, limiter outages, session fixation and revoked permissions. Adult assurance remains a policy question. Session security follows [Django 5.2 guidance](https://docs.djangoproject.com/en/5.2/topics/security/); OTP/throttles are additional explicit work, not framework defaults.
