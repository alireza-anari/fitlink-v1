import importlib
import importlib.util
from dataclasses import replace
from uuid import UUID, uuid4

import pytest

pytestmark = pytest.mark.unit


def contract():
    assert importlib.util.find_spec("apps.accounts.otp"), (
        "missing digest-only OTP contract"
    )
    return importlib.import_module("apps.accounts.otp")


def test_secrets_generator_has_six_digits_including_leading_zero(monkeypatch):
    otp = contract()
    monkeypatch.setattr(otp.secrets, "randbelow", lambda maximum: 0)
    assert otp.generate_code() == "000000"
    monkeypatch.setattr(otp.secrets, "randbelow", lambda maximum: 999999)
    assert otp.generate_code() == "999999"


def test_digest_binds_generation_purpose_context_identity_and_key(monkeypatch):
    otp = contract()
    from apps.accounts.security_keys import parse_key_ring

    ring = parse_key_ring(
        '{"a":"AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8=",'
        ' "b":"ERERERERERERERERERERERERERERERERERERERERERE="}',
        "a",
    )
    context = otp.OtpDigestContext(uuid4(), 1, "login", UUID(int=0), None, None)
    digest = otp.code_digest("001234", context, "a", ring=ring)
    assert len(digest) == 64 and "001234" not in digest
    for changed in [
        replace(context, challenge_uuid=uuid4()),
        replace(context, generation=2),
        replace(context, purpose="phone_change_old", context_uuid=uuid4()),
        replace(context, target_user_uuid=uuid4(), target_auth_version=2),
    ]:
        assert otp.code_digest("001234", changed, "a", ring=ring) != digest
    assert otp.code_digest("001234", context, "b", ring=ring) != digest
    calls = []
    compare = otp.hmac.compare_digest

    def tracked(left, right):
        calls.append((left, right))
        return compare(left, right)

    monkeypatch.setattr(otp.hmac, "compare_digest", tracked)
    assert otp.matches_code("001234", digest, context, "a", ring=ring)
    assert not otp.matches_code("999999", digest, context, "a", ring=ring)
    assert len(calls) == 2
