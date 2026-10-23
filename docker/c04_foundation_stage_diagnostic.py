#!/usr/bin/python3
"""Diagnostic ONLY: unchanged verifier, private raw output, finite stage metadata."""
import hashlib
import io
import json
import os
from pathlib import Path
import selectors
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from urllib import request
from urllib.error import HTTPError, URLError
import zipfile

SOURCE = "6c66199bd5ea3032d319fa6f727eb1d2e5e6e158"
NAMES = ("python", "uv", "npm", "docker", "sh")
LIMIT = 4 * 1024 * 1024
MARKERS = {
    "dns_marker": (b"Temporary failure in name resolution", b"no such host"),
    "tls_marker": (b"certificate verify failed", b"x509: certificate"),
    "daemon_marker": (b"Cannot connect to the Docker daemon",),
    "permission_marker": (b"permission denied", b"Permission denied"),
    "disk_marker": (b"No space left on device",),
    "image_fetch_marker": (b"failed to resolve source metadata", b"manifest unknown"),
}
def category(error):
    if isinstance(error, HTTPError):
        return "http_error"
    if isinstance(error, URLError):
        return "transport_unclassified"
    if isinstance(error, TimeoutError):
        return "timeout"
    if isinstance(error, (ValueError, AssertionError, KeyError, json.JSONDecodeError)):
        return "invalid_evidence"
    if isinstance(error, OSError):
        return "os_error"
    return "unknown"

def label(name, args, cwd):
    scope = "immutable_c01" if ".runtime/c01" in str(cwd) else "current_source"
    if name == "sh":
        if args and args[0] == "docker/verify_c02.sh":
            return "c02_verifier"
        if args and args[0] == "docker/verify_foundation.sh":
            return scope + ".foundation_verifier"
        return "other_shell"
    if name == "python":
        if args and args[0] in {"docker/c02_baseline.py", "docker/c03_baseline.py"}:
            return scope + ".source_check"
        if args and args[0] == "docker/generate_env.py":
            return scope + ".generate_private_configuration"
        return scope + ".python_other"
    if name == "npm":
        if args == ["ci"]:
            return scope + ".npm_ci"
        if args[:2] == ["run", "build:css"]:
            return scope + ".css"
        if args[:2] == ["run", "check:js"]:
            return scope + ".javascript"
        return scope + ".npm_other"
    if name == "uv":
        if args[:1] == ["sync"]:
            return scope + ".frozen_sync"
        for token, stage in [("collectstatic", "collectstatic"), ("pytest", "pytest"),
                             ("mypy", "mypy"), ("ruff", "ruff"), ("production_check.py", "production_check")]:
            if any(a == token or a.endswith("/" + token) for a in args):
                return scope + "." + stage
        return scope + ".uv_other"
    if name == "docker":
        if args[:2] == ["volume", "ls"]:
            return "owned_volume_inventory"
        if args[:1] == ["build"]:
            return scope + ".production_image_build"
        if args[:1] != ["compose"]:
            return "docker_other"
        project = "unknown_project"
        if "-p" in args and args.index("-p") + 1 < len(args):
            value = args[args.index("-p") + 1]
            project = {"fitlink-c02-immutable-c01": "immutable_c01",
                       "fitlink-c02-exact-upgrade": "same_database_upgrade",
                       "fitlink-foundation-verify": "current_clean"}.get(value, "unknown_project")
        command = next((a for a in args if a in {"config", "build", "up", "down", "run", "exec", "restart", "ps"}), "other")
        detail = command
        if command == "run":
            if "minio-init" in args:
                detail = "minio_initialization"
            elif "migrate" in args:
                detail = "migrate"
            elif "makemigrations" in args:
                detail = "migration_drift"
            elif "prepare" in args:
                detail = "prepare"
            elif "verify" in args:
                detail = "verify"
            elif "pytest" in args:
                detail = "browser_tests" if "browser" in args else "backend_tests"
            else:
                detail = "service_command"
        return project + ".compose_" + detail
    return "other"

