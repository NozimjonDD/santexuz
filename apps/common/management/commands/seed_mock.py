from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError

from apps.common.mock_seed import seed_mock_data


class Command(BaseCommand):
    help = "Development/test bazasi uchun barcha loyiha modellariga bog‘langan mock ma’lumot yaratadi (default: 20)."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=20, help="Har bir model uchun eng kam namuna soni (1–200).")
        parser.add_argument("--prefix", default="mock", help="Idempotent batch nomi, masalan mock yoki demo2.")
        parser.add_argument("--no-local-preview", action="store_true", help="Reserved localhost preview mijozini ishlatmaslik.")

    def handle(self, *args, **options):
        try:
            result = seed_mock_data(
                count=options["count"], prefix=options["prefix"],
                local_preview=not options["no_local_preview"],
            )
        except (ValueError, RuntimeError) as error:
            raise CommandError(str(error)) from None
        except ValidationError as error:
            raise CommandError(f"Mock yozuv validatsiyadan o‘tmadi; batch bekor qilindi: {error}") from None
        except DatabaseError:
            raise CommandError("Baza amali bajarilmadi; batch bekor qilindi. Migratsiyalar, DB ulanishi va prefix ziddiyatini tekshiring.") from None
        message = "Mavjud batch tekshirildi; yangi nusxa qo‘shilmadi." if result["reused"] else "Mock ma’lumotlar yaratildi."
        self.stdout.write(self.style.SUCCESS(message))
        for label, ids in sorted(result["records"].items()):
            self.stdout.write(f"  {label:<28} {len(ids):>5}")
        self.stdout.write("ServiceCenter yagona: 1. Bog‘liq akkauntlar va tarix jadvallarida son ko‘proq bo‘lishi mumkin.")
        self.stdout.write("Parollar ishlatib bo‘lmaydigan holatda; haqiqiy Telegram ID va jo‘natiladigan xabarlar yaratilmagan.")
        if not options["no_local_preview"]:
            self.stdout.write("Localhost UI: ‘Sinov akkaunti’ orqali kiring — mock buyurtmalar shu mijozga tegishli.")
