import requests
from django.conf import settings
from .models import Notification


def enqueue(user, event, order=None, payload=None):
    """Insert in the caller's transaction; a separate worker delivers after commit."""
    return Notification.objects.create(user=user, event=event, order_id=getattr(order, "pk", order), payload=payload or {})


def bot_call(method, payload):
    if not settings.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("telegram_not_configured")
    # Do not log response URLs: Telegram includes the secret token in the URL.
    try:
        response = requests.post(f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/{method}", json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        if not result.get("ok"):
            raise RuntimeError("telegram_rejected")
        return result["result"]
    except (requests.RequestException, ValueError) as exc:
        raise RuntimeError("telegram_delivery_failed") from None


def notification_text(notification):
    language = notification.user.language
    heading = {"uz": "Buyurtmangiz yangilandi", "ru": "Ваш заказ обновлён", "en": "Your order was updated"}.get(language, "Buyurtmangiz yangilandi")
    order = f" #{notification.order_id}" if notification.order_id else ""
    # Event labels are supplied in all three languages; payload never includes PII.
    label = EVENT_LABELS.get(notification.event, {}).get(language, heading)
    text = f"{label}{order}"
    if notification.event == "order.payment_received":
        data = notification.payload
        details = [f"{data.get('amount', '')} UZS", str(data.get("kind", "")), str(data.get("method", "")),
                   str(data.get("received_at", "")), str(data.get("receiver", ""))]
        fiscal = {"uz": "Ichki tasdiq. Fiskal chek kassadan/terminaldan beriladi.",
                  "ru": "Внутреннее подтверждение. Фискальный чек выдаётся кассой/терминалом.",
                  "en": "Internal confirmation. The fiscal receipt is issued by the cash register/terminal."}
        text += "\n" + " · ".join(details) + "\n" + fiscal.get(language, fiscal["uz"])
    if notification.event in {"order.preparation_started", "order.delivery_created", "order.delivery_updated"} and notification.payload.get("eta"):
        text += f"\nETA: {notification.payload['eta']}"
    if notification.event == "order.quote_published" and notification.payload.get("estimated_delivery_minutes") is not None:
        text += f"\n≈ {notification.payload['estimated_delivery_minutes']} min"
    if notification.event == "order.settlement_recorded":
        text += f"\n{notification.payload.get('amount', '')} UZS"
    if notification.event == "order.inspection_scheduled":
        text += f"\n{notification.payload.get('inspection_at', '')}"
    if notification.event == "order.schedule_updated":
        text += f"\n{notification.payload.get('starts_at', '')} — {notification.payload.get('ends_at', '')}"
        if notification.payload.get("reason"):
            text += f"\n{notification.payload['reason']}"
    return text[:4000]


EVENT_LABELS = {
    "payment.recorded": {"uz": "To‘lov qayd etildi", "ru": "Платёж зарегистрирован", "en": "Payment recorded"},
    "assignment.expired": {"uz": "Santexnik javob muddati tugadi", "ru": "Истёк срок ответа мастера", "en": "Plumber response overdue"},
}

_LABEL_ROWS = {
    "order.created": ("So‘rovingiz yuborildi", "Заявка отправлена", "Request submitted"),
    "order.urgent_confirmed": ("Shoshilinchlik tasdiqlandi", "Срочность подтверждена", "Urgency confirmed"),
    "order.plumber_assigned": ("Sizga so‘rov biriktirildi", "Вам назначена заявка", "A request was assigned to you"),
    "order.plumber_accepted": ("Santexnik so‘rovni qabul qildi", "Мастер принял заявку", "Plumber accepted your request"),
    "order.inspection_scheduled": ("Ko‘rik vaqti belgilandi", "Назначено время осмотра", "Inspection scheduled"),
    "order.estimate_submitted": ("Ish va materiallar ro‘yxati tayyor", "Список работ и материалов готов", "Work and materials list ready"),
    "order.store_assigned": ("Do‘kon biriktirildi", "Назначен магазин", "Store assigned"),
    "order.store_accepted": ("Do‘kon buyurtmani qabul qildi", "Магазин принял заказ", "Store accepted the order"),
    "order.store_rejected": ("Do‘kon buyurtmani rad etdi", "Магазин отклонил заказ", "Store declined the order"),
    "order.quote_published": ("Smeta tasdiqlashingizni kutmoqda", "Смета ожидает подтверждения", "Estimate awaits your approval"),
    "order.quote_approved": ("Smeta tasdiqlandi", "Смета подтверждена", "Estimate approved"),
    "order.quote_rejected": ("Smeta rad etildi", "Смета отклонена", "Estimate rejected"),
    "order.contract_signed": ("Shartnoma imzolandi", "Договор подписан", "Contract signed"),
    "order.payment_received": ("To‘lov tasdig‘i", "Подтверждение платежа", "Payment confirmation"),
    "order.preparation_started": ("Materiallar tayyorlanmoqda", "Материалы готовятся", "Materials being prepared"),
    "order.delivery_created": ("Yetkazish rejalashtirildi", "Доставка запланирована", "Delivery scheduled"),
    "order.delivery_updated": ("Yetkazish holati yangilandi", "Статус доставки обновлён", "Delivery updated"),
    "order.delivery_confirmed": ("Materiallar qabuli tasdiqlandi", "Получение материалов подтверждено", "Materials receipt confirmed"),
    "order.dispute_opened": ("Nizo qayd etildi", "Спор зарегистрирован", "Dispute recorded"),
    "order.schedule_updated": ("Ish jadvali yangilandi", "График работ обновлён", "Work schedule updated"),
    "order.work_started": ("Ish boshlandi", "Работа началась", "Work started"),
    "order.work_completed": ("Santexnik ishni yakunladi", "Мастер завершил работу", "Plumber completed the work"),
    "order.work_accepted": ("Ish natijasi tasdiqlandi", "Работа принята", "Work accepted"),
    "order.dispute_resolved": ("Nizo bo‘yicha qaror qayd etildi", "Решение по спору записано", "Dispute resolution recorded"),
    "order.cancelled": ("Buyurtma bekor qilindi", "Заказ отменён", "Order cancelled"),
    "order.refund_recorded": ("Pul qaytarilishi qayd etildi", "Возврат зарегистрирован", "Refund recorded"),
    "order.refund_authorized": ("Admin qaytarishga ruxsat berdi", "Администратор разрешил возврат", "Admin authorized the refund"),
    "order.cash_handover": ("Naqd pul markazga topshirildi", "Наличные переданы в центр", "Cash handed over to service center"),
    "order.settlement_recorded": ("Hamkor to‘lovi qayd etildi", "Выплата партнёру записана", "Partner payment recorded"),
    "phone.verified": ("Telefon tasdiqlandi", "Телефон подтверждён", "Phone verified"),
    "bot.welcome": ("Xush kelibsiz. Telefoningizni ulashing.", "Добро пожаловать. Поделитесь телефоном.", "Welcome. Share your phone number."),
    "order.assignment_expired": ("Santexnik javob muddati tugadi", "Истёк срок ответа мастера", "Plumber response overdue"),
    "order.plumber_rejected": ("Santexnik so‘rovni rad etdi", "Мастер отклонил заявку", "Plumber declined the request"),
}
EVENT_LABELS.update({event: dict(zip(("uz", "ru", "en"), labels)) for event, labels in _LABEL_ROWS.items()})
