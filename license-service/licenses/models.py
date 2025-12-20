"""
Licenses Models
"""

from django.db import models
from django.utils import timezone
from uuid6 import uuid7


class BaseModel(models.Model):
    """
    Abstract BaseModel
    """

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta
        """

        abstract = True


class Brand(BaseModel):
    """
    Brand Model
    """

    name = models.CharField(max_length=255, unique=True)
    api_key = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        """
        String rep
        """
        return self.name


class Product(BaseModel):
    """
    Product Model
    """

    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        related_name="products",
        null=True,
    )
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)

    class Meta:  # type: ignore
        """
        Meta
        """

        unique_together = ("brand", "code")

    def __str__(self) -> str:
        """
        Str Rep
        """
        return f"{self.brand and self.brand.name} - {self.code}"


class Customer(BaseModel):
    """
    Customer Model
    """

    email = models.EmailField(unique=True)

    def __str__(self) -> str:
        """
        Str Rep
        """
        return self.email


class LicenseKey(BaseModel):
    """
    LicenseKey Model
    """

    key = models.CharField(max_length=255, unique=True)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        related_name="license_keys",
        null=True,
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        related_name="license_keys",
        null=True,
    )

    def __str__(self) -> str:
        """
        String Rep
        """
        return f"{self.brand and self.brand.name} - {self.key}"


class LicenseStatus(models.TextChoices):
    """
    License Status
    """

    VALID = "valid", "Valid"
    SUSPENDED = "suspended", "Suspended"
    CANCELLED = "cancelled", "Cancelled"


class License(BaseModel):
    """
    License Model
    """

    license_key = models.ForeignKey(
        LicenseKey,
        on_delete=models.SET_NULL,
        related_name="licenses",
        null=True,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        related_name="licenses",
        null=True,
    )
    status = models.CharField(
        max_length=20,
        choices=LicenseStatus.choices,
        default=LicenseStatus.VALID,
    )
    expires_at = models.DateTimeField()

    class Meta:  # type: ignore
        """
        Meta
        """

        unique_together = ("license_key", "product")

    @property
    def is_active(self) -> bool:
        """
        Checks the license status is active

        :return: True if active, False if not
        :rtype: bool
        """
        return self.status == LicenseStatus.VALID and self.expires_at >= timezone.now()

    def __str__(self) -> str:
        """
        String Rep
        """
        return f"{self.product and self.product.code} ({self.status})"


class Activation(BaseModel):
    """
    Activation Model
    """

    license = models.ForeignKey(
        License,
        on_delete=models.SET_NULL,
        related_name="activations",
        null=True,
    )
    instance_identifier = models.CharField(max_length=255)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    class Meta:  # type: ignore
        """
        Meta
        """

        unique_together = ("license", "instance_identifier")

    def deactivate(self) -> None:
        """
        Deactivate a license

        """
        self.deactivated_at = timezone.now()
        self.save(update_fields=["deactivated_at"])

    @property
    def is_active(self) -> bool:
        return self.deactivated_at is None
