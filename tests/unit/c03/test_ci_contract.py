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


def task6_selected(source):
    required = {
        "tests/unit/c03/test_professional_fields.py",
        "tests/unit/c03/test_verification_binding.py",
        "tests/integration/c03/test_professional_setup.py",
        "tests/integration/c03/test_credential_revisions.py",
        "tests/integration/c03/test_bound_edit_races.py",
    }
    return required <= set(
        re.findall(r"tests/(?:unit|integration)/c03/test_[\w]+\.py", source)
    )


def test_task6_mandatory_selections_cannot_be_omitted():
    source = ENTRY.read_text()
    assert task6_selected(source), "Task 6 mandatory selection missing"
    for name in (
        "test_professional_fields",
        "test_verification_binding",
        "test_professional_setup",
        "test_credential_revisions",
        "test_bound_edit_races",
    ):
        assert not task6_selected(source.replace(name + ".py", "omitted.py"))


def test_task7_mandatory_selections_cannot_be_omitted():
    source = ENTRY.read_text()
    required = (
        "tests/unit/c03/test_verification_contract.py",
        "tests/integration/c03/test_verification_submission.py",
        "tests/integration/c03/test_verification_staff.py",
        "tests/integration/c03/test_verification_assignment_races.py",
    )
    assert all(name in source for name in required), "Task 7 selection missing"
    for name in required:
        assert not all(item in source.replace(name, "omitted") for item in required)


def test_task8_mandatory_selections_cannot_be_omitted():
    source = ENTRY.read_text()
    required = (
        "tests/unit/c03/test_publication_eligibility.py",
        "tests/integration/c03/test_verification_decisions.py",
        "tests/integration/c03/test_verification_decision_races.py",
        "tests/integration/c03/test_verification_revocation.py",
    )
    assert all(name in source for name in required), "Task 8 selection missing"
    for name in required:
        assert not all(item in source.replace(name, "omitted") for item in required)


def test_task9_lifetime_holds_cleanup_and_races_are_mandatory():
    source = ENTRY.read_text()
    required = (
        "tests/unit/c03/test_privacy_inventory.py",
        "tests/integration/c03/test_asset_holds.py",
        "tests/integration/c03/test_c03_deletion_effects.py",
        "tests/integration/c03/test_asset_cleanup_races.py",
    )
    assert all(name in source for name in required), "Task 9 selection missing"
    for name in required:
        assert not all(item in source.replace(name, "omitted") for item in required)


TRIGGER = "    branches: [accounts/c02-cloud, profiles/c03-cloud]"


def test_task14_exact_upgrade_final_job_cannot_be_omitted_or_weakened():
    workflow = (ROOT / ".github/workflows/ci.yml").read_text()

    def valid(source):
        marker = "  c03-final:\n"
        if marker not in source:
            return False
        final = source.split(marker, 1)[1]
        required = (
            "    if: github.ref == 'refs/heads/profiles/c03-cloud'\n",
            "ref: 0905be6c6ca608d469fe33e87f514b22591132d1",
            "path: .runtime/c02",
            "ref: 75c551e5b9bbbfb7777ee52b09a1993b681e921a",
            "path: .runtime/c02/.runtime/c01",
            "pytest tests/unit/c03/test_exact_baseline.py -q --strict-markers",
            "        run: sh docker/verify_c03.sh\n",
            ".runtime/c03-foundation-evidence/*.jsonl",
            "if-no-files-found: error",
        )
        return all(item in final for item in required) and not any(
            item in final
            for item in (
                "continue-on-error",
                "--deselect",
                "--reuse-db",
                "-m 'not",
                "|| true",
            )
        )

    assert valid(workflow)
    for old, new in (
        (
            "run: sh docker/verify_c03.sh",
            "run: pytest tests/integration/c03/test_c03_migrations.py",
        ),
        ("run: sh docker/verify_c03.sh", "run: echo fake-only-upgrade"),
        (
            "run: sh docker/verify_c03.sh",
            "run: sh docker/verify_c03.sh --native-processing-diagnostic",
        ),
        ("run: sh docker/verify_c03.sh", "run: sh docker/verify_foundation.sh"),
        ("ref: 0905be6c6ca608d469fe33e87f514b22591132d1", "ref: main"),
        ("path: .runtime/c02/.runtime/c01", "path: omitted"),
        (
            "run: sh docker/verify_c03.sh",
            "continue-on-error: true\n        run: sh docker/verify_c03.sh",
        ),
    ):
        assert not valid(workflow.replace(old, new))


