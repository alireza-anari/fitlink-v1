"""MinIO diagnostics classify evidence without exporting private stage text."""

import importlib
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

pytestmark = pytest.mark.unit


def observer():
    module = importlib.import_module("docker.c04_baseline_runtime")
    assert callable(getattr(module, "read_minio_private_log", None)), (
        "Missing bounded immutable clean_minio diagnostics"
    )
    return module


@pytest.mark.parametrize(
    "line,expected",
    [
        (
            "mc: <ERROR> Unable to initialize new alias "
            "from the provided credentials. PRIVATE",
            "readiness_or_alias_failure",
        ),
        ("Error response from daemon: PRIVATE", "docker_daemon_failure"),
        (
            "Error response from daemon: failed to create task for container PRIVATE",
            "container_startup_failure",
        ),
        (
            "dependency failed to start: container PRIVATE is unhealthy",
            "container_startup_failure",
        ),
        (
            "mc: <ERROR> Unable to make bucket `PRIVATE_URL`.",
            "bucket_configuration_failure",
        ),
        (
            "mc: <ERROR> Unable to set anonymous `none` for `PRIVATE_URL`.",
            "anonymous_access_policy_failure",
        ),
        (
            "mc: <ERROR> Unable to create new policy. PRIVATE_POLICY",
            "application_policy_creation_failure",
        ),
        (
            "mc: <ERROR> Unable to add new user. PRIVATE_USER",
            "application_user_creation_failure",
        ),
        (
            "mc: <ERROR> Unable to make user/group policy association. PRIVATE",
            "application_policy_attachment_failure",
        ),
    ],
)
def test_recognized_failure_exports_only_finite_classification(
    tmp_path, line, expected
):
    path = tmp_path / "clean_minio.log"
    path.write_text(line + "\nPRIVATE_SECRET PRIVATE_PHONE https://PRIVATE_ENDPOINT\n")
    result = observer().read_minio_private_log(path)
    assert result["log_state"] == "read"
    assert result["classification"] == expected
    assert result["acceptance"] is False
    assert "PRIVATE" not in json.dumps(result)
    assert "http" not in json.dumps(result)


@pytest.mark.parametrize(
    "text",
    [
        "Container PRIVATE Created\nContainer PRIVATE Started\n",
        "private message says Unable to add new user\n",
        "mc: <ERROR> Unable to initialize admin connection. PRIVATE\n",
        "mc: <ERROR> PRIVATE_UNKNOWN\n",
        "mc: <ERROR> Unable to add new user. PRIVATE\n"
        "mc: <ERROR> Unable to create new policy. PRIVATE\n",
    ],
)
def test_silent_or_ambiguous_log_never_guesses_failed_subcommand(tmp_path, text):
    path = tmp_path / "clean_minio.log"
    path.write_text(text)
    result = observer().read_minio_private_log(path)
    assert result["classification"] == "unknown_or_insufficient_evidence"
    assert "PRIVATE" not in json.dumps(result)


@pytest.mark.parametrize(
    "data,state",
    [
        pytest.param(b"", "empty", id="empty"),
        pytest.param(b"\xff", "malformed", id="invalid_utf8"),
        pytest.param(
            b"mc: <ERROR> Unable to add new user\x00PRIVATE", "malformed", id="nul"
        ),
        pytest.param(b"x" * 65537, "oversized", id="oversized"),
        pytest.param(b"x" * 8193, "malformed", id="oversized_line"),
    ],
)
def test_unusable_logs_have_explicit_bounded_outcomes(tmp_path, data, state):
    path = tmp_path / "clean_minio.log"
    path.write_bytes(data)
    result = observer().read_minio_private_log(path)
    assert result["log_state"] == state
    assert result["classification"] == "unknown_or_insufficient_evidence"
    assert result["evidence"] == []


def test_missing_and_symlink_logs_are_not_followed(tmp_path):
    path = tmp_path / "clean_minio.log"
    assert observer().read_minio_private_log(path)["log_state"] == "missing"
    secret = tmp_path / "private"
    secret.write_text("mc: <ERROR> Unable to add new user PRIVATE")
    path.symlink_to(secret)
    assert observer().read_minio_private_log(path)["log_state"] == "symlink"


