"""Installed C04 consumes source authority only through composition roots."""

from pathlib import Path

from tests.unit.c03.test_scope_boundary import imported_modules

ROOT = Path(__file__).resolve().parents[3]


def forbidden(source, package):
    return [
        n
        for n in imported_modules(source, package)
        if n.startswith(("apps.professionals", "apps.athletes"))
    ]


def test_marketplace_never_imports_private_source_models():
    for path in (ROOT / "apps/marketplace").rglob("*.py"):
        assert not forbidden(
            path.read_text(), ".".join(path.parent.relative_to(ROOT).parts)
        )
    assert forbidden(
        "from apps.professionals.models import ProfessionalProfile", "apps.marketplace"
    )
    assert forbidden("from ..athletes import selectors", "apps.marketplace")