def test_task10_private_preview_assistant_scope_dependency_gates_mandatory():
    source = ENTRY.read_text()
    required = (
        "tests/unit/c03/test_scope_boundary.py",
        "tests/integration/c03/test_owner_preview.py",
        "tests/integration/c03/test_assistant_primitive.py",
        "tests/integration/c03/test_c03_dependency_direction.py",
    )
    assert all(name in source for name in required), "Task 10 selection missing"
    for name in required:
        assert not all(item in source.replace(name, "omitted") for item in required)


C03_STEP = r"""      - name: C03 cumulative installed PostgreSQL contracts
        if: github.ref == 'refs/heads/profiles/c03-cloud'
        run: |
          python docker/c03_gate_diagnostics.py --acceptance postgresql \
            sh docker/verify_c03_incremental.sh
"""
C03_STORAGE_JOB = r"""  c03-storage:
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
        run: |
          python docker/c03_storage_slice.py
"""
DIAGNOSTIC_FOUNDATION = r"""        run: |
          if [ "$GITHUB_REF" = refs/heads/profiles/c03-cloud ]; then
            python docker/c03_foundation_evidence.py
          else
            sh docker/verify_c02.sh
          fi
"""
DIAGNOSTIC_ARTIFACT = """      - name: C03 bounded diagnostic evidence
        if: always() && github.ref == 'refs/heads/profiles/c03-cloud'
        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02
        with:
          name: c03-{phase}-diagnostics
          path: .runtime/c03-diagnostics/*.jsonl
          include-hidden-files: true
          if-no-files-found: error
"""
TIMEOUT_PROBE = """  c03-timeout-probe:
    if: github.ref == 'refs/heads/profiles/c03-cloud'
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262
        with:
          persist-credentials: false
      - name: Isolated actual Compose timeout ownership probe
        run: python docker/c03_timeout_probe.py
"""
FOUNDATION_ARTIFACT = DIAGNOSTIC_ARTIFACT.format(phase="foundation").replace(
    "          path: .runtime/c03-diagnostics/*.jsonl",
    "          path: |\n            .runtime/c03-diagnostics/*.jsonl\n"
    "            .runtime/c03-foundation-evidence/*.jsonl",
)

STORAGE_ARTIFACT = DIAGNOSTIC_ARTIFACT.format(phase="storage").replace(
    "          path: .runtime/c03-diagnostics/*.jsonl",
    "          path: |\n"
    "            .runtime/c03-diagnostics/*.jsonl\n"
    "            .runtime/c03-triage/*.jsonl",
)
PROCESSING_ARTIFACT = STORAGE_ARTIFACT.replace(
    "c03-storage-diagnostics", "c03-processing-diagnostics"
)
C03_PROCESSING_JOB = """  c03-processing:
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
      - name: Frozen processing gate environment
        run: uv sync --frozen --group dev
      - name: C03 real scanner and durable non-eager worker
        run: python docker/c03_processing_evidence.py
"""

TASK8_REPORT = """      - name: Task 8 metadata-only PostgreSQL verdict
        if: always() && github.ref == 'refs/heads/profiles/c03-cloud'
        run: sh docker/verify_c03_incremental.sh --task8-evidence
"""

