"""Finite conclusions from observed immediate exits; no timing inference."""


def classify(summary):
    rows = summary.get("operations")
    code = summary.get("init_exit_code")
    if not isinstance(rows, list):
        return "unobservable"
    starts = [r for r in rows if r["event"] == "start"]
    ends = [r for r in rows if r["event"] == "end"]
    if len(starts) != len(ends):
        return "incomplete_operation_observation"
    if code == 0:
        required = {"alias", "ready", "bucket", "anonymous", "policy", "user", "attach"}
        passed = {r["operation"] for r in ends if r["exit_code"] == 0}
        return (
            "initialization_completed"
            if required <= passed
            else "insufficient_evidence"
        )
    if not rows and code is not None and summary.get("container_exit_code") is None:
        return "docker_invocation_failed_underlying_unknown"
    failures = [r["operation"] for r in ends if r["exit_code"] != 0]
    if code and failures:
        if failures[-1] in {"bucket", "anonymous", "policy", "user", "attach"}:
            return failures[-1] + "_operation_failed"
        aliases = [r for r in ends if r["operation"] == "alias"]
        ready = [r for r in ends if r["operation"] == "ready"]
        if len(aliases) == 30 and not any(
            r["operation"] in {"bucket", "anonymous", "policy", "user", "attach"}
            for r in starts
        ):
            if all(r["exit_code"] != 0 for r in aliases) and not ready:
                return "alias_initialization_exhaustion"
            if (
                len(ready) == 30
                and all(r["exit_code"] == 0 for r in aliases)
                and all(r["exit_code"] != 0 for r in ready)
            ):
                return "readiness_exhaustion"
            return "alias_or_readiness_exhaustion"
    return "unknown_or_insufficient_evidence"
