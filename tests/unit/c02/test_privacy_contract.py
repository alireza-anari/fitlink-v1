import importlib
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from apps.accounts.contracts import SessionScope
from apps.accounts.sessions import AccountActor

pytestmark = pytest.mark.unit


def privacy():
    assert importlib.util.find_spec("apps.governance.privacy"), (
        "missing verified privacy intake"
    )
    return importlib.import_module("apps.governance.privacy")


@pytest.mark.parametrize(
    "offset,allowed", [(0, True), (600, True), (601, False), (-1, False)]
)
def test_recent_otp_authentication_boundary(offset, allowed):
    at = datetime(2026, 10, 5, tzinfo=UTC)
    actor = AccountActor(
        uuid4(), 1, SessionScope.NORMAL, uuid4(), at - timedelta(seconds=offset)
    )
    if allowed:
        privacy().require_recent_privacy_auth(actor, at)
    else:
        with pytest.raises(PermissionError):
            privacy().require_recent_privacy_auth(actor, at)


def test_naive_or_forged_auth_time_is_denied():
    at = datetime(2026, 10, 5, tzinfo=UTC)
    actor = AccountActor(uuid4(), 1, SessionScope.NORMAL, uuid4(), at)
    with pytest.raises(PermissionError):
        privacy().require_recent_privacy_auth(
            replace(actor, authenticated_at=at.replace(tzinfo=None)), at
        )


@pytest.mark.parametrize("kind", ["health", "account", "asset", "unknown"])
def test_uninstalled_hold_subject_cannot_be_used(kind):
    assert importlib.util.find_spec("apps.governance.retention"), (
        "missing bounded hold metadata"
    )
    module = importlib.import_module("apps.governance.retention")
    subject = module.ValidatedRecordSubject(kind, uuid4(), uuid4(), 1)
    with pytest.raises(PermissionError):
        module.is_record_held(subject, datetime.now(UTC))
