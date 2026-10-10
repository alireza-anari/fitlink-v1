from django.urls import path

from . import api, views

urlpatterns = [
    path("athlete/setup/", views.setup),
    path("athlete/baseline/<uuid:baseline_uuid>/", views.baseline_page),
    path("api/v1/athlete/profile/", api.ProfileView.as_view()),
    path("api/v1/athlete/baseline/draft/", api.DraftView.as_view()),
    path("api/v1/athlete/baseline/<uuid:baseline_uuid>/", api.BaselineView.as_view()),
    path(
        "api/v1/athlete/baseline/<uuid:baseline_uuid>/steps/<str:step>/",
        api.StepView.as_view(),
    ),
]
for action in ("submit", "correct", "clear-optional", "storage-consent"):
    urlpatterns.append(
        path(
            f"api/v1/athlete/baseline/<uuid:baseline_uuid>/{action}/",
            api.BaselineCommandView.as_view(command=action),
        )
    )
urlpatterns.append(
    path(
        "api/v1/athlete/baseline/<uuid:baseline_uuid>/storage-consent/revoke/",
        api.BaselineCommandView.as_view(command="revoke"),
    )
)
