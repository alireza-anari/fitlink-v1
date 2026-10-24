from django.utils import timezone


def test_renewal_invalid_binding_is_denied_before_database():
    from apps.assets import public_copies

    command = getattr(public_copies, "renew_revoked_public_copy", None)
    assert callable(command), "Missing bounded fresh-generation recovery"
    assert command("invalid", timezone.now(), authorize=lambda *args: None) == "denied"
