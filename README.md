# FitLink V1 — C01 Foundation

Private repository; current implementation lives on `foundation/c01-cloud`.
C01 provides only infrastructure and a neutral Persian RTL page. Accounts/OTP,
profiles and every subsequent product stage remain unimplemented.

- [Authoritative product specification](docs/product/V1_PRODUCT_SPEC.md)
- [Architecture](docs/architecture/V1_ARCHITECTURE.md)
- [Approved Foundation plan](docs/superpowers/plans/2026-10-03-project-foundation.md)
- [Setup and clean verification](docs/development/FOUNDATION_SETUP.md)
- [Foundation handoff and evidence](docs/development/FOUNDATION_HANDOFF.md)
- [Execution ledger and local/remote mappings](docs/implementation/C01_CLOUD_EXECUTION_LEDGER.md)

Start with the setup guide. Do not migrate a database using the default Django
User: this tree already sets `AUTH_USER_MODEL = 'accounts.User'` and includes the
minimal first migration. Nothing in this repository deploys or publishes a release.
