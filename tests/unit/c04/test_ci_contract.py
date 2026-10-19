"""C04 cannot advance on absent, skipped or wrong-source hosted gates."""

import importlib
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[3]
INHERITED = {
    "foundation",
    "c02-migrations",
    "c03-final",
    "c03-owner",
    "c03-staff",
    "c03-storage",
    "c03-processing",
    "c03-restart",
    "c03-timeout-probe",
    "c03-task14-native",
    "c03-evidence-audit",
}
REQUIRED = INHERITED | {"c04-baseline", "c04-postgresql", "c04-final"}


def test_current_publication_checkpoint_executes_task2_and_real_sql_rendering():
    import re

    data = workflow()
    postgres = "\n".join(
        s.get("run", "") for s in data["jobs"]["c04-postgresql"]["steps"]
    )
    final = "\n".join(s.get("run", "") for s in data["jobs"]["c04-final"]["steps"])
    wrapper = (ROOT / "docker/verify_c04.sh").read_text()
    match = re.search(r"verify_c04_incremental.sh --task ([0-9]+)", wrapper)
    assert match is not None
    stage = int(match[1])
    assert 2 <= stage <= 11
    assert f"sh docker/verify_c04_incremental.sh --task {stage}" in postgres
    assert (
        f'python docker/c04_acceptance.py --task {stage} --upstream "$C04_UPSTREAM"'
        in final
    )
    source = (ROOT / "docker/verify_c04_incremental.sh").read_text()
    for domain, number in (("professionals", "0018"), ("governance", "0015")):
        line = (
            f"uv run --frozen python manage.py sqlmigrate {domain} {number}"
            " --settings=config.settings.test"
        )
        assert line in source.splitlines()


def test_task2_checkpoint_rejects_prior_stage_runtime_even_with_same_job_names():
    import json
    from copy import deepcopy

    validate = validator().validate_checkpoint
    payload = json.loads(
        (ROOT / "docs/implementation/c04/checkpoints/task02-start.json").read_text()
    )
    entry, run, jobs = evidence()
    entry["task"] = 2
    payload.update(
        state="COMPLETE",
        task=2,
        hosted_acceptance={"entry": entry, "workflow": run, "jobs": jobs},
        runtime_evidence={
            name: {
                "exit_code": 0,
                "failed": 0,
                "skipped": 0,
                "cleanup_complete": True,
                "executed_task": 2,
            }
            for name in REQUIRED
        },
    )
    assert validate(payload)
    for name in ("c04-postgresql", "c04-final"):
        old = deepcopy(payload)
        for invalid in (1, 2.0, True, "2"):
            old["runtime_evidence"][name]["executed_task"] = invalid
            assert not validate(old)
        del old["runtime_evidence"][name]["executed_task"]
        assert not validate(old)


def workflow():
    path = ROOT / ".github/workflows/c04.yml"
    # RED observes actual existing trigger behavior before the C04 workflow exists.
    source = (
        path.read_text()
        if path.exists()
        else (ROOT / ".github/workflows/ci.yml").read_text()
    )
    return yaml.load(source, Loader=yaml.BaseLoader)


def test_c04_ref_runs_every_inherited_gate():
    data = workflow()
    assert data["on"] == {"push": {"branches": ["marketplace/c04-cloud"]}}, (
        "C04 execution ref has no isolated hosted trigger"
    )
    assert set(data["jobs"]) == REQUIRED
    assert set(data["jobs"]["c04-final"]["needs"]) == REQUIRED - {"c04-final"}


def validator():
    spec = importlib.util.find_spec("docker.c04_acceptance")
    assert spec is not None, "Missing exact-head acceptance validator"
    return importlib.import_module("docker.c04_acceptance")


def evidence():
    sha = "a" * 40
    run = {
        "id": 123,
        "head_sha": sha,
        "head_branch": "marketplace/c04-cloud",
        "status": "completed",
        "conclusion": "success",
        "run_attempt": 1,
        "path": ".github/workflows/c04.yml",
        "event": "push",
        "head_commit": {"id": sha, "tree_id": "c" * 40},
    }
    jobs = [
        {
            "name": name,
            "id": i + 1,
            "run_id": 123,
            "run_attempt": 1,
            "head_sha": sha,
            "status": "completed",
            "conclusion": "success",
        }
        for i, name in enumerate(sorted(REQUIRED))
    ]
    return (
        {
            "task": 1,
            "implementation_sha": sha,
            "implementation_tree": "c" * 40,
            "run_id": 123,
            "run_attempt": 1,
        },
        run,
        jobs,
    )


