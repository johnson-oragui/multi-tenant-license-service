"""
Test License Status
"""

from datetime import timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from licenses.models import LicenseActivation, LicenseStatus


@pytest.mark.django_db
def test_a_license_status_not_found(client: Client):
    """
    Test license status not found
    """
    url = reverse("license-status")
    response = client.post(
        url,
        data={"license_key": "INVALID-KEY"},
        format="json",
    )

    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()


@pytest.mark.django_db
def test_b_license_status_success(client: Client, license_key_with_licenses: dict):
    """
    Test license status success
    """
    license_key = license_key_with_licenses["license_key"]

    response = client.post(
        reverse("license-status"),
        data={"license_key": license_key.key},
        format="json",
    )
    print("response.json(): ", response.json())

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    inner_data = data["data"]

    assert inner_data["license_key"] == license_key.key
    assert inner_data["valid"] is True
    assert inner_data["customer_email"] == "user@example.com"
    assert len(inner_data["entitlements"]) == 2

    codes = {e["product_code"] for e in inner_data["entitlements"]}
    assert codes == {"rankmath", "content_ai"}


@pytest.mark.django_db
def test_c_license_status_active_seats(client: Client, license_key_with_licenses):
    """
    Test license status active seats
    """
    license_main = license_key_with_licenses["licenses"][0]

    # create two active activations
    LicenseActivation.objects.create(
        license=license_main,
        instance_identifier="site-1",
    )
    LicenseActivation.objects.create(
        license=license_main,
        instance_identifier="site-2",
    )

    response = client.post(
        reverse("license-status"),
        data={"license_key": license_main.license_key.key},
        format="json",
    )
    assert response.status_code == 200
    data = response.json()
    print("data: ", data)
    inner_data = data["data"]

    entitlements = inner_data["entitlements"]
    rankmath = next(e for e in entitlements if e["product_code"] == "rankmath")

    assert rankmath["active_seats"] == 2


@pytest.mark.django_db
def test_d_expired_license_reported(client: Client, license_key_with_licenses):
    """
    Test expired license reported
    """
    license_main = license_key_with_licenses["licenses"][0]

    license_main.expires_at = timezone.now() - timedelta(days=1)
    license_main.save(update_fields=["expires_at"])

    response = client.post(
        reverse("license-status"),
        data={"license_key": license_main.license_key.key},
        format="json",
    )
    data = response.json()
    inner_data = data["data"]

    entitlements = inner_data["entitlements"]
    rankmath = next(e for e in entitlements if e["product_code"] == "rankmath")

    assert rankmath["status"] == LicenseStatus.VALID
    assert inner_data["valid"] is False


@pytest.mark.django_db
def test_e_all_licenses_cancelled(client: Client, license_key_with_licenses):
    """
    Test all licenses cancelled
    """
    for license_ in license_key_with_licenses["licenses"]:
        license_.status = LicenseStatus.CANCELLED
        license_.save(update_fields=["status"])

    response = client.post(
        reverse("license-status"),
        data={"license_key": license_key_with_licenses["license_key"].key},
        format="json",
    )
    data = response.json()
    inner_data = data["data"]

    assert response.status_code == 200
    assert inner_data["valid"] is False