def append_event(config, value):
    data = (json.dumps(value, sort_keys=True) + "\n").encode()
    try:
        fd = os.open(config["events"], os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        try:
            if os.fstat(fd).st_size + len(data) <= LIMIT:
                os.write(fd, data)
        finally:
            os.close(fd)
    except OSError:
        # Missing telemetry is diagnosed as missing, never a substitute exit.
        pass

def delegate(name, args, config):
    started = time.monotonic()
    stage = label(name, args, Path.cwd())
    append_event(config, {"event": "start", "stage": stage, 
                          "seconds": round(started - config["origin"], 6)})
    prefix = bytearray()
    truncated = False
    code = 127
    try:
        with subprocess.Popen([config["executables"][name], *args],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE) as child:
            with selectors.DefaultSelector() as selector:
                selector.register(child.stdout, selectors.EVENT_READ, 1)
                selector.register(child.stderr, selectors.EVENT_READ, 2)
                while selector.get_map():
                    for key, _ in selector.select(1):
                        chunk = os.read(key.fileobj.fileno(), 65536)
                        if not chunk:
                            selector.unregister(key.fileobj)
                            continue
                        remaining = 65536 - len(prefix)
                        prefix.extend(chunk[:remaining])
                        truncated |= len(chunk) > remaining
                        # Preserve each delegated stream byte-for-byte. The original
                        # supervisor receives it; only its finite output reaches a
                        # private runner file, which is never uploaded or printed.
                        view = memoryview(chunk)
                        while view:
                            view = view[os.write(key.data, view):]
            code = child.wait()
    except OSError:
        code = 127
    markers = sorted(k for k, values in MARKERS.items()
                     if code and any(v in prefix for v in values))
    append_event(config, {"event": "end", "stage": stage, 
                          "seconds": round(time.monotonic() - config["origin"], 6),
                          "duration_seconds": round(time.monotonic() - started, 6),
                          "exit_code": code, "observed_markers": markers,
                          "private_prefix_truncated": truncated})
    return code if code >= 0 else 128 - code

class PublicRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        from urllib.parse import urlparse
        if urlparse(newurl).scheme != "https":
            raise ValueError("redirect_denied")
        return request.Request(newurl, method="GET")

def artifact_summary(identifier, expected):
    opener = request.build_opener(PublicRedirect())
    req = request.Request(
        "https://api.github.com/repos/alireza-anari/fitlink-v1/actions/artifacts/" + str(identifier) + "/zip",
        headers={"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"],
                 "Accept": "application/vnd.github+json", "User-Agent": "FitLink-Foundation-Diagnostic"})
    try:
        with opener.open(req, timeout=30) as response:
            data = response.read(8 * 1024 * 1024 + 1)
        if len(data) > 8 * 1024 * 1024:
            return {"artifact_id": identifier, "state": "oversized"}
        digest = hashlib.sha256(data).hexdigest()
        if digest != expected:
            return {"artifact_id": identifier, "state": "digest_mismatch"}
        counts = {}
        terminal = []
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            infos = archive.infolist()
            if len(infos) > 32 or sum(i.file_size for i in infos) > 32 * 1024 * 1024:
                return {"artifact_id": identifier, "state": "expanded_oversized"}
            for info in infos:
                if not info.filename.endswith(".jsonl"):
                    continue
                for line in archive.read(info).splitlines():
                    if len(line) > 65536:
                        return {"artifact_id": identifier, "state": "record_oversized"}
                    item = json.loads(line)
                    event = item.get("event")
                    if event in {"started", "safe_progress", "snapshot", "final_snapshot",
                                 "command_exited", "diagnostic_finished", "test_start",
                                 "test_end", "test_report", "pytest_exit", "observer_finished"}:
                        counts[event] = counts.get(event, 0) + 1
                    if event == "diagnostic_finished":
                        end = {"event": event}
                        for key in ["elapsed_seconds", "observed_returncode"]:
                            value = item.get(key)
                            if type(value) in (int, float) and -1000 <= value <= 100000:
                                end[key] = value
                        end["host_cleanup_complete"] = item.get("host_cleanup_complete") is True
                        end["container_cleanup_complete"] = item.get("container_cleanup", {}).get("complete") is True
                        terminal.append(end)
        return {"artifact_id": identifier, "state": "verified", "sha256": digest,
                "event_counts": counts, "terminal": terminal[:16]}
    except Exception as error:
        value = {"artifact_id": identifier, "state": category(error)}
        if isinstance(error, HTTPError):
            value["http_status"] = error.code
        return value

