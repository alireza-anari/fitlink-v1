import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from .managers import UserManager, canonical_phone


class User(AbstractBaseUser, PermissionsMixin):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    phone = models.CharField(
        max_length=13, unique=True, validators=[RegexValidator(r"\A\+989[0-9]{9}\Z")]
    )
    password = models.CharField(max_length=128, default="!")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    objects = UserManager()
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(phone__regex=r"^\+989[0-9]{9}$"),
                name="accounts_user_canonical_phone",
            )
        ]

    def save(self, *args, **kwargs):
        canonical_phone(self.phone)
        return super().save(*args, **kwargs)
