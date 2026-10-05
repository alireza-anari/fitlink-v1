import importlib
import importlib.util
from uuid import uuid4

import pytest
from django.apps import apps


def recovery():
    assert importlib.util.find_spec("apps.accounts.recovery"), (
        "missing audited manual recovery"
    )
    return importlib.import_module("apps.accounts.recovery")


def test_recovery_schema_is_registered_without_identity_documents():
    models = {model.__name__: model for model in apps.get_models()}
    assert {
        "RecoveryRequest",
        "RecoveryEvidenceMetadata",
        "PhoneChangeHistory",
    } <= models.keys(), "missing bounded recovery/history schema"
    for name in ["RecoveryRequest", "RecoveryEvidenceMetadata", "PhoneChangeHistory"]:
        assert not {
            "document",
            "content",
            "body",
            "transcript",
            "raw_receipt",
            "code",
        } & {f.name for f in models[name]._meta.fields}


def test_recovery_identity_input_uses_canonical_distinct_phones():
    module = recovery()
    assert module.normalize_recovery_phones("۰۹۱۲۳۴۵۶۷۸۹", "09123456788") == (
        "+989123456789",
        "+989123456788",
    )
    for old, new in [
        ("09123456789", "+989123456789"),
        ("private document", "09123456788"),
    ]:
        with pytest.raises(ValueError):
            module.normalize_recovery_phones(old, new)


def test_evidence_is_bounded_metadata_only():
    module = recovery()
    module.validate_evidence_metadata("identity_match", "verified", "a" * 64, uuid4())
    for classification, outcome, checksum, reference in [
        ("private transcript", "verified", "a" * 64, uuid4()),
        ("identity_match", "unbounded text", "a" * 64, uuid4()),
        ("identity_match", "verified", "private document", uuid4()),
        ("identity_match", "verified", "a" * 64, "https://private-evidence.example"),
    ]:
        with pytest.raises(ValueError):
            module.validate_evidence_metadata(
                classification, outcome, checksum, reference
            )


def test_sensitive_recovery_reads_require_a_transactional_recorder():
    import inspect

    module = recovery()
    for name in ["recovery_detail", "evidence_detail"]:
        parameters = inspect.signature(getattr(module, name)).parameters
        assert "record" in parameters, "missing mandatory evidence-access audit"
        assert parameters["record"].default is inspect.Parameter.empty


def test_every_allowlisted_evidence_classification_fits_schema():
    model = apps.get_model("accounts", "RecoveryEvidenceMetadata")
    from apps.accounts.recovery_models import EVIDENCE_TYPES

    assert model._meta.get_field("classification").max_length >= max(
        len(value) for value in EVIDENCE_TYPES
    )
