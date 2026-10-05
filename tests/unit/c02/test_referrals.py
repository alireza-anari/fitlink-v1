import importlib
import importlib.util
from dataclasses import fields

import pytest
from django.apps import apps

pytestmark = pytest.mark.unit


def contract():
    assert importlib.util.find_spec("apps.accounts.referrals"), (
        "missing safe referral attribution"
    )
    return importlib.import_module("apps.accounts.referrals")


def test_anonymous_descriptor_has_no_private_identity_or_authority():
    module = contract()
    assert {f.name for f in fields(module.ReferralDescriptor)} == {"link_uuid"}
    assert not hasattr(module, "grant_access")
    assert not hasattr(module, "convert_lead")


def test_digest_only_models_and_explicit_commands():
    module = contract()
    assert all(
        callable(getattr(module, name, None))
        for name in (
            "issue_referral",
            "resolve_referral",
            "bind_attribution",
            "revoke_referral",
        )
    )
    for name in ("InviteReferralLink", "ReferralAttribution"):
        model = apps.get_model("accounts", name)
        assert model._meta.constraints
        assert not {"token", "raw_token", "phone", "profile", "workspace", "reward"} & {
            field.name for field in model._meta.fields
        }


@pytest.mark.parametrize(
    "token",
    ["", "x", "a" * 10000, "../unsafe", "?phone=private"],
    ids=["empty", "short", "overlong", "path", "query"],
)
def test_malformed_token_is_uniformly_unresolved(token):
    assert contract().resolve_referral(token, None) is None
