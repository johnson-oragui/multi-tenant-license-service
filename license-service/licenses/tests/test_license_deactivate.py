"""
Test License Deactivation
"""

import pytest
from django.test import Client
from django.urls import reverse

from licenses.models import LicenseActivation
from licenses.tests.factories import (
    activation_factory,
    license_factory,
    license_key_factory,
    product_factory,
)
from licenses.tests.helpers import assert_audit_log

URL = reverse("license-deactivate")


@pytest.mark.django_db
def test_a_deactivate_license_instance_success(client: Client):
    """
    Test deactivate license instance success
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

    response = client.post(URL, payload, format="json")

    activation.refresh_from_db()

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert activation.deactivated_at is not None

    assert_audit_log(
        action="license_deactivated",
        actor_type="system",
        actor_id=None,
        target_type="license",
        target_id=activation.id,
        metadata_subset={
            "instance_identifier": "instance-001",
        },
    )


@pytest.mark.django_db
def test_b_deactivate_already_deactivated_instance_fails_cleanly(client: Client):
    """
    Test deactivate already deactivated instance fails cleanly
    """

    product = product_factory()
    key = license_key_factory()
    license_obj = license_factory(product=product, license_key=key)

    activation = activation_factory(
        license=license_obj,
        instance_identifier="instance-001",
    )
    activation.deactivate()

    payload = {
        "license_key": key.key,
        "product_code": product.code,
        "instance_identifier": "instance-001",
    }

    response = client.post(URL, payload, format="json")

    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()


@pytest.mark.django_db
def test_c_deactivate_fails_for_invalid_instance(client: Client):
    """
    Test deactivate fails for invalid instance
    """

    payload = {
        "license_key": "INVALID-KEY",
        "product_code": "PROD-X",
        "instance_identifier": "instance-001",
    }

    response = client.post(URL, payload, format="json")

    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False


@pytest.mark.django_db
def test_d_deactivate_does_not_create_new_activation(client: Client):
    """
    Test deactivate does not create new activation
    """

    product = product_factory()
    key = license_key_factory()
    license_obj = license_factory(product=product, license_key=key)

    activation_factory(
        license=license_obj,
        instance_identifier="instance-001",
    )

    initial_count = LicenseActivation.objects.count()

    payload = {
        "license_key": key.key,
        "product_code": product.code,
        "instance_identifier": "instance-001",
    }

    client.post(URL, payload, format="json")

    assert LicenseActivation.objects.count() == initial_count
