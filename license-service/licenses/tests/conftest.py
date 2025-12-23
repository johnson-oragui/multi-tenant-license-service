"""
Conftest
"""

from datetime import timedelta
from typing import Tuple

import pytest
from django.test import Client
from django.utils import timezone
from rest_framework.test import APIClient

from licenses.models import (
    Brand,
    Customer,
    License,
    LicenseKey,
    LicenseStatus,
    Product,
)
from licenses.tests.helpers import hash_value


@pytest.fixture
def brand():
    """
    Brand fix
    """
    return Brand.objects.create(
        name="Test Brand",
        api_key=hash_value("test-api-key-123"),
    )


@pytest.fixture
def api_client_with_brand_auth(brand) -> Tuple[Client, Brand]:
    """
    Returns (client, brand) authenticated via BrandAPIKeyAuthentication.
    """

    client = Client(headers={"X_API_KEY": "test-api-key-123"})

    return client, brand


@pytest.fixture
def api_client():
    """
    APIClient fix
    """
    return APIClient()


@pytest.fixture
def product(brand):
    """
    Product fix
    """
    return Product.objects.create(
        brand=brand,
        code="PRO",
        name="Pro Plan",
    )


@pytest.fixture
def customer():
    """
    Customer fix
    """
    return Customer.objects.create(email="user@example.com")


@pytest.fixture
def license_key(brand, customer):
    """
    License fix
    """
    return LicenseKey.objects.create(
        key="LIC-TEST-123",
        brand=brand,
        customer=customer,
    )


@pytest.fixture
def active_license(product, license_key):
    """
    Active license fix
    """
    return License.objects.create(
        license_key=license_key,
        product=product,
        status=LicenseStatus.VALID,
        expires_at=timezone.now() + timedelta(days=30),
    )


@pytest.fixture
def license_key_with_licenses(db, brand):
    """
    license key with licenses
    """

    customer = Customer.objects.create(
        email="user@example.com",
    )

    license_key = LicenseKey.objects.create(
        key="RM-TEST-KEY",
        brand=brand,
        customer=customer,
    )

    product_main = Product.objects.create(
        brand=brand,
        code="rankmath",
        name="RankMath",
    )

    product_addon = Product.objects.create(
        brand=brand,
        code="content_ai",
        name="Content AI",
    )

    license_main = License.objects.create(
        license_key=license_key,
        product=product_main,
        status=LicenseStatus.VALID,
        expires_at=timezone.now() + timedelta(days=30),
    )

    license_addon = License.objects.create(
        license_key=license_key,
        product=product_addon,
        status=LicenseStatus.SUSPENDED,
        expires_at=timezone.now() + timedelta(days=10),
    )

    return {
        "license_key": license_key,
        "licenses": [license_main, license_addon],
    }


@pytest.fixture
def other_brand():
    """
    Other brand
    """
    return Brand.objects.create(
        name="WPRocket",
        api_key=hash_value("wprocket-key"),
    )


@pytest.fixture
def licenses_bulk(brand, other_brand, customer):
    """
    Licenses bulk
    """
    expires_at = timezone.now() + timedelta(days=365)

    licenses = []

    # Brand A products
    for i in range(15):
        product = Product.objects.create(
            brand=brand,
            code=f"RM_{i}",
            name=f"RankMath Product {i}",
        )

        key = LicenseKey.objects.create(
            key=f"RM-KEY-{i}",
            brand=brand,
            customer=customer,
        )

        licenses.append(
            License.objects.create(
                license_key=key,
                product=product,
                expires_at=expires_at,
            )
        )

    # Brand B products
    for i in range(10):
        product = Product.objects.create(
            brand=other_brand,
            code=f"WP_{i}",
            name=f"WP Rocket Product {i}",
        )

        key = LicenseKey.objects.create(
            key=f"WP-KEY-{i}",
            brand=other_brand,
            customer=customer,
        )

        licenses.append(
            License.objects.create(
                license_key=key,
                product=product,
                expires_at=expires_at,
            )
        )

    return licenses
