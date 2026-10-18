"""Exact-source C04 hosted acceptance; success never includes skipped jobs."""

import argparse
import json
import re

INHERITED = frozenset(
    {
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
)


def required_jobs(task: int) -> frozenset[str]:
    if type(task) is not int or not 1 <= task <= 11:
        raise ValueError("Invalid C04 task")
    names = INHERITED | {"c04-baseline", "c04-postgresql", "c04-final"}
    if task >= 3:
        names |= {"c04-public-media"}
    if task >= 8:
        names |= {"c04-browser"}
    return frozenset(names)


def validate_completed_task_evidence(
    entry: dict, workflow: dict, jobs: list[dict]
) -> bool:
    """Validate freshly fetched attempt-specific job metadata, not a PASS string.

    Test counts/zero skips and cleanup must additionally be inspected from the
    actual runtime evidence before the execution ledger can mark COMPLETE.
    """
    try:
        names = required_jobs(entry["task"])
        sha, run_id, attempt = (
            entry[k] for k in ("implementation_sha", "run_id", "run_attempt")
        )
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
            return False
        tree = entry["implementation_tree"]
        if not isinstance(tree, str) or not re.fullmatch(r"[0-9a-f]{40}", tree):
            return False
        if workflow.get("head_commit", {}).get("id") != sha:
            return False
        if workflow.get("head_commit", {}).get("tree_id") != tree:
            return False
        if (
            type(run_id) is not int
            or run_id < 1
            or type(attempt) is not int
            or attempt < 1
        ):
            return False
        if any(
            workflow.get(k) != v
            for k, v in {
                "id": run_id,
                "head_sha": sha,
                "run_attempt": attempt,
                "head_branch": "marketplace/c04-cloud",
                "path": ".github/workflows/c04.yml",
                "event": "push",
                "status": "completed",
                "conclusion": "success",
            }.items()
        ):
            return False
        if len(jobs) != len(names) or {j["name"] for j in jobs} != names:
            return False
        ids = [j["id"] for j in jobs]
        if len(set(ids)) != len(ids) or any(type(i) is not int or i < 1 for i in ids):
            return False
        return all(
            all(
                job.get(k) == v
                for k, v in {
                    "run_id": run_id,
                    "run_attempt": attempt,
                    "head_sha": sha,
                    "status": "completed",
                    "conclusion": "success",
                }.items()
            )
            for job in jobs
        )
    except (KeyError, TypeError, ValueError):
        return False


def validate_checkpoint(payload: dict) -> bool:
    """Validate durable finite metadata before a checkpoint can claim completion."""
    try:
        if (
            type(payload.get("schema_version")) is not int
            or payload["schema_version"] != 1
        ):
            return False
        required_jobs(payload["task"])
        if payload["state"] not in {
            "NOT_STARTED",
            "RED",
            "IN_PROGRESS",
            "BLOCKED",
            "GREEN",
            "COMPLETE",
        }:
            return False
        for field, expected in {
            "approved_plan_commit": "ba82967cb2e21920076c5a0d25ed1988f777e943",
            "approved_plan_tree": "1478d691b2a60d95f6c0d2ce5e561d34f59a61c0",
            "approved_plan_blob": "f1225196c95a203e440afc4da362b74806e84f20",
            "immutable_c03_commit": "0a867328a6d8ee8c71ec9bd9eeb8910221d1b270",
            "immutable_c03_tree": "5c294cb330cf08b297cc01c8baa27adb1e6b93b7",
        }.items():
            if payload.get(field) != expected:
                return False
        if payload["state"] != "COMPLETE":
            return True
        hosted = payload["hosted_acceptance"]
        if not isinstance(hosted, dict) or not validate_completed_task_evidence(
            hosted["entry"], hosted["workflow"], hosted["jobs"]
        ):
            return False
        if hosted["entry"]["task"] != payload["task"]:
            return False
        runtime = payload["runtime_evidence"]
        if set(runtime) != required_jobs(payload["task"]):
            return False
        return all(
            item.get("exit_code") == 0
            and item.get("failed") == 0
            and item.get("skipped") == 0
            and item.get("cleanup_complete") is True
            for item in runtime.values()
        )
    except (KeyError, TypeError, ValueError, AttributeError):
        return False


def validate_upstream(task: int, needs: dict) -> bool:
    expected = required_jobs(task) - {"c04-final"}
    return set(needs) == expected and all(
        isinstance(value, dict) and value.get("result") == "success"
        for value in needs.values()
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=int, required=True)
    parser.add_argument("--upstream", required=True)
    args = parser.parse_args()
    if not validate_upstream(args.task, json.loads(args.upstream)):
        raise SystemExit("C04 upstream acceptance denied")
    print(
        "C04 upstream manifest accepted; final job and runtime evidence still required"
    )
