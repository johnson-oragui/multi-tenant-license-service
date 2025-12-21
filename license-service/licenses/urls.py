"""
License URLs
"""

from django.urls import path

from licenses.views import LicenseProvisionView

urlpatterns = [
    path("licenses/", LicenseProvisionView.as_view(), name="license-provision"),
]
