"""Append-only audit trail shared by API services and the staff admin."""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from project_backend.base_model import BaseModel


class AppendOnlyQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError("Audit yozuvlarini o‘zgartirish mumkin emas.")

    def delete(self):
        raise ValidationError("Audit yozuvlarini o‘chirish mumkin emas.")

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValidationError("Audit yozuvlarini o‘zgartirish mumkin emas.")


class AuditEvent(BaseModel):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="audit_events")
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    payload = models.JSONField(default=dict, blank=True)
    objects = AppendOnlyQuerySet.as_manager()

    class Meta:
        app_label = "common"
        db_table = "common_auditevent"
        ordering = ("-created_at", "-id")
        indexes = [models.Index(fields=("object_type", "object_id"), name="audit_object_idx"), models.Index(fields=("created_at",), name="audit_created_idx")]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("Audit yozuvlarini o‘zgartirish mumkin emas.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Audit yozuvlarini o‘chirish mumkin emas.")


def record(actor, action, obj, payload=None):
    """Only pass safe metadata: never passwords, tokens, or Telegram initData."""
    return AuditEvent.objects.create(
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        object_type=obj._meta.label_lower,
        object_id=str(obj.pk),
        payload=payload or {},
    )
