from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalog.models import Region, ServiceGroup
from apps.common.audit import record


class Command(BaseCommand):
    help = "Marhamat pilot hududi va TZdagi boshlang‘ich xizmat guruhlarini yaratadi; narx va yuridik matn kiritmaydi."

    @transaction.atomic
    def handle(self, *args, **options):
        region, created = Region.objects.get_or_create(code="andijon-marhamat", defaults={"name": "Andijon viloyati, Marhamat tumani"})
        if created:
            record(None, "pilot.seed", region)
        groups = [
            ("repair", "Ta’mirlash", "Ремонт", "Repair"),
            ("installation", "O‘rnatish/almashtirish", "Установка/замена", "Installation/replacement"),
            ("pipes-drainage", "Quvur/kanalizatsiya", "Трубы/канализация", "Pipes/drainage"),
            ("heating", "Isitish tizimi", "Отопление", "Heating"),
        ]
        for code, name, name_ru, name_en in groups:
            group, created = ServiceGroup.objects.get_or_create(code=code, defaults={"name": name, "name_ru": name_ru, "name_en": name_en})
            if created:
                record(None, "pilot.seed", group)
        self.stdout.write(self.style.SUCCESS("Pilot hudud va guruhlar tayyor. Tariflar, hamkorlar, markaz sozlamalari va shartnoma andozalarini admin kiritsin."))
