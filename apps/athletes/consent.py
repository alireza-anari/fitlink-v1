"""Fixed optional storage field set; no professional-sharing scope."""

from hashlib import sha256

from .validation import OPTIONAL_DEFAULTS

STORAGE_KIND = "athlete_baseline"
STORAGE_PURPOSE = "baseline_storage"
DISCLOSURE_SCHEMA = 1
DISCLOSURE_VERSION = "c03-baseline-storage-v1"
# Engineering disclosure descriptor. Approved user wording remains a release gate.
DISCLOSURE_HASH = sha256(
    ("self-only;schema=1;optional=" + ",".join(sorted(OPTIONAL_DEFAULTS))).encode()
).hexdigest()
