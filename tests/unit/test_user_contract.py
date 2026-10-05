import uuid

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.unit


def test_custom_user_contract():
    assert settings.AUTH_USER_MODEL == "accounts.User"
    user_model = get_user_model()
    assert user_model.USERNAME_FIELD == "phone"
    user = user_model(phone="+989123456789")
    assert isinstance(user.public_id, uuid.UUID)
    user.set_unusable_password()
    assert not user.has_usable_password()


@pytest.mark.parametrize(
    "phone", ["", "+989۱۲۳۴۵۶۷۸۹", "09123456789", "+989123456789\n"]
)
def test_invalid_phone_rejected_before_save(phone):
    with pytest.raises(ValueError):
        get_user_model().objects.create_user(phone)


def test_password_provisioning_rejected():
    with pytest.raises(ValueError, match="password"):
        get_user_model().objects.create_user("+989123456789", password="never-save-raw")


def test_superuser_flags_require_true():
    with pytest.raises(ValueError):
        get_user_model().objects.create_superuser("+989123456789", is_staff=False)
