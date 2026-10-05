from django.urls import path

from .api import StatusView
from .health import liveness, readiness

urlpatterns = [
    path("health/live/", liveness),
    path("health/ready/", readiness),
    path("api/v1/status/", StatusView.as_view()),
]
