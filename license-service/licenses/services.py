"""
Licenses Services Business Logic
"""

import secrets

from licenses.models import Brand, Customer, License, LicenseKey, Product


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
    product = Product.objects.select_related("brand").get(id=product_id)

    if product.brand_id != brand.id:  # type: ignore
        raise ValueError("Product does not belong to brand")

    customer, _ = Customer.objects.get_or_create(email=customer_email)

    license_key = LicenseKey.objects.create(
        key=generate_license_key(),
        brand=brand,
        customer=customer,
    )

    new_license = License.objects.create(
        license_key=license_key,
        product=product,
        expires_at=expires_at,
    )

    return new_license
