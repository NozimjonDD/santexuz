# Backend arxitekturasi

## Manbalar va qarorlar

Biznesning asosiy manbasi — `TZ_docs.md`. `ideas.md` va tarixiy `plan.md` keyingi imkoniyatlar va kelishuvlar tarixini beradi; ular TZdagi MVP chegarasini kengaytirmaydi. Amalga oshirish foydalanuvchining keyingi, bevosita topshirig‘i bilan boshlandi.

Patirchi (`D:\mark\patirchi\patirchi_mini_app`) ichidagi `project_backend/settings/base|development|production.py`, asosiy URL ulanishlari, `apps/api/v1/auth|site|admin/`, `apps/users/`, `apps/common/`, model/admin/migratsiyalar, `requirements/`, `templates/8mobile/base-common.html` va template view yondashuvi ko‘rib chiqildi. Quyidagi qatlamlar saqlandi, biznes esa Santex TZ uchun qayta yozildi:

| Qatlam | Vazifa |
|---|---|
| `apps/api/.../inputs.py` | Qabul qilinadigan maydon, tip, chegaralar; ortiqcha maydonlarni rad etish |
| `apps/api/.../views.py` | HTTP, autentifikatsiya, serializer va service chaqiruvi |
| `apps/orders/services.py` | Rollar, holatlar, narxlar, pul va buyurtma tranzaksiyalari |
| `apps/orders/selectors.py` | Foydalanuvchiga tegishli buyurtmalar va moliyaviy hisob |
| Domen modellari | Bog‘lanishlar, SQL cheklovlari, tarixiy snapshotlar |
| `apps/common/audit.py` | Yozuv qo‘shiladigan audit jurnali |
| `apps/tg_bot/` | Ishonchli Telegram kirish chegarasi, webhook va xabar navbati |

Patirchidagi `AllowAny` defaulti, CSRFdan ozod session autentifikatsiyasi, eski OTP/debug yo‘llari yoki ma’lumotlar bazasi/faylga bog‘langan loglar ko‘chirilmadi. API defaulti — JWT va `IsAuthenticated`; faqat katalog va Telegram kirishi alohida ochiq.

## SQL va tranzaksiyalar

PostgreSQL asosiy baza. SQL dizayni implementatsiyadan oldin `schema.sql` va `orders_schema.sql` fayllarida qayd etildi. `migrations/` fayllari qo‘lda yozildi; ular bu kompyuterda bajarilmadi. Django orqali haqiqiy sxema yaratiladi. SQL hujjatlari parallel o‘rnatish skripti emas.

Har bir buyurtma mutatsiyasi `transaction.atomic()` va buyurtmaning `select_for_update(of=('self',))` qulfi ostida ishlaydi. Qisman yetkazish ajratmalari, qabul, to‘lov, qaytarish, hamkor hisob-kitobi va smeta versiyasi bitta buyurtma doirasida ketma-ket yoziladi. Nullable hamkor bog‘lanishlari qulfga kiritilmaydi: PostgreSQL outer join chekloviga mos keladi.

Pul `Decimal` va UZSda, ikki kasr bilan; miqdor uch kasrgacha. Mijoz yoki santexnikdan xizmat narxi olinmaydi: hududiy tarifdan snapshot olinadi. Do‘kon material narxini beradi. SQLda musbat miqdor/to‘lov, koordinata oraliqlari va unikal versiya/idempotency cheklovlari bor. Katta hisoblar yozishdan oldin tekshiriladi.

SQLite `DB_ENGINE=sqlite` orqali boshqa kompyuterda funksional sinov uchun mavjud; row-lock va concurrency kafolati PostgreSQLdagidek emas. Production sozlamalari SQLitega ruxsat bermaydi.

## Tarix va smeta

- `ServiceItem` hududiy xizmat stavkasi, birlik, nom va kafolatni ko‘rik paytida saqlaydi. Keyingi tarif o‘zgarishi mavjud qatorni almashtirmaydi.
- `Quote` har narxlashda yangi versiya bo‘lib yaratiladi. Buyurtma bilan `version` birgalikda unikal.
- Snapshotda xizmat/material/yetkazish/shoshilinch narxlar, QQS bilan ekanligi, platforma haqi 0, avans, komissiyalar, hamkorlarning sof summasi va ETA manbasi qiymatlari saqlanadi.
- Mijozning tasdiq/rad so‘rovi `quote_version` ni majburiy yuboradi. Eski sahifa yangi smetani tasdiqlab yubora olmaydi.
- Material tayyorlash yoki ish boshlanishigacha o‘zgarish yangi smeta/tasdiq/shartnomani talab qiladi. Ortiqcha to‘lov bo‘lsa avval qaytariladi; avans yetmasa farqi olinadi.
- Smeta rad etilganda shu santexnik qayta smeta yubora olmaydi. Admin yopadi yoki boshqa mos santexnikni tayinlaydi.
- Bir chaqiruvda shoshilinch haq bir marta olinadi; bir necha xizmat bo‘lsa eng yuqori sozlangan shoshilinch stavka qo‘llanadi. Bu qoida foydalanuvchi katalogidagi bitta qat’iy chaqiruv haqini saqlash uchun tanlandi.

