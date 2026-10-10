from django.urls import path

from .api import (
    AbandonUploadView,
    BeginUploadView,
    FinalizeUploadView,
    OwnerContentView,
    UploadBodyView,
    UploadStatusView,
)

urlpatterns = [
    path("api/v1/profile-assets/<uuid:asset_uuid>/status/", UploadStatusView.as_view()),
    path(
        "api/v1/profile-assets/<uuid:asset_uuid>/content/", OwnerContentView.as_view()
    ),
    path("api/v1/profile-assets/begin/", BeginUploadView.as_view()),
    path("api/v1/profile-assets/<uuid:asset_uuid>/body/", UploadBodyView.as_view()),
    path(
        "api/v1/profile-assets/<uuid:asset_uuid>/finalize/",
        FinalizeUploadView.as_view(),
    ),
    path(
        "api/v1/profile-assets/<uuid:asset_uuid>/abandon/", AbandonUploadView.as_view()
    ),
]
