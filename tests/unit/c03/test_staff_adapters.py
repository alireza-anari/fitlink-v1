"""Native/API transport remains strict, private and free of domain ORM rules."""

import ast
import importlib
from pathlib import Path
from uuid import uuid4

import pytest
from django.test import RequestFactory

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[3]


def test_staff_forms_reject_unknown_authority_and_duplicate_fields():
    from django.http import QueryDict

    module = importlib.import_module("apps.professionals.staff_forms")
    assert hasattr(module, "DecisionForm"), "Missing bounded staff decision form"
    data = QueryDict(mutable=True)
    data.update({"operation_id": str(uuid4()), "is_superuser": "true"})
    assert not module.DecisionForm(data).is_valid()
    data.setlist("operation_id", [str(uuid4()), str(uuid4())])
    assert not module.DecisionForm(data).is_valid()


@pytest.mark.parametrize("name", ["staff_api.py", "staff_views.py", "staff_forms.py"])
def test_adapters_do_not_query_orm_or_derive_authority(name):
    tree = ast.parse((ROOT / "apps/professionals" / name).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            assert node.attr not in {"objects", "is_staff", "is_superuser", "groups"}
        if isinstance(node, ast.ImportFrom):
            assert node.module not in {
                ".models",
                "models",
                "verification_models",
                "restriction_models",
            }


def test_case_projection_does_not_expand_owner_or_command_dtos():
    from apps.professionals.contracts import VerificationTargetDTO

    assert set(VerificationTargetDTO.__dataclass_fields__) == {
        "id",
        "target",
        "state",
        "version",
    }


def test_staff_native_bootstrap_private_without_cached_case(monkeypatch):
    from apps.professionals import staff_views

    request = RequestFactory().get("/staff/professional-verification/queue/")
    request.session = {}
    monkeypatch.setattr("apps.assets.views.current_actor", lambda *args: object())
    result = staff_views.queue(request)
    assert result.status_code == 200
    assert result["Cache-Control"] == "private, no-store"
    assert result["X-Content-Type-Options"] == "nosniff"
    assert b'dir="rtl"' in result.content and b'lang="fa"' in result.content
    assert not request.session
