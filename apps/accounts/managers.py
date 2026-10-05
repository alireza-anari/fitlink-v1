import re

from django.contrib.auth.base_user import BaseUserManager


def canonical_phone(phone: str) -> str:
    if not isinstance(phone, str) or not re.fullmatch(r"\+989[0-9]{9}", phone):
        raise ValueError("Canonical Iranian mobile phone required")
    return phone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone: str, **extra_fields):
        canonical_phone(phone)
        if "password" in extra_fields:
            raise ValueError("Foundation does not provision passwords")
        user = self.model(phone=phone, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if (
            extra_fields["is_staff"] is not True
            or extra_fields["is_superuser"] is not True
        ):
            raise ValueError("Superuser flags must be true")
        return self.create_user(phone, **extra_fields)
