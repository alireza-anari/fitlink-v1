"""Task-only private restart barriers; no production task registration changes."""

import json
import os
import re
import sys
import time
from datetime import timedelta
from hashlib import sha256
from pathlib import Path
from uuid import UUID

from celery import shared_task

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PHONES = {
    name: f"+9891000000{number:02d}"
    for number, name in enumerate(
        ("before", "after", "scanner", "storage", "broker"), 13
    )
}
STAGE = "c03:task13:bounded-barrier"


def completed_evidence_valid(record):
    if not isinstance(record, dict):
        return False
    if not all(
        record.get(key) == value
        for key, value in {
            "head_sha": record.get("expected_sha"),
            "tree": record.get("expected_tree"),
            "head_branch": "profiles/c03-cloud",
            "event": "push",
            "status": "completed",
            "conclusion": "success",
        }.items()
    ):
        return False
    if not all(
        re.fullmatch(r"[0-9a-f]{40}", record.get(k, ""))
        for k in ("expected_sha", "expected_tree")
    ) or not record.get("id"):
        return False
    if (
        not isinstance(record.get("expected_spec_run"), int)
        or record["expected_spec_run"] < 1
    ):
        return False
    specification = record.get("specification", {})
    if not all(
        specification.get(key) == value
        for key, value in {
            "sha": record.get("expected_spec_sha"),
            "head_sha": record.get("expected_spec_sha"),
            "tree": record.get("expected_spec_tree"),
            "run_id": record.get("expected_spec_run"),
            "status": "completed",
            "event": "push",
            "head_branch": "profiles/c03-cloud",
        }.items()
    ) or not specification.get("jobs"):
        return False
    if not all(
        re.fullmatch(r"[0-9a-f]{40}", record.get(k, ""))
        for k in ("expected_spec_sha", "expected_spec_tree")
    ):
        return False
    jobs = record.get("jobs", [])
    names = {j.get("name") for j in jobs}
    required = record.get("required_jobs", [])
    if not required or names != set(required) or len(jobs) != len(required):
        return False
    for job in jobs:
        execution = job.get("execution", {})
        if (
            job.get("conclusion") != "success"
            or not job.get("id")
            or job.get("head_sha") != record["expected_sha"]
            or execution.get("real") is not True
            or execution.get("passed", 0) < 1
            or execution.get("skipped") != 0
            or execution.get("exitstatus") != 0
            or not execution.get("selections")
        ):
            return False
    return True


def services():
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    django.setup()
    from docker import c03_processing_probe

    return c03_processing_probe


def evidence(stage, **facts):
    folder = ROOT / ".runtime/c03-triage"
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / "task13.jsonl").open("a") as stream:
        stream.write(
            json.dumps({"event": "task13_restart", "stage": stage, **facts}) + "\n"
        )


def broker():
    from django.conf import settings
    from redis import Redis

    return Redis.from_url(
        settings.OTP_RATE_REDIS_URL, socket_connect_timeout=2, socket_timeout=2
    )


def wait_for(predicate, seconds=25):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.1)
    raise AssertionError("Task 13 bounded progress absent")


@shared_task(
    name="docker.c03_asset_restart_probe.crash_at_write",
    acks_late=True,
    reject_on_worker_lost=True,
    ignore_result=True,
)
def crash_at_write(asset_uuid, pv, lease_uuid, stage):
    if stage not in {"before", "after"}:
        return "denied"
    from django.db import connection
    from django.utils import timezone

    from apps.assets.storage import S3PrivateStore
    from config.use_cases.asset_processing import process_asset

    class BarrierStore(S3PrivateStore):
        def put_stream(self, key, stream, content_type, max_bytes):
            assert not connection.in_atomic_block
            if stage == "after":
                super().put_stream(key, stream, content_type, max_bytes)
            broker().set(STAGE, stage, ex=60)
            # Only the isolated test worker loads this module. The actual host
            # kills that worker; ordinary task time limits remain installed.
            wait_for(lambda: False, seconds=10)

    return process_asset(
        UUID(asset_uuid), pv, UUID(lease_uuid), timezone.now(), store=BarrierStore()
    )


@shared_task(
    name="docker.c03_asset_restart_probe.stale_delivery",
    acks_late=True,
    reject_on_worker_lost=True,
    ignore_result=True,
)
def stale_delivery(asset_uuid, pv, lease_uuid):
    from django.utils import timezone

    from config.use_cases.asset_processing import process_asset

    result = process_asset(UUID(asset_uuid), pv, UUID(lease_uuid), timezone.now())
    broker().set(STAGE, result, ex=60)


