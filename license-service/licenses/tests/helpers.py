"""
Test Helpers
"""

import base64
import hashlib
import hmac
import os

from licenses.models import AuditLog

SECRET_KEY = os.environ["API_KEY_HMAC_SECRET"]


def assert_audit_log(
    *,
    action: str,
    target_type: str,
    target_id,
    actor_type: str,
    actor_id=None,
    metadata_subset: dict | None = None,
):
    """
    Assert a matching audit log entry exists.
    """

    qs = AuditLog.objects.filter(
        action=action,
        target_type=target_type,
        target_id=target_id,
        actor_type=actor_type,
        actor_id=actor_id,
    )

    assert qs.exists(), f"AuditLog not found for action={action}"

    if metadata_subset:
        log = qs.latest("created_at")
        for key, value in metadata_subset.items():
            print("value: ", value)
            print("metadata: ", log.metadata.get(key))
            assert log.metadata.get(key) == value


def hash_value(value: str) -> str:
    """
    Hash a value using HMAC-SHA256 with a secret key.
    Fast and lightweight for rate limiting and caching.

    Args:
        value: The value to hash
        secret_key: Secret key for HMAC

    Returns:
        str: Base64-encoded hash
    """
    hash_obj = hmac.new(SECRET_KEY.encode(), value.encode(), hashlib.sha256)
    return base64.b64encode(hash_obj.digest()).decode()
