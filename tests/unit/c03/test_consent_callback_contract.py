"""Domain callbacks cannot bypass the inherited common consent checks."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest

from apps.governance import consents

pytestmark = pytest.mark.unit
AT = datetime(2026, 10, 8, tzinfo=UTC)


def scope():
    subject = SimpleNamespace(public_id=uuid4(), state_version=1)
    return subject, consents.ValidatedConsentScope(
        subject.public_id,
        subject.public_id,
        "baseline_storage",
        "athlete_baseline",
        uuid4(),
        1,
        AT + timedelta(days=1),
    )


def test_unknown_default_denied_and_server_callback_bounded():
    subject, value = scope()
    assert not consents._valid_scope(value, subject, AT)
    assert consents._valid_scope(value, subject, AT, scope_validator=lambda *_: True)
    assert not consents._valid_scope(
        value, subject, AT, scope_validator=lambda *_: False
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"subject_uuid": uuid4()},
        {"grantee_uuid": "bad"},
        {"object_uuid": "bad"},
        {"object_version": True},
        {"object_version": 0},
        {"purpose": "unknown"},
        {"expires_at": AT},
        {"expires_at": AT.replace(tzinfo=None)},
        {"kind": []},
    ],
)
def test_callback_cannot_override_common_denial(changes):
    subject, value = scope()
    assert not consents._valid_scope(
        replace(value, **changes), subject, AT, scope_validator=lambda *_: True
    )


def test_default_account_scope_remains_unchanged_with_callback():
    subject, value = scope()
    value = replace(
        value,
        purpose="account_metadata",
        kind="account_metadata",
        object_uuid=subject.public_id,
    )
    assert consents._valid_scope(value, subject, AT)
    assert consents._valid_scope(value, subject, AT, scope_validator=lambda *_: False)
    assert not consents._valid_scope(
        replace(value, object_uuid=uuid4()),
        subject,
        AT,
        scope_validator=lambda *_: True,
    )
