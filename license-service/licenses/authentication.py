"""
Licence Authentication
"""

from typing import Optional, Tuple

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from licenses.models import Brand


class BrandAPIKeyAuthentication(BaseAuthentication):
    """
    BrandAPIKeyAuthentication
    """

    def authenticate(self, request) -> Tuple[Optional[Brand], Optional[str]]:
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        api_key = request.headers.get("X-API-KEY")

        if not api_key:
            raise AuthenticationFailed(
                {"message": "Missing API Key", "success": False},
            )

        try:
            brand = Brand.objects.get(api_key=api_key)
        except Brand.DoesNotExist as exc:
            raise AuthenticationFailed("Invalid API Key") from exc
        return (brand, None)

    def authenticate_header(self, request):  # type: ignore
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return "X-API-KEY"
