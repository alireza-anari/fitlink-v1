import importlib
import importlib.util
from uuid import uuid4

import pytest

from apps.accounts.contracts import SecurityOutcome

pytestmark = pytest.mark.unit


def contract():
    assert importlib.util.find_spec("apps.governance"), (
        "missing governance audit contract"
    )
    return importlib.import_module("apps.governance.audit")


def test_valid_metadata_only_outcome():
    audit = contract()
    outcome = SecurityOutcome("otp.requested", "accepted", uuid4(), uuid4())
    assert audit.validate_outcome(outcome) == outcome


@pytest.mark.parametrize(
    "field", ["otp", "phone_value", "ip", "session", "evidence", "body"]
)
def test_private_values_are_not_audit_metadata(field):
    audit = contract()
    with pytest.raises(ValueError, match="Invalid audit metadata"):
        audit.validate_outcome(
            SecurityOutcome("otp.requested", "accepted", uuid4(), uuid4(), (field,))
        )


def test_unknown_actions_and_free_text_are_denied():
    audit = contract()
    for values in [
        dict(action="free private text"),
        dict(result="unknown"),
        dict(reason_code="+989123456789"),
    ]:
        base = dict(
            action="otp.requested",
            result="accepted",
            subject_uuid=uuid4(),
            correlation_id=uuid4(),
        )
        with pytest.raises(ValueError, match="Invalid audit metadata"):
            audit.validate_outcome(SecurityOutcome(**(base | values)))


def test_outbox_rejects_sensitive_or_untyped_payloads():
    outbox = importlib.import_module("apps.governance.outbox") if contract() else None
    for payload in [
        {"otp": "secret"},
        {"phone": "+989123456789"},
        {"session": "private"},
        {"user_uuid": "not-a-uuid"},
    ]:
        with pytest.raises(ValueError, match="Invalid outbox metadata"):
            outbox.validate_event(
                "account.security_changed", uuid4(), 1, payload, "security:1"
            )
    outbox.validate_event(
        "account.security_changed",
        uuid4(),
        1,
        {"user_uuid": str(uuid4())},
        "security:1",
    )
