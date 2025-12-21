"""
Util
"""

import base64
import hashlib
import hmac
from typing import Optional

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import exception_handler


class Util:
    """
    Util Class
    """

    secret_key = "578ufejmi444444444444ce3nmfuieixmiiUHYDUd"

    @staticmethod
    def hash_value(value: str, secret_key: str = secret_key) -> str:
        """
        Hash a value using HMAC-SHA256 with a secret key.
        Fast and lightweight for rate limiting and caching.

        Args:
            value: The value to hash
            secret_key: Secret key for HMAC

        Returns:
            str: Base64-encoded hash
        """
        hash_obj = hmac.new(secret_key.encode(), value.encode(), hashlib.sha256)
        return base64.b64encode(hash_obj.digest()).decode()

    @staticmethod
    def verify_hash(value: str, hash_digest: str, secret_key: str = secret_key) -> bool:
        """
        Verify a hashed value using HMAC-SHA256 with a secret key.
        Uses constant-time comparison to prevent timing attacks.

        Args:
            value: The original value to verify
            hash_digest: The hash to verify against
            secret_key: Secret key for HMAC

        Returns:
            bool: True if hash matches, False otherwise
        """
        expected_hash = Util.hash_value(value, secret_key)
        return hmac.compare_digest(expected_hash, hash_digest)


def custom_exc_handler(exc, context) -> Optional[Response]:
    """
    A custom exception handler
    """
    response = exception_handler(exc=exc, context=context)

    if response is not None and isinstance(exc, serializers.ValidationError):
        custom_res_data = {
            "success": False,
            "message": "",
        }
        data = response.data
        if isinstance(data, dict):
            for field, messages in data.items():
                if isinstance(messages, list):
                    custom_res_data["message"] = f"{field} {messages}"
                else:
                    custom_res_data["message"] = f"{field} {messages}"
        response.data = custom_res_data

    return response
