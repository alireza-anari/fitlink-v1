"""Normal C01 sessions and user identity on the same fresh, isolated PostgreSQL DB.

Executed first with immutable C01 code, then with current C02 after migrations.
Fixture session keys stay in a permission-restricted ignored manifest, never logs.
"""

import json
import os
import sys
from pathlib import Path
from uuid import UUID

sys.path.insert(0, os.getcwd())

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.contrib.sessions.models import Session  # noqa: E402
from django.db import connection  # noqa: E402
from django.test import Client  # noqa: E402

from apps.accounts.models import User  # noqa: E402


def snapshot():
    with connection.cursor() as cursor:
        cursor.execute("SELECT oid FROM pg_class WHERE relname='accounts_user'")
        oid = cursor.fetchone()[0]
    return {
        "users": list(
            User.objects.order_by("phone").values(
                "id",
                "public_id",
                "phone",
                "password",
                "is_active",
                "is_staff",
                "date_joined",
                "last_login",
            )
        ),
        "sessions": list(Session.objects.order_by("session_key").values()),
        "tables": connection.introspection.table_names(),
        "user_table_oid": oid,
    }


assert settings.DATABASES["default"]["NAME"] == "fitlink"
assert settings.DATABASES["default"]["HOST"] == "db"
assert settings.DEBUG  # Development-only isolated Compose runtime.
phase, filename = sys.argv[1:]
path = Path(filename)
if phase == "prepare":
    assert not path.exists()
    assert User.objects.count() == Session.objects.count() == 0
    tables = connection.introspection.table_names()
    assert "auth_user" not in tables
    assert "accounts_otpchallenge" not in tables
    assert "governance_auditevent" not in tables
    for index, active in enumerate((True, False)):
        user = User.objects.create_user(
            f"+98912345678{index}",
            is_active=active,
            public_id=UUID(f"aaaaaaaa-0000-4000-8000-00000000000{index + 1}"),
        )
        assert not user.has_usable_password()
        client = Client()
        client.force_login(user)
        assert client.session["_auth_user_id"] == str(user.pk)
    assert User.objects.count() == Session.objects.count() == 2
    with path.open("x") as stream:
        json.dump(snapshot(), stream, default=str)
    path.chmod(0o600)
elif phase == "verify":
    previous = json.loads(path.read_text())
    current = json.loads(json.dumps(snapshot(), default=str))
    assert current["users"] == previous["users"]
    assert current["sessions"] == previous["sessions"]
    assert current["user_table_oid"] == previous["user_table_oid"]
    assert set(previous["tables"]) <= set(current["tables"])
    assert "auth_user" not in current["tables"]
    users = list(User.objects.order_by("phone"))
    assert [u.state for u in users] == ["active", "suspended"]
    assert all(
        u.birth_date is None and u.adult_attested_at is None and u.auth_version == 1
        for u in users
    )
    from apps.accounts.recovery_models import PhoneChangeHistory
    from apps.accounts.security_models import AccountSessionControl

    assert not PhoneChangeHistory.objects.exists()
    assert not AccountSessionControl.objects.exists()
    for stored in previous["sessions"]:
        client = Client()
        client.cookies[settings.SESSION_COOKIE_NAME] = stored["session_key"]
        assert client.get("/api/v1/account/me/").status_code == 403
    # Read denial must preserve the historical rows and normal signed sessions.
    assert (
        json.loads(json.dumps(snapshot(), default=str))["sessions"]
        == previous["sessions"]
    )
else:
    raise ValueError("Unknown upgrade phase")
print("Exact C01 same-database upgrade probe passed: " + phase)
