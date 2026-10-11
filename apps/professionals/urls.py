from django.urls import path

from . import api, staff_api, staff_views, views

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

urlpatterns += [
    path("staff/professional-verification/queue/", staff_views.queue),
    path("staff/professional-verification/<uuid:verification_uuid>/", staff_views.case),
    path(
        "api/v1/staff/professional-verification/queue/",
        staff_api.StaffView.as_view(command="queue"),
    ),
    path(
        "api/v1/staff/professional-verification/<uuid:verification_uuid>/",
        staff_api.StaffView.as_view(),
    ),
    path(
        "api/v1/staff/professional-verification/<uuid:verification_uuid>/assign/",
        staff_api.StaffView.as_view(command="assign"),
    ),
    path(
        "api/v1/staff/professional-verification/<uuid:verification_uuid>/start/",
        staff_api.StaffView.as_view(command="start"),
    ),
    path(
        "api/v1/staff/professional-verification/<uuid:verification_uuid>/decide/",
        staff_api.StaffView.as_view(command="decide"),
    ),
    path(
        "api/v1/staff/professional-verification/<uuid:verification_uuid>/revoke/",
        staff_api.StaffView.as_view(command="revoke"),
    ),
    path(
        "api/v1/staff/professional-verification/<uuid:verification_uuid>/restrict-role/",
        staff_api.StaffView.as_view(command="restrict-role"),
    ),
    path(
        "api/v1/staff/professional-verification/<uuid:verification_uuid>/release-role-restriction/",
        staff_api.StaffView.as_view(command="release-role-restriction"),
    ),
    path(
        "api/v1/staff/professional-verification/<uuid:verification_uuid>/evidence/<uuid:asset_uuid>/",
        staff_api.StaffView.as_view(command="evidence"),
    ),
]
