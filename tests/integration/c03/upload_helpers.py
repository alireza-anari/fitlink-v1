"""Real session/HTTP authority and shared private-store fixtures."""

from io import BytesIO
from uuid import uuid4

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from apps.assets.storage import FakePrivateStore
from apps.professionals.models import ProfessionalProfile

from .profile_helpers import make_actor

PNG = b"\x89PNG\r\n\x1a\n" + b"synthetic quarantined bytes"
JPEG = b"\xff\xd8\xff" + b"synthetic quarantined bytes"
PREFIX = "/api/v1/profile-assets/"


def owner(phone="+989123456780"):
    s = make_actor(phone)
    s.profile = ProfessionalProfile.objects.create(user=s.user)
    s.client = Client(enforce_csrf_checks=True)
    s.client.cookies[settings.SESSION_COOKIE_NAME] = s.request.session.session_key
    response = s.client.get("/accounts/entry/")
    assert response.status_code == 200
    s.token = s.client.cookies[settings.CSRF_COOKIE_NAME].value
    return s


def post(s, suffix, data):
    return s.client.post(
        PREFIX + suffix, data, content_type="application/json", HTTP_X_CSRFTOKEN=s.token
    )


def begin(s, **changes):
    data = {
        "purpose": "avatar",
        "subject_uuid": str(s.profile.id),
        "declared_size": len(PNG),
        "declared_type": "image/png",
        "operation_id": str(uuid4()),
        **changes,
    }
    response = post(s, "begin/", data)
    assert response.status_code == 201, response.content
    assert response["Cache-Control"] == "no-store"
    return response.json(), data


def body(s, dto, data=PNG, *, name="source.png", media="image/png", csrf=True):
    return s.client.post(
        PREFIX + f"{dto['id']}/body/",
        {
            "expected_version": str(dto["version"]),
            "file": SimpleUploadedFile(name, data, media),
        },
        **({"HTTP_X_CSRFTOKEN": s.token} if csrf else {}),
    )


def received(s, **changes):
    dto, _ = begin(s, **changes)
    response = body(s, dto)
    assert response.status_code == 200, response.content
    return response.json()


def finalize(s, dto, operation=None):
    return post(
        s,
        f"{dto['id']}/finalize/",
        {"expected_version": dto["version"], "operation_id": str(operation or uuid4())},
    )


def shared_store(monkeypatch):
    import importlib.util

    # Called after a real HTTP behavioral assertion, never a collection gate.
    assert importlib.util.find_spec("config.use_cases.profile_assets")
    from config.use_cases import profile_assets

    store = FakePrivateStore()
    monkeypatch.setattr(profile_assets, "get_private_store", lambda: store)
    return store


class CountingStream(BytesIO):
    largest_read = 0

    def read(self, size=-1):
        assert 0 < size <= 65536, "Ingress requested unbounded bytes"
        self.largest_read = max(self.largest_read, size)
        return super().read(size)
