# C03 private processing setup (Task 5)

Task 5 installs private processing only. Production remains closed: configuration
rejects `ASSET_PROCESSING_ENABLED=true` until authenticated sanitized delivery is
installed and reviewed. The existing download command still denies all raw-source
reads. A quarantined upload or accepted outbox receipt is never a usable image.

## Reviewed dependencies, 2026-10-09

| Component | Selected artifact | Purpose and license |
|---|---|---|
| Pillow | 12.3.0, exact official PyPI artifacts/hashes in uv.lock | JPEG/PNG full decode, pixel reconstruction and server PNG encoding; MIT-CMU |
| ClamAV | 1.5.4_base, official multi-platform image below | Separate private INSTREAM daemon; GPLv2, no libclamav linking |

ClamAV image: `clamav/clamav@sha256:7769870154c74ce31b0047dd8771e81f7c4269278bc005782e9e419e4922c73d`.
Reviewed amd64 child: `sha256:4bd758114dbe0964edf6742cd8ddd98ed73eb8fcd70ce8bb4f53b19a79f07fe1`.
The installed sandbox supports Linux amd64 only; unsupported platforms fail closed.

Pillow's official 12.3.0 release includes a PDF decompression bound; PDF parsing
is excluded here. Its maintained release/security policy requires continued patch
review, not trust in a pin. ClamAV 1.5.4 fixes August 2026 parser and scanner issues;
older 1.5.x artifacts are not accepted. This review does not certify either native
parser as vulnerability-free. The application preserves upstream license notices
in installed artifacts. Any distributed scanner image must retain its license and
corresponding upstream source access; distribution obligations need release review.

Primary references:

- https://pillow.readthedocs.io/en/stable/about.html
- https://pillow.readthedocs.io/en/stable/handbook/security.html
- https://pillow.readthedocs.io/en/stable/releasenotes/12.3.0.html
- https://github.com/python-pillow/Pillow/security/advisories
- https://blog.clamav.net/2026/08/clamav-154-and-146-security-patch.html
- https://github.com/Cisco-Talos/clamav/releases/tag/clamav-1.5.4
- https://docs.clamav.net/manual/Usage/ClamdProtocol.html
- https://docs.clamav.net/manual/Installing/Docker.html
- https://github.com/Cisco-Talos/clamav

Maintenance responsibility belongs to the deployment maintainer. Before live
release, name that owner, subscribe to upstream security advisories, review image
and wheel bundled native libraries, rehearse updates against the complete hosted
gates, and establish signature-refresh/backlog/lease/exhaustion alerts. No specific
person or production policy has been invented. Pins change only through reviewed
checkpoints with official artifact hashes and repeatable real-service evidence.

## Bounds and private network

| Boundary | Enforced limit |
|---|---|
| Source raster | JPEG or PNG, 10,000,000 bytes, 20,000,000 pixels, dimension 10,000, one frame |
| Output | Server PNG, edge 512 avatar/logo or 1600 cover/evidence, at most 10,000,000 bytes |
| Decoder | Independent nonroot process; Linux seccomp allowlist denies file opens/writes, network, fork/exec and privilege changes |
| Decoder resources | 512 MiB address space, 20 CPU seconds, 30-second parent deadline; core/file size/process limits zero, 32 descriptors |
| Scanner client | Overall 10-second deadline including VERSION/INSTREAM/VERSION, 512-byte reply cap |
| Signatures | Reviewed engine 1.5.4; dated signatures at most 72 hours old, clock lead at most 5 minutes; rechecked before release |
| Processing | 60-second lease; 300-second retry delay; at most eight processing attempts and eight bounded prompts per attempt |
| Celery | Existing non-eager JSON tasks, 20-second soft/30-second hard limits retained |
| Hosted gates | Existing 180-second pytest, 600-second processing supervisor, inherited foundation/PostgreSQL windows retained |

The decoder preloads trusted JPEG metadata dependencies before denying file
access, then permits only JPEG and PNG registration and full decode. It rebuilds
RGB/RGBA pixels into a new object and writes deterministic PNG compression level 9.
Input EXIF/GPS/text/comments/XMP/ICC metadata is never copied. A scanner CLEAN
alone cannot authorize release. Local root environments unable to drop privileges
produce unavailable results; no root fallback or selected-test skip is provided.
After privilege drop, Linux parent-death SIGKILL and trusted caller-PID race checks
prevent a blocked decoder from surviving a killed worker parent. The syscall filter
then denies changing that safeguard before any untrusted input is read.

`scanner-signatures` has an internet connection only to obtain official databases.
It receives no uploaded bytes and exits before scanner startup. `scanner` has only
the internal `scan-private` network, no published ports, read-only database/root,
16 MiB temporary filesystem, dropped capabilities and no-new-privileges. Workers
reach that internal daemon. Source and derivative objects remain in private MinIO;
there are no public ACL, CORS, source URL, remote import or content-egress features.
Signature refresh is a separate trusted updater, never an upload forwarding path.

## Durable execution and recovery

The outbox handler inserts one pending attempt inside the existing dispatcher
transaction. It performs no scanning, decoding, signing or object transfer. The
reconciler claims work under owner/subject/asset/attempt locks, persists authority
versions/hash, sanitizer algorithm `jpeg-png-pixels-v1`, finite prompt counter and a random lease, commits, then prompts Celery with IDs only.
Broker acceptance ambiguity replaces the old lease so late messages cannot release
content. Worker loss is recovered from expired durable leases, independent of the
original prompt or process memory. Historical failed processing attempts remain.

Fresh account eligibility/auth version, exact subject/purpose/current binding,
asset version/processing generation/revocation/lease, and applicable record hold
and consent facts are rechecked before I/O and before ready commit. Holds retain
records but grant no ordinary access. Private credential upload is purpose-bound;
no nonexistent professional consent purpose is invented. Unknown, stale, failed,
exhausted or invalid processing remains unusable. Exceptions store finite codes,
never scanner raw messages, private keys, byte strings or source URLs.

A pending derivative row inventories its opaque private key before object write.
After a crash, an exact-byte/checksum match can be adopted; conflicting objects
remain denied. A stale job cannot release or overwrite that inventory. Source
bytes are not overwritten or deleted by processing. Destructive cleanup and
production retention policy remain separate later tasks.

Compose has separate `asset-beat` (`config.c03_celery`) reconciliation every 30
seconds and the unchanged inherited C02 Beat schedule/command. Start web, worker,
beat and asset-beat for development. The hosted Task 5 entry point is
`python docker/c03_processing_evidence.py`; it owns a fresh isolated project,
requires real PostgreSQL/Redis/private MinIO/ClamAV, runs all installed Task 5
suites, and performs bounded actual worker SIGKILL/broker restart/scanner outage
probes. Test-only crash barriers are explicitly loaded only in that probe worker;
production imports do not load them. Metadata-only journals preserve verdicts and
owned cleanup evidence. Missing/unhealthy services and selected skips fail gates.

No merge, deployment, public projection, later profile setup workflow, verification
review endpoint or raw-source delivery is part of Task 5. Live collection still
requires approved disclosure/retention/backup and verification procedures, private
network/ACL/secrets, scanner maintenance and authenticated derivative delivery.
