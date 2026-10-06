import pytest
from django.conf import settings
from django.test import Client

from apps.accounts.models import User

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.mark.parametrize("active", [True, False])
def test_normal_legacy_django_session_never_grants_c02_product_access(active):
    user = User.objects.create_user("+989123456789", is_active=active)
    client = Client()
    client.force_login(user)
    assert client.session.get("_auth_user_id") == str(user.pk)
    response = client.get("/api/v1/account/me/")
    assert response.status_code == 403
    assert response["Cache-Control"] == "no-store"
    assert settings.SESSION_COOKIE_NAME in client.cookies
    assert user.birth_date is None
