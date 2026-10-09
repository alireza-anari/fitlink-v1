"""Separate private reconciliation Beat; inherited C02 schedule stays exact."""

import os

from celery import Celery  # type: ignore[import-untyped]

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
app = Celery("fitlink-private-reconciler")
app.config_from_object("django.conf:settings", namespace="CELERY", force=True)
app.conf.update(
    CELERY_BEAT_SCHEDULE={
        "private-assets": {
            "task": "apps.assets.tasks.reconcile_private_assets",
            "schedule": 30.0,
        },
    }
)
