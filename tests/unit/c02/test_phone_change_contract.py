import importlib
import importlib.util

from django.apps import apps


def test_phone_change_has_owned_durable_context():
    assert "PhoneChangeIntent" in {
        model.__name__ for model in apps.get_app_config("accounts").get_models()
    }, "missing owned dual-proof intent"
    model = apps.get_model("accounts", "PhoneChangeIntent")
    assert {
        "old_phone_challenge",
        "new_phone_challenge",
        "issued_auth_version",
        "applied_at",
    } <= {field.name for field in model._meta.fields}
    assert not {"code", "raw_token", "password"} & {
        field.name for field in model._meta.fields
    }


def test_phone_change_commands_exist_without_recovery_shortcut():
    assert importlib.util.find_spec("apps.accounts.phone_change"), (
        "missing owned dual-proof command"
    )
    module = importlib.import_module("apps.accounts.phone_change")
    assert callable(module.begin_phone_change) and callable(module.apply_phone_change)
