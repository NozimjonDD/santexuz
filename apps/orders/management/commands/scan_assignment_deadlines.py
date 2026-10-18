from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order
from apps.tg_bot.services import enqueue
from apps.users.models import User


class Command(BaseCommand):
    help = "Notify staff once about expired plumber assignments without reassigning them."

    def handle(self, *args, **options):
        count = 0
        ids = Order.objects.filter(is_deleted=False, status=Order.Status.ASSIGNED, response_due_at__lte=timezone.now(),
                                   response_alerted_at__isnull=True).values_list("pk", flat=True)
        for order_id in ids.iterator():
            with transaction.atomic():
                order = Order.objects.select_for_update().get(pk=order_id)
                if order.is_deleted or order.status != Order.Status.ASSIGNED or order.response_alerted_at or not order.response_due_at or order.response_due_at > timezone.now():
                    continue
                staff = User.objects.filter(is_staff=True, is_active=True, is_deleted=False)
                if not staff.exists():
                    continue
                for recipient in staff:
                    enqueue(recipient, "order.assignment_expired", order, payload={"plumber_id": order.plumber_id})
                order.response_alerted_at = timezone.now()
                order.save(update_fields=["response_alerted_at", "updated_at"])
                count += 1
        self.stdout.write(f"{count} expired assignments notified.")
