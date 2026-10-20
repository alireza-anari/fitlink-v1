"""Current-stage metadata additions cannot weaken populated preservation."""

import copy
import json
from types import SimpleNamespace

import pytest
from django.apps import apps

from docker.c03_upgrade_probe import verify_preservation

pytestmark = pytest.mark.unit


def upgrade_metadata(monkeypatch):
    monkeypatch.setattr(
        "django.db.migrations.loader.MigrationLoader",
        lambda connection: SimpleNamespace(disk_migrations={}),
    )
    before = {
        "database_oid": 1,
        "tables": {
            name: {"oid": oid, "count": 0, "rows": []}
            for oid, name in enumerate(
                (
                    "accounts_user",
                    "django_migrations",
                    "django_content_type",
                    "auth_permission",
                ),
                start=1,
            )
        },
    }
    after = copy.deepcopy(before)
    for model in apps.get_models():
        if model._meta.app_label not in {
            "assets",
            "athletes",
            "professionals",
            "marketplace",
        }:
            continue
        index = len(after["tables"]["django_content_type"]["rows"]) + 1
        after["tables"]["django_content_type"]["rows"].append(
            json.dumps(
                {
                    "id": index,
                    "app_label": model._meta.app_label,
                    "model": model._meta.model_name,
                }
            )
        )
        for verb in model._meta.default_permissions:
            rows = after["tables"]["auth_permission"]["rows"]
            rows.append(
                json.dumps(
                    {
                        "id": len(rows) + 1,
                        "content_type_id": index,
                        "codename": f"{verb}_{model._meta.model_name}",
                        "name": f"Can {verb} {model._meta.verbose_name_raw}",
                    }
                )
            )
    for table in after["tables"].values():
        table["count"] = len(table["rows"])
    return before, after


def test_current_stage_accepts_exact_marketplace_installation_metadata(monkeypatch):
    before, after = upgrade_metadata(monkeypatch)
    assert verify_preservation(before, after)


@pytest.mark.parametrize("defect", ["future_type", "permission", "business_row"])
def test_current_stage_keeps_exact_preservation_rejections(monkeypatch, defect):
    before, after = upgrade_metadata(monkeypatch)
    if defect == "future_type":
        table = after["tables"]["django_content_type"]
        table["rows"].append(
            json.dumps(
                {
                    "id": 900,
                    "app_label": "payments",
                    "model": "charge",
                }
            )
        )
        table["count"] += 1
    elif defect == "permission":
        table = after["tables"]["auth_permission"]
        table["rows"].pop()
        table["count"] -= 1
    else:
        after["tables"]["marketplace_publicprofessionalprojection"] = {
            "oid": 999,
            "count": 1,
            "rows": ["{}"],
        }
    with pytest.raises(AssertionError, match="preservation"):
        verify_preservation(before, after)