# Exact approved C02 workflow blob, before the narrowly authorized extension.
C02_WORKFLOW_BLOB = "2f1f36ff45ca9ec8537413c2403640f9bb151bbe"
TASK14_FIXTURE = """      - name: Immutable completed C02 fixture for Task 14
        if: github.ref == 'refs/heads/profiles/c03-cloud'
        uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262
        with:
          ref: 0905be6c6ca608d469fe33e87f514b22591132d1
          path: .runtime/c02
          persist-credentials: false
      - name: Verify exact C02 source tree before use
        if: github.ref == 'refs/heads/profiles/c03-cloud'
        run: python docker/c03_baseline.py .runtime/c02
"""
TASK14_FOCUSED = """      - name: Task 14 focused behavioral contracts on real PostgreSQL
        if: github.ref == 'refs/heads/profiles/c03-cloud'
        env:
          C03_FOUNDATION_TRIAGE: '1'
          C03_FOUNDATION_EVIDENCE_DIRECTORY: .runtime/c03-diagnostics
        run: |
          mkdir .runtime/task14-focused-private
          chmod 700 .runtime/task14-focused-private
          umask 077
          result=0
          timeout -k 10s 180s uv run --frozen pytest tests/unit/c03/test_exact_baseline.py tests/unit/c03/test_final_rehearsal.py tests/integration/c03/test_upgrade_from_c02.py -q --strict-markers --tb=no --show-capture=no >.runtime/task14-focused-private/pytest.log 2>&1 || result=$?
          uv run --frozen python -c 'import json; from docker.c03_upgrade_probe import private_log_metadata; print("C03_TASK14_FOCUSED " + json.dumps(private_log_metadata(".runtime/task14-focused-private/pytest.log")))'
          exit "$result"
"""  # noqa: E501


def inherited_workflow_is_intact(source):
    inherited = source.replace(TRIGGER, "    branches: [accounts/c02-cloud]")
    inherited = re.sub(
        r"^  c03-(?:owner|staff|restart|evidence-audit|task14-native|final):\n"
        r".*?(?=^  [a-z][a-z0-9-]*:\n|\Z)",
        "",
        inherited,
        flags=re.M | re.S,
    )
    inherited = inherited.replace(TASK14_FIXTURE, "")
    inherited = inherited.replace(TASK14_FOCUSED, "")
    inherited = inherited.replace(
        DIAGNOSTIC_FOUNDATION, "        run: sh docker/verify_c02.sh\n"
    )
    for phase in ("postgresql", "timeout-probe"):
        inherited = inherited.replace(DIAGNOSTIC_ARTIFACT.format(phase=phase), "")
    inherited = inherited.replace(STORAGE_ARTIFACT, "")
    inherited = inherited.replace(FOUNDATION_ARTIFACT, "")
    inherited = inherited.replace(TIMEOUT_PROBE, "")
    inherited = inherited.replace(C03_STEP, "")
    inherited = inherited.replace(TASK8_REPORT, "")
    inherited = inherited.replace(C03_STORAGE_JOB, "")
    inherited = inherited.replace(C03_PROCESSING_JOB, "")
    inherited = inherited.replace(PROCESSING_ARTIFACT, "")
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
    assert source.count("        if:") == 20
    assert source.count(TASK8_REPORT) == 1
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
    source += (ROOT / "docker/verify_c03_processing.sh").read_text()
    source += (ROOT / "docker/verify_c03.sh").read_text()
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
        ("python docker/c03_storage_slice.py", "true"),
        ("    timeout-minutes: 30", "    continue-on-error: true"),
    ],
)
def test_storage_job_mutations_rejected(old, new):
    source = WORKFLOW.read_text()
    assert C03_STORAGE_JOB in source
    assert not inherited_workflow_is_intact(
        source.replace(C03_STORAGE_JOB, C03_STORAGE_JOB.replace(old, new))
    )


def test_real_scanner_non_eager_worker_gate_installed_by_task5():
    source = WORKFLOW.read_text()
    assert C03_PROCESSING_JOB in source
    gate = (ROOT / "docker/verify_c03_processing.sh").read_text()
    for name in (
        "scanner",
        "worker",
        "test_asset_processing.py",
        "test_processing_worker.py",
        "test_scanner_service.py",
        "test_image_sanitization.py",
        "test_scanner_contract.py",
    ):
        assert name in gate
    compose = (ROOT / "compose.yaml").read_text()
    assert "internal: true" in compose and "read_only: true" in compose
    assert "scanner-signatures:/var/lib/clamav:ro" in compose


def test_real_worker_crash_and_broker_restart_probe_is_mandatory():
    gate = (ROOT / "docker/verify_c03_processing.sh").read_text()
    for phase in (
        "prepare",
        "start",
        "recover",
        "scanner-outage",
        "scanner-restored",
        "periodic-prepare",
        "periodic-verify",
        "parent-death",
    ):
        assert "docker/c03_processing_probe.py " + phase in gate
    assert "kill -s SIGKILL worker" in gate
    assert "restart redis" in gate
    assert "--force-recreate worker" in gate


