"""Bounded baseline field inventory; retention grants no ordinary access."""

from .validation import NON_SENSITIVE_FIELDS, OPTIONAL_DEFAULTS

BASELINE_FIELDS = (*NON_SENSITIVE_FIELDS, *OPTIONAL_DEFAULTS)
# Submitted history is immutable. Clear draft fields or create a correction;
# full privileged erasure/export is deferred to the reviewed privacy pipeline.
