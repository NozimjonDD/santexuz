# Barcha loyiha modellari uchun mock seed

Development/test uchun `seed_mock` buyrug‘i mavjud. Default `--count 20`: loyiha applaridagi har bir konkret model uchun kamida 20 ta bog‘langan namuna yaratadi. Django tizim jadvallari (`Permission`, `ContentType`, session, JWT blacklist) va abstrakt modellar sun’iy ma’lumot bilan to‘ldirilmaydi. Profilning hudud/xizmat M2M bog‘lanishlari ham yaratiladi. Yangi migratsiya yoki Faker paketi kerak emas.

Faqat boshqa kompyuterdagi **alohida development/test bazasi** va tayyor virtual muhitda:

```bash
python manage.py migrate && python manage.py seed_mock
```

Settings development bo‘lishi kerak. Production sozlamalarida buyruq rad etiladi; majburlab productionga o‘tkazadigan flag yo‘q. `--settings` ni almashtirish bazaning manzilini almashtirmaydi: `.env` ham development/test bazasiga qarasin. Production deploy avtomatik ravishda bu buyruqni ishlatmaydi.

## Default natija

| Modellar | Batchdagi son |
| --- | ---: |
| Region, ServiceGroup, Service, ServiceRate, Material, ContractTemplate | har biri 20 |
| PlumberProfile, Store | har biri 20 |
| User | 61: 20 mijoz, 20 santexnik, 20 do‘kon, 1 staff |
| Consumer | 21: mijozlar va customer rolidagi synthetic staff profili |
| ServiceCenter | **1**, bazadagi singleton cheklovi saqlanadi |
| Order, ServiceItem, MaterialItem | har biri 20 |
| Quote, Contract | har biri 40: buyurtma uchun 2 versiya |
| Payment | 40: buyurtmaga avans va qoldiq |
| Refund, CashHandover | har biri 20 |
| Settlement | 40: santexnik va do‘kon hisob-kitobi |
| Delivery, DeliveryItem, Issue, Rating, Attachment | har biri 20 |
| Notification, BotUpdate | har biri 20 |
| OrderEvent, AuditEvent | holatlar tarixi sabab 20 dan ko‘p |

Batch hisoboti tegishli yozuvlar sonini chiqaradi; `AuditEvent` da qo‘shimcha bitta yakunlangan-batch markeri bor. Avvalgi ma’lumotlar o‘chirilmaydi. Mavjud xizmat markazi va haqiqiy preview akkaunti qayta ishlatilishi mumkin, shuning uchun yuqoridagi sonlar bazaning umumiy jami emas. `--count 1/2` da ham uch til uchun kamida 3 ta shartnoma andozasi yaratiladi.

Har bir buyurtma yakunlangan `closed` holatida: birinchi smeta tasdiqlanadi, avans yoziladi, naqd pul topshiriladi; ikkinchi smetada material narxi pasayadi, ortiqcha avans qaytariladi, yangi shartnoma saqlanadi. Yetkazish tasdiqlangan, namuna nizo hal qilingan, qoldiq to‘langan va ikki hamkor bilan hisob-kitob qilingan. `paid - refunded = final quote total`; qoldiq va hamkor qarzdorliklari nol. Bu fixture ma’lumotlari: real ish jarayoni shu vaqt ichida bajarilganini anglatmaydi.

Imzolangan shartnomalar, smetalar va audit/moliya jurnallari yaratilgach o‘zgartirilmaydi. DB triggerlari o‘chirilmaydi. Model validatsiyasi hamda mavjud unique/check cheklovlari bajariladi. Normal biznes servislarining bildirishnoma fan-out jarayoni chaqirilmaydi, shuning uchun oldindan mavjud staff akkauntlariga seed xabarlari tushmaydi.

## Lokal Mini Appda ko‘rish

