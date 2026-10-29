from django.db import models

from accounts.models import CustomUser
from .models import Auditlog

def snapshot(instance: models.Model, fields : tuple[str, ...]) -> dict[str, object]:
    """Copy the given field value. For foreign keys use the _d name, e.g 'verified_by_id'."""
    return {name: getattr(instance, name) for name in fields}

def log_action(*, actor: CustomUser, action : Auditlog.Action, target: models.Model, before : dict[str, object] | None = None, after : dict[str, object] | None = None, reason : str = "") -> Auditlog:
    """Create an audit log for a specific action."""
    return Auditlog.objects.create(
        actor=actor,
        action=action,
        target_type=target._meta.label_lower,
        target_id=str(target.pk),
        target_repr=str(target)[:255],
        before=before,
        after=after,
        reason=reason
    )
