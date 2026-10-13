"""Final Task 14 orchestration must retain every required source/service gate."""

import ast
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[3]

REQUIRED = (
    "docker/c03_baseline.py",
    "sh docker/verify_c02.sh",
    "run_step c02_populate c02 run",
    "run_step populated_preservation c03 run",
    "upgraded_capabilities probe replay",
    "upgraded_constraints probe constraints",
    "docker/c03_upgrade_probe.py clean",
    "manage.py makemigrations --check --dry-run",
    "manage.py showmigrations",
    "pytest tests/unit tests/integration",
    "tests/integration/test_minio_storage.py",
    "tests/integration/c03/test_scanner_service.py",
    "tests/integration/test_celery_roundtrip.py",
    "tests/e2e/c02 tests/e2e/test_foundation_smoke.py",
    "restart_probe prepare",
    "restart_probe start",
    "restart_probe verify",
    "restart_probe fault",
    "kill -s SIGKILL worker",
    "restart redis minio scanner",
    "clean_project=fitlink-c03-task14-clean",
    "docker/c03_timeout_probe.py",
    "--task11-owner",
    "--task12-staff",
    "tests/unit/c03/test_exact_baseline.py",
    "tests/unit/c03/test_final_rehearsal.py",
    "tests/integration/c03/test_upgrade_from_c02.py",
)


def final_gates_valid(source):
    code = "\n".join(
        line for line in source.splitlines() if not line.lstrip().startswith("#")
    )
    return (
        all(item in code for item in REQUIRED)
        and all(
            item not in code
            for item in ("--reuse-db", "--deselect", "continue-on-error")
        )
        and not any(line.strip() == "exit 0" for line in code.splitlines())
    )


def test_final_gates_include_all_c02_and_real_c03_services_browser():
    source = (ROOT / "docker/verify_c03.sh").read_text()
    assert final_gates_valid(source), "Task 14 actual final rehearsal is omitted"
    for item in REQUIRED:
        assert not final_gates_valid(source.replace(item, "omitted"))


def test_final_contract_rejects_comment_only_and_early_exit_substitutes():
    source = (ROOT / "docker/verify_c03.sh").read_text()
    assert final_gates_valid(source)
    fake = "#!/bin/sh\nexit 0\n" + "\n".join(
        "# " + line for line in source.splitlines()
    )
    assert not final_gates_valid(fake), "Comment-only gate falsely accepted"
    assert not final_gates_valid(source.replace("set -eu", "set -eu\nexit 0", 1))


def test_final_stage_propagates_early_function_failure(tmp_path):
    source = (ROOT / "docker/verify_c03.sh").read_text()
    function = source[source.index("run_step() {") : source.index("original_c02() (")]
    private = tmp_path / "private"
    evidence = tmp_path / "evidence"
    private.mkdir()
    evidence.mkdir()
    script = (
        "set -eu\nprivate='"
        + str(private)
        + "'\nevidence='"
        + str(evidence)
        + "'\n"
        + function
        + "fixture() { false; printf 'EARLY_FAILURE_SWALLOWED'; }\n"
        + "run_step synthetic fixture\n"
    )
    result = subprocess.run(
        ["sh", "-c", script], cwd=ROOT, capture_output=True, timeout=10
    )
    assert result.returncode != 0, "Final verifier swallowed an earlier gate failure"
    assert "EARLY_FAILURE_SWALLOWED" not in (private / "synthetic.log").read_text()


def test_private_rehearsal_diagnostics_never_export_exception_text_or_sessions(
    tmp_path,
):
    import json

    from docker.c03_upgrade_probe import private_log_metadata

    path = tmp_path / "private.log"
    sentinel = "PRIVATE-SNAPSHOT-SESSION-AND-OTP-SENTINEL"
    path.write_text(
        'File "/app/config/settings/env.py", line 17, in invalid\n'
        "ImproperlyConfigured: " + sentinel + " +989123000001\n"
        "FAILED tests/unit/c02/test_security_config.py::test_unsafe_config["
        + sentinel
        + "] - "
        + sentinel
        + "\n"
        "3 passed, 1 failed\n"
    )
    result = private_log_metadata(path)
    assert result["exceptions"] == ["ImproperlyConfigured"]
    assert result["counts"]["passed"] == [3]
    assert result["counts"]["failed"] == [1]
    assert result["locations"] == [{"file": "env.py", "line": 17}]
    assert sentinel not in json.dumps(result)
    assert "+989123000001" not in json.dumps(result)


def _docker_probe_dependencies(source):
    tree = ast.parse(source)
    dependencies = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            dependencies.update(
                alias.name for alias in node.names if alias.name.startswith("docker.")
            )
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("docker."):
                dependencies.add(node.module)
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "importlib"
            and node.func.attr == "import_module"
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
            and node.args[0].value.startswith("docker.")
        ):
            dependencies.add(node.args[0].value)
    return dependencies


def test_c02_population_probe_mounts_valid_package_root_and_all_dependencies():
    verifier = (ROOT / "docker/verify_c03.sh").read_text()
    wrapper = (ROOT / "docker/c03_upgrade_probe.py").read_text()
    assert "ROOT = Path(__file__).resolve().parents[1]" in wrapper

    populate_start = verifier.index("run_step c02_populate ")
    populate_end = verifier.index("# The same project/db/container", populate_start)
    populate = verifier[populate_start:populate_end]
    assert (
        '"$root/docker/c03_upgrade_probe.py:/app/docker/c03_upgrade_probe.py:ro"'
        in populate
    )
    assert (
        "/opt/venv/bin/python /app/docker/c03_upgrade_probe.py prepare "
        in populate.replace("\\\n", "")
    )

    dependencies = _docker_probe_dependencies(wrapper)
    assert dependencies
    for module in dependencies:
        relative = module.replace(".", "/") + ".py"
        mount = f'"$root/{relative}:/app/{relative}:ro"'
        assert mount in populate, f"Missing read-only C02 probe dependency: {module}"

    preserve_start = verifier.index("run_step populated_preservation ")
    preserve_end = verifier.index("# Deliberate C03 commands", preserve_start)
    preserve = verifier[preserve_start:preserve_end]
    assert "/probe.py" not in preserve
    assert (
        "/opt/venv/bin/python docker/c03_upgrade_probe.py verify "
        in preserve.replace("\\\n", "")
    )


def test_native_processing_launches_python_below_a_bounded_supervisor():
    source = (ROOT / "docker/verify_c03.sh").read_text()
    launchers = [
        line
        for line in source.splitlines()
        if "docker/c03_upgrade_probe.py" in line
        and ("diagnostic unused" in line or line.startswith("probe()"))
    ]
    assert len(launchers) == 2
    assert all(
        "checks timeout -k 5s 240s /opt/venv/bin/python" in line for line in launchers
    ), "Task14 native decoder caller must have a non-PID1 parent with a finite bound"
