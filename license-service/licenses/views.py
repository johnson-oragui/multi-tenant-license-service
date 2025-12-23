"""
Licenses Views
"""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from common.schema_pagination import StandardLimitOffsetPagination
from licenses.authentication import BrandAPIKeyAuthentication
from licenses.serializers import (
    BadRequestResponseSerializer,
    BrandSignupResponseSerializer,
    BrandSignupSerializer,
    ConflictResponseSerializer,
    LicenseDeactivateSerializer,
    LicenseDeactivateteResponseSerializer,
    LicenseListByEmailResponseSerializer,
    LicenseListByEmailSerializer,
    LicenseProvisionResponseSerializer,
    LicenseProvisionSerializer,
    LicenseReinstateResponseSerializer,
    LicenseRevokeResponseSerializer,
    LicenseRevokeSerializer,
    LicenseStatusResponseSerializer,
    LicenseStatusSerializer,
    LicenseSuspendResponseSerializer,
    LicenseSuspendSerializer,
    LicenseValidateResponseSerializer,
    LicenseValidateSerializer,
    UnauthenticatedResponseSerializer,
    serialize_license_list,
)
from licenses.services import (
    create_brand,
    deactivate_license_instance,
    get_license_status,
    list_licenses_by_customer_email,
    provision_license,
    reinstate_license,
    revoke_license,
    suspend_license,
    validate_and_activate_license,
)


@extend_schema(
    summary="Brand signup",
    description="Public endpoint to create a brand and issue an API key.",
    responses={
        status.HTTP_201_CREATED: BrandSignupResponseSerializer,
        status.HTTP_400_BAD_REQUEST: BadRequestResponseSerializer,
        status.HTTP_401_UNAUTHORIZED: UnauthenticatedResponseSerializer,
        status.HTTP_409_CONFLICT: ConflictResponseSerializer,
    },
    request=BrandSignupSerializer,
    methods=["POST"],
    tags=["BRANDS"],
)
class BrandSignupView(APIView):
    """
    Public endpoint to create a brand and issue an API key.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request: Request) -> Response:
        """
        Public endpoint to create a brand and issue an API key.
        """
        serializer = BrandSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data: dict = serializer.validated_data  # type: ignore
        try:
            result = create_brand(name=validated_data["name"])
        except ValueError as exc:
            return Response(
                data={"message": str(exc), "success": False}, status=status.HTTP_409_CONFLICT
            )

        response_data = BrandSignupResponseSerializer(
            data={
                "data": result,
                "message": "Brand Account created successfully",
                "success": True,
            }
        )
        response_data.is_valid(raise_exception=True)

        return Response(data=response_data.validated_data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Provision a license",
    description="Create a license key (if not created yet) and license for a customer",
    responses={
        status.HTTP_201_CREATED: LicenseProvisionResponseSerializer,
        status.HTTP_400_BAD_REQUEST: BadRequestResponseSerializer,
        status.HTTP_401_UNAUTHORIZED: UnauthenticatedResponseSerializer,
    },
    request=LicenseProvisionSerializer,
    methods=["POST"],
    tags=["LICENSES"],
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
    tags=["LICENSES"],
    summary="Validate and activate a license",
    description="Validate and activate a license",
    responses={
        status.HTTP_200_OK: LicenseProvisionResponseSerializer,
        status.HTTP_400_BAD_REQUEST: BadRequestResponseSerializer,
        status.HTTP_401_UNAUTHORIZED: UnauthenticatedResponseSerializer,
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
    tags=["LICENSES"],
    summary="Deactivate a license",
    description="Deactivate a license",
    responses={
        status.HTTP_200_OK: LicenseDeactivateteResponseSerializer,
        status.HTTP_400_BAD_REQUEST: BadRequestResponseSerializer,
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
        response_data = LicenseDeactivateteResponseSerializer(
            data={"message": "License successfully deactivated"}
        )
        response_data.is_valid()

        return Response(data=response_data.validated_data)


@extend_schema(
    tags=["LICENSES"],
    summary="Suspends a license",
    description="Suspends a license",
    responses={
        status.HTTP_200_OK: LicenseSuspendResponseSerializer,
        status.HTTP_400_BAD_REQUEST: BadRequestResponseSerializer,
        status.HTTP_401_UNAUTHORIZED: UnauthenticatedResponseSerializer,
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

        response_data = LicenseSuspendResponseSerializer(
            data={"message": "License successfully suspended"}
        )
        response_data.is_valid()

        return Response(
            data=response_data.validated_data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["LICENSES"],
    summary="Revoke a license",
    description="Revoke a license",
    responses={
        status.HTTP_200_OK: LicenseRevokeResponseSerializer,
        status.HTTP_400_BAD_REQUEST: BadRequestResponseSerializer,
        status.HTTP_401_UNAUTHORIZED: UnauthenticatedResponseSerializer,
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

        response_data = LicenseRevokeResponseSerializer(
            data={"message": "License successfully Revoked"}
        )
        response_data.is_valid()

        return Response(
            data=response_data.validated_data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["LICENSES"],
    summary="Reinstate a license",
    description="Reinstate a license",
    responses={
        status.HTTP_200_OK: LicenseReinstateResponseSerializer,
        status.HTTP_400_BAD_REQUEST: BadRequestResponseSerializer,
        status.HTTP_401_UNAUTHORIZED: UnauthenticatedResponseSerializer,
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

        response_data = LicenseReinstateResponseSerializer(
            data={"message": "License successfully Reinstated"}
        )
        response_data.is_valid()

        return Response(
            data=response_data.validated_data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["LICENSES"],
    summary="Check  license Status",
    description="Check  license Status",
    responses={
        status.HTTP_200_OK: LicenseStatusResponseSerializer,
        status.HTTP_400_BAD_REQUEST: BadRequestResponseSerializer,
        status.HTTP_401_UNAUTHORIZED: UnauthenticatedResponseSerializer,
    },
    request=LicenseStatusSerializer,
    methods=["POST"],
)
class LicenseStatusView(APIView):
    """
    Check License status
    """

    authentication_classes = []

    def post(self, request: Request) -> Response:
        """
        Check License status
        """
        serializer = LicenseStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data: dict = serializer.validated_data  #  type: ignore

        try:
            result = get_license_status(license_key=validated_data["license_key"])
        except ValueError as exc:
            return Response(
                {"success": False, "message": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_data = LicenseStatusResponseSerializer(data=result)
        response_data.is_valid(raise_exception=True)

        return Response(
            data=response_data.validated_data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["LICENSES"],
    summary="List licenses by customer email",
    description="List all licenses associated with a customer email across all brands",
    request=LicenseListByEmailSerializer,
    responses={
        status.HTTP_200_OK: LicenseListByEmailResponseSerializer,
        status.HTTP_401_UNAUTHORIZED: UnauthenticatedResponseSerializer,
    },
    methods=["POST"],
)
class LicenseListByEmailView(APIView):
    """
    List licenses by customer email (brand-only).
    """

    authentication_classes = [BrandAPIKeyAuthentication]
    pagination_class = StandardLimitOffsetPagination

    def post(self, request: Request) -> Response:
        """
        List licenses by customer email (brand-only).
        """
        serializer = LicenseListByEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data: dict = serializer.validated_data  #  type: ignore

        results = list_licenses_by_customer_email(
            customer_email=validated_data.get("customer_email", ""),
            actor_type="brand",
            actor_id=request.user.id,
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(results, request)

        # Transform paginated objects
        results = serialize_license_list(page)

        return paginator.get_paginated_response(
            {
                "success": True,
                "message": "Licenses retrieved successfully",
                "data": results,
            }
        )
