"""C03 private DTO and explicit future-domain absence contracts."""

import ast
import importlib
import importlib.util
from dataclasses import fields, is_dataclass
from pathlib import Path

import pytest
from django.apps import apps
from django.urls import Resolver404, resolve

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[3]
FUTURE = {
    "marketplace",
    "discovery",
    "publication",
    "packages",
    "billing",
    "crm",
    "relationships",
    "workouts",
    "nutrition",
    "messaging",
    "appointments",
    "reviews",
    "ai",
    "health",
    "tracking",
    "goals",
    "progress",
}


def imported_modules(source):
    result = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            result.extend(item.name for item in node.names)
        if isinstance(node, ast.ImportFrom) and not node.level:
            result.append(node.module or "")
            result.extend((node.module or "") + "." + item.name for item in node.names)
    return result


def future_imports(source):
    return [
        name
        for name in imported_modules(source)
        if any(
            name == f"apps.{domain}" or name.startswith(f"apps.{domain}.")
            for domain in FUTURE
        )
    ]


@pytest.mark.parametrize("domain", sorted(FUTURE))
def test_future_dependency_negative_mutations(domain):
    assert future_imports(f"from apps.{domain} import services")
    assert future_imports(f"import apps.{domain}.services")


def test_no_c04_route_index_projection_or_c09_fields():
    assert not (FUTURE & {config.label for config in apps.get_app_configs()})
    forbidden_models = {
        "PublicProfessionalProfile",
        "ProfessionalProjection",
        "SearchIndex",
        "HealthLimitationsProfile",
        "HealthDeclaration",
        "ProgressPhoto",
        "ClientAssignment",
        "AssistantInvitation",
        "Subscription",
        "CoachingPlan",
    }
    assert not (forbidden_models & {model.__name__ for model in apps.get_models()})
    for name in ("athletes", "professionals", "assets"):
        for path in (ROOT / "apps" / name).rglob("*.py"):
            assert not future_imports(path.read_text()), path.relative_to(ROOT)
    for label in ("athletes", "professionals"):
        for model in apps.get_app_config(label).get_models():
            assert not (
                {
                    "slug",
                    "is_public",
                    "published_at",
                    "health_history",
                    "injuries",
                    "medications",
                    "allergies",
                    "client_id",
                }
                & {field.name for field in model._meta.fields}
            )


@pytest.mark.parametrize(
    "path",
    [
        "/professional/preview/",
        "/api/v1/professional/preview/",
        "/professionals/example/",
        "/api/v1/professionals/",
        "/marketplace/",
        "/search/",
        "/sitemap.xml",
        "/api/v1/professional/assistants/",
        "/assistant/activate/",
        "/api/v1/health/",
        "/api/v1/inbox/",
        "/api/v1/plans/",
    ],
)
def test_task10_installs_no_public_or_assistant_adapters(path):
    with pytest.raises(Resolver404):
        resolve(path)


def test_preview_dto_is_explicit_and_contains_no_internal_binding():
    module = importlib.import_module("apps.professionals.contracts")
    assert hasattr(module, "OwnerPreviewDTO"), "Missing private preview DTO"
    cls = module.OwnerPreviewDTO
    assert is_dataclass(cls) and cls.__dataclass_params__.frozen
    names = {field.name for field in fields(cls)}
    assert {
        "identity_verified",
        "identity_status",
        "roles",
        "verified_roles",
        "cache_control",
        "robots",
        "media",
    } <= names
    assert not (
        {
            "identity_name",
            "credentials",
            "evidence",
            "evidence_binding",
            "source_asset",
            "source_key",
            "snapshot_hash",
            "explanation",
            "publication_url",
            "slug",
            "fields",
        }
        & names
    )


@pytest.mark.parametrize(
    "module,commands",
    [
        ("apps.professionals.preview", ("owner_preview",)),
        (
            "apps.professionals.assistants",
            ("define_assistant_role", "revoke_assistant_role"),
        ),
    ],
)
def test_private_boundaries_exist_without_public_routes(module, commands):
    assert importlib.util.find_spec(module), f"Missing private boundary: {module}"
    loaded = importlib.import_module(module)
    assert all(callable(getattr(loaded, name, None)) for name in commands)
