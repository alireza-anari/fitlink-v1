"""Raw quarantine source denial cannot reveal identity or asset authority."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from io import BytesIO
from uuid import UUID, uuid4

import pytest

from apps.accounts.contracts import SessionScope
from apps.accounts.sessions import AccountActor
from apps.assets.contracts import AssetNotFound
from apps.assets.policies import validate_context
from config.use_cases import profile_assets

pytestmark = pytest.mark.unit
AT = datetime(2026, 10, 9, tzinfo=UTC)


def actor():
    return AccountActor(uuid4(), 1, SessionScope.NORMAL, uuid4(), AT)


def test_later_authenticated_actor_is_valid_only_at_its_own_fixture_time():
    first = actor()
    later = replace(actor(), authenticated_at=AT + timedelta(microseconds=1))
    assert isinstance(later.user_uuid, UUID) and isinstance(later.control_id, UUID)
    assert later.auth_version == 1
    validate_context(first, AT)
    with pytest.raises(PermissionError):
        validate_context(later, AT)
    validate_context(later, AT + timedelta(microseconds=1))


@pytest.mark.parametrize(
    "context", ["owner", "foreign", "future", "invalid", "stale", "staff", "time"]
)
def test_raw_source_is_uniformly_unavailable_without_database_or_storage(
    context, monkeypatch
):
    caller, at = actor(), AT
    if context == "future":
        caller = replace(caller, authenticated_at=AT + timedelta(microseconds=1))
    elif context == "invalid":
        caller = None
    elif context == "stale":
        caller = replace(caller, auth_version=0)
    elif context == "time":
        at = None

    def forbidden_store():
        pytest.fail("Forbidden raw-source storage access")

    monkeypatch.setattr(profile_assets, "get_private_store", forbidden_store)
    # Unit DB access is forbidden too: no existence/current-authority query.
    for identifier in (UUID("00000000-0000-0000-0000-000000000001"), uuid4()):
        with pytest.raises(AssetNotFound) as denied:
            profile_assets.authorized_profile_download(
                caller,
                identifier,
                "avatar",
                at,
                staff_context=object() if context == "staff" else None,
            )
        assert str(denied.value) == "Asset unavailable"


@pytest.mark.parametrize("command", ["begin", "receive", "finalize", "abandon"])
def test_upload_mutations_still_reject_future_authentication(command):
    caller = replace(actor(), authenticated_at=AT + timedelta(microseconds=1))
    identifier, operation = uuid4(), uuid4()
    with pytest.raises(PermissionError):
        if command == "begin":
            profile_assets.begin_profile_upload(
                caller,
                "avatar",
                identifier,
                operation,
                AT,
                declared_size=1,
                declared_type="image/png",
            )
        elif command == "receive":
            profile_assets.receive_profile_upload(
                caller, identifier, 1, BytesIO(b"x"), AT
            )
        else:
            getattr(profile_assets, command + "_profile_upload")(
                caller, identifier, 1, operation, AT
            )
