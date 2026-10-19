from datetime import timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from apps.tg_bot.models import Notification
from apps.tg_bot.services import bot_call, notification_text


class Command(BaseCommand):
    help = "Deliver a bounded outbox batch. Run periodically on the runtime machine."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)

    def handle(self, *args, **options):
        for _ in range(max(0, options["limit"])):
            with transaction.atomic():
                item = (Notification.objects.select_for_update(skip_locked=True, of=("self",))
                        .select_related("user").filter(sent_at__isnull=True, next_attempt_at__lte=timezone.now())
                        .order_by("id").first())
                if not item:
                    break
                item.attempts += 1
                try:
                    if not item.user.telegram_id or not item.user.is_active or item.user.is_deleted:
                        raise RuntimeError("telegram_recipient_unavailable")
                    payload = {"chat_id": item.user.telegram_id, "text": notification_text(item)}
                    if settings.MINI_APP_URL:
                        payload["reply_markup"] = {"inline_keyboard": [[{"text": "Mini App", "web_app": {"url": settings.MINI_APP_URL}}]]}
                    if item.event == "bot.welcome":
                        keyboard = [[{"text": "☎️ Telefon / Телефон / Phone", "request_contact": True}]]
                        if settings.MINI_APP_URL:
                            keyboard.append([{"text": "Mini App", "web_app": {"url": settings.MINI_APP_URL}}])
                        payload["reply_markup"] = {"keyboard": keyboard, "resize_keyboard": True}
                    bot_call("sendMessage", payload)
                    item.sent_at = timezone.now()
                    item.last_error = ""
                except RuntimeError as exc:
                    item.last_error = str(exc)[:100]
                    item.next_attempt_at = timezone.now() + timedelta(seconds=min(3600, 30 * 2 ** min(item.attempts, 7)))
                item.save(update_fields=["attempts", "sent_at", "last_error", "next_attempt_at"])
        self.stdout.write("Outbox batch completed.")
