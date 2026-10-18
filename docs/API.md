# REST API v1

Bazaviy prefiks: `/api/v1/`. JWT: `Authorization: Bearer <access>`. Login faqat Telegram server imzosi yoki staff login/paroli bilan. Katalogdan tashqari default ruxsat — autentifikatsiyalangan foydalanuvchi.

Pul JSONda ikki kasrli matn (`"125000.00"`), miqdor uch kasrgacha. Vaqt ISO 8601 va timezone bilan. Listlar `count`, `next`, `previous`, `results`; `limit` 1–100, `offset` 0 dan. Buyurtma javobidagi barcha pul UZS. Narxlar QQS bilan; fiskal chek kassa/terminaldan beriladi.

Xato shakli:

```json
{"error":true,"status_code":400,"detail":{"quote_version":["Smeta yangilangan. Yangi versiyani ko‘rib chiqing."]}}
```

`401`: JWT/signatura noto‘g‘ri; `403`: rol mos emas; `404`: mavjud emas yoki foydalanuvchiga tegishli emas; `400`: maydon/biznes holati noto‘g‘ri. Tashqi provayder sozlanmagan yoki vaqtincha ishlamasa biznesga yolg‘on ETA yozilmaydi; `400 detail.routing` qaytadi. Kutilmagan server xatolari maxfiy ichki ma’lumotni APIga chiqarish uchun ushlanmaydi; production `DEBUG=False`.

## Auth

| Metod va yo‘l | Ma’lumot / natija |
|---|---|
| `POST auth/telegram/` | `{init_data, language?: uz|ru|en}` → `{access,refresh,user}` |
| `POST auth/staff/` | `{username,password}` → tokenlar; faqat faol staff |
| `POST auth/refresh/` | `{refresh}` → yangi access va aylantirilgan refresh; eski refresh bloklanadi |
| `POST auth/logout/` | `{refresh}` → `204`; faqat token egasi |
| `GET auth/me/` | Profil, rol, telefon tasdiqlangan sana, til, staff belgisi |
| `PATCH auth/me/` | Faqat `first_name`, `last_name`, `language`; telefon/rol/huquq o‘zgarmaydi |
| `GET auth/notifications/` | Faqat o‘z xabarlari; lokalizatsiyalangan `text`, `event`, `order_id`, `read_at` |
| `POST auth/notifications/{id}/read/` | O‘z xabarini o‘qildi qilish; takrorlash xavfsiz |

Telegram `init_data` — frontenddagi o‘zgartirilmagan `Telegram.WebApp.initData`. `initDataUnsafe`, oddiy `telegram_id` yoki mijoz yuborgan telefon kirish isboti emas. Yangi akkaunt faqat `customer`; admin oldindan yaratgan hamkor roli login paytida saqlanadi. Telefon botning foydalanuvchi o‘ziga tegishli kontakt webhooki bilan tasdiqlanadi.

Bot endpointi API v1 tashqarisida: `POST /telegram/webhook/`. Telegram `update_id`, private chat/from va kontakt `user_id` tekshiriladi. `X-Telegram-Bot-Api-Secret-Token` majburiy. Takroriy update qayta bajarilmaydi. `/start` yangi mijoz va welcome outbox yaratadi.

## Ochiq katalog — `common/`

Quyidagilarda `GET /` va `GET /{id}/` mavjud: `regions`, `service-groups`, `services`, `service-rates`, `materials`, `plumbers`, `stores`.

| Yo‘l | Filter / maxfiylik |
|---|---|
| `common/regions/` | Faqat faol hudud |
| `common/service-groups/` | Faol guruhlar va uz/ru/en nomlar |
| `common/services/?group={id}` | Faol xizmat, faol guruh, birlik va kafolat |
| `common/service-rates/?region={id}&group={id}` | `region` majburiy; hududiy birlik narxi va shoshilinch stavka |
| `common/materials/?search=quvur` | Faol mahsulot; nom/marka qidiruvi |
| `common/plumbers/?region={id}&group={id}` | Faol profil, ism, tajriba, yo‘nalish, tasdiqlangan reyting; telefon/komissiyasiz |
| `common/plumbers/{id}/photo/` | Faol profilning xavfsiz image streami; media storage yo‘li ochilmaydi |
| `common/plumbers/{id}/reviews/` | Faqat moderatsiyadan o‘tgan baho/izoh, muallif telefoni/manzilisiz |
| `common/stores/` | Barcha faol do‘konlar, hudud bo‘yicha cheklanmaydi; telefon/komissiyasiz |
| `common/stores/{id}/reviews/` | Faqat moderatsiyadan o‘tgan baho va izohlar |
| `common/service-center/` | Markaz nomi, manzil, telefon, ish kun/soatlari; sozlanmagan bo‘lsa `null` |

