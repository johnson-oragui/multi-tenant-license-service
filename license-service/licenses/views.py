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
    BadRequestResponseSerializer,
    LicenseDeactivateSerializer,
    LicenseDeactivateteResponseSerializer,
    LicenseProvisionResponseSerializer,
    LicenseProvisionSerializer,
    LicenseReinstateResponseSerializer,
    LicenseRevokeResponseSerializer,
    LicenseRevokeSerializer,
    LicenseSuspendResponseSerializer,
    LicenseSuspendSerializer,
    LicenseValidateResponseSerializer,
    LicenseValidateSerializer,
    UnauthenticatedResponseSerializer,
)
from licenses.services import (
    deactivate_license_instance,
    provision_license,
    reinstate_license,
    revoke_license,
    suspend_license,
    validate_and_activate_license,
)


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


@extend_schema(
    summary="Validate and activate a license",
    description="Validate and activate a license",
    responses={
        status.HTTP_200_OK: LicenseProvisionResponseSerializer,
        400: BadRequestResponseSerializer,
        401: UnauthenticatedResponseSerializer,
    },
    request=LicenseValidateSerializer,
    methods=["POST"],
)
class LicenseValidateView(APIView):
    """
    License Validate View
    """

    authentication_classes = []

    def post(self, request: Request) -> Response:
        """
        Validate and activate a license
        """
        serializer = LicenseValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data: dict = serializer.validated_data  # type: ignore

        try:
            result = validate_and_activate_license(
                license_key=validated_data.get("license_key", ""),
                product_code=validated_data.get("product_code", ""),
                instance_identifier=validated_data.get("instance_identifier", ""),
            )
        except ValueError as exc:
            return Response(
                data={"message": str(exc), "success": False},
                status=status.HTTP_404_NOT_FOUND,
            )

        if result.get("success") is False:
            return Response(
                data=result,
                status=status.HTTP_403_FORBIDDEN,
            )
        response_serializer = LicenseValidateResponseSerializer(data=result)
        response_serializer.is_valid(raise_exception=True)

        return Response(
            data=response_serializer.validated_data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    summary="Deactivate a license",
    description="Deactivate a license",
    responses={
        status.HTTP_200_OK: LicenseDeactivateteResponseSerializer,
        400: BadRequestResponseSerializer,
    },
    request=LicenseDeactivateSerializer,
    methods=["POST"],
)
class LicenseDeactivateView(APIView):
    """
    Deactivate a license instance
    """

    authentication_classes = []

    def post(self, request: Request) -> Response:
        """
        Deactivate a license instance
        """
        serializer = LicenseDeactivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data: dict = serializer.validated_data  #  type: ignore

        try:
            deactivate_license_instance(
                license_key=validated_data.get("license_key", ""),
                instance_identifier=validated_data.get("instance_identifier", ""),
            )
        except ValueError as exc:
            return Response(
                {"success": False, "message": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )
        response_data = LicenseDeactivateteResponseSerializer()

        return Response(data=response_data.validated_data)


@extend_schema(
    summary="Suspends a license",
    description="Suspends a license",
    responses={
        status.HTTP_200_OK: LicenseSuspendResponseSerializer,
        400: BadRequestResponseSerializer,
        401: UnauthenticatedResponseSerializer,
    },
    request=LicenseSuspendSerializer,
    methods=["POST"],
)
class LicenseSuspendView(APIView):
    """
    Suspends a license
    """

    authentication_classes = [BrandAPIKeyAuthentication]

    def post(self, request: Request, license_id: str):
        """
        Suspends a license
        """
        serializer = LicenseSuspendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data: dict = serializer.validated_data  #  type: ignore

        try:
            suspend_license(
                license_id=license_id,
                actor_type="brand",
                actor_id=request.user.id,
                reason=validated_data.get("reason"),
                deactivate_existing=validated_data["deactivate_existing"],
            )
        except ValueError as exc:
            return Response(
                {"success": False, "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_data = LicenseSuspendResponseSerializer()

        return Response(
            data=response_data.validated_data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    summary="Revoke a license",
    description="Revoke a license",
    responses={
        status.HTTP_200_OK: LicenseRevokeResponseSerializer,
        400: BadRequestResponseSerializer,
        401: UnauthenticatedResponseSerializer,
    },
    request=LicenseRevokeSerializer,
    methods=["POST"],
)
class LicenseRevokeView(APIView):
    """
    Revoke License
    """

    authentication_classes = [BrandAPIKeyAuthentication]

    def post(self, request: Request, license_id: str):
        """
        Revoke License
        """
        serializer = LicenseRevokeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data: dict = serializer.validated_data  #  type: ignore

        try:
            revoke_license(
                license_id=license_id,
                actor_type="brand",
                actor_id=request.user.id,
                reason=validated_data.get("reason"),
            )
        except ValueError as exc:
            return Response(
                data={"message": str(exc), "success": False},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_data = LicenseRevokeResponseSerializer()

        return Response(
            data=response_data.validated_data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    summary="Reinstate a license",
    description="Reinstate a license",
    responses={
        status.HTTP_200_OK: LicenseReinstateResponseSerializer,
        400: BadRequestResponseSerializer,
        401: UnauthenticatedResponseSerializer,
    },
    request=None,
    methods=["POST"],
)
class LicenseReinstateView(APIView):
    """
    Reinstate a License
    """

    authentication_classes = [BrandAPIKeyAuthentication]

    def post(self, request: Request, license_id: str):
        """
        Reinstate a License
        """

        try:
            reinstate_license(
                license_id=license_id,
                actor_type="brand",
                actor_id=request.user.id,
            )
        except ValueError as exc:
            return Response(
                data={"message": str(exc), "success": False},
                status=(
                    status.HTTP_403_FORBIDDEN
                    if "Only suspended" in str(exc)
                    else status.HTTP_404_NOT_FOUND
                ),
            )

        response_data = LicenseReinstateResponseSerializer()

        return Response(
            data=response_data.validated_data,
            status=status.HTTP_200_OK,
        )
