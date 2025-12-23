"""
Licenses Services Business Logic
"""

import secrets

from django.db import transaction
from django.utils import timezone

from licenses.audit import log_event
from licenses.models import (
    Brand,
    Customer,
    License,
    LicenseActivation,
    LicenseKey,
    LicenseStatus,
    Product,
)


def generate_license_key() -> str:
    """
    Generates a random key for license use
    """
    return f"LIC-{secrets.token_hex(6).upper()}"


def provision_license(
    *,
    brand: Brand,
    product_id: str,
    customer_email: str,
    expires_at: str,
) -> License:
    """
    Provisions a license for a product

    :param brand: The brand
    :type brand: Brand
    :param product_id: The product id belonging to the brand
    :type product_id: str
    :param customer_email: the email of the customer
    :type customer_email: str
    :param expires_at: expiration for the license
    :return: The newly provisioned license
    :rtype: License
    """
    with transaction.atomic():
        product = Product.objects.select_related("brand").get(id=product_id)

        if product.brand_id != brand.id:  # type: ignore
            raise ValueError("Product does not belong to brand")

        customer, _ = Customer.objects.get_or_create(email=customer_email)

        license_key, _ = LicenseKey.objects.get_or_create(
            defaults={"key": generate_license_key()},
            brand=brand,
            customer=customer,
        )

        new_license = License.objects.create(
            license_key=license_key,
            product=product,
            expires_at=expires_at,
        )

        log_event(
            data={
                "actor_type": "brand",
                "actor_id": brand.id,
                "action": "license_provisioned",
                "target_type": "license",
                "target_id": new_license.id,
            },
            metadata={
                "product_id": str(product.id),
                "customer_email": customer_email,
            },
        )

        return new_license


def validate_and_activate_license(
    *,
    license_key: str,
    product_code: str,
    instance_identifier: str,
) -> dict:
    """
    Validates a license key and activates it for a given instance.
    """
    with transaction.atomic():

        # resolve license
        try:
            license_exists = (
                License.objects.select_related("license_key")
                .select_related("license_key")
                .select_for_update()
                .get(
                    license_key__key=license_key,
                    product__code=product_code,
                )
            )
        except License.DoesNotExist as exc:
            raise ValueError("License does not exist") from exc

        # license validity checks
        if license_exists.status == LicenseStatus.CANCELLED:
            return {
                "success": False,
                "message": "license has been revoked",
            }

        if license_exists.status == LicenseStatus.SUSPENDED:
            return {
                "success": False,
                "message": "license is suspended",
            }

        if license_exists.expires_at < timezone.now():
            return {
                "success": False,
                "message": "license has expired",
            }

        # Check for existing active activation (idempotency)
        existing = LicenseActivation.objects.filter(
            license=license_exists,
            instance_identifier=instance_identifier,
            deactivated_at__isnull=True,
        ).first()

        if existing:
            return {
                "success": True,
                "data": {
                    "status": "active",
                    "activation_id": existing.id,
                },
                "message": "License already activated on this instance",
            }

        # Enforce activation limit
        active_count = LicenseActivation.objects.filter(
            license=license_exists,
            deactivated_at__isnull=True,
        ).count()

        if active_count >= license_exists.seat_limit:
            return {
                "success": False,
                "message": "Activation limit has expired",
            }

        # Create activation
        activation = LicenseActivation.objects.create(
            license=license_exists,
            instance_identifier=instance_identifier,
        )

        # Audit log

        log_event(
            data={
                "actor_type": "system",
                "actor_id": None,
                "action": "license_activated",
                "target_type": "license",
                "target_id": license_exists.id,
            },
            metadata={
                "instance_identifier": instance_identifier,
            },
        )

        return {
            "success": True,
            "message": "License successfully activated",
            "data": {
                "status": "activated",
                "activation_id": activation.id,
            },
        }


@transaction.atomic
def deactivate_license_instance(
    *,
    license_key: str,
    instance_identifier: str,
) -> None:
    """
    Deactivates a license key.
    """
    try:
        activation = (
            LicenseActivation.objects.select_for_update()
            .select_related("license__license_key")
            .get(
                license__license_key__key=license_key,
                instance_identifier=instance_identifier,
                deactivated_at__isnull=True,
            )
        )

        activation.deactivate()

        log_event(
            data={
                "actor_type": "system",
                "actor_id": None,
                "action": "license_deactivated",
                "target_type": "license",
                "target_id": activation.id,
            },
            metadata={
                "instance_identifier": instance_identifier,
            },
        )
    except LicenseActivation.DoesNotExist as exc:
        raise ValueError("Active activation not found") from exc


