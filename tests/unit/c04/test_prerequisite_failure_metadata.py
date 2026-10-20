"""A failed immutable prerequisite exports finite metadata, never its raw log."""

import json

import pytest

from docker import c04_baseline_runtime as observer


def classifier():
    fn = getattr(observer, "classify_prerequisite_private_log", None)
    assert callable(fn), "Missing finite immutable-prerequisite failure metadata"
    return fn


@pytest.mark.parametrize(
    "message,category",
    [
        ("dependency failed to start", "service_start_failed"),
        ("container PRIVATE_NAME is unhealthy", "service_unhealthy"),
        ("Error response from daemon: PRIVATE_VALUE", "docker_daemon_error"),
        ("failed to resolve source metadata for PRIVATE_URL", "image_metadata_failed"),
        ("429 Too Many Requests PRIVATE_TOKEN", "rate_limited"),
        ("TLS handshake timeout PRIVATE_TOKEN", "tls_timeout"),
    ],
)
def test_prerequisite_failure_categories_never_export_provider_content(
    message, category
):
    value = classifier()(message, set())
    assert category in value["categories"]
    assert "PRIVATE_" not in json.dumps(value)


def test_prerequisite_failure_progress_and_locations_are_bounded():
    path = "tests/integration/test_minio_storage.py"
    text = (
        "load metadata for PRIVATE_URL\n"
        "exporting to image PRIVATE_IMAGE\n"
        + "\n".join(f"{path}:{n}: PRIVATE_VALUE" for n in range(1, 100))
        + "\nprivate/customer.py:123: PRIVATE_VALUE"
    )
    value = classifier()(text, {path})
    assert value["last_phase"] == "image_export"
    assert len(value["failure_metadata"]["locations"]) == 12
    assert "PRIVATE_" not in json.dumps(value)
    assert "customer.py" not in json.dumps(value)