def main():
    root = Path.cwd()
    output = root / ".runtime/foundation-stage-diagnostic"
    output.mkdir(mode=0o700, exist_ok=True)
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if source != SOURCE:
        raise ValueError("source_mismatch")
    summaries = [
        artifact_summary(12511439392, "2a0ccbdfe6a15dfeb4528203e6e88ccdfc6f33c24912e6160d45d739c08f63a2"),
        artifact_summary(12500689823, "99bdd654ab830501938a04bc12ab76df8dc36f23ae61f1230c7c3e9ad35e29fd"),
    ]
    # Verify private-byte capture/forwarding and original nonzero status without
    # publishing the synthetic secret or subprocess command/arguments.
    real = {name: shutil.which(name) for name in NAMES}
    if not all(real.values()):
        raise ValueError("required_executable_missing")
    config = {"executables": real, "events": str(output / "selfcheck-private.jsonl"), "origin": time.monotonic()}
    with tempfile.TemporaryFile() as private:
        saved = (os.dup(1), os.dup(2))
        try:
            os.dup2(private.fileno(), 1)
            os.dup2(private.fileno(), 2)
            code = delegate("python", ["-c", "import sys;print('synthetic-private-sentinel');sys.exit(17)"], config)
        finally:
            os.dup2(saved[0], 1); os.dup2(saved[1], 2)
            os.close(saved[0]); os.close(saved[1])
        private.seek(0)
        assert code == 17 and private.read() == b"synthetic-private-sentinel\n"
    self_events = Path(config["events"]).read_text()
    assert "synthetic-private-sentinel" not in self_events
    assert json.loads(self_events.splitlines()[-1])["exit_code"] == 17
    Path(config["events"]).unlink()
    with tempfile.TemporaryDirectory(prefix="fitlink-foundation-observer-") as temporary:
        folder = Path(temporary)
        config["events"] = str(output / "stages.jsonl")
        config["origin"] = time.monotonic()
        config_path = folder / "config.json"
        config_path.write_text(json.dumps(config))
        config_path.chmod(0o600)
        for name in NAMES:
            (folder / name).symlink_to(Path(__file__).resolve())
        env = dict(os.environ)
        env.pop("GITHUB_TOKEN", None)
        env["PATH"] = str(folder) + os.pathsep + env["PATH"]
        env["FITLINK_FOUNDATION_OBSERVER_CONFIG"] = str(config_path)
        probe = subprocess.run([str(folder / "python"), "-c", "import sys;print('synthetic-private-sentinel');sys.exit(17)"], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        assert probe.returncode == 17 and probe.stdout == b"synthetic-private-sentinel\n" and not probe.stderr
        assert "synthetic-private-sentinel" not in Path(config["events"]).read_text()
        assert label("docker", ["compose", "-p", "fitlink-c02-immutable-c01", "run", "--rm", "minio-init", "synthetic-private-sentinel"], root) == "immutable_c01.compose_minio_initialization"
        started = time.monotonic()
        limit_reason = None
        with tempfile.TemporaryFile() as private:
            child = subprocess.Popen([real["python"], "docker/c03_foundation_evidence.py"],
                                     env=env, stdout=private, stderr=subprocess.STDOUT)
            while child.poll() is None:
                if time.monotonic() - started > 1860 or os.fstat(private.fileno()).st_size > 32 * 1024 * 1024:
                    limit_reason = "outer_bound"
                    child.send_signal(signal.SIGINT)
                    try:
                        child.wait(timeout=45)
                    except subprocess.TimeoutExpired:
                        child.terminate()
                    break
                time.sleep(1)
            code = child.wait(timeout=60)
        # Raw supervisor output and raw command streams are never exported.
        clean = not subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], text=True)
        fixture_checks = {}
        for name, script, path in [("c01", "docker/c02_baseline.py", ".runtime/c01"), ("c02", "docker/c03_baseline.py", ".runtime/c02")]:
            with tempfile.TemporaryFile() as private_check:
                checked = subprocess.run([real["python"], script, path], stdout=private_check, stderr=subprocess.STDOUT, timeout=30)
                fixture_checks[name] = checked.returncode
        stages = output / "stages.jsonl"
        size = stages.stat().st_size if stages.exists() else 0
        result = {"diagnostic_only": True, "acceptance": False, "application_sha": SOURCE,
                  "source_unchanged": clean, "fixture_source_exit_codes": fixture_checks, "artifacts": summaries,
                  "exit_code": code, "elapsed_seconds": round(time.monotonic() - started, 6),
                  "outer_limit": limit_reason, "stage_bytes": size,
                  "stage_truncated": size >= LIMIT - 4096,
                  "supervisor_window_seconds": 1800,
                  "instrumentation": "PATH delegates exact original executables, argv and stdin; piped stream forwarding adds process and scheduling overhead; no acceptance equivalence claimed",
                  "selfcheck_exit_preservation_and_redaction": True}
        (output / "result.json").write_text(json.dumps(result, sort_keys=True))
        print("FOUNDATION_DIAGNOSTIC " + json.dumps(result, sort_keys=True), flush=True)
        return 0 if clean and not any(fixture_checks.values()) and limit_reason is None else 1


