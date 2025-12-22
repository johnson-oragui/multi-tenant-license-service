"""
License URLs
"""

from django.urls import path

from licenses.views import (
    LicenseDeactivateView,
    LicenseProvisionView,
    LicenseReinstateView,
    LicenseRevokeView,
    LicenseValidateView,
    LicenseSuspendView,
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
]