Defaultda birinchi mijoz `__santex_local_preview__`: localhostdagi **Sinov akkaunti** shu akkauntga kiradi va 20 ta mock buyurtmani ko‘radi. Akkaunt yangi bo‘lsa, mavjud development login bilan bir xil email/telefon/parol cheklovlari bilan yaratiladi. Shu nomdagi begona yoki yuqori huquqli akkaunt bo‘lsa, seed uni o‘zgartirmay to‘xtaydi.

Preview akkauntini umuman ishlatmay, alohida mijozlarga buyurtma taqsimlash:

```bash
python manage.py seed_mock --count 20 --prefix isolated --no-local-preview
```

Haqiqiy Telegram ID yaratilmaydi (`telegram_id=NULL`), barcha yangi akkauntlarning paroli ishlatib bo‘lmaydigan holatda. Mock staff superuser emas. Notification yozuvlari `mock_seed` belgisi va to‘ldirilgan `sent_at` bilan yaratiladi, shuning uchun outbox worker ularni yubormaydi; bu Telegramga haqiqatan yetkazilgan degani emas. BotUpdate IDlari real webhook qabul qilmaydigan manfiy oraliqda.

Santexnik suratlari va buyurtma biriktirmalari kichik, haqiqiy PNG fayllardir; `MEDIA_ROOT/mock/<prefix>/` ichida saqlanadi. Ularda `MOCK` yozuvi bor. Shartnoma matnlari uch tilda **faqat sinov uchun, yuridik hujjat emas** deb belgilangan. PDF fayli oldindan yaratilmaydi; mavjud endpoint snapshotdan generatsiya qiladi va odatdagidek `CONTRACT_FONT_PATH` talab etadi.

## Takrorlash va xato holatlari

Bir xil `prefix`, `count` va preview rejimida qayta bajarish yangi nusxa qo‘shmaydi. Yakun belgisi, yozuvlar va fayllar tekshiriladi. Shu batch yozuvlari arxivlangan/o‘chirilgan, fayli yo‘qolgan yoki modellar ro‘yxati o‘zgargan bo‘lsa xato qaytadi; mavjud immutable tarix tuzatilmaydi.

Yangi alohida to‘plam uchun:

```bash
python manage.py seed_mock --count 20 --prefix demo2
```

`count` 1–200, `prefix` 1–24 ta kichik lotin harfi/raqam/defis bo‘lishi kerak. Bir prefix uchun `count` yoki preview flagini keyin o‘zgartirish rad etiladi. Reset/o‘chirish flagi yo‘q. PostgreSQLda parallel seedlar bitta transaction advisory lock bilan navbatlanadi. SQLite’da parallel yozish ziddiyati yuz bersa muvaffaqiyatsiz batch bekor qilinadi va qayta bajarish mumkin.

Xato bo‘lsa barcha batch DB yozuvlari bitta tranzaksiya bilan rollback qilinadi. File storage tranzaksiyaga kirmagani uchun aynan shu urinish yaratgan fayllar alohida tozalanadi; eski fayllar va boshqa batchlar o‘chirilmaydi. To‘satdan process/server uzilishi yoki storage delete xatosida qolgan `mock/<prefix>/` fayllarini operator ko‘rib chiqishi mumkin; DB yakun markeri yo‘q bo‘lsa batch tugamagan.

## Tekshirish

`apps/common/test_mock_seed.py`: barcha modellar qamrovi/validatsiyasi, moliyaviy balans, takroriy chaqiruv, production cheklovi, reserved akkaunt to‘qnashuvi, mavjud markazni saqlash, fayl yo‘qolishi va xatoda DB/fayl rollback testlari. Tashqi HTTP so‘rovlar taqiqlanadi, fayllar testda InMemoryStorage ichida saqlanadi.

Bu yangi buyruq va testlar yozish kompyuterida **bajarilmagan**. Boshqa kompyuterda, alohida test bazasi uchun:

```bash
python manage.py test apps.common.test_mock_seed --settings=project_backend.settings.test
```
