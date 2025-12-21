"""
Licenses Views
"""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from licenses.authentication import BrandAPIKeyAuthentication
from licenses.serializers import (
    LicenseProvisionResponseSerializer,
    LicenseProvisionSerializer,
    UnauthenticatedResponseSerializer,
    BadRequestResponseSerializer,
)
from licenses.services import provision_license


@extend_schema(
    summary="Provision a license",
    description="Create a license key (if not created yet) and license for a customer",
    responses={
        201: LicenseProvisionResponseSerializer,
        400: BadRequestResponseSerializer,
        401: UnauthenticatedResponseSerializer,
    },
    request=LicenseProvisionSerializer,
    methods=["POST"],
)
class LicenseProvisionView(APIView):
    """
    LicenseProvisionView
    """

    authentication_classes = [BrandAPIKeyAuthentication]

    def post(self, request: Request) -> Response:
        """
        Provisions a license for a product
        """
        serializer = LicenseProvisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data: dict = serializer.validated_data  # type: ignore

        try:
            new_license = provision_license(
                brand=request.user,
                product_id=validated_data["product_id"],
                customer_email=validated_data["customer_email"],
                expires_at=validated_data["expires_at"],
            )
        except ValueError as exc:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "message": str(exc),
                    "success": False,
                },
            )
        response_data = {
            "success": True,
            "data": {
                "license_id": new_license.id,
                "license_key": new_license.license_key and new_license.license_key.key,
                "status": new_license.status,
                "expires_at": new_license.expires_at,
            },
            "message": "License provisioned successfully.",
        }
        response_serializer = LicenseProvisionResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)
        return Response(
            data=response_serializer.validated_data,
            status=status.HTTP_201_CREATED,
        )