def prepare(stage):
    p = services()
    p.prepare(PHONES[stage])
    evidence(stage + "_durable_receipt_without_prompt")


def start(stage):
    p = services()
    from config.use_cases.asset_processing import scan_due_assets

    broker().delete(STAGE)
    assert (
        scan_due_assets(
            p.timezone.now(),
            1,
            enqueue=lambda a, v, lease: crash_at_write.apply_async(
                args=[str(a), v, str(lease), stage], retry=False
            ),
        )
        == 1
    )
    wait_for(lambda: broker().get(STAGE) == stage.encode(), seconds=20)
    asset = p.row(PHONES[stage])
    derivative = asset.derivatives.get()
    assert asset.state == "processing" and derivative.state == "pending"
    store = p.S3PrivateStore()
    if stage == "before":
        try:
            store.head(derivative.key)
        except FileNotFoundError:
            pass
        else:
            raise AssertionError("Unexpected pre-write object")
    else:
        assert (
            sha256(store.read_limited(derivative.key, 10_000_000)).hexdigest()
            == derivative.sha256
        )
    evidence(stage + "_real_worker_blocked_before_commit")


def fault(stage):
    p = services()
    from config.use_cases.asset_processing import process_asset, scan_due_assets

    asset = p.row(PHONES[stage])
    if stage == "broker":
        assert scan_due_assets(p.timezone.now(), 1) == 1
        attempt = p.AssetProcessingAttempt.objects.get(asset=asset, state="pending")
        assert attempt.failure_code == "broker_unavailable"
    else:
        assert scan_due_assets(p.timezone.now(), 1, enqueue=lambda *a: None) == 1
        attempt = p.AssetProcessingAttempt.objects.get(asset=asset, state="running")
        result = process_asset(asset.id, 1, attempt.lease_uuid, p.timezone.now())
        assert result == stage + "_unavailable"
    asset.refresh_from_db()
    assert (
        asset.state != "ready" and not asset.derivatives.filter(state="ready").exists()
    )
    evidence(stage + "_actual_outage_denied")


def verify(stage):
    p = services()
    from config.use_cases.asset_processing import scan_due_assets

    asset = p.row(PHONES[stage])
    old = (
        p.AssetProcessingAttempt.objects.filter(asset=asset)
        .order_by("-attempt")
        .first()
    )
    inventory = list(asset.derivatives.values_list("id", "key", "sha256"))
    p.AssetProcessingAttempt.objects.filter(pk=old.pk).update(
        lease_until=p.timezone.now() - timedelta(seconds=1)
    )
    assert scan_due_assets(p.timezone.now(), 1) == 1

    def ready():
        asset.refresh_from_db()
        return asset.state == "ready"

    wait_for(ready)
    derivative = asset.derivatives.get(state="ready")
    if inventory:
        assert inventory == [(derivative.id, derivative.key, derivative.sha256)]
    assert (
        p.AssetProcessingAttempt.objects.filter(asset=asset, state="ready").count() == 1
    )
    assert (
        p.OutboxDeliveryReceipt.objects.filter(event__aggregate_uuid=asset.id).count()
        == 1
    )
    store = p.S3PrivateStore()
    for key, digest in (
        (asset.source_key, asset.sha256),
        (derivative.key, derivative.sha256),
    ):
        assert sha256(store.read_limited(key, 10_000_000)).hexdigest() == digest
    broker().delete(STAGE)
    stale_delivery.apply_async(
        args=[str(asset.id), 1, str(old.lease_uuid)], retry=False
    )
    wait_for(lambda: broker().get(STAGE) == b"denied")
    assert asset.derivatives.count() == 1
    assert scan_due_assets(p.timezone.now(), 1) == 0
    evidence(
        stage + "_recovered_one_effect_stale_delivery_denied",
        engine=p.AssetProcessingAttempt.objects.get(
            asset=asset, state="ready"
        ).scanner_engine,
        signature=p.AssetProcessingAttempt.objects.get(
            asset=asset, state="ready"
        ).scanner_signature,
        retry=2,
        source_digest=asset.sha256,
        derivative_digest=derivative.sha256,
    )


