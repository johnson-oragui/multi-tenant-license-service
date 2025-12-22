"""
Test factory
"""

from django.utils import timezone

from licenses.models import (
    License,
    LicenseActivation,
    LicenseKey,
    LicenseStatus,
    Product,
)


def product_factory(code="PROD-001"):
    """
    product factory
    """
    return Product.objects.create(code=code, name="Test Product")


def license_key_factory(key="TEST-KEY-123"):
    """
    license key factory
    """
    return LicenseKey.objects.create(key=key)


def license_factory(
    *,
    product,
    license_key,
    status=LicenseStatus.VALID,
    expires_at=None,
):
    """
    license factory
    """
    return License.objects.create(
        product=product,
        license_key=license_key,
        status=status,
        expires_at=expires_at or (timezone.now() + timezone.timedelta(days=30)),
    )


def activation_factory(*, license, instance_identifier):
    """
    activation factory
    """
    return LicenseActivation.objects.create(
        license=license,
        instance_identifier=instance_identifier,
    )
