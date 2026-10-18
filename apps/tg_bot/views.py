import hmac
import re
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.audit import record
from apps.users.models import User
from apps.api.v1.auth.services import get_or_create_telegram_user
from .models import BotUpdate
from .services import enqueue


class TelegramWebhookView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = []

    @transaction.atomic
    def post(self, request):
        expected = settings.TELEGRAM_WEBHOOK_SECRET
        if not expected or not hmac.compare_digest(request.headers.get("X-Telegram-Bot-Api-Secret-Token", ""), expected):
            raise PermissionDenied("Invalid webhook secret.")
        if not isinstance(request.data, dict):
            raise ValidationError("A JSON object is required.")
        update_id = request.data.get("update_id")
        if type(update_id) is not int or not 0 <= update_id < 2**63:
            raise ValidationError("Invalid update id.")
        _, created = BotUpdate.objects.get_or_create(update_id=update_id)
        if not created:
            return Response({"ok": True})
        message = request.data.get("message", {})
        if not isinstance(message, dict):
            raise ValidationError("Invalid message.")
        sender = message.get("from", {})
        chat = message.get("chat", {})
        if not isinstance(sender, dict) or not isinstance(chat, dict):
            raise ValidationError("Invalid sender or chat.")
        if type(sender.get("id")) is not int or not 0 < sender["id"] < 2**63 or sender.get("is_bot"):
            return Response({"ok": True})
        if chat.get("type") != "private" or chat.get("id") != sender.get("id"):
            return Response({"ok": True})
        user = User.objects.select_for_update().filter(telegram_id=sender.get("id"), is_active=True, is_deleted=False).first()
        text = message.get("text", "")
        start = isinstance(text, str) and text.split(" ", 1)[0] in {"/start", f"/start@{settings.TELEGRAM_BOT_USERNAME}"}
        if not user and start:
            user = get_or_create_telegram_user(sender)
            if not user.is_active or user.is_deleted:
                return Response({"ok": True})
        if not user:
            return Response({"ok": True})
        contact = message.get("contact")
        if contact:
            if not isinstance(contact, dict):
                raise ValidationError("Invalid contact.")
            if contact.get("user_id") != sender.get("id"):
                raise ValidationError("Share your own Telegram contact.")
            digits = re.sub(r"[\s()+-]", "", str(contact.get("phone_number", "")))
            if not re.fullmatch(r"[1-9]\d{7,14}", digits):
                raise ValidationError("Invalid phone number.")
            user.phone_number = "+" + digits
            user.phone_verified_at = timezone.now()
            user.save(update_fields=["phone_number", "phone_verified_at"])
            record(user, "auth.phone_verified", user)
            enqueue(user, "phone.verified")
        elif start:
            enqueue(user, "bot.welcome")
        return Response({"ok": True})
