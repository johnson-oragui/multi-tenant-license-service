"""
Test License Revoke
"""

import typing

import pytest
from django.test import Client
from django.urls import reverse

from licenses.models import Brand, License, LicenseStatus
from licenses.tests.helpers import assert_audit_log


@pytest.mark.django_db
def test_a_revoke_license_success(
    api_client_with_brand_auth: typing.Tuple[Client, Brand],
    active_license: License,
):
    """
    Test revoke license success
    """

    client, brand = api_client_with_brand_auth
    url = reverse("license-revoke", args=[active_license.id])
    payload = {"reason": "fraudulent use"}

    response = client.post(url, payload, format="json")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    active_license.refresh_from_db()
    assert active_license.status == LicenseStatus.CANCELLED

    # Audit log assertion
    assert_audit_log(
        action="license_revoked",
        actor_type="brand",
        actor_id=brand.id,
        target_type="license",
        target_id=active_license.id,
        metadata_subset={
            "reason": "fraudulent use",
        },
    )


@pytest.mark.django_db
def test_b_revoke_license_idempotent(
    api_client_with_brand_auth,
    active_license,
):
    """
    Test revoke license idempotent
    """
    client, brand = api_client_with_brand_auth
    url = reverse("license-revoke", args=[active_license.id])

    active_license.status = LicenseStatus.CANCELLED
    active_license.save(update_fields=["status"])

    response = client.post(url, {}, format="json")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # No duplicate side effects.
    # log not saved
    with pytest.raises(match="AuditLog not found for action=license_revoked"):
        assert_audit_log(
            action="license_revoked",
            actor_type="brand",
            actor_id=brand.id,
            target_type="license",
            target_id=active_license.id,
            metadata_subset={
                "reason": None,
            },
        )


@pytest.mark.django_db
def test_c_revoke_nonexistent_license(api_client_with_brand_auth):
    """
    Test revoke nonexistent license
    """
    client, _ = api_client_with_brand_auth
    url = reverse("license-revoke", args=["00000000-0000-0000-0000-000000000000"])

    response = client.post(url, {}, format="json")

    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
