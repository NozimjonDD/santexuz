# Qabul mezonlari va tekshirish holati

**Joriy holat — 2026-10-18:** foydalanuvchining `verify.sh` xatosini shu kompyuterda qayta chiqarish haqidagi aniq ko‘rsatmasi bilan tekshiruv bajarildi. Git Bash orqali `scripts/verify.sh` exit 0 bilan tugadi: konfiguratsiya, model/migratsiya mosligi, qat’iy OpenAPI validatsiyasi, migratsiyalar, seed va backend testlari o‘tdi.

**Natija:** 70 testdan 68 tasi muvaffaqiyatli, 2 ta PostgreSQL row-lock testi SQLite sabab o‘tkazib yuborildi. Oxirgi to‘liq test bajarilishi 16.465 soniya. Python 3.14 va loyihaning mavjud `venv` muhiti ishlatildi. Paket o‘rnatilmadi, dev server yoki build ishga tushirilmadi. Frontend Node testlari, real Telegram, PostgreSQL concurrency va vizual sifat hali tasdiqlanmagan.

Lokal preview testlari ham bajarildi: localhost/DEBUG/flag chegaralari, CSRF, IPv6, haqiqiy akkaunt bilan to‘qnashuv va preview tokenlarini productionda rad etish.

## TZ bilan bog‘lanish

| TZ 13-bo‘lim mezoni | Implementatsiya | Yozilgan testlar |
|---|---|---|
| 1. Telegram/til/telefon/manzil/rozilik | `auth/services.py`, `tg_bot/views.py`, `orders.create_order` | Auth HMAC/contact testlari, so‘rov validation testi |
| 2. Tayinlash, qabul/rad, deadline | `assign_plumber`, `respond_plumber`, `scan_assignment_deadlines` | Hamkor rad javobi, huquq, bir martalik deadline xabari |
| 3. Telefon maxfiyligi | Participant selector, public/order serializer proyeksiyalari | Begona buyurtma `404`, ochiq profilda telefon/komissiya yo‘qligi |
| 4. Ko‘rik va hududiy hisob | `schedule_inspection`, `submit_estimate`, ServiceRate snapshot | To‘liq HTTP oqimi, tarif o‘zgargach snapshot saqlanishi |
| 5. Do‘kon va boshlash to‘siqlari | `assign_store`, `respond_store`, `price_materials`, `_ready_to_start` | Imzo/avanssiz boshlash, qayta narxlash va versiya |
| 6. Narxlar ajratilishi | Immutable Quote, `Decimal`, bitta delivery fee | Qisman yetkazishda jami saqlanishi, bitta shoshilinch ustama |
| 7. Shartnoma | Til/versiya/taraf/smeta snapshot, sign service, private PDF | Eski imzolangan nusxa saqlanishi, PDF endpointning participant scope testi |
| 8. To‘lov/kvitansiya/handover/settlement | Pul jurnallari, idempotency, outbox receipt | To‘liq oqim, overpayment/early balance, parallel to‘lovlar |
| 9. Routing/ETA/qisman yetkazish | OSRM adapter, alohida Delivery/DeliveryItem | Adapter valid/error testlari, qisman qabul, ortiqcha ajratishni rad etish |
| 10. Qabul va nizo | `report_issue`, `resolve_dispute`, payment/settlement guards | Nizoda bloklash, resolution, bekor qilish/refund istisnolari |
| 11. Moderatsiyalangan baho | Rating moderation, public partner reviews | Moderatsiyadan oldin/yakunida umumiy reyting va izoh |
| 12. Hisobot va audit | Staff JSON/CSV/XLSX, append-only audit/DB triggers | Eksport formatlari, staff huquqi, raw SQL mutatsiyasini rad etish |

Asosiy test fayllari:

- `apps/api/v1/auth/tests.py`: Telegram signatura, muddat, duplicate parametr, inactive user, rol xavfsizligi, kontakt/webhook, JWT refresh/logout.
- `apps/api/v1/tests/test_workflow.py`: API orqali buyurtma hayot sikli, rol/mulkchilik, smeta, avans, qisman yetkazish, nizo, refund, settlement, rating, private media va eksport.
- `apps/api/v1/tests/test_management.py`: katalog CRUD, hamkor provision, markaz, andoza, audit, seed va schema/docs ruxsatlari.
- `apps/orders/tests.py`: PostgreSQL row lock ostida bir xil va turli idempotency kalitlari bilan parallel to‘lov. SQLite bu testlarni o‘tkazib yuboradi.
- `apps/tg_bot/tests.py`: outbox rollback, qayta urinish, kontakt/Mini App tugmalari, lokalizatsiya va shaxsiy inbox.
- `apps/common/tests.py`: routing javobini aylantirish, sozlanmagan yoki noto‘g‘ri provider javobi.

Har bir order action uchun anonymous va begona foydalanuvchi holatlari alohida matrix bilan yozilgan. Testlar haqiqiy Telegram yoki routing tarmog‘iga so‘rov yubormaydi; tashqi chegaralar mock qilinadi. Bu real provider mosligi tekshirildi degani emas.

## Boshqa kompyuterda

Backend papkasida faollashtirilgan virtual muhit, haqiqiy `.env` va PostgreSQL mavjud bo‘lgach:

```bash
python -m pip install -r requirements/develop.txt && bash scripts/verify.sh
```

Skript Django konfiguratsiyasi, migratsiya/model mosligi, migratsiyalar va barcha testlarni tekshiradi. PostgreSQL test bazasini yaratishga ruxsat kerak. Haqiqiy runtime sozlamalari uchun `README.md` ga qarang.

