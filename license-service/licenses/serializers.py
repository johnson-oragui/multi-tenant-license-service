"""
Licenses Serializers
"""

# pylint: disable=abstract-method

from typing import Any

from rest_framework import serializers

from licenses.models import Product


class BaseResponseSerializer(serializers.Serializer):
    """
    Base Response Serializer
    """

    message = serializers.CharField()
    success = serializers.BooleanField(default=True)
    data: Any


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


class LicenseProvisionResponseSerializer(BaseResponseSerializer):
    """
    License Provision Response Serializer
    """

    message = serializers.CharField(default="License provisioned successfully.")
    data = LicenseDataSerializer()


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


# ++++++++++++++++ LicenseValidate Activate +++++++++++++++++++++++
class LicenseValidateSerializer(serializers.Serializer):
    """
    License Validate Serializer
    """

    license_key = serializers.CharField()
    product_code = serializers.CharField()
    instance_identifier = serializers.CharField()


class LicenseValidateDataSerializer(serializers.Serializer):
    """
    License Validate Data Serializer
    """

    activation_id = serializers.UUIDField()
    status = serializers.CharField()


class LicenseValidateResponseSerializer(BaseResponseSerializer):
    """
    License Validate Serializer
    """

    message = serializers.CharField(default="License successfully activated")
    data: Any = LicenseValidateDataSerializer()


# ++++++++++++++++ LicenseValidate Deactivate +++++++++++++++++++++++
class LicenseDeactivateSerializer(serializers.Serializer):
    """
    License Validate Serializer
    """

    license_key = serializers.CharField()
    product_code = serializers.CharField()
    instance_identifier = serializers.CharField()


class LicenseDeactivateteResponseSerializer(BaseResponseSerializer):
    """
    License deactivate Serializer
    """

    message = serializers.CharField(default="License successfully deactivated")


# +++++++++++++ License Suspend ++++++++++++++++
class LicenseSuspendSerializer(serializers.Serializer):
    """
    License Suspend Serializer
    """

    reason = serializers.CharField(required=False, allow_blank=True)
    deactivate_existing = serializers.BooleanField(default=False)


class LicenseSuspendResponseSerializer(BaseResponseSerializer):
    """
    License Suspend Response Serializer
    """

    message = serializers.CharField(default="License successfully suspended")


# +++++++++++++ License Revoke ++++++++++++++++
class LicenseRevokeSerializer(serializers.Serializer):
    """
    License Revoke Serializer
    """

    reason = serializers.CharField(required=False, allow_blank=True)


class LicenseRevokeResponseSerializer(BaseResponseSerializer):
    """
    License Revoke Response Serializer
    """

    message = serializers.CharField(default="License successfully Revoked")


# +++++++++++++ License Reinstate ++++++++++++++++


class LicenseReinstateResponseSerializer(BaseResponseSerializer):
    """
    License Reinstate Response Serializer
    """

    message = serializers.CharField(default="License successfully Reinstated")


# ++++++++++++ icense status check ++++++++++++++++
class LicenseStatusSerializer(serializers.Serializer):
    """
    License Status Serializer
    """

    license_key = serializers.CharField()


class LicenseEntitlementSerializer(serializers.Serializer):
    """
    License Entitlement Serializer
    """

    product_code = serializers.CharField()
    status = serializers.CharField()
    expires_at = serializers.DateTimeField()
    seat_limit = serializers.IntegerField(required=False, allow_null=True)
    active_seats = serializers.IntegerField()
    remaining_seats = serializers.IntegerField(required=False, allow_null=True)


class LicenseStatusDataSerializer(serializers.Serializer):
    """
    License Status Data Serializer
    """

    entitlements = serializers.ListField(child=LicenseEntitlementSerializer())
    license_key = serializers.CharField()
    customer_email = serializers.EmailField()
    valid = serializers.BooleanField()


class LicenseStatusResponseSerializer(BaseResponseSerializer):
    """
    License Status Response Serializer
    """

    data = LicenseStatusDataSerializer()
