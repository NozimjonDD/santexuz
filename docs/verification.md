# Qabul mezonlari va tekshirish holati

**Holat: kod va testlar yozilgan; test/migratsiya/build bajarilmagan.** Bu kompyuter foydalanuvchi qoidasiga ko‘ra faqat kod yozish uchun. Python, Django, paket installer, test, linter, formatter yoki server ishlatilmadi. Fayllar va bog‘lanishlar faqat matndan ko‘rib chiqildi.

Manba fayllarida 56 ta `test_*` metod yozilgan; bu bajarilgan testlar soni yoki coverage o‘lchovi emas.

Keyingi lokal preview o‘zgarishi uchun `apps/api/v1/auth/test_development.py` da yana 7 ta test yozildi: localhost/DEBUG/flag chegaralari, CSRF, IPv6, haqiqiy akkaunt bilan to‘qnashuv va preview tokenlarini productionda rad etish. Ular ham bajarilmadi.

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

Test natijasi, coverage foizi, production ishlashi yoki PDFning vizual sifati bu topshiriqda **tasdiqlanmagan**. Real tarif/hamkor/markaz/yuridik matnlar kiritilmaguncha pilotni ishga tushirish yakunlanmaydi.

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

`Code Review` connectorida faqat PR/CI diagnostika vositasi mavjud. Git repozitoriy/PR berilmagani sabab undan review yoki CI xulosasi olinmadi. Matn ko‘rigi test natijasi sifatida ko‘rsatilmaydi.
