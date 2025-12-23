"""
Licenses Test License provision
"""

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from licenses.models import Brand, Product
from licenses.tests.helpers import hash_value


@pytest.mark.django_db
def test_a_brand_can_provision_license(client: Client):
    """
    Test brand can provision license
    """

    brand = Brand.objects.create(
        name="Test Brand",
        api_key=hash_value("test-key"),
    )
    product = Product.objects.create(
        brand=brand,
        code="PRO",
        name="Pro Plan",
    )

    response = client.post(
        reverse("license-provision"),
        data={
            "product_id": str(product.id),
            "customer_email": "user@example.com",
            "expires_at": (timezone.now() + timezone.timedelta(days=30)).isoformat(),
        },
        HTTP_X_API_KEY="test-key",
        content_type="application/json",
    )

    assert response.status_code == 201
    data: dict = response.json()
    assert "license_key" in data.get("data", {})


@pytest.mark.django_db
def test_b_when_wrong_product_id_returns_400(client: Client):
    """
    Test when wrong product id passed to wrong brand returns 400
    """

    brand1 = Brand.objects.create(
        name="Test Brand",
        api_key=hash_value("test-key"),
    )
    brand2 = Brand.objects.create(
        name="Test Brand 2",
        api_key="test-key-2",
    )
    product2 = Product.objects.create(
        brand=brand2,
        code="PRO",
        name="Pro Plan",
    )

    # authenticate with brand1, and pass product id from brand2
    response = client.post(
        reverse("license-provision"),
        data={
            "product_id": str(product2.id),
            "customer_email": "user1@example.com",
            "expires_at": (timezone.now() + timezone.timedelta(days=30)).isoformat(),
        },
        HTTP_X_API_KEY="test-key",
        content_type="application/json",
    )

    assert response.status_code == 400
    data: dict = response.json()
    assert "Product does not belong to brand" == data.get("message")


@pytest.mark.django_db
def test_c_when_invalid_product_id_returns_400(client: Client):
    """
    Test when invalid product id returns 400
    """

    brand1 = Brand.objects.create(
        name="Test Brand",
        api_key=hash_value("test-key"),
    )

    response = client.post(
        reverse("license-provision"),
        data={
            "product_id": "fake-product-id",
            "customer_email": "user1@example.com",
            "expires_at": (timezone.now() + timezone.timedelta(days=30)).isoformat(),
        },
        HTTP_X_API_KEY="test-key",
        content_type="application/json",
    )

    assert response.status_code == 400
    data: dict = response.json()
    assert "Must be a valid UUID." in data.get("message", "")

    response = client.post(
        reverse("license-provision"),
        data={
            "product_id": "11111111-1111-1111-1111-111111111111",
            "customer_email": "user1@example.com",
            "expires_at": (timezone.now() + timezone.timedelta(days=30)).isoformat(),
        },
        HTTP_X_API_KEY="test-key",
        content_type="application/json",
    )

    assert response.status_code == 400
    data: dict = response.json()
    assert "Product does not exist" in data.get("message", "")