def test_private_reconciler_does_not_replace_inherited_beat():
    from config.c03_celery import app as private
    from config.celery import app as inherited

    assert inherited.conf.beat_schedule == {
        "c02-outbox-scan": {
            "task": "apps.governance.tasks.scan_pending",
            "schedule": 30.0,
        }
    }
    assert private.conf.beat_schedule == {
        "private-assets": {
            "task": "apps.assets.tasks.reconcile_private_assets",
            "schedule": 30.0,
        }
    }
    assert private.conf.task_always_eager is False
    assert '"config.c03_celery:app"' in (ROOT / "compose.yaml").read_text()


def owner_gate_valid(workflow, gate):
    match = re.search(
        r"^  c03-owner:\n.*?(?=^  [a-z][a-z0-9-]*:\n|\Z)", workflow, flags=re.M | re.S
    )
    if match is None:
        return False
    job = match.group()
    required = (
        "tests/unit/c03/test_api_schema.py",
        "tests/unit/c03/test_forms.py",
        "tests/unit/c03/test_native_adapters.py",
        "tests/integration/c03/test_owner_api.py",
        "tests/e2e/c03/test_owner_setup.py",
        "tests/e2e/c03/test_private_uploads.py",
        "tests/e2e/c02",
        "--strict-markers",
        "--tracing=off",
        "--screenshot=off",
        "--video=off",
        "dc up -d --wait db redis minio scanner",
        "dc up -d --wait web worker",
        "trap cleanup EXIT",
    )
    return (
        "    if: github.ref == 'refs/heads/profiles/c03-cloud'\n" in job
        and "sh docker/verify_c03_incremental.sh --task11-owner" in job
        and "--acceptance storage" in job
        and "continue-on-error" not in workflow
        and "pull_request:" not in workflow
        and TRIGGER in workflow
        and all(item in gate for item in required)
        and not any(
            re.search(r"(?:--ignore|--deselect|(?:^|\s)-(?:k|m)\s)", line)
            for line in gate.splitlines()
            if "pytest " in line
            for line in [line.split("pytest ", 1)[1]]
        )
    )


def test_owner_browser_gate_installed_by_task11():
    workflow, gate = WORKFLOW.read_text(), ENTRY.read_text()
    assert owner_gate_valid(workflow, gate)
    for required in (
        "tests/integration/c03/test_owner_api.py",
        "tests/e2e/c03/test_owner_setup.py",
        "tests/e2e/c03/test_private_uploads.py",
        "tests/e2e/c02",
        "dc up -d --wait db redis minio scanner",
        "trap cleanup EXIT",
    ):
        assert not owner_gate_valid(workflow, gate.replace(required, "omitted"))
    for old, new in (
        ("  c03-owner:", "  other:"),
        ("sh docker/verify_c03_incremental.sh --task11-owner", "true"),
        (TRIGGER, "    branches: [main, '*']"),
    ):
        assert not owner_gate_valid(workflow.replace(old, new), gate)
    assert not owner_gate_valid(workflow + "continue-on-error: true", gate)
    assert not owner_gate_valid(workflow + "pull_request:\n", gate)


@pytest.mark.parametrize(
    "option", ["-k fake", "--deselect=mandatory", "-m unit", "--ignore=tests/e2e/c03"]
)
def test_owner_gate_cannot_narrow_mandatory_selection(option):
    gate = ENTRY.read_text().replace(
        "tests/e2e/c03/test_owner_setup.py",
        "tests/e2e/c03/test_owner_setup.py " + option,
    )
    assert not owner_gate_valid(WORKFLOW.read_text(), gate)


def test_owner_job_wrong_branch_and_fake_only_rejected():
    workflow = WORKFLOW.read_text()
    job = re.search(
        r"^  c03-owner:\n.*?(?=^  [a-z][a-z0-9-]*:\n|\Z)", workflow, flags=re.M | re.S
    ).group()
    wrong = job.replace("refs/heads/profiles/c03-cloud", "refs/heads/main")
    assert not owner_gate_valid(workflow.replace(job, wrong), ENTRY.read_text())
    assert not owner_gate_valid(
        workflow,
        ENTRY.read_text().replace(
            "dc up -d --wait db redis minio scanner", "true # db redis minio scanner"
        ),
    )


