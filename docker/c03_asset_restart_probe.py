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


def log_evidence(name, log):
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
    stages = {e.get("stage") for e in events}
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
            "selections": ["actual_compose_timeout_probe"],
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
        "selections": selections or [name],
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

    def get(path, *, raw=False):
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
        text = data.decode("utf-8")
        return text if raw else json.loads(text)

    ledger = (ROOT / "docs/implementation/C03_EXECUTION_LEDGER.md").read_text()
    for expected in AUTHORITY:
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
            proof = log_evidence(
                job["name"], get(f"actions/jobs/{job['id']}/logs", raw=True)
            )
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
