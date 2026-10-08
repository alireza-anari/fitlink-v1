"""Reject loss of inherited gates and fail closed before running service tests."""

import hashlib
import os
import re
import socket
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github/workflows/ci.yml"
ENTRY = ROOT / "docker/verify_c03_incremental.sh"
TRIGGER = "    branches: [accounts/c02-cloud, profiles/c03-cloud]"
C03_STEP = """      - name: C03 cumulative installed PostgreSQL contracts
        if: github.ref == 'refs/heads/profiles/c03-cloud'
        run: sh docker/verify_c03_incremental.sh
"""
C03_STORAGE_JOB = """  c03-storage:
    if: github.ref == 'refs/heads/profiles/c03-cloud'
    runs-on: ubuntu-24.04
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@d0cc045d04ccac9d8b7881df0226f9e82c39688e
        with:
          version: '0.12.19'
          python-version: '3.13.15'
          enable-cache: false
      - name: Frozen private storage gate environment
        run: uv sync --frozen --group dev
      - name: C03 real private MinIO and owned upload contracts
        run: sh docker/verify_c03_storage.sh
"""
# Exact approved C02 workflow blob, before the narrowly authorized extension.
C02_WORKFLOW_BLOB = "2f1f36ff45ca9ec8537413c2403640f9bb151bbe"


def inherited_workflow_is_intact(source):
    inherited = source.replace(TRIGGER, "    branches: [accounts/c02-cloud]")
    inherited = inherited.replace(C03_STEP, "")
    inherited = inherited.replace(C03_STORAGE_JOB, "")
    data = inherited.encode()
    digest = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data)
    return digest.hexdigest() == C02_WORKFLOW_BLOB


def test_only_two_literal_push_branches_no_pr_or_wildcard():
    source = WORKFLOW.read_text()
    assert TRIGGER in source
    assert "pull_request:" not in source
    branches = re.search(r"branches: \[([^\]]+)\]", source).group(1).split(", ")
    for branch, expected in (
        ("accounts/c02-cloud", True),
        ("profiles/c03-cloud", True),
        ("main", False),
        ("foundation/c01-cloud", False),
        ("profiles/c03-plan", False),
        ("profiles/other", False),
    ):
        assert (branch in branches) is expected


def test_accounts_branch_retains_all_existing_gates():
    assert inherited_workflow_is_intact(WORKFLOW.read_text())


def test_c03_branch_runs_inherited_plus_installed_gates():
    source = WORKFLOW.read_text()
    assert source.count(C03_STEP) == 1
    assert inherited_workflow_is_intact(source)


def test_c03_conditions_cannot_exclude_c02_regression():
    source = WORKFLOW.read_text()
    assert source.count("        if:") == 1
    assert C03_STEP in source
    assert inherited_workflow_is_intact(source)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("sh docker/verify_c02.sh", "true"),
        ("uv run --frozen pytest tests/unit", "uv run --frozen pytest tests/unit/c03"),
        ("75c551e5b9bbbfb7777ee52b09a1993b681e921a", "main"),
        ("  foundation:\n", "  foundation:\n    if: false\n"),
        ("    timeout-minutes: 60", "    continue-on-error: true"),
        ("    branches: [", "    branches: [main, "),
        ("tests/integration/c02", "tests/integration/c03"),
    ],
)
def test_inherited_gate_mutations_rejected(old, new):
    source = WORKFLOW.read_text()
    assert old in source
    assert not inherited_workflow_is_intact(source.replace(old, new, 1))


def test_required_service_unavailable_is_failure():
    assert ENTRY.is_file(), "C03 cumulative service entry point is missing"
    with socket.socket() as unavailable:
        unavailable.bind(("127.0.0.1", 0))
        env = {
            **os.environ,
            "POSTGRES_HOST": "127.0.0.1",
            "POSTGRES_PORT": str(unavailable.getsockname()[1]),
        }
        result = subprocess.run(
            ["sh", str(ENTRY)],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=20,
        )
    assert result.returncode != 0
    assert "C03 PostgreSQL/Redis readiness failed" in result.stdout
    assert "passed" not in result.stdout