@pytest.mark.parametrize(
    "defect",
    [
        "missing",
        "skipped",
        "wrong_head",
        "wrong_attempt",
        "wrong_branch",
        "duplicate",
        "fake",
        "extra",
        "not_complete",
    ],
)
def test_missing_skipped_wrong_head_or_fake_service_job_rejected(defect):
    module = validator()
    entry, run, jobs = evidence()
    assert module.validate_completed_task_evidence(entry, run, jobs)
    if defect == "missing":
        jobs.pop()
    elif defect == "skipped":
        jobs[0]["conclusion"] = "skipped"
    elif defect == "wrong_head":
        jobs[0]["head_sha"] = "b" * 40
    elif defect == "wrong_attempt":
        jobs[0]["run_attempt"] = 2
    elif defect == "wrong_branch":
        run["head_branch"] = "profiles/c03-cloud"
    elif defect == "duplicate":
        jobs.append(jobs[0].copy())
    elif defect == "fake":
        jobs[0]["name"] = "fake-only-service"
    elif defect == "extra":
        jobs.append({**jobs[0], "id": 999, "name": "unreviewed"})
    else:
        jobs[0]["status"] = "in_progress"
    assert not module.validate_completed_task_evidence(entry, run, jobs)


def test_inherited_workflow_is_byte_identical():
    import hashlib

    assert (
        hashlib.sha1(
            b"blob "
            + str(
                len(body := (ROOT / ".github/workflows/ci.yml").read_bytes())
            ).encode()
            + b"\0"
            + body
        ).hexdigest()
        == "6c48c8e36e887ac4189f8b8c24916a55451f46f0"
    )


def inherited_jobs_unchanged(data):
    from copy import deepcopy

    original = yaml.load(
        (ROOT / ".github/workflows/ci.yml")
        .read_text()
        .replace("refs/heads/profiles/c03-cloud", "refs/heads/marketplace/c04-cloud"),
        Loader=yaml.BaseLoader,
    )
    for name in INHERITED:
        observed = deepcopy(data["jobs"][name])
        # Only this exact additive fixture is permitted in the current-source
        # unit/full-rehearsal jobs. All inherited executable steps stay exact.
        if name in {"foundation", "c03-final"}:
            fixtures = [
                step
                for step in observed["steps"]
                if step.get("name")
                == "Immutable C03 source fixture for C04 unit controls"
            ]
            if len(fixtures) != 1 or fixtures[0] != {
                "name": "Immutable C03 source fixture for C04 unit controls",
                "uses": "actions/checkout@11d5960a326750d5838078e36cf38b85af677262",
                "with": {
                    "ref": "0a867328a6d8ee8c71ec9bd9eeb8910221d1b270",
                    "path": ".runtime/c03",
                    "persist-credentials": "false",
                },
            }:
                return False
            observed["steps"].remove(fixtures[0])
        if observed != original["jobs"][name]:
            return False
    return True


@pytest.mark.parametrize("name", sorted(INHERITED))
def test_inherited_executable_jobs_cannot_be_omitted_or_faked(name):
    data = workflow()
    assert inherited_jobs_unchanged(data)
    # Replacing any inherited executable invocation with a green echo is
    # forbidden even if its job name and final status look legitimate.
    step = next(step for step in data["jobs"][name]["steps"] if "run" in step)
    step["run"] = "echo fake-only-service"
    assert not inherited_jobs_unchanged(data)


def test_aggregate_rejects_skipped_upstream_before_completion():
    module = validator()
    needs = {name: {"result": "success"} for name in REQUIRED - {"c04-final"}}
    assert module.validate_upstream(1, needs)
    needs["c03-final"]["result"] = "skipped"
    assert not module.validate_upstream(1, needs)


def test_acceptance_binds_workflow_path_event_and_source_tree():
    module = validator()
    entry, run, jobs = evidence()
    entry["implementation_tree"] = "c" * 40
    run.update(
        {
            "path": ".github/workflows/c04.yml",
            "event": "push",
            "head_commit": {"id": entry["implementation_sha"], "tree_id": "c" * 40},
        }
    )
    assert module.validate_completed_task_evidence(entry, run, jobs)
    run["path"] = ".github/workflows/fake.yml"
    assert not module.validate_completed_task_evidence(entry, run, jobs)


@pytest.mark.parametrize("field", ["event", "tree_id", "commit_id"])
def test_acceptance_rejects_wrong_source_envelope(field):
    module = validator()
    entry, run, jobs = evidence()
    assert module.validate_completed_task_evidence(entry, run, jobs)
    if field == "event":
        run["event"] = "workflow_dispatch"
    elif field == "tree_id":
        run["head_commit"]["tree_id"] = "d" * 40
    else:
        run["head_commit"]["id"] = "d" * 40
    assert not module.validate_completed_task_evidence(entry, run, jobs)


def test_checkpoint_schema_cannot_claim_incomplete_acceptance():
    import json

    module = validator()
    validate = getattr(module, "validate_checkpoint", None)
    assert callable(validate), "Missing durable checkpoint schema validation"
    payload = json.loads(
        (ROOT / "docs/implementation/c04/checkpoints/task01-start.json").read_text()
    )
    assert validate(payload)
    payload["state"] = "COMPLETE"
    assert not validate(payload)