def current_restart_evidence_valid(events):
    required = {
        stage + suffix
        for stage in ("before", "after")
        for suffix in (
            "_durable_receipt_without_prompt",
            "_real_worker_blocked_before_commit",
            "_recovered_one_effect_stale_delivery_denied",
        )
    }
    required |= {
        stage + suffix
        for stage in ("scanner", "storage", "broker")
        for suffix in (
            "_durable_receipt_without_prompt",
            "_actual_outage_denied",
            "_recovered_one_effect_stale_delivery_denied",
        )
    }
    stages = [e.get("stage") for e in events if e.get("event") == "task13_restart"]
    calls = [
        e
        for e in events
        if e.get("event") == "test_report" and e.get("phase") == "call"
    ]
    exits = [e.get("exitstatus") for e in events if e.get("event") == "pytest_exit"]
    expected_functions = {
        "test_processor_crash_before_after_derivative_write_before_commit",
        "test_scanner_storage_broker_failure_recovered",
        "test_current_state_consent_hold_during_job",
        "test_bounded_exhaustion_never_ready",
    }
    found = {e.get("node", "").split("::")[-1].split("[")[0] for e in calls}
    return (
        set(stages) == required
        and len(stages) == len(required)
        and exits == [0]
        and len(calls) == 10
        and found == expected_functions
        and all(e.get("outcome") == "passed" for e in calls)
        and all(
            e.get("node", "").startswith(
                "tests/integration/c03/test_c03_failure_recovery.py::"
            )
            for e in calls
        )
        and not any(e.get("outcome") in {"skipped", "failed"} for e in events)
    )


def run():
    from docker.c03_gate_diagnostics import watch

    os.chdir(ROOT)
    folder = ROOT / ".runtime/c03-triage"
    if folder.exists():
        return 1
    folder.mkdir(parents=True)
    folder.chmod(0o777)
    override = ROOT / ".runtime/c03-task13-compose.yml"
    override.write_text("""services:
  checks:
    environment:
      PYTEST_PLUGINS: docker.c03_pytest_triage
      C03_TRIAGE_EVIDENCE_FILE: /app/.runtime/c03-triage/processing.jsonl
  worker:
    command:
      ["uv", "run", "--frozen", "celery", "--quiet", "-A", "config.celery:app",
       "worker", "--loglevel=WARNING", "--concurrency=1", "--hostname=foundation@%h",
       "-I", "docker.c03_asset_restart_probe"]
""")
    os.environ["COMPOSE_FILE"] = f"compose.yaml:{override}"
    result = watch(
        "storage",
        ["sh", "docker/verify_c03_incremental.sh", "--task13-restart"],
        acceptance=True,
    )
    for path in sorted(folder.glob("*.jsonl")):
        for line in path.read_text().splitlines():
            print(
                "C03_TASK13 " + json.dumps(json.loads(line), sort_keys=True), flush=True
            )
    if result == 0:
        journal = [
            json.loads(line)
            for path in folder.glob("*.jsonl")
            for line in path.read_text().splitlines()
        ]
        if not current_restart_evidence_valid(journal):
            return 1
    return result


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "run":
        return run()
    if mode == "audit":
        return audit()
    if len(sys.argv) != 3 or sys.argv[2] not in PHONES:
        return 1
    {"prepare": prepare, "start": start, "fault": fault, "verify": verify}[mode](
        sys.argv[2]
    )
    return 0