## Buyurtmalar — `site/orders/`

`GET site/orders/` — o‘z mijoz buyurtmalari yoki hozir tayinlangan hamkor buyurtmalari. `?region=`, `?group=`, `?status=` filterlari bor. `GET site/orders/{id}/` — shu buyurtma tafsiloti.

`POST site/orders/` faqat tasdiqlangan telefonli mijoz uchun (`201`):

```json
{
  "region_id": 1,
  "service_group_id": 1,
  "address": "Marhamat tumani, ko‘cha va uy",
  "latitude": "40.500000",
  "longitude": "72.300000",
  "description": "Krandan suv sizmoqda",
  "is_urgent": false,
  "consent": true
}
```

Quyidagi barcha amallar `POST site/orders/{id}/{amal}/` ko‘rinishida. Ko‘rsatilmagan maydon yuborilmaydi. Odatda yangilangan `Order` javobi qaytadi. Hamkor rad qilib buyurtmadan chiqarilganda `200 {detail:"Action recorded."}` qaytadi; u bundan keyin shaxsiy buyurtma ma’lumotini olmaydi.

| Amal | Rol | Body va qoida |
|---|---|---|
| `plumber-response` | Tayinlangan santexnik | `{accept,reason?}`; radga sabab majburiy |
| `inspection` | Qabul qilgan santexnik | `{inspection_at}`; kelajakdagi bepul ko‘rik |
| `estimate` | Qabul qilgan santexnik | `{services:[{service_id,quantity}],materials:[{material_id?,name?,unit?,brand?,note?,quantity}]}` |
| `store-response` | Tayinlangan do‘kon | `{accept,reason?}`; radga sabab majburiy |
| `material-prices` | Qabul qilgan do‘kon | `{items:[{id,unit_price,available,replacement_name?,supply_minutes?}],delivery_fee,preparation_minutes}` |
| `work-schedule` | Santexnik | `{starts_at,ends_at,reason?}`; jadval o‘zgarsa sabab majburiy |
| `approve-quote` | Mijoz | `{quote_version}`; aynan ko‘rilgan joriy versiya; ish jadvali/andoza mavjud bo‘lishi kerak |
| `reject-quote` | Mijoz | `{quote_version,reason?}`; shu santexnik qayta smeta yubormaydi |
| `payments` | Staff yoki qabul qilgan santexnik | `{amount,method:cash|terminal,kind:advance|balance,idempotency_key}` |
| `begin-preparation` | Do‘kon | `{}`; tasdiqlangan smeta, imzolangan joriy shartnoma va yetarli avans |
| `deliveries` | Do‘kon | `{items:[{item_id,quantity}],eta?}`; har yetkazish alohida, umumiy miqdordan oshmaydi |
| `deliveries/{delivery_id}/status` | Do‘kon | `{status:preparing|dispatched|delivered,eta?}`; ketma-ket holatlar |
| `deliveries/{delivery_id}/confirm` | Mijoz | `{}`; do‘kon yetkazildi degach mijoz qabuli |
| `issues` | Mijoz | `{description}`; ochiq nizo to‘lov/settlementni bloklaydi |
| `start-work` | Santexnik | `{}`; imzo/avans va barcha material qabul qilingan bo‘lishi kerak |
| `complete-work` | Santexnik | `{}`; ish tugadi, mijoz tasdig‘i hali alohida |
| `accept-work` | Mijoz | `{}`; qoldiq to‘lovga ruxsat; to‘liq to‘langan bo‘lsa yopiladi |
| `cancel` | Mijoz yoki staff | `{reason?,company_failure?:false}`; kompaniya sababini faqat staff belgilaydi |
| `rating` | Mijoz | `{plumber_score:1..5,store_score:1..5,comment?}`; yopilgan buyurtma, bir marta |
| `attachments` | Maqsadga bog‘liq | `multipart/form-data`: `file`, `purpose:request|issue|completion`; `201` |

Erkin materialda `name`, `unit`, `quantity` majburiy. Katalog materialida nom/birlik katalogdan olinadi. `services` kamida bitta qator; xizmat takrorlanmaydi. `material-prices.items` buyurtmadagi har bir materialni aynan bir marta qamraydi. Yo‘q mahsulot uchun muqobil yoki olib kelish vaqti kerak.

