"""One bounded paired real-PostgreSQL/Redis Task 7 private-fixture check."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SOURCE_SHA = "2b2790cdf9019338ddeb09f9df2fdfb1fa0dd331"
SOURCE_TREE = "f4a49666111ce27d6c12cc6aff89f3430c7ea243"
PARENT_TEST = (
    "tests/integration/c04/test_educational_posts.py::"
    "test_post_current_parent_and_account_authority"
)
PUBLIC_POST_TEST = (
    "tests/integration/c04/test_educational_posts.py::"
    "test_confirmed_post_activates_only_complete_copies_and_edit_withdraws"
)
PRIVATE_TESTS = (
    "tests/integration/c04/test_educational_posts.py::"
    "test_post_receipt_payload_and_expected_version_are_fenced",
    "tests/integration/c04/test_post_races.py::"
    "test_stale_post_edit_cannot_replace_current_revision",
    "tests/integration/c04/test_post_races.py::"
    "test_concurrent_same_version_post_edit_has_one_winner",
)
CHARACTERIZATION = (
    "tests/integration/c04/test_educational_posts.py::"
    "test_private_post_owner_has_no_public_parent"
)
ORIGINAL_SELECTION = (*PRIVATE_TESTS, PUBLIC_POST_TEST)
CANDIDATE_SELECTION = (*PRIVATE_TESTS, PUBLIC_POST_TEST, CHARACTERIZATION, PARENT_TEST)
CHANGED_TEST_PATHS = (
    "tests/integration/c04/post_helpers.py",
    "tests/integration/c04/test_educational_posts.py",
    "tests/integration/c04/test_post_races.py",
)
LOCKS = ("uv.lock", "package-lock.json")


class StageFailure(Exception):
    def __init__(self, stage, classification):
        super().__init__(classification)
        self.stage = stage
        self.classification = classification


def git(source: Path, argument: str) -> str:
    value = subprocess.check_output(
        ["git", "-C", str(source), "rev-parse", argument],
        stderr=subprocess.DEVNULL,
        text=True,
        timeout=10,
    )
    return value.strip()


def identity(source: Path) -> dict:
    status = subprocess.check_output(
        ["git", "-C", str(source), "status", "--porcelain=v1", "--untracked-files=all"],
        stderr=subprocess.DEVNULL,
        text=True,
        timeout=10,
    )
    return {
        "head": git(source, "HEAD"),
        "tree": git(source, "HEAD^{tree}"),
        "clean": status == "",
    }


def file_hashes(source: Path) -> dict:
    return {
        name: hashlib.sha256((source / name).read_bytes()).hexdigest()
        for name in LOCKS
    }


def run(stages: list[dict], name: str, command: list[str], cwd: Path, env: dict, limit: int) -> None:
    started = time.monotonic()
    code = 127
    expired = False
    with tempfile.TemporaryFile() as private_output:
        try:
            proc = subprocess.run(
                command,
                cwd=str(cwd),
                env=env,
                stdout=private_output,
                stderr=subprocess.STDOUT,
                timeout=limit,
                check=False,
            )
            code = proc.returncode
        except subprocess.TimeoutExpired:
            code = 124
            expired = True
        except OSError:
            code = 127
    stages.append({
        "stage": name,
        "exit_code": int(code),
        "timed_out": expired,
        "wall_seconds": round(time.monotonic() - started, 6),
        "raw_logs_discarded": True,
    })
    if code != 0:
        raise StageFailure(name, "timeout" if expired else "nonzero_exit")


def validated_metrics(path: Path, source: Path, exact_count: int) -> dict:
    if not path.is_file():
        raise StageFailure("test_metrics", "missing_metrics")
    data = json.loads(path.read_text(encoding="utf-8"))
    expected = identity(source)
    cases = data.get("cases", [])
    if (
        data.get("source_sha") != expected["head"]
        or data.get("source_tree") != expected["tree"]
        or data.get("pytest_exit_code") != 0
        or len(cases) != exact_count
        or any(row.get("status") != "passed" for row in cases)
    ):
        raise StageFailure("test_metrics", "incomplete_or_failed")
    return data


def compare(original: dict, candidate: dict) -> dict:
    old = {row["test"]: row for row in original["cases"]}
    new = {row["test"]: row for row in candidate["cases"]}
    if not set(PRIVATE_TESTS).issubset(old) or not set(PRIVATE_TESTS).issubset(new):
        raise StageFailure("comparison", "missing_private_cases")
    values = []
    for name in PRIVATE_TESTS:
        before = old[name]["phases"]["call"]
        after = new[name]["phases"]["call"]
        values.append({
            "test": name,
            "original_call_wall_seconds": before,
            "candidate_call_wall_seconds": after,
            "observed_delta_seconds": round(after - before, 6),
            "original_setup_wall_seconds": old[name]["phases"]["setup"],
            "candidate_setup_wall_seconds": new[name]["phases"]["setup"],
            "original_teardown_wall_seconds": old[name]["phases"]["teardown"],
            "candidate_teardown_wall_seconds": new[name]["phases"]["teardown"],
        })
    return {
        "paired_case_durations": values,
        "private_call_wall_original_total_seconds": round(
            sum(v["original_call_wall_seconds"] for v in values), 6
        ),
        "private_call_wall_candidate_total_seconds": round(
            sum(v["candidate_call_wall_seconds"] for v in values), 6
        ),
        "private_call_wall_delta_seconds": round(
            sum(v["observed_delta_seconds"] for v in values), 6
        ),
        "interpretation": (
            "One original then one candidate pass on the same hosted runner; "
            "order, cold-start and host variance remain confounders. "
            "This is not a suite-wide runtime improvement guarantee."
        ),
    }


def main() -> int:
    root = Path(os.environ.get("GITHUB_WORKSPACE", ".")).resolve()
    original = (root / ".runtime/task07-original").resolve()
    output = root / ".runtime/task07-private-fixture"
    output.mkdir(parents=True, exist_ok=True)
    control = root / "docker/task07_private_fixture_phase.py"
    stages: list[dict] = []
    failure = None
    original_before = {}
    candidate_before = {}
    original_after = {}
    candidate_after = {}
    hashes_before = {}
    hashes_after = {}
    report = {}
    result_code = 1
    env = dict(os.environ)
    for key in ("GITHUB_TOKEN", "ACTIONS_RUNTIME_TOKEN", "ACTIONS_ID_TOKEN_REQUEST_TOKEN"):
        env.pop(key, None)

    try:
        current = "preflight_identity"
        original_before = identity(original)
        candidate_before = identity(root)
        hashes_before = {"original": file_hashes(original), "candidate": file_hashes(root)}
        if (
            original_before != {"head": SOURCE_SHA, "tree": SOURCE_TREE, "clean": True}
            or not candidate_before["clean"]
            or candidate_before["head"] != os.environ.get("GITHUB_SHA")
        ):
            raise StageFailure(current, "source_identity_mismatch")
        if hashes_before["original"] != hashes_before["candidate"]:
            raise StageFailure(current, "dependency_lock_mismatch")

        run(stages, "original_lock_check", ["uv", "lock", "--check"], original, env, 90)
        run(stages, "candidate_lock_check", ["uv", "lock", "--check"], root, env, 90)
        run(stages, "original_frozen_sync", ["uv", "sync", "--frozen", "--group", "dev"], original, env, 300)
        run(stages, "candidate_frozen_sync", ["uv", "sync", "--frozen", "--group", "dev"], root, env, 300)

        run(
            stages, "candidate_ruff",
            ["uv", "run", "--frozen", "--no-sync", "ruff", "check",
             *CHANGED_TEST_PATHS],
            root, env, 40,
        )
        run(
            stages, "candidate_format",
            ["uv", "run", "--frozen", "--no-sync", "ruff", "format", "--check",
             *CHANGED_TEST_PATHS],
            root, env, 40,
        )
        run(
            stages, "candidate_migration_drift",
            ["uv", "run", "--frozen", "--no-sync", "python", "manage.py",
             "makemigrations", "--check", "--dry-run"],
            root, env, 90,
        )

        common_environment = {
            "DJANGO_SETTINGS_MODULE": "config.settings.test",
            "FITLINK_FIXTURE_SOURCE_TREE": SOURCE_TREE,
        }
        for label, source, choices in (
            ("original", original, ORIGINAL_SELECTION),
            ("candidate", root, CANDIDATE_SELECTION),
        ):
            destination = output / f"{label}.json"
            test_env = dict(env)
            test_env.update(common_environment)
            test_env["FITLINK_FIXTURE_PHASE_PATH"] = str(destination)
            test_env["FITLINK_FIXTURE_SOURCE_SHA"] = identity(source)["head"]
            test_env["FITLINK_FIXTURE_SOURCE_TREE"] = identity(source)["tree"]
            test_env["PYTHONPATH"] = os.pathsep.join(
                [str(root / "docker"), str(source), env.get("PYTHONPATH", "")]
            )
            run(
                stages, f"{label}_focused_pytest",
                ["uv", "run", "--frozen", "--no-sync", "pytest", "-q",
                 "--strict-markers", "--tb=no", "--show-capture=no",
                 "-p", "task07_private_fixture_phase", *choices],
                source, test_env, 300,
            )
            if label == "original":
                before = validated_metrics(destination, source, 4)
            else:
                after = validated_metrics(destination, source, 9)

        report = compare(before, after)
        passed_parent_cases = [
            row for row in after["cases"]
            if row["test"].startswith(PARENT_TEST + "[")
            and row["status"] == "passed"
        ]
        if (
            len(passed_parent_cases) != 4
            or not any(row["test"] == PUBLIC_POST_TEST for row in after["cases"])
            or not any(row["test"] == CHARACTERIZATION for row in after["cases"])
        ):
            raise StageFailure("preserved_publication_coverage", "coverage_incomplete")
        report["published_parent_parameter_cases_passed"] = 4
        report["unchanged_confirmed_public_post_case_passed"] = True
        report["private_owner_characterization_passed"] = True
        result_code = 0
    except StageFailure as exc:
        failure = {"stage": exc.stage, "classification": exc.classification}
    except Exception as exc:
        failure = {"stage": "diagnostic_harness", "classification": type(exc).__name__[:64]}
    finally:
        try:
            original_after = identity(original)
            candidate_after = identity(root)
            hashes_after = {"original": file_hashes(original), "candidate": file_hashes(root)}
        except Exception:
            original_after = {"head": None, "tree": None, "clean": False}
            candidate_after = {"head": None, "tree": None, "clean": False}
        preserved = (
            bool(original_before)
            and original_before == original_after
            and bool(candidate_before)
            and candidate_before == candidate_after
            and bool(hashes_before)
            and hashes_before == hashes_after
        )
        if not preserved:
            result_code = 1
            if failure is None:
                failure = {"stage": "preservation", "classification": "source_or_lock_changed"}
        evidence = {
            "schema_version": 1,
            "diagnostic_only": True,
            "accepted_task7": False,
            "source_sha": SOURCE_SHA,
            "source_tree": SOURCE_TREE,
            "candidate_sha": os.environ.get("GITHUB_SHA"),
            "original_source_before": original_before,
            "original_source_after": original_after,
            "candidate_source_before": candidate_before,
            "candidate_source_after": candidate_after,
            "dependency_lockfile_sha256_before": hashes_before,
            "dependency_lockfile_sha256_after": hashes_after,
            "preserved": preserved,
            "run_stages": stages,
            "original_test_count_expected": 4,
            "candidate_test_count_expected": 9,
            "paired_comparison": report,
            "host_cpu_count": os.cpu_count(),
            "explicit_docker_resources_created": 0,
            "service_resources": "GitHub-managed PostgreSQL and Redis service containers",
            "failure": failure,
            "local_unpublished_checkout_accessed": False,
            "no_product_or_historical_source_modified": True,
        }
        (output / "outcome.json").write_text(
            json.dumps(evidence, sort_keys=True) + "\n", encoding="utf-8"
        )
    return result_code


if __name__ == "__main__":
    raise SystemExit(main())
