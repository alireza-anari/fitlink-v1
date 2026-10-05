from django.urls import path

from .api import StatusView
from .health import liveness, readiness
from .referral_views import referral_landing
from .views import foundation

urlpatterns = [
    path("", foundation),
    path("i/<str:token>/", referral_landing),
    path("health/live/", liveness),
    path("health/ready/", readiness),
    path("api/v1/status/", StatusView.as_view()),
]
