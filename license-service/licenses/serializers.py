"""
Licenses Serializers
"""

# pylint: disable=abstract-method

from typing import Any

from rest_framework import serializers

from licenses.models import Product


class LicenseProvisionSerializer(serializers.Serializer):
    """
    License Provision Serializer
    """

    product_id = serializers.UUIDField()
    customer_email = serializers.EmailField()
    expires_at = serializers.DateTimeField()

    def validate_product_id(self, value: serializers.UUIDField) -> serializers.UUIDField:
        """
        Validate Product ID
        """
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product does not exist")
        return value


# +++++++++++++++++ RESPONSE DATA ++++++++++++++++++++++++++++
class LicenseDataSerializer(serializers.Serializer):
    """
    License Data Serializer
    """

    license_id = serializers.UUIDField()
    license_key = serializers.CharField(allow_null=True, default=None)
    status = serializers.CharField(default="active")
    expires_at = serializers.DateTimeField()


class LicenseProvisionResponseSerializer(serializers.Serializer):
    """
    License Provision Response Serializer
    """

    message = serializers.CharField(default="License provisioned successfully.")
    success = serializers.BooleanField()
    data: Any = LicenseDataSerializer()


# +++++++++++++++ 401 ++++++++++++++++++++++


class UnauthenticatedResponseSerializer(serializers.Serializer):
    """
    Unauthenticated Response Serializer
    """

    message = serializers.CharField(default="Unauthenticated")
    success = serializers.BooleanField(default=False)


# +++++++++++++++ 400 ++++++++++++++++++++++


class BadRequestResponseSerializer(serializers.Serializer):
    """
    Bad Request Response Serializer
    """

    message = serializers.CharField(default="Bad Request")
    success = serializers.BooleanField(default=False)
