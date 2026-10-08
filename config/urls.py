from django.urls import path

from apps.accounts.urls import urlpatterns as account_routes
from apps.assets.urls import urlpatterns as asset_routes
from apps.governance.views import privacy_page

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
urlpatterns += account_routes
urlpatterns += asset_routes
urlpatterns += [path("privacy/requests/", privacy_page)]
