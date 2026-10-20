"""Real media fixtures cannot silently select fake service configuration."""

from types import SimpleNamespace

import pytest

from tests.integration.c04 import test_public_media_services as media


@pytest.mark.parametrize(
    "storage,processing",
    [(None, "true"), ("fake", "true"), ("s3", None), ("s3", "false")],
)
def test_real_media_settings_reject_unprovisioned_services(
    monkeypatch, storage, processing
):
    for key, value in (
        ("STORAGE_BACKEND", storage),
        ("ASSET_PROCESSING_ENABLED", processing),
    ):
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)
    settings = SimpleNamespace(STORAGE_BACKEND="fake", ASSET_PROCESSING_ENABLED=False)
    configure = getattr(media, "real_service_settings", None)
    assert callable(configure), "Missing explicit real-service test settings boundary"
    with pytest.raises(AssertionError):
        configure(settings)
    assert settings.STORAGE_BACKEND == "fake" and not settings.ASSET_PROCESSING_ENABLED


def test_real_media_settings_use_provisioned_origin_without_changing_providers(
    monkeypatch,
):
    monkeypatch.setenv("STORAGE_BACKEND", "s3")
    monkeypatch.setenv("ASSET_PROCESSING_ENABLED", "true")
    settings = SimpleNamespace(STORAGE_BACKEND="fake", ASSET_PROCESSING_ENABLED=False)
    configure = getattr(media, "real_service_settings", None)
    assert callable(configure), "Missing explicit real-service test settings boundary"
    configure(settings)
    assert (
        settings.STORAGE_BACKEND == "s3" and settings.ASSET_PROCESSING_ENABLED is True
    )