`GET site/orders/{id}/attachments/{attachment_id}/download/` va `GET site/orders/{id}/contracts/{contract_id}/pdf/` faqat ishtirokchilar uchun. Fayl byte stream, `Cache-Control: private, no-store`. `storage/private/` uchun to‘g‘ridan-to‘g‘ri URL yo‘q. JPEG, PNG, WebP, MP4 va MOV ruxsat etiladi; MIME/header va hajm tekshiriladi.

`Order` tafsilotida: statuslar, ko‘rik/ish jadvali, o‘zgarish vaqtlari, customer, qabuldan so‘ng plumber, store, xizmat/material qatorlari, barcha smeta versiyalari, shartnomalar, to‘lov/qaytarish tasdiqlari, qisman yetkazishlar, nizolar, baho, attachment download yo‘llari va hodisalar. Komissiyalar oddiy snapshot proyeksiyasidan chiqariladi. Accounting mijozga jami/to‘langan/avans/qoldiqni, hamkorga faqat to‘langan settlement yig‘indisini beradi.

Smetadagi `estimated_delivery_minutes` — tayyorlash va integratsiyadan olingan yo‘l vaqti yig‘indisi. Qog‘oz imzo/avans qachon tugashi noma’lum bo‘lgani uchun smeta paytida yolg‘on mutlaq kelish sanasi berilmaydi. Tayyorlash boshlangach xabarda mutlaq ETA paydo bo‘ladi; har Delivery o‘z ETA qiymatiga ega. Bekor qilingan buyurtmaning qoldiq undiruvi va yangi hamkor qarzdorligi nol: undagi `total` va snapshot komissiyalari tarixiy smeta ma’lumotidir.

## CRM — `admin/`

Faqat faol staff. Quyidagi kolleksiyalar uchun `GET/POST`, element uchun `GET/PUT/PATCH/DELETE` mavjud. `is_active` li obyektlar o‘chirilganda deaktivatsiya qilinadi; bog‘langan tarixga zarar yetkazuvchi o‘chirish rad etiladi.

| Resurs | Asosiy yoziladigan maydonlar |
|---|---|
| `regions` | name, code, is_active |
| `service-groups` | name, name_ru, name_en, code, is_active |
| `services` | group, name, name_ru, name_en, unit, warranty_days, is_active |
| `service-rates` | region, service, unit_price, urgent_fee; region+service unikal |
| `materials` | name, unit, brand, is_active |
| `contract-templates` | language, version, text, is_active; matn/til/versiya keyin o‘zgarmaydi, yangi versiya yaratiladi |
| `users` | username, password?, telegram_id?, first_name, last_name, phone_number?, language, role, is_active, is_staff |
| `plumbers` | user, regions[], services[] (guruh idlari), commission_rate?, experience_years, photo?, is_active |
| `stores` | user, name, address, latitude?, longitude?, commission_rate?, is_active |

`password` javobda yo‘q; yangi parol Django validatoridan o‘tadi. Password berilmagan Telegram akkauntida password login yo‘q. `is_superuser`, `groups`, `user_permissions`, `phone_verified_at` CRMdan yozilmaydi. Superuser CRM ro‘yxatidan chiqarilgan. Staff o‘zini deaktivatsiya yoki staffdan chiqarolmaydi. Mavjud akkaunt roli qayta tasniflanmaydi; hamkorni Telegramga kirishidan avval tegishli rol bilan provision qiling.

`GET/PUT/PATCH admin/service-center/`: bitta markaz. `name,address,phone,opening_time,closing_time,working_days[]` (0=dushanba..6=yakshanba), `default_plumber_commission`, `default_store_commission`, `advance_kind:percent|fixed`, `advance_value`, `plumber_response_minutes`. Haqiqiy operatsion qiymatlar majburiy; avtomatik taxminlar yo‘q.

`GET admin/orders/`, `GET admin/orders/{id}/`: barcha buyurtmalar, qo‘shimcha staff moliyasi, komissiyalar, to‘langan settlementlar va refund limiti. `POST admin/orders/` bilan so‘rov yaratilmaydi; mijoz roziligini chetlab o‘tmaslik uchun `405`.

Quyidagilar `admin/orders/{id}/` ostida:

