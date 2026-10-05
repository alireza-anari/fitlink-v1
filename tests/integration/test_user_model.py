import uuid

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_user_phone_unique_and_canonical():
    model = get_user_model()
    model.objects.create_user("+989123456789")
    with transaction.atomic(), pytest.raises(IntegrityError):
        model.objects.create_user("+989123456789")
    with transaction.atomic(), pytest.raises(IntegrityError):
        model.objects.bulk_create([model(phone="bad")])


def test_user_defaults_to_unusable_password():
    user = get_user_model().objects.create_user("+989123456789")
    assert not user.has_usable_password()
    assert not user.check_password("anything")


def test_public_id_is_uuid():
    assert isinstance(
        get_user_model().objects.create_user("+989123456789").public_id, uuid.UUID
    )


def test_superuser_flags_require_true():
    model = get_user_model()
    with pytest.raises(ValueError):
        model.objects.create_superuser("+989123456789", is_superuser=False)
    assert model.objects.create_superuser("+989123456789").is_staff