def test_wrapper_records_clean_minio_without_reexecution_or_exit_suppression(
    tmp_path, monkeypatch, capsys
):
    module = observer()
    baseline = tmp_path / ".runtime/c03"
    private = baseline / ".runtime/task14-private"
    private.mkdir(parents=True)
    (private / "clean_minio.log").write_text(
        "mc: <ERROR> Unable to add new user PRIVATE"
    )
    monkeypatch.setattr(module, "verify_baseline", Mock(return_value="original-tree"))
    command = Mock(return_value=SimpleNamespace(returncode=17))
    monkeypatch.setattr(module.subprocess, "run", command)
    assert module.run(tmp_path) == 17
    command.assert_called_once_with(["sh", "docker/verify_c03.sh"], cwd=baseline)
    records = list((tmp_path / ".runtime/c04-baseline-evidence").glob("*.json"))
    assert len(records) == 1
    result = json.loads(records[0].read_text())
    assert result["exit_code"] == 17
    assert (
        result["logs"]["clean_minio"]["classification"]
        == "application_user_creation_failure"
    )
    assert "PRIVATE" not in records[0].read_text() + capsys.readouterr().out


def test_nonregular_log_does_not_replace_original_result_with_reader_error(tmp_path):
    path = tmp_path / "clean_minio.log"
    path.mkdir()
    result = observer().read_minio_private_log(path)
    assert result["log_state"] == "not_regular"
    assert result["classification"] == "unknown_or_insufficient_evidence"


def test_log_permission_failure_has_no_path_or_exception_message(tmp_path, monkeypatch):
    module = observer()

    def denied(*args):
        raise PermissionError(13, "PRIVATE_PATH PRIVATE_SECRET")

    monkeypatch.setattr(module.os, "open", denied)
    result = module.read_minio_private_log(tmp_path / "clean_minio.log")
    assert result["log_state"] == "unreadable"
    assert "PRIVATE" not in json.dumps(result)


def test_marker_prefix_collision_never_invents_an_operation(tmp_path):
    path = tmp_path / "clean_minio.log"
    path.write_text("mc: <ERROR> Unable to add new usernames PRIVATE")
    assert (
        observer().read_minio_private_log(path)["classification"]
        == "unknown_or_insufficient_evidence"
    )


def test_ansi_error_is_redacted_before_classification(tmp_path):
    path = tmp_path / "clean_minio.log"
    path.write_text("\x1b[31mmc: <ERROR>\x1b[0m Unable to add new user. PRIVATE\n")
    result = observer().read_minio_private_log(path)
    assert result["classification"] == "application_user_creation_failure"
    assert "PRIVATE" not in json.dumps(result)


def test_immutable_silent_alias_contract_cannot_be_classified_by_duration(tmp_path):
    # Its stdout/stderr redirects discard both alias and readiness errors.
    path = tmp_path / "clean_minio.log"
    path.write_text(" Container PRIVATE Created\n Container PRIVATE Started\n")
    result = observer().read_minio_private_log(path)
    assert result["classification"] == "unknown_or_insufficient_evidence"
    assert result["evidence"] == []


def test_descriptor_close_error_cannot_replace_original_subprocess_exit(
    tmp_path, monkeypatch
):
    module = observer()
    baseline = tmp_path / ".runtime/c03"
    private = baseline / ".runtime/task14-private"
    private.mkdir(parents=True)
    (private / "clean_minio.log").write_text("PRIVATE")
    monkeypatch.setattr(module, "verify_baseline", Mock(return_value="original-tree"))
    monkeypatch.setattr(
        module.subprocess, "run", Mock(return_value=SimpleNamespace(returncode=17))
    )
    close = module.os.close

    def fail_close(descriptor):
        close(descriptor)
        raise OSError("PRIVATE_CLOSE_ERROR")

    with monkeypatch.context() as patch:
        patch.setattr(module.os, "close", fail_close)
        assert module.run(tmp_path) == 17
    result = json.loads(
        next((tmp_path / ".runtime/c04-baseline-evidence").glob("*.json")).read_text()
    )
    assert result["logs"]["clean_minio"]["log_state"] == "unreadable"
    assert "PRIVATE" not in json.dumps(result)


def test_conflicting_daemon_evidence_is_order_independent(tmp_path):
    path = tmp_path / "clean_minio.log"
    lines = [
        "Error response from daemon: PRIVATE_OTHER_FAILURE",
        "Error response from daemon: failed to create task for container PRIVATE",
    ]
    path.write_text("\n".join(lines))
    first = observer().read_minio_private_log(path)
    path.write_text("\n".join(reversed(lines)))
    second = observer().read_minio_private_log(path)
    assert first == second
    assert first["classification"] == "unknown_or_insufficient_evidence"
