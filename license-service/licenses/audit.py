"""
License Audit
"""

from licenses.models import AuditLog


def log_event(
    *,
    data: dict,
    metadata=None,
):
    """
    Creates a log event
    """
    AuditLog.objects.create(
        actor_type=data.get("actor_type"),
        actor_id=data.get("actor_id"),
        action=data.get("action"),
        target_type=data.get("target_type"),
        target_id=data.get("target_id"),
        metadata=metadata or {},
    )
