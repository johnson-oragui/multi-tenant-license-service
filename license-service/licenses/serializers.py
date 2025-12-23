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


# +++++++++++++++ 409 ++++++++++++++++++++++


class ConflictResponseSerializer(serializers.Serializer):
    """
    Conflict Response Serializer
    """

    message = serializers.CharField(default="Conflict")
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


# ++++++++++++ License status check ++++++++++++++++
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


# ++++++++++++ License Listing ++++++++++++++++


class LicenseListByEmailSerializer(serializers.Serializer):
    """
    License List By Email Serializer
    """

    customer_email = serializers.EmailField()


class BrandSerializer(serializers.Serializer):
    """
    Brand Serializer
    """

    id = serializers.CharField()
    name = serializers.CharField()


class ProductSerializer(serializers.Serializer):
    """
    Prouct Serializer
    """

    id = serializers.CharField()
    code = serializers.CharField()
    name = serializers.CharField()


class LicenseListItemSerializer(serializers.Serializer):
    """
    License List Item Serializer
    """

    license_id = serializers.UUIDField()
    license_key = serializers.CharField()

    brand = BrandSerializer()
    product = ProductSerializer()

    status = serializers.CharField()
    expires_at = serializers.DateTimeField()
    is_active = serializers.BooleanField()
    active_seats = serializers.IntegerField()


class LicenseListByEmailResponseSerializer(BaseResponseSerializer):
    """
    License List By Email Response Serializer
    """

    data = LicenseListItemSerializer(many=True)
    message = serializers.CharField(default="Licenses retrieved successfully")


def serialize_license_list(licenses) -> list[dict]:
    """
    Serialize license list
    """
    results = []

    for lic in licenses:
        results.append(
            {
                "license_id": lic.id,
                "license_key": lic.license_key.key if lic.license_key else None,
                "brand": {
                    "id": lic.product.brand.id,
                    "name": lic.product.brand.name,
                },
                "product": {
                    "id": lic.product.id,
                    "code": lic.product.code,
                    "name": lic.product.name,
                },
                "status": lic.status,
                "expires_at": lic.expires_at,
                "is_active": lic.is_active,
                "active_seats": lic.active_seats,
            }
        )

    return results


# +++++++++++++++++++ SIGNUP BRAND +++++++++++++++++
class BrandSignupSerializer(serializers.Serializer):
    """
    Brand Signup Serializer
    """

    name = serializers.CharField(max_length=255)


class BrandSignupDataSerializer(serializers.Serializer):
    """
    Brand Signup Data Serializer
    """

    id = serializers.UUIDField()
    api_key = serializers.CharField()
    name = serializers.CharField()


class BrandSignupResponseSerializer(BaseResponseSerializer):
    """
    Brand Signup Response Serializer
    """

    data = BrandSignupDataSerializer()