def staff_gate_valid(workflow, gate):
    match = re.search(
        r"^  c03-staff:\n.*?(?=^  [a-z][a-z0-9-]*:\n|\Z)", workflow, flags=re.M | re.S
    )
    if match is None:
        return False
    job = match.group()
    marker = 'if [ "${1:-}" = --task12-staff ]; then'
    if marker not in gate or "\n# Read the existing" not in gate:
        return False
    block = gate.split(marker, 1)[1].split("\n# Read the existing", 1)[0]
    executable = [line.strip() for line in block.splitlines() if "#" not in line]
    required_commands = (
        "dc up -d --wait db redis minio scanner",
        "dc up -d --wait web worker",
        "dc run --rm minio-init",
        "dc exec -T scanner clamdscan "
        "--config-file=/etc/clamav/clamd.c03.conf --ping=1",
        'exec env C03_STAFF_CHILD=1 timeout -k 10s 900s sh "$0" --task12-staff',
        "trap cleanup EXIT",
        '[ "$backend_exit" -eq 0 ] && [ "$browser_exit" -eq 0 ]',
    )
    if not all(command in executable for command in required_commands):
        return False
    selections = (
        (
            "checks",
            "180",
            "tests/unit/c03/test_staff_adapters.py "
            "tests/integration/c03/test_verification_api.py",
            " || backend_exit=$?",
        ),
        (
            "browser",
            "240",
            "tests/e2e/c03/test_staff_verification.py",
            " --tracing=off --screenshot=off --video=off || browser_exit=$?",
        ),
        (
            "browser",
            "300",
            "tests/e2e/c02",
            " --tracing=off --screenshot=off --video=off",
        ),
    )
    for service, seconds, suites, suffix in selections:
        tail = (
            f"{service} timeout -k 10s {seconds}s uv run --frozen pytest "
            f"{suites} -q --strict-markers{suffix}"
        )
        if not any(
            line.startswith("dc run --rm --no-deps ") and line.endswith(tail)
            for line in executable
        ):
            return False
    return (
        "    if: github.ref == 'refs/heads/profiles/c03-cloud'\n" in job
        and "sh docker/verify_c03_incremental.sh --task12-staff" in job
        and "--acceptance storage" in job
        and owner_gate_valid(workflow, gate)
        and all(
            value in gate
            for value in (
                "tests/unit/c03/test_staff_adapters.py",
                "tests/integration/c03/test_verification_api.py",
                "tests/e2e/c03/test_staff_verification.py",
                "--task12-staff",
                "--tracing=off --screenshot=off --video=off",
            )
        )
    )


def test_task12_staff_api_browser_and_inherited_gates_mandatory():
    workflow, gate = WORKFLOW.read_text(), ENTRY.read_text()
    assert staff_gate_valid(workflow, gate)
    for item in (
        "tests/unit/c03/test_staff_adapters.py",
        "tests/integration/c03/test_verification_api.py",
        "tests/e2e/c03/test_staff_verification.py",
        "tests/e2e/c03/test_owner_setup.py",
        "tests/e2e/c02",
        "dc up -d --wait db redis minio scanner",
        "trap cleanup EXIT",
    ):
        assert not staff_gate_valid(workflow, gate.replace(item, "omitted"))
    for item in ("--task12-staff", "--acceptance storage", TRIGGER):
        assert not staff_gate_valid(workflow.replace(item, "omitted"), gate)
    for extra in (
        "continue-on-error: true",
        "pull_request:",
        "    branches: [main, '*']",
    ):
        assert not staff_gate_valid(workflow.replace(TRIGGER, extra), gate)


