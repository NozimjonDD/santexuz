# Santex Mini App — Django backend

`docs/TZ_docs.md` bo‘yicha mijoz, santexnik, do‘kon va xizmat markazi uchun DRF backend. Patirchi loyihasining `apps/api/v1/auth|site|admin`, domen applari, `project_backend/settings/` va `templates/8mobile/` tuzilishi o‘rganilib, shu loyiha uchun qo‘llandi. Patirchining maxfiy sozlamalari, eski biznes modellari va tashqi UI aktivlari ko‘chirilmadi.

## Tuzilish

```text
apps/
  api/common/                 # katalog va ochiq hamkor profillari
  api/v1/auth/                # Telegram, staff JWT, profil, xabarnomalar
  api/v1/site/                # mijoz/santexnik/do‘kon buyurtma APIlari
  api/v1/admin/               # CRM kataloglari, tayinlash, hisob-kitob, eksport
  common/                     # audit, ruxsat, pagination, routing adapter, template view
  users/                      # akkauntlar va hamkor profillari
  catalog/                    # hudud, xizmat, tarif, material, markaz va shartnoma andozasi
  orders/                     # model, selector, tranzaksion service va PDF
  tg_bot/                     # webhook, kontakt tekshiruvi va transactional outbox
project_backend/settings/     # base / development / production / test
templates/8mobile/            # Mini App bazasi va boshlang‘ich mijoz sahifasi
static/miniapp/               # sahifaning lokal CSS/JS fayllari
requirements/                # base / develop / production
docs/                        # TZ, SQL dizayn, arxitektura, API va tekshirish holati
```

SQL dizayn avval yozildi: `docs/schema.sql` va `docs/orders_schema.sql`. Amaldagi sxema uchun yagona manba Django migratsiyalaridir; SQL hujjatlarini migratsiyaga qo‘shimcha ravishda bazaga qo‘llamang. PostgreSQL asosiy baza. SQLite alohida sinov imkoniyati; ishlab chiqarishda PostgreSQL majburiy.

## Boshqa kompyuterda dastlabki sozlash

Python 3.11 yoki 3.12 va PostgreSQL talab qilinadi. Shu kompyuterda paket o‘rnatish, Django ishga tushirish, migratsiya yoki test bajarilmadi.

1. Backend papkasini boshqa kompyuterga ko‘chiring; virtual muhit yarating va faollashtiring.
2. `.env.example` dan `.env` yarating yoki mavjud `.env` dagi bo‘sh qiymatlarni to‘ldiring. `.env` gitdan chiqarilgan; uni alohida uzating.
3. `SECRET_KEY` uchun noyob tasodifiy qiymat, PostgreSQL baza/foydalanuvchi/parol, Telegram tokeni, webhook siri va HTTPS Mini App manzilini kiriting. `.env` dagi `CHANGE_ME` qiymati bilan dastur boshlanmaydi.

```bash
python -m pip install -r requirements/develop.txt && python manage.py migrate && python manage.py seed_pilot && python manage.py test --settings=project_backend.settings.test
```

Test bazasini yaratish uchun test foydalanuvchisiga `CREATEDB` ruxsati yoki DBA tayyorlagan test baza kerak. Testlar alohida bazada ishlaydi. Django testlari test sxemasini o‘zi yaratadi; haqiqiy biznes bazasini test bazasi sifatida bermang.

```bash
python manage.py createsuperuser
```

Admin orqali markaz manzili/telefon/ish vaqti, avans, komissiyalar, xizmatlar/tariflar, hamkor akkauntlari/profillari va uz/ru/en shartnoma andozalarini kiriting. `seed_pilot` faqat Marhamat hududi va TZdagi to‘rtta xizmat guruhini yaratadi; haqiqiy narx yoki yuridik matn yaratmaydi.

`ROUTING_BASE_URL` OSRM-compatible routing xizmatining asosiy manzili bo‘lishi kerak. Bu qiymat bo‘lmasa, yakuniy smeta taxminiy yo‘l vaqti bilan chiqarilmaydi: API konfiguratsiya xatosini qaytaradi. PDF uchun `CONTRACT_FONT_PATH` ga o‘zbekcha/ruscha belgilarni qo‘llaydigan TTF shriftning mutlaq yo‘lini bering, masalan Linuxdagi DejaVu Sans.

## API va operatsiya

### Telegramsiz lokal ko‘rish

