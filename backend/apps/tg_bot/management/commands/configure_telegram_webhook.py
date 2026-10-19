"""Explicit remote setup; never registers a webhook during deployment/import."""
from urllib.parse import urlsplit, urlunsplit

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.tg_bot.services import bot_call


class Command(BaseCommand):
    help = "Inspect Telegram webhook; pass --register to explicitly set the HTTPS webhook and Mini App menu."

    def add_arguments(self, parser):
        parser.add_argument("--register", action="store_true")

    def handle(self, *args, **options):
        mini_app = urlsplit(settings.MINI_APP_URL)
        if mini_app.scheme != "https" or not mini_app.hostname or mini_app.username or mini_app.password:
            raise CommandError("MINI_APP_URL must use HTTPS.")
        if len(settings.TELEGRAM_WEBHOOK_SECRET) < 32:
            raise CommandError("Set TELEGRAM_WEBHOOK_SECRET (at least 32 characters).")
        webhook = urlunsplit((mini_app.scheme, mini_app.netloc, "/telegram/webhook/", "", ""))
        try:
            if options["register"]:
                bot_call("setWebhook", {
                    "url": webhook,
                    "secret_token": settings.TELEGRAM_WEBHOOK_SECRET,
                    "allowed_updates": ["message"],
                    # Do not discard queued user updates during an upgrade.
                    "drop_pending_updates": False,
                })
                bot_call("setChatMenuButton", {"menu_button": {
                    "type": "web_app", "text": "Mini App", "web_app": {"url": settings.MINI_APP_URL},
                }})
                self.stdout.write("Webhook and Mini App menu registered.")
            info = bot_call("getWebhookInfo", {})
        except RuntimeError as error:
            raise CommandError(f"Telegram operation failed: {error}. Check credentials/network; retry is safe.") from None
        # Do not print raw provider errors or URLs that may contain credentials.
        matches = info.get("url") == webhook
        self.stdout.write(f"Webhook URL matches: {matches}; pending updates: {info.get('pending_update_count', 0)}")
        if not matches:
            raise CommandError("Webhook is missing or mismatched. Inspect HTTPS and server logs.")
        if info.get("last_error_date"):
            self.stderr.write("Telegram has a recorded delivery error; inspect HTTPS/server logs and send /start to verify current delivery.")
