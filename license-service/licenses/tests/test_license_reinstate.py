"""
Test License Reinstate
"""

import pytest
from django.urls import reverse

from licenses.models import License, LicenseStatus
from licenses.tests.helpers import assert_audit_log


@pytest.mark.django_db
def test_a_reinstate_suspended_license(
    api_client_with_brand_auth,
    active_license: License,
):
    """
    Test reinstate suspended license
    """
    client, brand = api_client_with_brand_auth
    # Precondition
    active_license.status = LicenseStatus.SUSPENDED
    active_license.save(update_fields=["status"])

    url = reverse("license-reinstate", args=[active_license.id])

    response = client.post(url, {}, format="json")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    active_license.refresh_from_db()
    assert active_license.status == LicenseStatus.VALID

    # Audit log assertion
    assert_audit_log(
        action="license_reinstated",
        actor_type="brand",
        actor_id=brand.id,
        target_type="license",
        target_id=active_license.id,
    )


@pytest.mark.django_db
def test_b_reinstate_non_suspended_license_forbidden(
    api_client_with_brand_auth,
    active_license,
):
    """
    Test reinstate non suspended license forbidden
    """
    client, _ = api_client_with_brand_auth
    url = reverse("license-reinstate", args=[active_license.id])

    response = client.post(url, {}, format="json")

    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False


@pytest.mark.django_db
def test_c_reinstate_nonexistent_license(api_client_with_brand_auth):
    """
    Test reinstate nonexistent license
    """
    client, _ = api_client_with_brand_auth
    url = reverse("license-reinstate", args=["00000000-0000-0000-0000-000000000000"])

    response = client.post(url, {}, format="json")

    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
