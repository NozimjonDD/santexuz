from django.conf import settings
from django.db import models
from django.utils import timezone

from project_backend.base_model import BaseModel


class Notification(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    event = models.CharField(max_length=100)
    order_id = models.BigIntegerField(null=True, blank=True)
    payload = models.JSONField(default=dict)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    next_attempt_at = models.DateTimeField(default=timezone.now)
    last_error = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "tg_bot_notification"
        ordering = ["-id"]
        indexes = [models.Index(fields=["sent_at", "next_attempt_at"], name="notification_pending_idx")]


class BotUpdate(BaseModel):
    update_id = models.BigIntegerField(unique=True)

    class Meta:
        db_table = "tg_bot_botupdate"