| Metod / amal | Body / natija |
|---|---|
| `GET eligible-plumbers/` | Hudud, guruh, faol akkaunt va rad etilgan smeta tarixiga mos ustalar |
| `GET available-stores/` | Hududdan qat’i nazar faol do‘konlar |
| `POST confirm-urgent/` | `{confirmed}`; markaz ish vaqti va mijoz so‘rovi bilan |
| `POST assign-plumber/` | `{plumber_id}`; bu User id, PlumberProfile id emas |
| `POST assign-store/` | `{store_id}`; bu do‘konning User idsi |
| `POST sign-contract/` | `{}`; staff to‘rt taraf qog‘oz imzosi yig‘ilganini qayd etadi |
| `POST resolve-dispute/` | `{note,accept_work:true|false}`; majburiy qaror izohi |
| `POST refunds/` | `{amount,reason,idempotency_key}`; qaytarish limiti va summa tekshiriladi |
| `POST settlements/` | `{partner:plumber|store,amount,idempotency_key}`; yopilgan, to‘liq to‘langan, nizosiz buyurtma |
| `POST payments/{payment_id}/cash-handover/` | `{}`; santexnik qabul qilgan naqd pul markazga berilganini tasdiqlaydi |
| `POST ratings/{rating_id}/moderate/` | `{approved}`; umumiy profilga chiqishini boshqaradi |

CRM order view site action yo‘llarini ham meros oladi, ammo service ichidagi rol talablari saqlanadi: staff mijozning o‘rniga smeta yoki material qabulini tasdiqlay olmaydi. Staff uchun `payments`, `cancel`, attachment/contract o‘qish kabi ruxsat etilgan amallar ishlaydi.

`GET admin/audit-events/`, `GET admin/audit-events/{id}/`: faqat o‘qish. Filterlar `actor`, `object_type`, `object_id`, `action`. API, ORM va DB triggerlari audit o‘zgartirish/o‘chirishiga ruxsat bermaydi.

Mijoz bekor qilgandan keyin kompaniya aybi aniqlansa, staff `cancel` amalini `company_failure:true` va majburiy `reason` bilan qayta yuborishi mumkin: bu yangi bekor qilish emas, auditlangan refund ruxsatidir. Shundan keyin haqiqiy qaytarish `refunds` orqali qayd etiladi. Qaytarish jami qabul qilingan puldan oshmaydi.

To‘langan buyurtmaning qayta smetasi rad etilsa, tayyorlash/ish boshlanmagan holatda staff olingan pulni `refunds` bilan qaytarib, keyin boshqa santexnikni tayinlay oladi. Sof olingan pul nol bo‘lmaguncha qayta tayinlash bloklanadi. Oldingi santexnikning naqd pul topshirish tarixi yo‘qolmaydi.

`GET admin/reports/?export=json|csv|xlsx&region={id}&status={status}&date_from=YYYY-MM-DD&date_to=YYYY-MM-DD`: buyurtma kesimida jami, avans, mijoz to‘lovi, refund, qoldiq, ikkala komissiya va sof to‘lov/qarzdorlik. `export` ishlatiladi, DRF renderer uchun ajratilgan `format` parametri emas. CSV UTF-8 BOM bilan, XLSX `UZS` varag‘i bilan. Excel formula injection himoyasi bor. Moliyaviy qiymatlar aniqlik uchun matn sifatida eksport qilinadi.

## Idempotency va tartib

Payment, refund va settlement uchun `idempotency_key` har bir jurnal ichida unikal va 1–128 belgi. Bir xil buyurtma, summa, tur va qabul qiluvchi bilan takror yuborilsa oldingi amal qaytariladi, ikkinchi pul yozuvi yaratilmaydi. Shu kalit boshqa buyurtma yoki boshqa summa uchun ishlatilsa `400`.

Asosiy ketma-ketlik: mijoz so‘rovi → staff tayinlash → santexnik qabul/ko‘rik/smeta/jadval → staff do‘kon → do‘kon qabul/narx → mijoz aniq smeta versiyasini tasdiqlaydi → staff qog‘oz imzoni qayd etadi → avans → tayyorlash/yetkazish/qabul → ish → mijoz yakuniy qabul → qoldiq → yopilish → hamkor hisob-kitobi va moderatsiyalangan baho.

## OpenAPI

`GET /api/schema/` va `/api/docs/` staff ruxsatini talab qiladi. Faqat shu o‘qish endpointlarida JWT bilan birga Django admin staff sessiyasi ham qabul qilinadi: `/admin/` ga kirib, keyin `/api/docs/` ni ochish mumkin. Biznes APIlari yozish uchun JWT talab qiladi. Boshqa kompyuterda `python manage.py spectacular --file openapi.yaml` bilan schema eksporti mavjud.