@transaction.atomic
def suspend_license(
    *,
    license_id: str,
    actor_type: str,
    actor_id,
    reason: str | None = None,
    deactivate_existing: bool = False,
) -> None:
    """
    Temporarily suspend a license.
    """

    license__ = License.objects.select_for_update().get(id=license_id)

    if license__.status == LicenseStatus.CANCELLED:
        raise ValueError("Cancelled licenses cannot be suspended")

    if license__.status == LicenseStatus.SUSPENDED:
        return  # idempotent

    license__.status = LicenseStatus.SUSPENDED
    license__.save(update_fields=["status"])

    if deactivate_existing:
        (
            LicenseActivation.objects.filter(
                license=license__,
                deactivated_at__isnull=True,
            ).update(deactivated_at=timezone.now())
        )

    log_event(
        data={
            "actor_type": actor_type,
            "actor_id": actor_id,
            "action": "license_suspended",
            "target_type": "license",
            "target_id": license__.id,
        },
        metadata={
            "reason": reason,
            "deactivated_existing": deactivate_existing,
        },
    )


@transaction.atomic
def reinstate_license(
    *,
    license_id: str,
    actor_type: str,
    actor_id,
) -> None:
    """
    Reinstate a suspended license.
    """

    try:
        license__ = License.objects.select_for_update().get(id=license_id)
    except License.DoesNotExist as exc:
        raise ValueError("License does not exist") from exc

    if license__.status != LicenseStatus.SUSPENDED:
        raise ValueError("Only suspended licenses can be reinstated")

    license__.status = LicenseStatus.VALID
    license__.save(update_fields=["status"])

    log_event(
        data={
            "actor_type": actor_type,
            "actor_id": actor_id,
            "action": "license_reinstated",
            "target_type": "license",
            "target_id": license__.id,
        },
        metadata={},
    )


@transaction.atomic
def revoke_license(
    *,
    license_id: str,
    actor_type: str,
    actor_id,
    reason: str | None = None,
) -> None:
    """
    Permanently revoke a license.
    """
    try:
        license__ = License.objects.select_for_update().get(id=license_id)
    except License.DoesNotExist as exc:
        raise ValueError("License does not exist") from exc

    if license__.status == LicenseStatus.CANCELLED:
        return  # idempotent

    license__.status = LicenseStatus.CANCELLED
    license__.save(update_fields=["status"])

    (
        LicenseActivation.objects.filter(license=license__, deactivated_at__isnull=True).update(
            deactivated_at=timezone.now()
        )
    )

    log_event(
        data={
            "actor_type": actor_type,
            "actor_id": actor_id,
            "action": "license_revoked",
            "target_type": "license",
            "target_id": license__.id,
        },
        metadata={
            "reason": reason,
        },
    )


def get_license_status(*, license_key: str) -> dict:
    """
    Get license status
    """

    license_key_exists = (
        LicenseKey.objects.prefetch_related(
            "licenses",
            "licenses__license_activations",
            "licenses__product",
        )
        .filter(key=license_key)
        .first()
    )

    if not license_key_exists:
        raise ValueError("License key not found")

    if not license_key_exists:
        raise ValueError("License key not found")

    entitlements = []
    valid_any = False

    for license_ in license_key_exists.licenses.all():  # type: ignore
        active_seats = license_.license_activations.filter(deactivated_at__isnull=True).count()

        seat_limit = license_.seat_limit  # nullable
        remaining = seat_limit - active_seats if seat_limit is not None else None

        is_valid = license_.status == LicenseStatus.VALID and license_.expires_at > timezone.now()

        if is_valid:
            valid_any = True

        entitlements.append(
            {
                "product_code": license_.product.code,
                "status": license_.status,
                "expires_at": license_.expires_at,
                "seat_limit": seat_limit,
                "active_seats": active_seats,
                "remaining_seats": remaining,
            }
        )

    return {
        "success": True,
        "message": "License check success",
        "data": {
            "license_key": license_key_exists.key,
            "customer_email": license_key_exists.customer and license_key_exists.customer.email,
            "entitlements": entitlements,
            "valid": valid_any,
        },
    }
