"""Real-service C04 worker contract; no production task or provider replacement."""

import json
import os
import re
import sys
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
STATE = ROOT / ".runtime/c04-media-private.json"


def failure_metadata(error, phase):
    from docker.c03_storage_errors import error_category

    allowed = {
        "worker-prepare",
        "worker-written",
        "worker-recover",
        "periodic-verify",
        "scanner-outage",
        "scanner-restored",
    }
    frames = []
    for frame in traceback.extract_tb(error.__traceback__)[-16:]:
        try:
            path = Path(frame.filename).resolve().relative_to(ROOT)
        except (ValueError, OSError):
            continue
        name = path.as_posix()
        if (
            name.startswith(("apps/", "config/", "docker/", "tests/"))
            and re.fullmatch(r"[A-Za-z0-9_./-]+\.py", name)
            and (ROOT / path).is_file()
            and re.fullmatch(r"[A-Za-z0-9_<>]+", frame.name)
            and type(frame.lineno) is int
            and 0 < frame.lineno <= 100_000
        ):
            frames.append({"file": name, "function": frame.name, "line": frame.lineno})
    return {
        "phase": phase if phase in allowed else "unknown",
        "error_class": error_category(error),
        "frames": frames[-8:],
    }


def event(stage, **metadata):
    folder = ROOT / ".runtime/c04-media-evidence"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "probe.jsonl"
    with path.open("a") as stream:
        stream.write(
            json.dumps({"event": "real_public_media_probe", "stage": stage, **metadata})
            + "\n"
        )
    path.chmod(0o644)


def run_gate():
    folder = ROOT / ".runtime/c03-triage"
    if folder.exists():
        return 1
    folder.mkdir(parents=True, mode=0o777)
    folder.chmod(0o777)
    os.environ["COMPOSE_FILE"] = "compose.yaml:docker/compose.c04-media-evidence.yml"
    from docker.c03_gate_diagnostics import watch

    code = watch("storage", ["sh", "docker/verify_c04_media.sh"], acceptance=True)
    for path in folder.glob("*.jsonl"):
        for line in path.read_text().splitlines():
            print(
                "C04_MEDIA_CASE " + json.dumps(json.loads(line), sort_keys=True),
                flush=True,
            )
    for path in (ROOT / ".runtime/c03-diagnostics").glob("storage-*.jsonl"):
        for line in path.read_text().splitlines():
            print(
                "C04_MEDIA_EVIDENCE " + json.dumps(json.loads(line), sort_keys=True),
                flush=True,
            )
    for path in (ROOT / ".runtime/c04-media-evidence").glob("*.jsonl"):
        for line in path.read_text().splitlines():
            print(
                "C04_MEDIA_PROBE " + json.dumps(json.loads(line), sort_keys=True),
                flush=True,
            )
    return code


def setup():
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    django.setup()


def redis_client():
    from django.conf import settings
    from redis import Redis

    return Redis.from_url(settings.CELERY_BROKER_URL)


def state():
    return json.loads(STATE.read_text())


def save(value):
    with STATE.open("w") as stream:
        json.dump(value, stream)
    STATE.chmod(0o600)


def wait(predicate, seconds=35):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.25)
    raise AssertionError("Public media bounded worker contract incomplete")


def copy():
    from apps.assets.models import PublicAssetCopy

    return PublicAssetCopy.objects.get(pk=UUID(state()["copy_uuid"]))


def ready():
    from apps.professionals.publication_models import ProfessionalPublication

    row = copy()
    return (
        row.state == "ready"
        and ProfessionalPublication.objects.filter(
            pk=row.publication_uuid,
            current_revision_id=row.release_revision_uuid,
            state="published",
        ).exists()
    )


def worker_prepare():
    from django.conf import settings
    from django.utils import timezone

    from apps.assets import public_copies, tasks
    from apps.assets.storage import S3PrivateStore
    from tests.integration.c04.test_public_copies import api, selected
    from tests.integration.c04.test_public_media_services import raster

    assert settings.STORAGE_BACKEND == "s3" and settings.ASSET_PROCESSING_ENABLED
    assert callable(getattr(tasks, "process_public_asset_copy", None)), (
        "Missing non-eager public copy task"
    )
    assert callable(getattr(public_copies, "scan_due_public_copies", None))
    assert not STATE.exists(), "Existing probe work preserved"
    person, asset, draft = selected(settings, confirmed=False)
    derivative = asset.derivatives.get(purpose="owner_preview")
    body = raster()
    from hashlib import sha256

    derivative.sha256 = sha256(body).hexdigest()
    derivative.save(update_fields=["sha256"])
    S3PrivateStore().put(derivative.key, body, "image/png")
    from tests.integration.c04.publication_helpers import confirm

    confirm(person, draft)
    release = api().authorize_public_media(
        draft.publication_id, draft.revision_id, "avatar", timezone.now()
    )
    dto = public_copies.prepare_public_copy(
        release, timezone.now(), authorize=api().validate_release
    )
    actor = person.actor
    save(
        {
            "copy_uuid": str(dto.id),
            "profile_uuid": str(person.profile.id),
            "source_uuid": str(asset.id),
            "publication_uuid": str(draft.publication_id),
            "actor": {
                "user_uuid": str(actor.user_uuid),
                "auth_version": actor.auth_version,
                "scope": actor.scope.value,
                "control_id": str(actor.control_id),
                "authenticated_at": actor.authenticated_at.isoformat(),
            },
        }
    )
    redis_client().set("c04-media-block:" + dto.id.hex, "1", ex=180)
    assert api().scan_due_public_copies(timezone.now(), 100) == 1
    event("real_worker_queued")


