import os

# Celery currently ships no typing marker.
from celery import Celery  # type: ignore[import-untyped]

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
app = Celery("fitlink")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