AUTHORITY = [
    {
        "task": 1,
        "run": 37698722147,
        "sha": "63edc7c0bd641fea0da3e3ddbd9d4bc6cd06853e",
        "tree": "bad6dce76654a836cbd58b524b1fdee65868e6cd",
        "jobs": ["c02-migrations", "foundation"],
    },
    {
        "task": 2,
        "run": 37723166576,
        "sha": "d619d7ee7e495e377157e4e1f99e111f103caeca",
        "tree": "d7f4270f71a698e7940c5f205db9b335a9b8f793",
        "jobs": ["foundation", "c02-migrations"],
    },
    {
        "task": 3,
        "run": 37735571394,
        "sha": "f58ba8af713c8105611e383d844281c6df77171f",
        "tree": "dc3c0b03fa95e297e67f962df24f3eef8ff88b68",
        "jobs": ["c02-migrations", "foundation"],
    },
    {
        "task": 4,
        "run": 37907594072,
        "sha": "1edf4e69bedd562708b9dbc0a252015ebfd1a7c6",
        "tree": "0491ffb8de1cb44533cc6dd3f8621213e8ed9b52",
        "jobs": ["foundation", "c03-storage", "c03-timeout-probe", "c02-migrations"],
    },
    {
        "task": 5,
        "run": 37934189103,
        "sha": "da89a64082ff5aee8b76ac6369725c0050381726",
        "tree": "a9445ee4e72e74f930ebd81c1fd6275d79e8f0c6",
        "jobs": [
            "foundation",
            "c03-storage",
            "c02-migrations",
            "c03-processing",
            "c03-timeout-probe",
        ],
    },
    {
        "task": 6,
        "run": 37951875791,
        "sha": "0153cef544dbf3675fbf6eadf6959b9bb06a8e77",
        "tree": "c0f68f26e9201524f2be68b5cdf8f4d98581dbf0",
        "jobs": [
            "foundation",
            "c03-storage",
            "c02-migrations",
            "c03-timeout-probe",
            "c03-processing",
        ],
    },
    {
        "task": 7,
        "run": 37979891641,
        "sha": "7a6457a7e969393bcc43417f86597340ad0ef613",
        "tree": "38d1c9173ab32915e9e4c798a2bdd7a2cde4fffb",
        "jobs": [
            "c03-storage",
            "c02-migrations",
            "foundation",
            "c03-processing",
            "c03-timeout-probe",
        ],
    },
    {
        "task": 8,
        "run": 38026094064,
        "sha": "1349e484d3c29b1ad7767fd0840466d9d0bee558",
        "tree": "b4f944dce4df19d7a8a069e330397d8c91795307",
        "jobs": [
            "foundation",
            "c03-timeout-probe",
            "c02-migrations",
            "c03-processing",
            "c03-storage",
        ],
    },
    {
        "task": 9,
        "run": 38053735759,
        "sha": "27d7916432c26effa9fdf735fd1dffc0ff5a8ec5",
        "tree": "571e42ca20df1991dbf4dc93b3b1337a18359003",
        "jobs": [
            "c03-timeout-probe",
            "c03-processing",
            "foundation",
            "c02-migrations",
            "c03-storage",
        ],
    },
    {
        "task": 10,
        "run": 38062981527,
        "sha": "c6b06df579c30f9a4b95f04eda2a4d3a40949e37",
        "tree": "3f646d0e75d617f2b2daf1e22cef624cad8c8b50",
        "jobs": [
            "foundation",
            "c03-storage",
            "c02-migrations",
            "c03-timeout-probe",
            "c03-processing",
        ],
    },
    {
        "task": 11,
        "run": 38113535678,
        "sha": "27a6e2f57d48a66c75fd507155c821bf7a1832fa",
        "tree": "d6046f576694572b2c1cc52d9179aab10adddce7",
        "jobs": [
            "c02-migrations",
            "c03-storage",
            "c03-timeout-probe",
            "foundation",
            "c03-processing",
            "c03-owner",
        ],
    },
    {
        "task": 12,
        "run": 38119065811,
        "sha": "b93c198ff58638123edd6bb13e20998e4d2bf762",
        "tree": "7179e46f2dee23d4d4c1825fa875d030260af816",
        "jobs": [
            "c02-migrations",
            "c03-owner",
            "c03-processing",
            "c03-storage",
            "c03-staff",
            "foundation",
            "c03-timeout-probe",
        ],
    },
]