@pytest.mark.parametrize(
    "defect", ["services", "api_fake", "browser_fake", "skip", "timeout", "cleanup"]
)
def test_task12_gate_cannot_hide_missing_execution_in_owner_block(defect):
    workflow, gate = WORKFLOW.read_text(), ENTRY.read_text()
    start = gate.index('if [ "${1:-}" = --task12-staff ]; then')
    end = gate.index("\n# Read the existing", start)
    block = gate[start:end]
    if defect == "services":
        block = block.replace("dc up -d --wait db redis minio scanner", "true")
    elif defect == "api_fake":
        block = block.replace(
            "checks timeout -k 10s 180s uv run --frozen pytest", "checks true #"
        )
    elif defect == "browser_fake":
        block = block.replace(
            "browser timeout -k 10s 240s uv run --frozen pytest", "browser true #"
        )
    elif defect == "skip":
        block = block.replace(
            "--strict-markers || backend_exit=$?",
            "--strict-markers -m unit || backend_exit=$?",
        )
    elif defect == "timeout":
        block = block.replace("timeout -k 10s 900s", "true #")
    else:
        block = block.replace("trap cleanup EXIT", "true")
    assert not staff_gate_valid(workflow, gate[:start] + block + gate[end:])


TASK13_BLOCK_SHA256 = "e6182e62f7b8a90c4121df3d2a2368c80ef3951b8b6ef2d75c291c53937c208d"
TASK13_ENTRY_SHA256 = "e12dc145dd8e18f21e7d3f1d6481a317631aad07964df21f9fc4dd17f2738d06"
TASK13_JOB_SHA256 = {
    "c03-restart": "b27ceac7eb05ed777be063d4e4cebb29733ae9f95f70886afb0bfb9f292c6e22",
    "c03-evidence-audit": (
        "f0a08d28c4154064d46e513ab8cd78e52790c6f5b5fcdda37bb4147049954647"
    ),
}


def task13_installed(workflow, entry):
    if "# Task 13 bounded consolidation" not in entry or "# Task 11 uses" not in entry:
        return False
    block = entry.split("# Task 13 bounded consolidation", 1)[1].split(
        "# Task 11 uses", 1
    )[0]
    if hashlib.sha256(block.encode()).hexdigest() != TASK13_BLOCK_SHA256:
        return False
    from tests.unit.test_c03_foundation_evidence import (
        INHERITED_FOUNDATION_LENGTH,
        TASK13_SUFFIX,
        foundation_extension_valid,
    )

    body = (ROOT / "docker/verify_foundation.sh").read_bytes()
    if (
        not foundation_extension_valid(body)
        or body[INHERITED_FOUNDATION_LENGTH:] != TASK13_SUFFIX
    ):
        return False
    inherited_entry = entry.split("\n# Task 14 focused preservation negatives;", 1)[0]
    # Recorded C04 budget correction only. Keep the original source hash and
    # reject every other byte change; immutable C03 retains its original test.
    current_bound = 'exec env C03_GATE_CHILD=1 timeout -k 10s 450s sh "$0"'
    historical_bound = 'exec env C03_GATE_CHILD=1 timeout -k 10s 300s sh "$0"'
    if inherited_entry.count(current_bound) != 1 or historical_bound in inherited_entry:
        return False
    inherited_entry = inherited_entry.replace(current_bound, historical_bound, 1)
    if hashlib.sha256(inherited_entry.encode()).hexdigest() != TASK13_ENTRY_SHA256:
        return False
    required_jobs = {
        "c03-restart": "python docker/c03_asset_restart_probe.py run",
        "c03-evidence-audit": "python docker/c03_asset_restart_probe.py audit",
    }
    for name, command in required_jobs.items():
        match = re.search(
            rf"^  {name}:\n.*?(?=^  [a-z][a-z0-9-]*:\n|\Z)",
            workflow,
            flags=re.M | re.S,
        )
        if (
            not match
            or hashlib.sha256(match.group().encode()).hexdigest()
            != TASK13_JOB_SHA256[name]
            or command not in match.group().split("\n        run: ")[-1]
        ):
            return False
        if (
            "    if: github.ref == 'refs/heads/profiles/c03-cloud'\n"
            not in match.group()
        ):
            return False
    return (
        inherited_workflow_is_intact(workflow)
        and owner_gate_valid(workflow, entry)
        and 'if [ "${1:-}" = --task11-owner ]; then' in entry
        and staff_gate_valid(workflow, entry)
        and 'if [ "${1:-}" = --task13-restart ]; then' in entry
        and 'if [ "${1:-}" = --task13-foundation ]; then' in entry
        and "tests/integration/c03/test_c03_failure_recovery.py" in entry
        and "continue-on-error" not in workflow
        and "pull_request:" not in workflow
    )