def prepare():
    output = Path.cwd() / ".runtime/foundation-stage-diagnostic"
    output.mkdir(mode=0o700, exist_ok=True)
    commands = [
        ("verify_c01_source", ["python", "docker/c02_baseline.py", ".runtime/c01"]),
        ("verify_c02_source", ["python", "docker/c03_baseline.py", ".runtime/c02"]),
        ("lock_check", ["uv", "lock", "--check"]),
        ("frozen_dependencies", ["uv", "sync", "--frozen", "--group", "dev"]),
        ("npm_dependencies", ["npm", "ci"]),
        ("css_build", ["npm", "run", "build:css"]),
        ("javascript_check", ["npm", "run", "check:js"]),
        ("static_build", ["uv", "run", "--frozen", "python", "manage.py", "collectstatic", "--noinput", "--settings=config.settings.build", "--ignore=src/styles.css"]),
    ]
    origin = time.monotonic()
    for stage, args in commands:
        started = time.monotonic()
        code = 127
        bound = False
        with tempfile.TemporaryFile() as private:
            child = subprocess.Popen(args, stdout=private, stderr=subprocess.STDOUT, start_new_session=True)
            while child.poll() is None:
                if time.monotonic() - started > 180 or time.monotonic() - origin > 600 or os.fstat(private.fileno()).st_size > 16 * 1024 * 1024:
                    bound = True
                    os.killpg(child.pid, signal.SIGTERM)
                    try:
                        child.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        os.killpg(child.pid, signal.SIGKILL)
                    break
                time.sleep(0.2)
            code = child.wait(timeout=15)
            private.seek(0)
            prefix = private.read(65536)
        value = {"event": "preparation", "stage": stage, "exit_code": code,
                 "duration_seconds": round(time.monotonic() - started, 6), "bound": bound,
                 "observed_markers": sorted(k for k, values in MARKERS.items() if code and any(v in prefix for v in values))}
        with (output / "preparation.jsonl").open("a") as file:
            file.write(json.dumps(value, sort_keys=True) + "\n")
        print("FOUNDATION_PREPARATION " + json.dumps(value, sort_keys=True), flush=True)
        if code or bound:
            return 1
    return 0

if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        try:
            raise SystemExit(prepare())
        except Exception as error:
            print("FOUNDATION_PREPARATION " + json.dumps({"error_category": category(error)}), flush=True)
            raise SystemExit(1) from None
    if sys.argv[1:] == ["verify-upload"]:
        try:
            identifier = int(os.environ["DIAGNOSTIC_ARTIFACT_ID"])
            expected = os.environ["DIAGNOSTIC_ARTIFACT_SHA256"].removeprefix("sha256:")
            assert len(expected) == 64 and all(c in "0123456789abcdef" for c in expected)
            value = artifact_summary(identifier, expected)
            print("FOUNDATION_UPLOADED_ARTIFACT " + json.dumps(value, sort_keys=True), flush=True)
            raise SystemExit(0 if value["state"] == "verified" else 1)
        except Exception as error:
            print("FOUNDATION_UPLOADED_ARTIFACT " + json.dumps({"state": category(error)}), flush=True)
            raise SystemExit(1) from None
    name = Path(sys.argv[0]).name
    if name in NAMES:
        try:
            configuration = json.loads(Path(os.environ["FITLINK_FOUNDATION_OBSERVER_CONFIG"]).read_text())
            raise SystemExit(delegate(name, sys.argv[1:], configuration))
        except Exception:
            raise SystemExit(127) from None
    try:
        raise SystemExit(main())
    except Exception as error:
        print("FOUNDATION_DIAGNOSTIC " + json.dumps({"diagnostic_only": True, "acceptance": False, "error_category": category(error)}), flush=True)
        raise SystemExit(1) from None
