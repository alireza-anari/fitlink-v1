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


def test_staff_api_passes_exact_decision_to_existing_command(monkeypatch):
    from dataclasses import asdict
    from types import SimpleNamespace

    from apps.professionals import staff_api
    from apps.professionals.contracts import VerificationStaffDTO
    from config.use_cases import professional_verification as commands

    identifier = uuid4()
    values = {
        "target_uuid": uuid4(),
        "decision": "approve",
        "expected_case_version": 3,
        "expected_target_version": 2,
        "expected_binding": object(),
        "step_up_id": uuid4(),
        "reason_code": "credentials_approved",
        "explanation": "Synthetic bounded explanation",
        "operation_id": uuid4(),
    }
    actor = object()
    called = []
    result = VerificationStaffDTO(identifier, "under_review", 4, None, (), "", (), None)

    def decide(actual_actor, **kwargs):
        called.append((actual_actor, kwargs))
        return result

    monkeypatch.setattr(commands, "decide_verification_target", decide)
    view = staff_api.StaffView(command="decide")
    monkeypatch.setattr(view, "actor", lambda request: actor)
    monkeypatch.setattr(view, "payload", lambda request, serializer: dict(values))
    response = view.post(SimpleNamespace(), identifier)
    assert response.status_code == 200, "Missing staff decision command adapter"
    assert response.data == asdict(result)
    assert called[0][0] is actor
    assert called[0][1]["verification_uuid"] == identifier
    assert {
        k: v for k, v in called[0][1].items() if k not in {"verification_uuid", "at"}
    } == values


@pytest.mark.parametrize(
    "binding",
    [
        {"evidence_revision": True},
        {"owner": str(uuid4())},
        {"restriction_token": {"episodes": [[str(uuid4()), 1, "false"]]}},
    ],
)
def test_staff_binding_rejects_forged_types_unknown_keys(binding):
    from apps.professionals.serializers import StaffBinding

    values = {
        "evidence_revision": 1,
        "decision_version": 1,
        "declaration_version": 1,
        "snapshot_hash": "a" * 64,
        "restriction_token": {"episodes": []},
    }
    values.update(binding)
    assert not StaffBinding(data=values).is_valid()


def test_staff_binding_roundtrip_does_not_derive_current_authority():
    from apps.professionals.serializers import StaffBinding

    values = {
        "evidence_revision": 3,
        "decision_version": 4,
        "declaration_version": 2,
        "snapshot_hash": "a" * 64,
        "restriction_token": {"episodes": []},
    }
    serializer = StaffBinding(data=values)
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data.evidence_revision == 3
    assert serializer.validated_data.restriction_token.episodes == ()


def test_native_staff_hidden_binding_roundtrip_preserves_typed_command():
    from types import SimpleNamespace

    from apps.professionals.contracts import StaffReviewTargetDTO
    from apps.professionals.restrictions import RestrictionToken
    from apps.professionals.staff_forms import DecisionForm, RoleForm
    from apps.professionals.staff_views import case_forms
    from apps.professionals.verification_selectors import TargetReviewBinding

    token = RestrictionToken(((uuid4(), 2, True),))
    binding = TargetReviewBinding(2, 3, 1, "a" * 64, token)
    target = StaffReviewTargetDTO(
        uuid4(), "coach", "under_review", 2, uuid4(), 4, None, binding
    )
    row = case_forms(
        SimpleNamespace(version=3, review_targets=(target,)), {"step_up_id": uuid4()}
    )["review_rows"][0]
    for cls, name in ((DecisionForm, "decision_form"), (RoleForm, "restrict_form")):
        rendered = row[name]
        submitted = {field.name: field.value() for field in rendered}
        if cls is DecisionForm:
            submitted.update(
                decision="approve", explanation="Synthetic bounded explanation"
            )
        parsed = cls(submitted)
        assert parsed.is_valid(), parsed.errors
        if cls is DecisionForm:
            assert parsed.cleaned_data["expected_binding"] == binding
        else:
            assert parsed.cleaned_data["expected_restriction_token"] == token
