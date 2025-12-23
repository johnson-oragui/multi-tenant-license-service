"""
License URLs
"""

from django.urls import path

from licenses.views import (
    LicenseDeactivateView,
    LicenseListByEmailView,
    LicenseProvisionView,
    LicenseReinstateView,
    LicenseRevokeView,
    LicenseStatusView,
    LicenseSuspendView,
    LicenseValidateView,
)

urlpatterns = [
    path(
        "licenses/",
        LicenseProvisionView.as_view(),
        name="license-provision",
    ),
    path(
        "licenses/validate",
        LicenseValidateView.as_view(),
        name="license-validate",
    ),
    path(
        "licenses/deactivate",
        LicenseDeactivateView.as_view(),
        name="license-deactivate",
    ),
    path(
        "licenses/<uuid:license_id>/revoke/",
        LicenseRevokeView.as_view(),
        name="license-revoke",
    ),
    path(
        "licenses/<uuid:license_id>/reinstate/",
        LicenseReinstateView.as_view(),
        name="license-reinstate",
    ),
    path(
        "licenses/<uuid:license_id>/suspend/",
        LicenseSuspendView.as_view(),
        name="license-suspend",
    ),
    path(
        "licenses/status/",
        LicenseStatusView.as_view(),
        name="license-status",
    ),
    path(
        "licenses/email-listing/",
        LicenseListByEmailView.as_view(),
        name="license-email-listing",
    ),
]
