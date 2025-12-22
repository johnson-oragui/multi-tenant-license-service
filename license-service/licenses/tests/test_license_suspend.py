"""
Test License Suspend
"""

import pytest
from django.test import Client
from django.urls import reverse

from licenses.models import LicenseActivation, LicenseStatus
from licenses.tests.factories import (
    activation_factory,
    license_factory,
    license_key_factory,
    product_factory,
)
from licenses.tests.helpers import assert_audit_log


@pytest.mark.django_db
def test_a_suspend_license_success(api_client_with_brand_auth):
    """
    Test suspend license success
    """
    client, brand = api_client_with_brand_auth

    product = product_factory()
    key = license_key_factory()
    new_license = license_factory(product=product, license_key=key)

    url = reverse("license-suspend", args=[new_license.id])

    payload = {
        "reason": "non-payment",
        "deactivate_existing": False,
    }

    response = client.post(url, payload, format="json")

    new_license.refresh_from_db()

    assert response.status_code == 200
    assert new_license.status == LicenseStatus.SUSPENDED

    assert_audit_log(
        action="license_suspended",
        actor_type="brand",
        actor_id=brand.id,
        target_type="license",
        target_id=new_license.id,
        metadata_subset={
            "reason": "non-payment",
            "deactivated_existing": False,
        },
    )


@pytest.mark.django_db
def test_b_suspend_license_deactivates_existing_instances(api_client_with_brand_auth):
    """
    Test suspend license deactivates existing instances
    """
    client, _ = api_client_with_brand_auth

    product = product_factory()
    key = license_key_factory()
    license_obj = license_factory(product=product, license_key=key)

    activation_factory(
        license=license_obj,
        instance_identifier="instance-001",
    )

    url = reverse("license-suspend", args=[license_obj.id])

    payload = {
        "reason": "policy violation",
        "deactivate_existing": True,
    }

    response = client.post(url, payload, format="json")

    active_count = LicenseActivation.objects.filter(
        license=license_obj,
        deactivated_at__isnull=True,
    ).count()

    license_obj.refresh_from_db()

    assert response.status_code == 200
    assert license_obj.status == LicenseStatus.SUSPENDED
    assert active_count == 0


@pytest.mark.django_db
def test_c_suspend_license_is_idempotent(api_client_with_brand_auth):
    """
    Test suspend license is idempotent
    """
    client, _ = api_client_with_brand_auth

    product = product_factory()
    key = license_key_factory()
    license_obj = license_factory(
        product=product,
        license_key=key,
        status=LicenseStatus.SUSPENDED,
    )

    url = reverse("license-suspend", args=[license_obj.id])

    payload = {
        "reason": "retry",
        "deactivate_existing": False,
    }

    response = client.post(url, payload, format="json")

    assert response.status_code == 200


@pytest.mark.django_db
def test_d_suspend_cancelled_license_fails(api_client_with_brand_auth):
    """
    Test suspend cancelled license fails
    """
    client, _ = api_client_with_brand_auth

    product = product_factory()
    key = license_key_factory()
    license_obj = license_factory(
        product=product,
        license_key=key,
        status=LicenseStatus.CANCELLED,
    )

    url = reverse("license-suspend", args=[license_obj.id])

    payload = {
        "reason": "invalid",
        "deactivate_existing": False,
    }

    response = client.post(url, payload, format="json")

    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False


@pytest.mark.django_db
def test_e_suspend_license_requires_authentication(client: Client):
    """
    Test suspend license requires authentication
    """

    url = reverse("license-suspend", args=["11111111-1111-1111-1111-111111111111"])

    payload = {
        "reason": "test",
        "deactivate_existing": False,
    }

    response = client.post(url, payload, format="json")

    assert response.status_code == 401