Qo‘lda: Telegram botda `/start` → o‘z kontaktini ulashish → Mini App; haqiqiy routing bilan ETA; uch tildagi PDFni ochib/chop etib ko‘rish; qog‘ozdagi to‘rt imzo jarayoni; reverse proxy orqali begona foydalanuvchi private media ololmasligini tekshirish.

Coverage foizi, production ishlashi va PDFning vizual sifati **tasdiqlanmagan**. Yuqoridagi SQLite backend test natijasi tasdiqlangan. Real tarif/hamkor/markaz/yuridik matnlar kiritilmaguncha pilotni ishga tushirish yakunlanmaydi.

## Matn asosidagi review

Mustaqil agent reviewi orqali topilgan va tuzatilgan holatlar:

- Telegram web frame ochilishi va yangi foydalanuvchining `/start` onboarding oqimi.
- Webhookda input tiplari, kontakt egasi va idempotency.
- Mijoz ko‘rmagan yangi smetani tasdiqlab yubormaslik uchun aniq versiya.
- PostgreSQL nullable joinlarga `FOR UPDATE` qo‘llashdan saqlanish.
- Hamkor radidan keyin muvaffaqiyatli amalni `404` qilib yubormaslik.
- Staff/hamkor proyeksiyalarida komissiya va telefon maxfiyligi.
- Naqd pul topshirilmaguncha yakuniy settlementni bloklash.
- Global idempotency kalitida turli buyurtmalar o‘rtasidagi unique conflictni `400`ga aylantirish.
- Moliyaviy Decimal qiymatlarini JSON/XLSXda aniq matn shaklida chiqarish.
- Qayta smeta refundidan keyin qolgan pulni to‘liq qaytarish; bekor qilingandan keyingi admin ruxsati va boshqa santexnikka xavfsiz qayta tayinlash.
- Shartnoma/avansdan oldin yolg‘on kelish sanasi bermaslik va bekor qilingan buyurtmada qoldiq qarzdorlikni ko‘rsatmaslik.

`Code Review` connectorida faqat PR/CI diagnostika vositasi mavjud. PR ko‘rsatilmagani sabab undan review yoki CI xulosasi olinmadi. Matn ko‘rigi test natijasi sifatida ko‘rsatilmaydi.

## 2026-10-18 UI va optimizatsiya qo‘shimchasi

Rolga mos Mini App ekranlari, uch til, adaptiv kartalar/formalar, lokal read-only dizayn namoyishi va API ulanishi yozildi. Tafsilot: `docs/miniapp_ui.md`. Oldingi “faqat boshlang‘ich mijoz UI” qamrovi shu o‘zgarishda kengaytirildi.

`scripts/miniapp_api.test.mjs`: frontend modul sintaksisi, parallel refresh, kechikkan 401, bo‘sh/204 javoblar, refresh rad etilishi, multipart/CSRF, pagination va abort holatlari uchun testlar yozildi; Node testlari hali bajarilmagan. `apps/api/v1/tests/test_review.py`: deleted account/catalog, production preview chegarasi, order bucket, moliyaviy jami, doimiy query soni va barcha immutable jurnallar uchun raw SQL himoyasi testlari muvaffaqiyatli bajarildi. Eksport testi streaming javoblarni o‘qishga moslandi va o‘tdi.

```bash
bash scripts/verify.sh && node --test scripts/miniapp_api.test.mjs
```

Node 22+ va oldindan tayyorlangan Python/PostgreSQL muhiti kerak. Runtime va vizual tekshiruv boshqa kompyuter vazifasi. Yangi UI uchun 320/390/768/1280px, UZ/RU/EN, uch rol, katta shrift, Telegram klaviaturasi va safe area ko‘rilishi kerak.

## `verify.sh` xatolari va tuzatishlar

- SQLite BaseModel migratsiyalarida jadvallar qayta yaratilganda custom triggerlar yo‘qolgan. Yangi `common.0005`, `catalog.0005`, `orders.0006` migratsiyalari audit, andoza, shartnoma va pul jurnallari himoyasini tiklaydi. PostgreSQL triggerlariga tegmaydi. Oldingi qo‘llangan migratsiyalar tahrirlanmadi.
- Attachment testi OS vaqtinchalik katalogining Windows sandbox ruxsatiga bog‘liq edi. Fixture saqlash uchun Django InMemoryStorage ishlatildi; huquq va fayl oqimi testi saqlandi.
- Custom JWT va refresh uchun OpenAPI adapterlari, public/staff serializerlarining alohida component nomlari, aniq enum nomlari va Telegram webhook request/response sxemasi qo‘shildi. `spectacular --validate --fail-on-warn` exit 0 bilan o‘tdi.
- Faqat test sozlamalarida kutilgan 4xx loglar kamaytirildi; 500 xatolar va test assertionlari ko‘rinib qoladi. Production loglari o‘zgarmadi.
- `scripts/verify.py` barcha olti bosqich uchun yagona cross-platform runner. `verify.sh` loyihaning virtual muhitini aniqlab shu runnerni bajaradi. PowerShellda Bashsiz `python scripts/verify.py` ishlatiladi. Shell fayllariga Git LF satr yakuni belgilandi.

SQLite’da keyingi jadvalni qayta yaratuvchi schema migratsiyalarida custom triggerlar yana tekshirilishi va zarur bo‘lsa shu migratsiya zanjirida tiklanishi kerak.

Backend tekshirish buyrug‘i (virtual muhit faollashtirilgan):

```bash
python scripts/verify.py
```
