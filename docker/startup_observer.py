"""Bounded private startup capture; public values are finite numeric metadata only."""

import json
import os
import subprocess
import threading
import time

LIMIT = 1048576
SERVICES = frozenset(
    {
        "db",
        "redis",
        "minio",
        "scanner",
        "scanner-signatures",
        "web",
        "worker",
        "beat",
        "checks",
        "minio-init",
    }
)
# IDs describe observed messages, not an inferred underlying root cause.
RULES = (
    (
        1,
        "daemon_availability",
        (b"cannot connect to the docker daemon", b"is the docker daemon running"),
    ),
    (
        2,
        "networking",
        (
            b"port is already allocated",
            b"address already in use",
            b"failed to bind host port",
            b"failed to create network",
            b"network not found",
        ),
    ),
    (3, "permissions", (b"permission denied", b"operation not permitted")),
    (
        4,
        "compose_configuration",
        (
            b"additional properties",
            b"no configuration file provided",
            b"invalid compose project",
            b"services must be a mapping",
        ),
    ),
    (
        5,
        "image_retrieval",
        (
            b"manifest unknown",
            b"pull access denied",
            b"toomanyrequests",
            b"failed to resolve reference",
            b"failed to fetch anonymous token",
        ),
    ),
    (
        6,
        "readiness_health",
        (b"is unhealthy", b"did not start", b"timeout waiting for containers"),
    ),
    (
        7,
        "container_creation_startup",
        (
            b"failed to create task",
            b"oci runtime create failed",
            b"failed to create shim task",
        ),
    ),
)


def classify(code, raw, daemon_code, states):
    matches = []
    if isinstance(raw, bytes) and len(raw) <= 2 * LIMIT + 1:
        lowered = raw.lower()
        matches = [
            (i, category)
            for i, category, patterns in RULES
            if any(p in lowered for p in patterns)
        ]
    if code == 0:
        category = "startup_succeeded"
    elif matches:
        category = (
            matches[0][1]
            if len({x[1] for x in matches}) == 1
            else "multiple_observed_categories"
        )
    elif any(x.get("health") == "unhealthy" for x in states):
        category = "readiness_health"
    else:
        category = "unclassified"
    return {
        "category": category,
        "matched_rule_ids": [x[0] for x in matches],
        "daemon_probe_exit_code": daemon_code,
        "underlying_cause_established": False,
    }


def private_run(args, folder, seconds, cwd=None):
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(folder, 0o700)
    start = time.monotonic_ns()
    result = {"start_ns": start}
    counts = {}
    faults = []

    def drain(pipe, name):
        count = 0
        try:
            with (folder / name).open("wb") as output:
                os.chmod(folder / name, 0o600)
                while True:
                    data = pipe.read(65536)
                    if not data:
                        break
                    remaining = max(0, LIMIT - count)
                    if remaining:
                        output.write(data[:remaining])
                    count += len(data)
        except Exception:
            faults.append(name)
        finally:
            pipe.close()
            counts[name] = count

    try:
        process = subprocess.Popen(
            ["timeout", "-k", "10s", str(seconds) + "s", *args],
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        threads = [
            threading.Thread(target=drain, args=(pipe, name), daemon=True)
            for pipe, name in [(process.stdout, "stdout"), (process.stderr, "stderr")]
        ]
        for thread in threads:
            thread.start()
        code = process.wait()
        for thread in threads:
            thread.join(timeout=15)
        result["capture_complete"] = not faults and not any(
            t.is_alive() for t in threads
        )
    except OSError:
        code = 127
        result["capture_complete"] = False
    result.update(exit_code=code, end_ns=time.monotonic_ns())
    for name in ["stdout", "stderr"]:
        result[name + "_bytes"] = counts.get(name)
        result[name + "_truncated"] = counts.get(name, 0) > LIMIT
    return result


def safe_state(raw):
    try:
        service = raw["Config"]["Labels"]["com.docker.compose.service"]
        if service not in SERVICES:
            return None
        s = raw["State"]
        health = s.get("Health", {})
        status = s.get("Status")
        hs = health.get("Status", "not_configured")
        return {
            "service": service,
            "state": status
            if status
            in {
                "created",
                "restarting",
                "running",
                "removing",
                "paused",
                "exited",
                "dead",
            }
            else "unknown",
            "running": s.get("Running") if type(s.get("Running")) is bool else None,
            "exit_code": s.get("ExitCode") if type(s.get("ExitCode")) is int else None,
            "oom_killed": s.get("OOMKilled")
            if type(s.get("OOMKilled")) is bool
            else None,
            "health": hs
            if hs in {"starting", "healthy", "unhealthy", "not_configured"}
            else "unknown",
            "failing_streak": health.get("FailingStreak")
            if type(health.get("FailingStreak")) is int
            else None,
            "health_observation_count": len(health.get("Log", []))
            if isinstance(health.get("Log", []), list)
            and len(health.get("Log", [])) <= 100
            else None,
        }
    except (KeyError, TypeError):
        return None


def snapshot(m):
    started = time.monotonic_ns()

    probe_number = 0

    def probe(args):
        nonlocal probe_number
        probe_number += 1
        result = private_run(
            args, m.PRIVATE / ("probe-" + str(started) + "-" + str(probe_number)), 8
        )
        raw = None
        folder = m.PRIVATE / ("probe-" + str(started) + "-" + str(probe_number))
        if result["capture_complete"] and not result["stdout_truncated"]:
            raw = (folder / "stdout").read_bytes()
        return result["exit_code"], raw

    daemon_code, _ = probe(["docker", "info", "--format", "{{.ServerVersion}}"])
    ps_code, raw = probe(
        [
            "docker",
            "ps",
            "-aq",
            "--filter",
            "label=com.docker.compose.project=" + m.PROJECT,
        ]
    )
    states = []
    inspect_code = None
    if ps_code == 0 and raw is not None:
        ids = raw.decode("ascii", errors="ignore").split()
        import re

        if len(ids) <= 12 and all(re.fullmatch("[a-f0-9]{12,64}", x) for x in ids):
            if ids:
                inspect_code, body = probe(["docker", "inspect", *ids])
                try:
                    objects = json.loads(body) if body is not None else []
                    for obj in objects:
                        state = safe_state(obj)
                        if state is not None:
                            states.append(state)
                except (ValueError, TypeError):
                    inspect_code = None
            else:
                inspect_code = 0
    return {
        "start_ns": started,
        "end_ns": time.monotonic_ns(),
        "daemon_exit_code": daemon_code,
        "container_list_exit_code": ps_code,
        "inspect_exit_code": inspect_code,
        "services": states,
    }


def observe(m, args, seconds, stage):
    if stage not in {"services", "runtime"}:
        raise ValueError("invalid_startup_stage")
    folder = m.PRIVATE / ("capture-" + stage)
    capture = private_run(args, folder, seconds, cwd=m.SOURCE)
    state = snapshot(m)  # Always before the caller can enter cleanup.
    raw = None
    if capture["capture_complete"]:
        raw = b"\n".join((folder / name).read_bytes() for name in ["stdout", "stderr"])
    classification = classify(
        capture["exit_code"], raw, state["daemon_exit_code"], state["services"]
    )
    return {
        "stage": stage,
        "command_family": "docker_compose_up_detached_wait",
        "command_identity": "docker compose up -d --wait db redis minio scanner"
        if stage == "services"
        else "docker compose up -d --wait web worker beat",
        "requested_services": ["db", "redis", "minio", "scanner"]
        if stage == "services"
        else ["web", "worker", "beat"],
        "capture": capture,
        "before_cleanup": state,
        "classification": classification,
    }
