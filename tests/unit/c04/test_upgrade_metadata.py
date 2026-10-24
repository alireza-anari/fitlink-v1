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
    before, after = task7_metadata(monkeypatch)
    assert verify_preservation(before, after)


@pytest.mark.parametrize("defect", ["future_type", "permission", "business_row"])
def test_current_stage_keeps_exact_preservation_rejections(monkeypatch, defect):
    before, after = task7_metadata(monkeypatch)
    assert verify_preservation(before, after)
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


def task7_metadata(monkeypatch):
    before, after = upgrade_metadata(monkeypatch)
    names = {
        "moderationcase",
        "moderationhistory",
        "publiccontentreport",
        "publiccontentoperation",
    }
    for model in apps.get_models():
        if model._meta.app_label != "governance" or model._meta.model_name not in names:
            continue
        rows = after["tables"]["django_content_type"]["rows"]
        identifier = len(rows) + 1
        rows.append(
            json.dumps(
                {
                    "id": identifier,
                    "app_label": "governance",
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
                        "content_type_id": identifier,
                        "codename": f"{verb}_{model._meta.model_name}",
                        "name": f"Can {verb} {model._meta.verbose_name_raw}",
                    }
                )
            )
        after["tables"][model._meta.db_table] = {
            "oid": 20000 + identifier,
            "count": 0,
            "rows": [],
        }
    for table in after["tables"].values():
        table["count"] = len(table["rows"])
    return before, after


def test_task7_populated_upgrade_accepts_only_exact_moderation_metadata(monkeypatch):
    before, after = task7_metadata(monkeypatch)
    assert verify_preservation(before, after)


def test_preservation_failure_predicate_never_exports_arbitrary_exception_text():
    from docker import c03_upgrade_probe as probe

    classifier = getattr(probe, "preservation_predicate", None)
    assert callable(classifier), "Missing finite preservation predicate classifier"
    assert classifier(AssertionError("preservation exact C03 content types")) == (
        "exact_content_types"
    )
    for error in [
        AssertionError("private-sentinel"),
        RuntimeError("private-sentinel"),
        AssertionError(),
        AssertionError("x", "private-sentinel"),
    ]:
        assert classifier(error) == "unknown"


def test_preservation_diagnostic_keeps_original_prefix_and_deadlines():
    from pathlib import Path

    from docker.c04_preservation_observation import prefix

    source = Path("docker/verify_c03.sh").read_text()
    original = source.split("# Deliberate C03 commands only after exact preservation")[
        0
    ]
    observed = prefix(source)
    assert (
        observed.replace(
            "docker/c04_preservation_probe.py /rehearsal/metadata.json",
            "docker/c03_upgrade_probe.py verify /rehearsal/metadata.json",
        )
        == original
    )
    assert "900s docker compose" in observed
    assert "run_step exact_original_c02 original_c02" in observed
    assert "run_step populated_preservation" in observed
    for broken in [
        "unknown",
        source
        + "# Deliberate C03 commands only after exact preservation and session checks.",
    ]:
        with pytest.raises(ValueError):
            prefix(broken)


def populated_task7_metadata(monkeypatch):
    before, after = task7_metadata(monkeypatch)
    old = {
        "id": 10000,
        "app": "accounts",
        "name": "0001_initial",
        "applied": "2026-01-01T00:00:00Z",
    }
    installed = {
        ("accounts", "0001_initial"),
        ("professionals", "0019_c04_educational_posts"),
        ("assets", "0011_c04_educational_image_purpose"),
        ("governance", "0016_c04_public_moderation"),
    }
    monkeypatch.setattr(
        "django.db.migrations.loader.MigrationLoader",
        lambda connection: SimpleNamespace(disk_migrations=installed),
    )
    for state in (before, after):
        state["tables"]["django_migrations"]["rows"].append(json.dumps(old))
        state["tables"]["accounts_user"]["rows"].append(
            json.dumps({"id": 1, "auth_version": 1})
        )
    for index, (app, name) in enumerate(
        sorted(installed - {("accounts", "0001_initial")})
    ):
        after["tables"]["django_migrations"]["rows"].append(
            json.dumps(
                {
                    "id": 10001 + index,
                    "app": app,
                    "name": name,
                    "applied": "2026-01-02T00:00:00Z",
                }
            )
        )
    for state in (before, after):
        for table in state["tables"].values():
            table["count"] = len(table["rows"])
    return before, after


@pytest.mark.parametrize(
    "catalog", ["django_content_type", "auth_permission", "django_migrations"]
)
@pytest.mark.parametrize("defect", ["missing", "extra", "modified", "duplicate"])
def test_task7_preservation_rejects_inexact_catalog_sets(monkeypatch, catalog, defect):
    before, after = populated_task7_metadata(monkeypatch)
    assert verify_preservation(before, after), "Valid starting fixture is required"
    table = after["tables"][catalog]
    if defect == "missing":
        table["rows"].pop()
    else:
        row = json.loads(table["rows"][-1])
        if defect == "modified":
            row["model" if catalog == "django_content_type" else "name"] = "forged"
            table["rows"][-1] = json.dumps(row)
        else:
            row["id"] += 50000
            if defect == "extra":
                row["model" if catalog == "django_content_type" else "name"] = "future"
            table["rows"].append(json.dumps(row))
    table["count"] = len(table["rows"])
    with pytest.raises(AssertionError, match="preservation"):
        verify_preservation(before, after)


@pytest.mark.parametrize(
    "defect",
    ["database_oid", "table_oid", "row_value", "original_catalog", "missing_table"],
)
def test_task7_preservation_keeps_original_identity_and_data(monkeypatch, defect):
    before, after = populated_task7_metadata(monkeypatch)
    assert verify_preservation(before, after)
    if defect == "database_oid":
        after["database_oid"] += 1
    elif defect == "table_oid":
        after["tables"]["accounts_user"]["oid"] += 1
    elif defect == "row_value":
        after["tables"]["accounts_user"]["rows"] = [
            json.dumps({"id": 1, "auth_version": 2})
        ]
    elif defect == "original_catalog":
        row = json.loads(after["tables"]["django_migrations"]["rows"][0])
        row["name"] = "changed_original"
        after["tables"]["django_migrations"]["rows"][0] = json.dumps(row)
    else:
        del after["tables"]["accounts_user"]
    with pytest.raises(AssertionError, match="preservation"):
        verify_preservation(before, after)


@pytest.mark.parametrize(
    "model",
    [
        "moderationcase",
        "moderationhistory",
        "publiccontentreport",
        "publiccontentoperation",
    ],
)
def test_task7_upgrade_never_seeds_moderation_business_rows(monkeypatch, model):
    before, after = populated_task7_metadata(monkeypatch)
    assert verify_preservation(before, after)
    after["tables"]["governance_" + model].update(count=1, rows=['{"id":1}'])
    with pytest.raises(AssertionError, match="no automatic C03 business rows"):
        verify_preservation(before, after)
