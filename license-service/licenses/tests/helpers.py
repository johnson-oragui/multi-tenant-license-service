"""
Test Helpers
"""

from licenses.models import AuditLog


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