def test_private_storage_probe_starts_from_script_path_and_fails_closed():
    with socket.socket() as unavailable:
        unavailable.bind(("127.0.0.1", 0))
        result = subprocess.run(
            [
                "uv",
                "run",
                "--frozen",
                "python",
                str(ROOT / "docker/c03_storage_probe.py"),
            ],
            cwd=ROOT,
            env={
                **os.environ,
                "POSTGRES_HOST": "127.0.0.1",
                "POSTGRES_PORT": str(unavailable.getsockname()[1]),
            },
            capture_output=True,
            text=True,
            timeout=20,
        )
    assert result.returncode != 0
    assert "C03 PostgreSQL/Redis/private MinIO readiness failed" in result.stdout
    assert "ModuleNotFoundError" not in result.stderr
    assert "passed" not in result.stdout


def test_every_installed_mandatory_c03_test_selected():
    assert ENTRY.is_file(), "C03 cumulative test selection is missing"
    source = ENTRY.read_text() + (ROOT / "docker/verify_c03_storage.sh").read_text()
    installed = {
        str(path.relative_to(ROOT))
        for folder in ("tests/unit/c03", "tests/integration/c03")
        for path in (ROOT / folder).glob("test_*.py")
    }
    selected = set(re.findall(r"tests/(?:unit|integration)/c03/test_[\w]+\.py", source))
    assert selected == installed
    assert "--strict-markers" in source


def test_task1_sql_evidence_covers_all_installed_migrations():
    source = ENTRY.read_text()
    for label in ("athletes", "professionals", "assets", "governance"):
        for migration in (ROOT / "apps" / label / "migrations").glob("[0-9]*.py"):
            number = migration.name.split("_", 1)[0]
            if label == "governance" and int(number) <= 10:
                continue
            assert f"sqlmigrate {label} {number}" in source


def test_task2_profile_authority_and_races_are_mandatory():
    selected = set(
        re.findall(r"tests/(?:unit|integration)/c03/test_[\w]+\.py", ENTRY.read_text())
    )
    assert {
        "tests/unit/c03/test_profile_policy.py",
        "tests/integration/c03/test_owned_profiles.py",
        "tests/integration/c03/test_profile_races.py",
    } <= selected


def test_task3_baseline_consent_and_races_are_mandatory():
    source = ENTRY.read_text()
    for suite in (
        "test_baseline_fields",
        "test_consent_callback_contract",
        "test_baseline_workflow",
        "test_baseline_consent",
        "test_baseline_races",
    ):
        assert suite + ".py" in source


def test_private_storage_gate_installed_by_task4():
    assert WORKFLOW.read_text().count(C03_STORAGE_JOB) == 1
    gate = ROOT / "docker/verify_c03_storage.sh"
    assert gate.is_file(), "Task 4 real storage gate absent"
    source = gate.read_text()
    assert "build minio minio-init checks" in source
    assert "up -d --wait db redis minio" in source
    for suite in (
        "test_private_assets.py",
        "test_upload_lifecycle.py",
        "test_upload_races.py",
        "test_minio_storage.py",
        "test_storage.py",
    ):
        assert suite in source
    assert "continue-on-error" not in WORKFLOW.read_text()
    assert "-v" not in source.split("cleanup()", 1)[1].split("}", 1)[0]


@pytest.mark.parametrize(
    "old,new",
    [
        ("refs/heads/profiles/c03-cloud", "refs/heads/accounts/c02-cloud"),
        ("sh docker/verify_c03_storage.sh", "true"),
        ("    timeout-minutes: 30", "    continue-on-error: true"),
    ],
)
def test_storage_job_mutations_rejected(old, new):
    source = WORKFLOW.read_text()
    assert C03_STORAGE_JOB in source
    assert not inherited_workflow_is_intact(
        source.replace(C03_STORAGE_JOB, C03_STORAGE_JOB.replace(old, new))
    )