def worker_written():
    from apps.assets.models import PublicCopyAttempt
    from apps.assets.storage import S3PrivateStore

    row = copy()
    wait(lambda: redis_client().exists("c04-media-written:" + row.id.hex))
    attempt = PublicCopyAttempt.objects.get(copy=row, generation=1)
    assert attempt.state == "running" and S3PrivateStore().head(attempt.key).size > 0
    assert not ready()
    event("real_output_written_before_commit")


def worker_recover():
    from django.utils import timezone

    from apps.assets.models import PublicCopyAttempt
    from apps.assets.storage import S3PrivateStore
    from config.use_cases import public_media

    row = copy()
    previous = PublicCopyAttempt.objects.get(copy=row, generation=1)
    assert not ready() and S3PrivateStore().head(previous.key).size > 0
    redis_client().delete("c04-media-block:" + row.id.hex)
    # Fixture-only lease expiration after an actual SIGKILL, as in C03's probe.
    PublicCopyAttempt.objects.filter(pk=previous.pk).update(
        lease_until=timezone.now() - timedelta(seconds=1)
    )
    assert public_media.scan_due_public_copies(timezone.now(), 100) == 1
    wait(ready)
    row.refresh_from_db()
    assert row.generation == 2
    assert PublicCopyAttempt.objects.filter(copy=row).count() == 2
    assert S3PrivateStore().head(previous.key).size > 0
    event("sigkill_recovered_new_generation_once")


def new_release():
    from django.conf import settings

    from apps.accounts.sessions import AccountActor, SessionScope
    from apps.assets.models import PublicAssetCopy
    from apps.professionals.models import ProfessionalProfile
    from apps.professionals.publication_models import ProfessionalPublication
    from tests.integration.c04.publication_helpers import configure, confirm, prepare

    value = state()
    actor = value["actor"]
    actor = AccountActor(
        UUID(actor["user_uuid"]),
        actor["auth_version"],
        SessionScope(actor["scope"]),
        UUID(actor["control_id"]),
        datetime.fromisoformat(actor["authenticated_at"]),
    )
    configure(settings)
    person = SimpleNamespace(
        profile=ProfessionalProfile.objects.get(pk=value["profile_uuid"]), actor=actor
    )
    from apps.professionals.publication_contracts import PublicationMediaSelection

    draft = prepare(
        person, media=(PublicationMediaSelection("avatar", UUID(value["source_uuid"])),)
    )
    confirm(person, draft)
    # Only the production confirmation hook may create this durable work.
    row = PublicAssetCopy.objects.get(
        release_revision_uuid=draft.revision_id, purpose="avatar"
    )
    assert (
        ProfessionalPublication.objects.get(pk=draft.publication_id).current_revision_id
        is None
    )
    value["copy_uuid"] = str(row.id)
    save(value)


def periodic_verify():
    new_release()
    # No explicit task/scan prompt: the existing installed private Beat must find it.
    wait(ready)
    event("existing_beat_discovers_unprompted_copy")


def scanner_outage():
    from apps.assets.models import PublicCopyAttempt

    new_release()
    wait(lambda: PublicCopyAttempt.objects.filter(copy=copy(), state="failed").exists())
    assert not ready()
    event("real_scanner_outage_denies_readiness")


def scanner_restored():
    from django.utils import timezone

    from apps.assets.models import PublicCopyAttempt
    from config.use_cases import public_media

    # Advance only this fixture's retry timer, never production bounds.
    PublicCopyAttempt.objects.filter(copy=copy(), state="failed").update(
        next_attempt_at=timezone.now() - timedelta(seconds=1)
    )
    assert public_media.scan_due_public_copies(timezone.now(), 100) == 1
    wait(ready)
    event("real_scanner_restore_recovers_current_copy")


def install_worker_probe():
    from apps.assets import public_copies

    original = public_copies.get_publication_store

    class ObservedPublicationStore:
        def __init__(self):
            self.backend = original()

        def head(self, key):
            return self.backend.head(key)

        def read_limited(self, key, maximum):
            return self.backend.read_limited(key, maximum)

        def put(self, key, data, content_type):
            self.backend.put(key, data, content_type)
            identifier = key.split("/")[1]
            client = redis_client()
            if client.exists("c04-media-block:" + identifier):
                client.set("c04-media-written:" + identifier, "1", ex=180)
                wait(lambda: not client.exists("c04-media-block:" + identifier), 60)

    public_copies.get_publication_store = ObservedPublicationStore


if os.environ.get("C04_MEDIA_PROBE_WORKER") == "1":
    install_worker_probe()


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "run":
        raise SystemExit(run_gate())
    setup()
    phases = {
        "worker-prepare": worker_prepare,
        "worker-written": worker_written,
        "worker-recover": worker_recover,
        "periodic-verify": periodic_verify,
        "scanner-outage": scanner_outage,
        "scanner-restored": scanner_restored,
    }
    try:
        phases[mode]()
    except Exception as error:
        event("contract_failed", **failure_metadata(error, mode))
        raise SystemExit(1) from None
