from django.urls import path

from . import api

urlpatterns = [
    path("accounts/entry/", api.entry_bootstrap),
    path("api/v1/auth/otp/request/", api.OtpRequestView.as_view()),
    path("api/v1/auth/otp/verify/", api.OtpVerifyView.as_view()),
    path("api/v1/auth/logout/", api.LogoutView.as_view()),
    path("api/v1/auth/logout-all/", api.LogoutAllView.as_view()),
    path("api/v1/account/me/", api.AccountView.as_view()),
    path("api/v1/account/phone-change/", api.PhoneChangeView.as_view()),
    path("api/v1/account/phone-change/proof/request/", api.ChangeRequestView.as_view()),
    path("api/v1/account/phone-change/proof/verify/", api.ChangeProofView.as_view()),
    path("api/v1/account/phone-change/apply/", api.ChangeApplyView.as_view()),
    path("api/v1/recovery/requests/", api.RecoveryIntakeView.as_view()),
    path(
        "api/v1/recovery/requests/<uuid:request_uuid>/status/",
        api.RecoveryStatusView.as_view(),
    ),
    path(
        "api/v1/recovery/requests/<uuid:request_uuid>/new-phone/request/",
        api.RecoveryOtpRequestView.as_view(),
    ),
    path(
        "api/v1/recovery/requests/<uuid:request_uuid>/new-phone/verify/",
        api.RecoveryOtpProofView.as_view(),
    ),
    path("api/v1/staff/recovery/<uuid:request_uuid>/", api.StaffRecoveryView.as_view()),
    path(
        "api/v1/staff/recovery/<uuid:request_uuid>/evidence/",
        api.StaffEvidenceView.as_view(),
    ),
    path(
        "api/v1/staff/recovery/<uuid:request_uuid>/decision/",
        api.StaffDecisionView.as_view(),
    ),
    path(
        "api/v1/staff/recovery/<uuid:request_uuid>/apply/", api.StaffApplyView.as_view()
    ),
    path("api/v1/privacy/requests/", api.PrivacyView.as_view()),
    path("api/v1/privacy/requests/<uuid:request_uuid>/", api.PrivacyView.as_view()),
]