`Quote`, pul jurnallari va hodisalar ORM hamda PostgreSQL/SQLite triggerlari bilan o‘zgartirish/o‘chirishdan himoyalangan. Shartnoma nusxasi matn, til, andoza versiyasi, taraflar va smetaga bog‘langan snapshotdan yaratiladi. Imzolangan nusxani o‘zgartirish mumkin emas. DB egasi triggerlarni o‘chira oladi; shu sababli runtime va migratsiya akkauntlari ajratilishi kerak.

## Huquqlar va maxfiylik

Staff barcha CRM amallariga kira oladi; `is_superuser` API orqali berilmaydi. Hamkorlar faqat hozir o‘zlariga biriktirilgan buyurtmalarni ko‘radi. Begona buyurtma identifikatori `404` qaytaradi. Biriktirilishi rad etilgan yoki almashtirilgan hamkor keyingi buyurtma ma’lumotlariga kira olmaydi.

Ochiq profillarda telefon va komissiya yo‘q. Santexnik qabul qilgach uning raqami faqat biriktirilgan mijoz/staffga ko‘rinadi. Do‘kon raqami mijozga yoki boshqa hamkorga berilmaydi. Buyurtma kontrakti, fayllari, aloqa/manzil ma’lumotlari qatnashuvchilargagina ochiq. Hamkor hisobida faqat berilgan yakuniy to‘lov yig‘indisi bor; stavka va hisoblangan sof qarzdorlik staffga tegishli.

Telegram loginida `initData` serverda bot tokenidan hosil bo‘lgan HMAC bilan tekshiriladi; muddat, takroriy parametr, noto‘g‘ri user/bot va kelajak sanasi rad etiladi. Telegram id yoki telefonni frontend tasdiqlay olmaydi. Kontakt webhookda jo‘natuvchi va kontakt `user_id` bir xil bo‘lishi kerak. Staff akkauntining telefon/Telegram bog‘lanishi o‘zgarsa eski telefon tasdig‘i bekor qilinadi.

Mini App HTML Telegram web ichida ochilishi uchun faqat shu sahifa Telegram frame-ancestor siyosatiga ega. Boshqa sahifalar odatiy clickjacking himoyasini saqlaydi. APIlar cookie session orqali yozmaydi; Django admin CSRF bilan ishlaydi.

## Integratsiyalar

Telegram bildirishnomasi buyurtma bilan bitta tranzaksiyada outboxga tushadi. Worker xatoda backoff bilan qayta urinadi. Telegram sirli tokeni URLda bo‘lgani uchun provider exceptionining to‘liq matni logga yozilmaydi. Ichki xabarlar JWT bilan foydalanuvchining o‘ziga ko‘rinadi; to‘lov xabari summa, tur, sana, qabul qiluvchi va fiskal bo‘lmaganligini ko‘rsatadi. Til uz/ru/en.

Routing alohida `travel_minutes(store, order)` adapterida. OSRM-compatible provider konfiguratsiyasiz soxta yo‘l vaqti berilmaydi. Provayder tanlovi/keylari ishga tushirishda to‘ldiriladi. Qisman yetkazishning o‘z ETA/statusi bor; yetkazish haqi smetada bir marta saqlanadi.

Smetada tayyorlash+yo‘lning nisbiy davomiyligi saqlanadi. Qog‘oz imzo va avans vaqti noma’lum bo‘lgani uchun mutlaq ETA faqat tayyorlash boshlangach yoki Delivery yaratilgach hisoblanadi. Bekor qilingan buyurtmalarda yangi qoldiq undiruvi/hamkor qarzdorligi nol; tarixiy smeta va pul jurnallari saqlanadi.

PDF ReportLab yordamida faqat saqlangan snapshotdan yaratiladi. Unicode TTF shrifti serverda sozlanishi kerak. Yuridik andozalar dasturchi tomonidan to‘ldirilmaydi.

## Chegaralar

React CRM va barcha hamkor Mini App ekranlari alohida frontend ishi. Bu topshiriqda ularning REST kontraktlari tayyorlandi, Django template bazasi va mijozning boshlang‘ich interfeysi yozildi. Onlayn to‘lov, jonli kuryer xaritasi, avtomatik material kalkulyatori, bonus/reklama TZga ko‘ra yo‘q.

Haqiqiy Telegram/webhook, routing, Unicode PDF ko‘rinishi, media proxy siyosati, PostgreSQL concurrency va paketlarning birgalikda ishlashi boshqa kompyuterda tekshirilishi shart. Testlar yozilgan; bu mashinada bajarilmagan.

Texnik manbalar: [Telegram Mini App server validation](https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app), [Telegram Bot API](https://core.telegram.org/bots/api), [Django 5.2](https://docs.djangoproject.com/en/5.2/), [Simple JWT rasmiy kodi](https://github.com/jazzband/djangorestframework-simplejwt).

## Keyinchalik qilinadigan options:
https://www.servicetitan.com/market/commercial-contractor-software/service-replacement 
- Tijorat binolarda Santexnik ximat
- Qurilish binoda Santexnik ximat
- Aholi uylarida Santexnik ximat