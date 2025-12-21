"""
Brand Throttling
"""

from rest_framework.throttling import SimpleRateThrottle

from licenses.util import Util


class BrandRateThrottle(SimpleRateThrottle):
    """
    Custom rate throttle for brand-related API endpoints.
    Limits requests per user based on the 'brand' scope defined in settings.
    """

    scope = "brand"

    def get_cache_key(self, request, view):
        """
        Generate a unique cache key for throttling.

        Args:
            request: The HTTP request object
            view: The view being accessed

        Returns:
            str: Cache key in format "brand:{user_id}" for authenticated users
            None: For unauthenticated users (no throttling applied)
        """
        # Skip throttling for unauthenticated users
        if not request.user:
            return None

        # Create unique cache key per user to track their request count
        return f"brand:{request.user.id}"


class AnonymousRateThrottle(SimpleRateThrottle):
    """
    Rate throttle for anonymous/unauthenticated users.
    Uses IP address hashing for identification.
    """

    scope = "anon"

    def get_cache_key(self, request, view):
        """
        Generate cache key based on hashed IP address.

        Returns:
            str: Cache key in format "anon:{hashed_ip}"
        """
        ip_address = request.META.get("REMOTE_ADDR", "")
        hashed_ip = Util.hash_value(value=ip_address)
        return f"anon:{hashed_ip}"