def test_existing_c02_gates_not_removed():
    workflow, entry = WORKFLOW.read_text(), ENTRY.read_text()
    assert task13_installed(workflow, entry), "Task 13 consolidation is not installed"
    for item in ("tests/integration/c02", TRIGGER, "sh docker/verify_c02.sh"):
        assert not task13_installed(workflow.replace(item, "omitted"), entry)


def test_every_incremental_gate_still_installed():
    workflow, entry = WORKFLOW.read_text(), ENTRY.read_text()
    assert task13_installed(workflow, entry), "Task 13 resilience/evidence gate absent"
    for item in (
        "--task11-owner",
        "--task12-staff",
        "--task13-restart",
        "--task13-foundation",
        "tests/integration/c03/test_c03_failure_recovery.py",
    ):
        assert not task13_installed(workflow, entry.replace(item, "omitted"))


def test_completed_task_has_authoritative_service_evidence():
    from docker.c03_asset_restart_probe import completed_evidence_valid

    # Synthetic validator specimen only; never used as historical authority.
    record = {
        "expected_sha": "a" * 40,
        "expected_tree": "b" * 40,
        "head_sha": "a" * 40,
        "tree": "b" * 40,
        "event": "push",
        "head_branch": "profiles/c03-cloud",
        "status": "completed",
        "conclusion": "success",
        "id": 1,
        "required_jobs": ["foundation", "c02-migrations", "c03-processing"],
        "jobs": [
            {
                "id": i + 1,
                "name": name,
                "head_sha": "a" * 40,
                "conclusion": "success",
                "execution": {
                    "real": True,
                    "passed": 1,
                    "skipped": 0,
                    "exitstatus": 0,
                    "selections": [name],
                },
            }
            for i, name in enumerate(["foundation", "c02-migrations", "c03-processing"])
        ],
    }
    record.update(
        expected_spec_sha="c" * 40,
        expected_spec_tree="d" * 40,
        expected_spec_run=2,
        specification={
            "sha": "c" * 40,
            "tree": "d" * 40,
            "run_id": 2,
            "head_sha": "c" * 40,
            "status": "completed",
            "event": "push",
            "head_branch": "profiles/c03-cloud",
            "jobs": [2],
        },
    )
    assert completed_evidence_valid(record)
    import copy

    for defect in (
        "head",
        "tree",
        "absent",
        "skipped",
        "fake",
        "selection",
        "spec_absent",
        "spec_head",
        "spec_tree",
        "spec_run",
    ):
        bad = copy.deepcopy(record)
        if defect == "spec_absent":
            bad.pop("specification")
        elif defect.startswith("spec_"):
            key = {"spec_head": "sha", "spec_tree": "tree", "spec_run": "run_id"}[
                defect
            ]
            bad["specification"][key] = 3 if key == "run_id" else "f" * 40
        elif defect == "head":
            bad["head_sha"] = "c" * 40
        elif defect == "tree":
            bad["tree"] = "c" * 40
        elif defect == "absent":
            bad["jobs"].pop()
        else:
            field, value = {
                "skipped": ("skipped", 1),
                "fake": ("real", False),
                "selection": ("selections", []),
            }[defect]
            bad["jobs"][-1]["execution"][field] = value
        assert not completed_evidence_valid(bad), defect


@pytest.mark.parametrize(
    "old,new",
    [
        ("dc kill -s SIGKILL worker", "true # dc kill -s SIGKILL worker"),
        ("dc restart redis minio scanner", "dc restart redis"),
        ("timeout -k 10s 600s", "true # timeout -k 10s 600s"),
        ("probe verify", "echo probe verify"),
        ("trap cleanup EXIT", "true"),
        ("--strict-markers", "--strict-markers -k safe"),
        (
            "tests/e2e/c03/test_staff_verification.py",
            "tests/e2e/c03/test_owner_setup.py",
        ),
    ],
)
def test_task13_exact_owned_processes_and_selections_cannot_be_weakened(old, new):
    entry = ENTRY.read_text()
    assert old in entry
    assert not task13_installed(WORKFLOW.read_text(), entry.replace(old, new))


