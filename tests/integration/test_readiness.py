from unittest.mock import patch

import pytest
from django.test import Client, override_settings
from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class Protected(APIView):
    def post(self, request):
        return Response({"ok": True})


urlpatterns = [path("protected/", Protected.as_view())]


def test_real_readiness():
    assert Client().get("/health/ready/").status_code == 200
    with patch("config.health.database_available", return_value=False):
        assert Client().get("/health/ready/").status_code == 503
        assert Client().get("/health/live/").status_code == 200


@override_settings(ROOT_URLCONF=__name__)
def test_session_auth_and_csrf(user):
    client = Client(enforce_csrf_checks=True)
    assert client.post("/protected/").status_code == 403
    client.force_login(user)
    assert client.post("/protected/").status_code == 403
