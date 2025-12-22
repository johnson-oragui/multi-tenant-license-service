"""
License Validate Test
"""

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from licenses.models import LicenseActivation, LicenseStatus
from licenses.tests.factories import (
    activation_factory,
    license_factory,
    license_key_factory,
    product_factory,
)
from licenses.tests.helpers import assert_audit_log

DEFAULT_ACTIVATION_LIMIT = 3


@pytest.mark.django_db
def test_a_validate_and_activate_success(client: Client):
    """
    Test validate and activate success
    """
    product = product_factory(code="PROD-A")
    key = license_key_factory(key="VALID-KEY")
    _ = license_factory(product=product, license_key=key)

    payload = {
        "license_key": "VALID-KEY",
        "product_code": "PROD-A",
        "instance_identifier": "instance-001",
    }

    response = client.post(reverse("license-validate"), payload, format="json")

    assert response.status_code == 200
    data = response.json()
    print(data)
    assert data["success"] is True
    assert data["data"]["status"] == "activated"

    activation_id = data["data"]["activation_id"]
    assert LicenseActivation.objects.filter(id=activation_id).exists()


@pytest.mark.django_db
def test_b_validate_is_idempotent_for_same_instance(client: Client):
    """
    Test validate is idempotent for same instance
    """
    product = product_factory()
    key = license_key_factory()
    license_obj = license_factory(product=product, license_key=key)

    activation = activation_factory(
        license=license_obj,
        instance_identifier="instance-001",
    )

    payload = {
        "license_key": key.key,
        "product_code": product.code,
        "instance_identifier": "instance-001",
    }

    response = client.post(reverse("license-validate"), payload, format="json")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["activation_id"] == str(activation.id)
    assert LicenseActivation.objects.count() == 1


@pytest.mark.django_db
def test_c_validate_fails_when_activation_limit_exceeded(client: Client):
    """
    Test validate fails when activation limit exceeded
    """
    product = product_factory()
    key = license_key_factory()
    license_obj = license_factory(product=product, license_key=key)

    for i in range(DEFAULT_ACTIVATION_LIMIT):
        activation_factory(
            license=license_obj,
            instance_identifier=f"instance-{i}",
        )

    payload = {
        "license_key": key.key,
        "product_code": product.code,
        "instance_identifier": "instance-extra",
    }

    response = client.post(reverse("license-validate"), payload, format="json")

    assert response.status_code == 403
    data = response.json()
    print("data: ", data)
    assert data["success"] is False
    assert "Activation limit" in data["message"]


@pytest.mark.django_db
def test_d_validate_fails_for_suspended_license(client: Client):
    """
    Test validate fails for suspended license
    """
    product = product_factory()
    key = license_key_factory()
    license_factory(
        product=product,
        license_key=key,
        status=LicenseStatus.SUSPENDED,
    )

    payload = {
        "license_key": key.key,
        "product_code": product.code,
        "instance_identifier": "instance-001",
    }

    response = client.post(reverse("license-validate"), payload, format="json")

    assert response.status_code == 403
    data = response.json()
    print("data: ", data)
    assert data["success"] is False
    assert "suspended" in data["message"].lower()


@pytest.mark.django_db
def test_e_validate_fails_for_revoked_license(client: Client):
    """
    Test validate fails for revoked license
    """
    product = product_factory()
    key = license_key_factory()
    license_factory(
        product=product,
        license_key=key,
        status=LicenseStatus.CANCELLED,
    )

    payload = {
        "license_key": key.key,
        "product_code": product.code,
        "instance_identifier": "instance-001",
    }

    response = client.post(reverse("license-validate"), payload, format="json")

    assert response.status_code == 403
    data = response.json()
    print("data: ", data)
    assert data["success"] is False
    assert "revoked" in data["message"].lower()


@pytest.mark.django_db
def test_f_validate_fails_for_expired_license(client: Client):
    """
    Test validate fails for expired license
    """
    product = product_factory()
    key = license_key_factory()

    license_factory(
        product=product,
        license_key=key,
        expires_at=timezone.now() - timezone.timedelta(days=1),
    )

    payload = {
        "license_key": key.key,
        "product_code": product.code,
        "instance_identifier": "instance-001",
    }

    response = client.post(reverse("license-validate"), payload, format="json")

    assert response.status_code == 403
    data = response.json()
    print("data: ", data)
    assert data["success"] is False
    assert "expired" in data["message"].lower()


@pytest.mark.django_db
def test_g_validate_fails_for_invalid_license_key(client: Client):
    """
    Test validate fails for invalid license key
    """
    payload = {
        "license_key": "NON-EXISTENT",
        "product_code": "UNKNOWN",
        "instance_identifier": "instance-001",
    }

    response = client.post(reverse("license-validate"), payload, format="json")

    assert response.status_code == 404
    data = response.json()
    print("data: ", data)
    assert data["success"] is False
    assert "does not exist" in data["message"].lower()


@pytest.mark.django_db
def test_h_validate_and_activate_creates_audit_log(client: Client):
    """
    Test validate and activate creates audit log
    """
    product = product_factory(code="PROD-A")
    key = license_key_factory(key="VALID-KEY")
    license_ = license_factory(product=product, license_key=key)

    payload = {
        "license_key": license_.license_key.key,  # type: ignore
        "product_code": license_.product.code,  # type: ignore
        "instance_identifier": "machine-123",
    }

    response = client.post(reverse("license-validate"), payload)

    assert response.status_code == 200

    assert_audit_log(
        action="license_activated",
        actor_type="system",
        actor_id=None,
        target_type="license",
        target_id=license_.id,
        metadata_subset={
            "instance_identifier": "machine-123",
        },
    )