def test_task13_worker_barriers_keep_canonical_broker_names():
    from docker.c03_asset_restart_probe import crash_at_write, stale_delivery

    assert crash_at_write.name == "docker.c03_asset_restart_probe.crash_at_write"
    assert stale_delivery.name == "docker.c03_asset_restart_probe.stale_delivery"
    assert (
        "run: uv run --frozen python docker/c03_asset_restart_probe.py run"
        in WORKFLOW.read_text()
    )


@pytest.mark.parametrize(
    "name,log",
    [
        ("c03-storage", 'C03_X {"event":"pytest_exit","exitstatus":0}\n91 passed\n'),
        (
            "c03-owner",
            'C03_X {"event":"pytest_exit","exitstatus":0}\n' * 2 + "75 passed\n",
        ),
        ("foundation", "c02_baseline.py\n311 passed\n710 passed\n38 passed\n"),
        ("c02-migrations", "269 passed\ndurable redis-cli\n"),
    ],
)
def test_task13_count_only_fake_execution_is_rejected(name, log):
    from docker.c03_asset_restart_probe import log_evidence

    with pytest.raises(AssertionError):
        log_evidence(name, log)


def test_task13_early_success_cannot_bypass_protected_modes():
    entry = ENTRY.read_text().replace(
        "set -eu\n", 'set -eu\nif [ "${1:-}" = --task13-restart ]; then exit 0; fi\n', 1
    )
    assert not task13_installed(WORKFLOW.read_text(), entry)


def test_task13_installed_contract_requires_foundation_suffix(monkeypatch):
    from tests.unit.test_c03_foundation_evidence import INHERITED_FOUNDATION_LENGTH

    path = ROOT / "docker/verify_foundation.sh"
    prefix = path.read_bytes()[:INHERITED_FOUNDATION_LENGTH]
    original = Path.read_bytes
    monkeypatch.setattr(
        Path, "read_bytes", lambda p: prefix if p == path else original(p)
    )
    assert not task13_installed(WORKFLOW.read_text(), ENTRY.read_text())


def restart_specimen():
    functions = [
        ("test_processor_crash_before_after_derivative_write_before_commit", 2),
        ("test_scanner_storage_broker_failure_recovered", 3),
        ("test_current_state_consent_hold_during_job", 4),
        ("test_bounded_exhaustion_never_ready", 1),
    ]
    events = [
        {
            "event": "test_report",
            "phase": "call",
            "outcome": "passed",
            "node": "tests/integration/c03/test_c03_failure_recovery.py::" + name,
        }
        for name, count in functions
        for _ in range(count)
    ]
    for stage in ("before", "after", "scanner", "storage", "broker"):
        for suffix in (
            "_durable_receipt_without_prompt",
            "_real_worker_blocked_before_commit"
            if stage in ("before", "after")
            else "_actual_outage_denied",
            "_recovered_one_effect_stale_delivery_denied",
        ):
            events.append({"event": "task13_restart", "stage": stage + suffix})
    return events + [{"event": "pytest_exit", "exitstatus": 0}]


def test_task13_restart_acceptance_requires_actual_selected_cases_and_all_stages():
    import copy

    from docker.c03_asset_restart_probe import current_restart_evidence_valid

    good = restart_specimen()
    assert current_restart_evidence_valid(good)
    for defect in ("empty", "missing_stage", "skipped", "wrong_file", "setup_failed"):
        bad = copy.deepcopy(good)
        if defect == "empty":
            bad = []
        elif defect == "missing_stage":
            bad.pop(10)
        elif defect == "skipped":
            bad[0]["outcome"] = "skipped"
        elif defect == "wrong_file":
            for event in bad[:10]:
                event["node"] = event["node"].replace(
                    "test_c03_failure_recovery.py", "test_other.py"
                )
        else:
            bad.append({"event": "test_report", "phase": "setup", "outcome": "failed"})
        assert not current_restart_evidence_valid(bad), defect
