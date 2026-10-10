from django.urls import path

from . import api, views

urlpatterns = [
    path("professional/setup/", views.setup),
    path("professional/preview/", views.preview),
    path("professional/verification/", views.verification_page),
    path("api/v1/professional/profile/", api.ProfileView.as_view()),
    path("api/v1/professional/profile/steps/<str:step>/", api.StepView.as_view()),
    path("api/v1/professional/preview/", api.PreviewView.as_view()),
    path("api/v1/professional/credentials/", api.CredentialView.as_view()),
    path(
        "api/v1/professional/credentials/<uuid:credential_uuid>/revise/",
        api.CredentialView.as_view(command="revise"),
    ),
    path(
        "api/v1/professional/credentials/<uuid:credential_uuid>/withdraw/",
        api.CredentialView.as_view(command="withdraw"),
    ),
    path(
        "api/v1/professional/verification/draft/", api.VerificationCommandView.as_view()
    ),
    path(
        "api/v1/professional/verification/<uuid:verification_uuid>/",
        api.VerificationView.as_view(),
    ),
    path(
        "api/v1/professional/verification/<uuid:verification_uuid>/submit/",
        api.VerificationCommandView.as_view(command="submit"),
    ),
    path(
        "api/v1/professional/verification/<uuid:verification_uuid>/withdraw/",
        api.VerificationCommandView.as_view(command="withdraw"),
    ),
]