SPECIFICATION_AUTHORITY = [
    {
        "sha": "7a18a32c7706dcd11329f8aa778c4d8076311ffd",
        "run": 37571066990,
        "tree": "c1612b6a910dd100c9559a24e653de7e013f77b3",
    },
    {
        "sha": "fa636833df15fbbec1ed9f6d19dd121fcabc3df7",
        "run": 37721913275,
        "tree": "67bd30c20f3a49b285dacfdefb97a701d7ed5489",
    },
    {
        "sha": "9424a32173c6d8be7dc60730f9c2d0ee2430510e",
        "run": 37725704752,
        "tree": "d1124179622fa5404327f12332e53537830502c5",
    },
    {
        "sha": "759f1531c9d1a008818546ec61c5112aec32494c",
        "run": 37745213821,
        "tree": "576abcb70305d19a06d6c2374c11691a0195d96f",
    },
    {
        "sha": "c0f5d420ba99e5c21411570459758f7ec56c3d95",
        "run": 37926898643,
        "tree": "6cf6e118409b97d996ea28ea229a78a3f6bd7f72",
    },
    {
        "sha": "701078b3fb308dae929dbed4fb876f2c14b3fa7f",
        "run": 37949114753,
        "tree": "b4af0969846ac4f897dbcc68800649a30da92968",
    },
    {
        "sha": "302062fa13dbe88e20d6848fc196508201bba2a7",
        "run": 37975683660,
        "tree": "4563ebdc64d1b158cb86e45f88cace87003f1c2b",
    },
    {
        "sha": "fa3d0c9c42e4c987549b7ac7399a38bba5455dd4",
        "run": 37985939065,
        "tree": "4f612a25ddddeb5062e82cfe8d45340d90b3832b",
    },
    {
        "sha": "e37900f1e6971654ac50cbdbb8407320e47cb70d",
        "run": 38045752487,
        "tree": "f2a3aa93c643d15da92b723bbfbf11fbe38d1eb6",
    },
    {
        "sha": "c7a0b349f16b2a06340ef4a0aa4ef0db896c472f",
        "run": 38058891938,
        "tree": "9b9a82a354808c77dce6f07e409099597e4dbcde",
    },
    {
        "sha": "0597ffc3c9cd428bbcffcd12880367d4cdd0bf8f",
        "run": 38068682504,
        "tree": "b735126bef70ace22897e992b8af24f67732b073",
    },
    {
        "sha": "ce244b043940d06091e64bffa45da00a40f527fe",
        "run": 38117010549,
        "tree": "56b50c8b2aa8203f0bfa516054da14beb3b8e72c",
    },
]


def log_evidence(name, log, selection_proof=None):
    events = []
    for line in log.splitlines():
        if "C03_" in line and "{" in line:
            try:
                events.append(json.loads(line[line.index("{") :]))
            except json.JSONDecodeError:
                continue
    assert not any(int(x) for x in re.findall(r"(\d+) (?:skipped|failed)", log))
    assert not any(e.get("skipped", 0) or e.get("failed", 0) for e in events)
    exits = [e["exitstatus"] for e in events if e.get("event") == "pytest_exit"]
    assert all(x == 0 for x in exits)
    calls = [e for e in events if e.get("event") == "test_report"]
    assert all(e.get("outcome") == "passed" for e in calls)
    counts = [int(x) for x in re.findall(r"(\d+) passed", log)]
    counts += [e.get("passed", 0) for e in events]
    counts += [sum(e.get("phase") == "call" for e in calls)]
    selections = sorted({e.get("node", "").split("::")[0] for e in calls})
    if not selections and name != "c03-timeout-probe":
        assert selection_proof and selection_proof.get("verified") is True
        selections = selection_proof["selections"]
        assert selections and all(s.startswith("tests/") for s in selections)
    stages = {e.get("stage") for e in events}
    if selection_proof is None and name in {
        "c03-storage",
        "c03-owner",
        "c03-staff",
        "c03-processing",
    }:
        minimum = {
            "c03-storage": 91,
            "c03-owner": 75,
            "c03-staff": 67,
            "c03-processing": 62,
        }[name]
        assert sum(e.get("phase") == "call" for e in calls) >= minimum
    if name == "c03-processing":
        assert {
            "real_worker_scanned_before_sigkill",
            "broker_restart_expired_lease_recovered_once",
            "injected_real_scanner_outage_denied",
            "real_scanner_post_fault_healthy",
            "actual_separate_beat_recovered_missed_prompt",
            "actual_decoder_died_on_parent_sigkill",
        } <= stages
        assert exits and max(counts) >= 62
    elif name == "c03-storage":
        assert exits and max(counts) >= 91
    elif name == "c03-owner":
        assert len(exits) >= 2 and max(counts) >= 75
    elif name == "c03-staff":
        assert len(exits) >= 2 and max(counts) >= 67
    elif name == "c03-timeout-probe":
        assert re.search(r'"supervisor_contract_satisfied":\s*true', log)
        return {
            "real": True,
            "passed": 1,
            "skipped": 0,
            "exitstatus": 0,
            "selections": ["docker/c03_timeout_probe.py"],
        }
    elif name == "c02-migrations":
        assert 269 in counts and "durable" in log and "redis-cli" in log
    elif name == "foundation":
        assert "c02_baseline.py" in log
        assert max(counts) >= 311
        # Earlier runs report raw suites; later runs report all six supervised
        # execution journals and aggregate counts without private stdout.
        assert (38 in counts and 710 <= max(counts)) or (
            len(exits) >= 3 and max(counts) >= 1000
        )
    else:
        raise AssertionError("Unknown authoritative job")
    assert sum(counts) > 0
    return {
        "real": True,
        "passed": sum(counts),
        "skipped": 0,
        "exitstatus": 0,
        "selections": selections,
    }