`project_backend.settings.development` rejimida `DEV_LOCAL_LOGIN=true` (default) bo‘lsa, `http://127.0.0.1:8000/` yoki `http://localhost:8000/` da **Brauzerda sinov uchun kirish** tugmasi chiqadi. Alohida `__santex_local_preview__` mijoz akkaunti yaratiladi: u admin/hamkor huquqiga ega emas, Telegramga bog‘lanmagan va sinov telefoni bilan ishlaydi. Shu akkaunt orqali yuborilgan buyurtmalar bazada saqlanadi. Hudud/guruhlar uchun avval `seed_pilot` kerak; haqiqiy tarif va yuridik ma’lumotlar avtomatik kiritilmaydi.

Kirish faqat development flag + `DEBUG=True` + localhost host + loopback ulanishida, CSRF bilan himoyalangan POST orqali ishlaydi. Productionda endpoint ulanmaydi va sahifada tugma chiqmaydi. Lokal kirishni o‘chirish: `.env` da `DEV_LOCAL_LOGIN=false`. `X-Forwarded-For` ga ishonilmaydi; lokal proxy ortida development serverni ommaga ochmang.

Preview akkauntining JWT access/refresh tokenlari ham shu chegarani tekshiradi: development yopilgach yoki productionda bu tokenlar ishlamaydi, hatto bir xil baza va JWT siri ishlatilsa ham.

- `/api/v1/auth/`: Telegram kirishi, staff login, refresh/logout, profil va shaxsiy xabarlar.
- `/api/v1/common/`: katalog, hududiy tariflar, yordam ma’lumoti, hamkor profili va moderatsiyalangan izohlar.
- `/api/v1/site/orders/`: buyurtmalar va rolga bog‘langan amallar.
- `/api/v1/admin/`: CRM boshqaruvi va moliyaviy hisobotlar.
- `/api/schema/` va `/api/docs/`: staff uchun OpenAPI/Swagger. JWT yoki Django adminning staff sessiyasi bilan ochiladi; biznes APIlariga yozish uchun JWT kerak.
- `/telegram/webhook/`: `X-Telegram-Bot-Api-Secret-Token` bilan himoyalangan Bot API webhook.
- `/admin/`: Django admin; buyurtma va moliya jurnallari o‘qish uchun. Biznes amallari CRM REST API orqali bajariladi.

Webhookni Telegram Bot API `setWebhook` bilan HTTPS manzilga bog‘lang va `.env` dagi `TELEGRAM_WEBHOOK_SECRET` ni `secret_token` sifatida yuboring. Botning `/start` xabari kontakt ulashish va Mini App tugmalarini navbatga qo‘yadi. Foydalanuvchi o‘z kontaktini yuborgandagina telefon tekshiriladi; frontend telefonni tasdiqlay olmaydi.

Serverda ikki boshqaruv buyrug‘ini muntazam (masalan, har daqiqada) scheduler orqali ishga tushiring:

```bash
python manage.py scan_assignment_deadlines && python manage.py deliver_notifications --limit 100
```

Outbox biznes tranzaksiyasi bilan birga saqlanadi. Telegramga yetkazish xatosi buyurtmani yo‘qotmaydi; navbat keyin qayta urinadi. Yetkazish **at least once**: Telegram javobidan keyin worker uzilib qolsa xabar takrorlanishi mumkin. Buyurtma moliyasi idempotency kalitlari orqali takrorlanishdan himoyalangan.

Productionda `DJANGO_SETTINGS_MODULE=project_backend.settings.production`, HTTPS va aniq host/originlar ishlating. `storage/private/` ni nginx yoki boshqa ochiq media alias orqali tarqatmang. Buyurtma fayllari faqat tekshirilgan API orqali olinadi. Runtime DB akkauntiga DML ruxsatlari, migratsiya akkauntiga alohida DDL ruxsatlari bering; runtime akkauntiga `TRUNCATE`, trigger o‘chirish yoki jadval egasi huquqini bermang.

## Qamrov va tekshirish holati

To‘liq REST biznes oqimlari yozildi. Mini App template boshlang‘ich mijoz oqimi: Telegram kirish, telefon ulashish, so‘rov, buyurtma holati, smeta va qabul amallari. Barcha santexnik/do‘kon ekranlari va alohida React CRM frontend bu backend topshirig‘ida qurilmadi; ular hujjatlashtirilgan APIlardan foydalanadi.

Testlar yozilgan, **bajarilmagan**. Arxitektura va kod matni mustaqil agent ko‘rigidan o‘tkazildi; runtime natijasi tasdiqlanmagan. Hozirgi backend papkasida git repozitoriy topilmadi, shuning uchun commit/push qilinmadi.

Batafsil: [arxitektura](docs/architecture.md), [API shartnomasi](docs/API.md), [qabul mezonlari va testlar](docs/verification.md), [amalga oshirish rejasi](docs/implementation_plan.md).