def audit():
    from urllib.parse import urlparse
    from urllib.request import HTTPRedirectHandler, Request, build_opener

    class PublicRedirect(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            assert urlparse(newurl).scheme == "https"
            # API token is never forwarded to signed artifact/log hosts.
            return Request(newurl, method="GET")

    opener = build_opener(PublicRedirect())
    token = os.environ.get("GITHUB_TOKEN")
    assert token, "Read-only Actions token unavailable"

    def get(path, *, raw=False, binary=False):
        url = "https://api.github.com/repos/alireza-anari/fitlink-v1/" + path
        request = Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "FitLink-C03-audit",
            },
        )
        with opener.open(request, timeout=20) as response:
            data = response.read(4_000_001)
        assert len(data) <= 4_000_000
        if binary:
            return data
        text = data.decode("utf-8")
        return text if raw else json.loads(text)

    ledger = (ROOT / "docs/implementation/C03_EXECUTION_LEDGER.md").read_text()
    import base64
    import io
    import zipfile

    def source(path, sha):
        body = get(f"contents/{path}?ref={sha}")
        assert body["encoding"] == "base64"
        return base64.b64decode(body["content"]).decode()

    def artifact_selections(expected):
        rows = get(f"actions/runs/{expected['run']}/artifacts?per_page=100")[
            "artifacts"
        ]
        selections = set()
        proofs = []
        # A failed earlier attempt's artifact cannot replace a successful journal.
        for row in sorted(rows, key=lambda a: a["created_at"], reverse=True):
            if row["expired"] or "diagnostics" not in row["name"]:
                continue
            binding = row["workflow_run"]
            assert (
                binding["id"] == expected["run"]
                and binding["head_sha"] == expected["sha"]
            )
            data = get(f"actions/artifacts/{row['id']}/zip", binary=True)
            assert "sha256:" + sha256(data).hexdigest() == row["digest"]
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                assert sum(i.file_size for i in archive.infolist()) <= 16_000_000
                for info in archive.infolist():
                    if not info.filename.endswith(".jsonl"):
                        continue
                    events = [
                        json.loads(line)
                        for line in archive.read(info).decode().splitlines()
                    ]
                    exits = [
                        e.get("exitstatus")
                        for e in events
                        if e.get("event") == "pytest_exit"
                    ]
                    reports = [e for e in events if e.get("event") == "test_report"]
                    calls = [e for e in reports if e.get("phase") == "call"]
                    if (
                        not exits
                        or any(exits)
                        or not calls
                        or any(e.get("outcome") != "passed" for e in reports)
                    ):
                        continue
                    nodes = {e["node"].split("::")[0] for e in calls}
                    assert all(n.startswith("tests/") for n in nodes)
                    selections.update(nodes)
                    proofs.append(
                        {
                            "id": row["id"],
                            "digest": row["digest"],
                            "journal": info.filename,
                        }
                    )
        return sorted(selections), proofs

    legacy_counts = {
        1: {
            "c02-migrations": [269, 135],
            "foundation": [311, 70, 90, 2, 5, 1, 2, 710, 2, 38, 5, 1, 2],
        },
        2: {
            "c02-migrations": [269, 136, 78],
            "foundation": [329, 70, 90, 2, 5, 1, 2, 789, 2, 38, 5, 1, 2],
        },
        3: {
            "c02-migrations": [269, 137, 78, 82],
            "foundation": [382, 70, 90, 2, 5, 1, 2, 872, 2, 38, 5, 1, 2],
        },
    }
    for expected, spec in zip(AUTHORITY, SPECIFICATION_AUTHORITY, strict=True):
        spec_run = get(f"actions/runs/{spec['run']}")
        spec_tree = get(f"git/commits/{spec['sha']}")["tree"]["sha"]
        spec_jobs = get(f"actions/runs/{spec['run']}/jobs?filter=latest&per_page=100")[
            "jobs"
        ]
        assert spec_jobs and all(
            j["run_id"] == spec["run"]
            and j["head_sha"] == spec["sha"]
            and j["status"] == "completed"
            for j in spec_jobs
        )
        comparison = get(f"compare/{spec['sha']}...{expected['sha']}")
        assert comparison["merge_base_commit"]["sha"] == spec["sha"]
        # Older published ledger entries use independently verified abbreviations.
        assert spec["sha"] in ledger or spec["sha"][:8] in ledger
        assert spec["tree"] in ledger or spec["tree"][:8] in ledger
        observed_selections, artifact_proofs = artifact_selections(expected)
        assert all(str(expected[k]) in ledger for k in ("run", "sha", "tree"))
        run = get(f"actions/runs/{expected['run']}")
        tree = get(f"git/commits/{expected['sha']}")["tree"]["sha"]
        jobs = get(f"actions/runs/{expected['run']}/jobs?filter=latest&per_page=100")[
            "jobs"
        ]
        assert all(j["run_id"] == expected["run"] for j in jobs)
        checked = []
        for job in jobs:
            assert job["status"] == "completed" and all(
                s["conclusion"] == "success" for s in job["steps"]
            )
            log = get(f"actions/jobs/{job['id']}/logs", raw=True)
            selection_proof = None
            if expected["task"] <= 3:
                assert [
                    int(x) for x in re.findall(r"(\d+) passed", log)
                ] == legacy_counts[expected["task"]][job["name"]]
                entry = (
                    "docker/verify_c03_incremental.sh"
                    if job["name"] == "c02-migrations"
                    else "docker/verify_foundation.sh"
                )
                invoked = (
                    "docker/verify_c03_incremental.sh"
                    if job["name"] == "c02-migrations"
                    else "docker/verify_c02.sh"
                )
                assert (
                    invoked in log
                    and "Durable quota restart probe passed: verify" in log
                    if job["name"] == "c02-migrations"
                    else invoked in log
                )
                script = source(entry, expected["sha"])
                selections = sorted(
                    set(
                        re.findall(
                            r"tests/(?:unit|integration|e2e)(?:/[\w./]+)?", script
                        )
                    )
                )
                assert selections
                selection_proof = {
                    "verified": True,
                    "selections": selections,
                    "source": expected["sha"],
                    "counts": legacy_counts[expected["task"]][job["name"]],
                }
            elif artifact_proofs:
                selection_proof = {
                    "verified": True,
                    "selections": observed_selections,
                    "artifacts": artifact_proofs,
                }
            proof = log_evidence(job["name"], log, selection_proof)
            if selection_proof:
                proof["selection_provenance"] = selection_proof
            checked.append(
                {
                    "id": job["id"],
                    "name": job["name"],
                    "head_sha": job["head_sha"],
                    "conclusion": job["conclusion"],
                    "execution": proof,
                }
            )
        record = {
            **run,
            "expected_sha": expected["sha"],
            "expected_tree": expected["tree"],
            "tree": tree,
            "required_jobs": expected["jobs"],
            "jobs": checked,
            "expected_spec_sha": spec["sha"],
            "expected_spec_tree": spec["tree"],
            "expected_spec_run": spec["run"],
            "specification": {
                "sha": spec["sha"],
                "tree": spec_tree,
                "run_id": spec_run["id"],
                "head_sha": spec_run["head_sha"],
                "status": spec_run["status"],
                "event": spec_run["event"],
                "head_branch": spec_run["head_branch"],
                "jobs": [j["id"] for j in spec_jobs],
            },
        }
        assert completed_evidence_valid(record)
        evidence(
            "historical_task_verified",
            task=expected["task"],
            run=expected["run"],
            head=expected["sha"],
            tree=tree,
            jobs=[j["id"] for j in checked],
        )
        print(
            "C03_TASK13_EVIDENCE "
            + json.dumps(
                {
                    "task": expected["task"],
                    "run": expected["run"],
                    "head": expected["sha"],
                    "tree": tree,
                    "jobs": [j["id"] for j in checked],
                    "specification": record["specification"],
                    "executions": [{"job": j["id"], **j["execution"]} for j in checked],
                    "verified": True,
                }
            ),
            flush=True,
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        evidence("failed", error_class=type(error).__name__)
        raise SystemExit(1) from None
