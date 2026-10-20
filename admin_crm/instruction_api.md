# Santex — Backend va API ishlab chiqish yo‘riqnomasi

**Sana:** 20.10.2026  
**Holat:** mavjud React CRM va TZ asosidagi backend handoff; API hali amalga oshirilmagan.  
**Asosiy manbalar:** [TZ](docs/TZ_docs.md), [React UI spetsifikatsiyasi](docs/reactjs.md).  
**Auditoriya:** Django/DRF backend dasturchisi va React integratsiyasini bajaruvchi dasturchi.

## 1. UI hujjatga mosmi?

**Admin CRM doirasidagi asosiy ekranlar va oqimlar TZga mos tuzilgan. To‘liq mahsulot va serverdagi biznes jarayonlari hali tayyor emas.** Standart `PUBLIC_API_MOCK=True` rejimida ma’lumot statik JSONdan olinib React xotirasida tahrirlanadi; refresh JSONni qayta yuklaydi. `False` rejimida `PUBLIC_API_BASE_URL` orqali GET ma’lumotlari olinadi, yozish bloklanadi. Joriy connector va DTO talabi §17da; bu qolgan backend commandlari bajarilganini anglatmaydi.

Quyidagi baho manba kodini o‘qish orqali berildi. Ushbu kompyuterda ilova, test, typecheck, build yoki brauzer QA ishga tushirilmadi; vizual moslik va ishlash natijasi tasdiqlanmagan.

| TZ / UI talabi | Hozirgi CRMdagi joy | Backend uchun qolgan ish |
| --- | --- | --- |
| TZ §9, React §6: admin boshqaruvi | Dashboard, buyurtmalar, beshta katalog/profil, moliya, hisobot, andozalar, reyting, audit, sozlamalar | Doimiy saqlash, API va haqiqiy akkauntlar |
| TZ §6.5–10: qo‘lda tayinlash | Buyurtma tafsiloti; mos faol Marhamat ustalari, barcha hududdagi faol do‘konlar | Tayinlash tarixi, hamkor qabul/rad javobi, usta javob muddati |
| TZ §4–6: smeta va narxlar | Xizmat/material qatorlari, yetkazish, shoshilinch haq, platforma haqi 0, QQS ichida | Server hisoblari, narx manbasi, haqiqiy mijoz tasdig‘i |
| TZ §4, §9: versiyalar | Tasdiqlangan smeta nusxasi, eski smeta va imzolangan shartnoma tarixi | Tranzaksion, o‘zgarmas snapshotlar; rad qilingan smeta bo‘yicha alohida qoida |
| TZ §6.12,16: tayyorlash va qisman yetkazish | Jarayon tabida muddat, qismlar, status va ETA | Do‘kon amallari, haqiqiy ETA integratsiyasi va xabarnoma |
| TZ §6.14, §9: to‘rt tomon shartnomasi | Andoza/tillar/versiyalar, to‘rt imzo belgisi, matn preview | Haqiqiy PDF, hujjat nusxasi, xodim identifikatori va vaqt |
| TZ §8: moliya | Avans/qoldiq, naqd topshirish, hamkor hisob-kitobi, qaytarish demo yozuvlari | Ishonchli moliyaviy jurnal, haqiqiy tasdiqlovchi, parallel amallardan himoya |
| TZ §6.17–19: qabul va nizo | Material/ish qabulini demo qilish; nizo va admin izohi | Mijozning o‘z akkauntidagi tasdiq, media va qaror jarayoni |
| TZ §6.20: reyting | Moderatsiya, ko‘rsatish/yashirish | Mijoz yuborishi, buyurtmaga egalik va yakunlanish tekshiruvi |
| TZ §8–9: hisobot | Oltita hisobot turi; filtrlangan lokal CSV | Server agregatlari, to‘liq dataset CSV/XLSX; XLSX hozir demo xabar |
| TZ §3,10: audit va ruxsat | Lokal audit jadvali va demo aktyor nomlari | O‘zgarmas server auditi, individual staff akkauntlari, obyekt ruxsatlari |
| TZ §6.2–3,12: media va xarita | Belgilangan placeholderlar | Maxfiy upload/download, koordinatalar, provayder |
| TZ §3–4,11: Mini App va tillar | CRM o‘zbekcha; Mini App ushbu ilovaga kirmaydi | Django Templates Mini App: mijoz/usta/do‘kon, UZ/RU/EN va Telegram |

### 1.1. Demo bilan TZ orasidagi muhim farqlar

Backend yozishda quyidagilarni frontenddan tayyor biznes qoida deb ko‘chirmang:

1. **Mijoz va hamkor amallarini admin simulyatsiya qiladi.** `OrderDetail.tsx`, `EstimatePanel.tsx`dagi demo tasdiq/status tugmalari real foydalanuvchi tasdig‘i emas. API rejimida tegishli rolning haqiqiy amali kerak. Xodim qog‘oz imzoni qayd etishi esa TZda alohida ruxsat etilgan.
2. **Rad etish hayoti to‘liq ajratilmagan.** UI umumiy `rejected` statusiga ega, lekin usta rad javobi, do‘konning sababli rad javobi va mijoz smetani rad etishi uchun alohida tarix/model yo‘q. TZ §6.8 bo‘yicha rad qilingan smetani o‘sha santexnik tahrirlab qayta yubora olmaydi. Admin yopish yoki boshqa ustaga tayinlashni tanlaydi.
3. **Barcha moliyaviy yozuvlar demoda ikki bosqichli.** TZ naqd topshirish va hamkorlarga pul berishda markaz xodimi tasdig‘ini aniq talab qiladi. Har bir mijoz to‘lovi uchun ham alohida ikkinchi tasdiq yoki boshqa xodim majburiyligi TZda belgilanmagan. Yakuniy tasdiqlash siyosati kelishiladi.
4. **Demo qo‘shimcha cheklovlar qo‘yadi:** nizo avansni ham bloklaydi; avans belgilangan miqdordan ortiq qabul qilinmaydi; ish boshlangach yangi yetkazish qismi qo‘shilmaydi. TZ nizoda qoldiq va yakuniy hamkor hisob-kitobini bloklaydi. Qolgan cheklovlarni alohida qarorsiz talabga aylantirmang.
5. **Yetkazish va shoshilinch haq taqsimoti ochiq.** `rules.ts` yetkazish haqini do‘kon sof summasiga qo‘shadi, shoshilinch haqni hamkor sof summasiga qo‘shmaydi. TZ faqat komissiya bazalarini belgilaydi; bu ikki daromadning oluvchisi va hisob-kitob tartibi alohida kelishilishi kerak.
6. **Pul aniqligi demo qarori.** UI qator summalarini butun so‘mga `Math.round` qiladi. TZdagi UZS talabi yaxlitlash, kasr xona va miqdor aniqligini belgilamaydi. Bular server va buxgalteriya bilan bir xil qoida sifatida kelishiladi.
7. **Bekor qilish hisobi soddalashtirilgan.** Demoda bekor qilingan buyurtmaning mijoz qoldig‘i 0; ayrim hamkor qarzlari 0 yoki `null`. Backend oldingi majburiyatlarni o‘chirib yubormaydi: real zarar, qaror, qaytarish va hisob tuzatishi alohida qayd etiladi. UI faqat to‘liq/qaytarmaslik qarorini ko‘rsatadi; qisman qaytarish siyosati belgilanmagan.
8. **ETA namunaviy.** Demo tayyorlashda bir soat keyingi vaqtni yaratishi mumkin. Backend buni haqiqiy yo‘l ETA deb qaytarmaydi; provayder ishlamasa vaqt noma’lumligi yoki qo‘lda berilgan taxmin aniq ko‘rsatiladi. Provaydersiz yechim TZdagi yo‘l ETA integratsiyasi bajarildi degani emas.
9. **Audit va rozilik lokal.** Demo nomi, checkbox va brauzer vaqti haqiqiy shaxsni/rozilikni isbotlamaydi. Server rozilik matni versiyasi, kim, qachon va qaysi manbadan tasdiqlaganini saqlaydi. Lokal takror audit yozuvlarini serverga ko‘chirmang.

## 2. Talablar ustuvorligi va MVP chegarasi

1. Biznes qoidalar uchun `docs/TZ_docs.md` asosiy manba; uning holati DRAFT.
2. `docs/reactjs.md` statik admin UI chegarasini belgilaydi.
3. Ushbu fayldagi endpointlar, DTOlar, papkalar va texnik tanlovlar **taklif etilayotgan kontrakt**. Ular mavjud yoki allaqachon tasdiqlangan API emas. Amalga oshirishdan oldin tanlovlar OpenAPI sxemasiga mahkamlanadi.
4. UI kodi talablar orasidagi bo‘shliqni o‘zicha yopuvchi manba bo‘lmaydi. Ochiq biznes masalasi yashirin default bilan hal qilinmaydi; tegishli amal aniq xato bilan to‘xtatiladi.

MVP: Marhamat, bitta markaz, santexnika, UZS, qo‘lda tayinlash, qog‘oz imzo, naqd/terminal yozuvlari. Onlayn to‘lov provayderi, avtomatik material kalkulyatori, kuryer akkaunti/jonli GPS, bonus/reklama/premium, boshqa kasblar va kafolat da’volari kiritilmaydi.

## 3. Backend tuzilishi

TZ talabi: Python + Django + DRF; Mini App Django Templates/CSS/JS, admin React. Django versiyasi, baza, hosting va saqlash provayderi TZda ochiq. Tranzaksiya va qator qulflashni qo‘llaydigan PostgreSQL — texnik taklif, tasdiqlangan talab emas.

Tavsiya etilayotgan modullar:

```text
accounts/       # staff, Telegram identity, sessions, role/object permissions
catalog/        # region, category, unit, service, area rate, material
partners/       # plumber, shop, Telegram linkage, commission policy
orders/         # assignments, schedules, commands, timeline, dispute/cancellation
estimates/      # immutable versions, line snapshots, approvals
contracts/      # template families/versions, order snapshots, PDF/signature records
finance/        # receipts, cash custody, settlement, refunds, ledger
reviews/        # customer submissions and moderation
notifications/ # in-app inbox, Telegram outbox, retry jobs, response deadlines
files/          # private media and authorized document access
reporting/      # dashboard, reports, exports
audit/          # append-only actor/action/change events
settings/       # pilot center and versioned operational defaults
```

DRF view/serializer so‘rovni tekshiradi; biznes amali domain service/command qatlamida bajariladi. Bitta amal tartibi: autentifikatsiya → ruxsat → idempotency tekshiruvi → tranzaksiya va kerakli lock → versiya/holat tekshiruvi → hisob/saqlash → audit va outbox → commit. Telegram/PDF/eksport kabi tashqi ishlarni ochiq DB tranzaksiyasi ichida bajarmang.

Model constraintlari va tranzaksiyalar ham yaxlitlikni himoya qiladi. Faqat serializer yoki React validatsiyasi yetarli emas. Staff REST API va Mini App bir xil biznes service qatlamidan foydalanadi.

## 4. Ma’lumot modeli va UI bilan xaritalash

Ichki IDlar uchun UUID, foydalanuvchiga ko‘rinadigan buyurtma raqami uchun alohida `number` taklif qilinadi. `DEMO-*`, `P-*`, `SH-*` prefikslariga biznes mantiq bog‘lanmasin. Tarixiy buyurtmada ishtirok etgan profil/katalogni oddiy DELETE bilan yo‘qotmang; faolsizlantirish va maxfiylik bo‘yicha o‘chirish alohida jarayon.

| Model | Asosiy maydonlar va qoidalar | Reactdagi mos qism |
| --- | --- | --- |
| StaffUser / TelegramIdentity | Individual staff login, faol holat; tekshirilgan Telegram ID, role, language; usta/do‘kon profiliga admin boshqaradigan bog‘lanish | Hozir haqiqiy akkaunt modeli yo‘q |
| Customer / ConsentRecord | Ism, ulashilgan telefon, Telegram identity; rozilik matni versiyasi, order, vaqt, manba; staff yaratgan so‘rovda kimning nomidan qayd etilgani | `Customer`, `Order.consent` |
| Plumber | Ism, telefon, foto, hudud, xizmat yo‘nalishlari, tajriba, izoh, faol holat, nullable individual komissiya | `Plumber` |
| Shop | Nom, kontakt vakili, manzil/hudud, telefon, bitta umumiy Telegram akkaunt, izoh, faol holat, nullable komissiya | `Shop` |
| Region / Category / Unit | Barqaror kod va tarjima nomlari; pilot chegarasi serverda | Hozir matn va `categories` konstantasi |
| Service / AreaRate | UZ/RU/EN nom, kategoriya, birlik, kafolat, tavsif, faol/ko‘rinish; hududga bog‘liq stavka va qat’iy shoshilinch tarif, versiya/amal vaqti | `Service.areaRate`, `emergencyFee` — bitta pilot hududga soddalashtirilgan |
| Material | Nom, guruh, marka, o‘lcham/model, birlik, tavsif, faol holat. Buyurtma narxi umumiy katalog narxi emas | `Material` |
| Order | Mijoz, hudud/xizmat, manzil, lat/lng, izoh/media, urgent so‘rov/tasdiq, umumiy holat, joriy hamkorlar, versiya, vaqtlar | `Order` |
| AssignmentAttempt | Order, partner turi/ID, tayinlagan xodim/vaqt, pending/accepted/rejected/superseded, javob va sabab, usta uchun response deadline | `assignedAt`, `plumberId`, `shopId`dan kengroq |
| Schedule / OrderEvent | Ko‘rik va taxminiy ish boshlanish/tugash, o‘zgarish sababi, haqiqiy prep/work start va finish vaqtlar, actor | `inspectionAt`, `workStart`, `workEnd`, `etaReason`, booleans, `timeline` |
| EstimateVersion / Line | Order, versiya, muallif va assignment, draft/submitted/approved/rejected/superseded; qator snapshotlari, miqdor, birlik, narx, marka, mavjudlik/ta’minot taxmini | `estimate`, `confirmedEstimate`, `estimateHistory` |
| EstimateApproval | Aniq versiya, mijoz identity, accepted/rejected, vaqt, ixtiyoriy rad sababi | Hozir faqat `approved` boolean |
| OrderFinancialTerms | Avans mode/value; hamkor stavkalari, ularning manbasi va versiyasi; qaysi smetaga bog‘liqligi | `advance`, `commissions` |
| ContractTemplateVersion | Barqaror family ID, til, versiya, matn, note, draft/active/archived, muallif/vaqt | `ContractTemplate`; family nomga tenglashtirilmasin |
| OrderContract | Template/estimate versiyasi, tomonlar va shartlar snapshoti, til, PDF ID/hash, har to‘rt imzo qaydi, qayd etgan staff/vaqt, ixtiyoriy scan | `contract`, `contractHistory` |
| DeliveryPart / MaterialReceipt | Order/shop, label, preparing/transit/delivered, ETA va source, vaqt/sabab; mijoz qabul qaydi yoki muammo/foto | `deliveries`, `materialReceived` |
| WorkAcceptance | Ustaning bajarildi hodisasi, ixtiyoriy foto, mijoz qabul/rad vaqti/identity | `workStarted`, `customerCompleted` |
| Dispute / CancellationDecision | Sabab, tomon, ochilgan vaqt, media, admin qarori/izoh/vaqt; cancel uchun earliest start dalili va refund qarori | `dispute`, `cancelReason`, `refundDecision` |
| PaymentRecord / LedgerEntry | Order, tur/usul/summa, haqiqiy hodisa va qayd vaqti, oluvchi/topshiruvchi, recorded/confirmed/voided, actorlar, original/reversal havolasi | `Payment`; confirmed yozuv immutable |
| Review | Order, mijoz, aynan tayinlangan hamkor, 1–5, izoh, pending/published/hidden, moderatsiya actor/vaqt/sabab | `Review` |
| AuditEvent / Notification | Actor ID/role, amal, obyekt, o‘zgarish, server vaqti, request/event ID; xabarning qabul qiluvchisi/tili/kanali/statusi | `AuditEvent` va shell bildirishnomalari |
| CenterSettings | Markaz kontakt/ish vaqti/timezone, responseMinutes, nullable standart avans/komissiyalar, tillar va bildirishnoma sozlamasi, versiya | `Settings` |

Tarixiy snapshotga xizmat/material nomi, birlik, hududiy narx manbasi, tegishli hamkor, tomon rekvizitlari va tegishli moliyaviy shartlar yoziladi. Faqat o‘zgaruvchan katalog FKlariga tayanmang. Katalog/standart komissiya o‘zgarsa eski tasdiqlangan majburiyat qayta hisoblanmaydi.

## 5. API umumiy kontrakti — taklif

- Base path: `/api/v1/`. Staff: `/api/v1/admin/`; Mini App: `/api/v1/mini/`. TZ API versiyalash usulini hali belgilamagan.
- JSON maydonlari `snake_case`; React domaini `camelCase`. O‘girish alohida adapterda, JSX ichida emas.
- Pul va kasr miqdorlar JSONda decimal satr: `"125000.00"`, `"2.5"`; valyuta `"UZS"`. Aniqlik/yaxlitlash §9 va §15da kelishiladi. `null` — noma’lum, `"0.00"` — ma’lum nol. Server float hisob ishlatmaydi.
- Sana/vaqt ISO 8601, offset bilan; server UTCda saqlaydi, UI `Asia/Tashkent`da ko‘rsatadi. Lokal vaqt offsetisiz qabul qilinmaydi. Telegram ID transportda satr sifatida beriladi.
- Tizim actor, rol, server timestamp, status, jami, komissiya summasi, tasdiq va auditni o‘zi belgilaydi. Clientdan shu maydonlarni yozishga urinish `400` beradi; jimgina qabul qilinmasin.
- Ro‘yxat: `count`, `next`, `previous`, `results`; `page`, `page_size` (taklif: default 25, max 100). Saralash faqat ruxsat etilgan maydonlar; teng qiymatlarda ID bilan barqaror tartib.
- Qidiruv `search`; ordering `ordering=-created_at`; bo‘sh filtr yuborilmaydi. Enum va noma’lum filterlar uchun aniq validatsiya bo‘lsin.
- Tahrir/commandlarda `expected_version` majburiy. Eskirgan versiyada `409 version_conflict`; server joriy versiyani qaytaradi. Mustaqil resource o‘z versiyasiga ega; moliyaviy amal order va tegishli hisob qatorlarini ham lock qiladi.
- Takror bajarilishi xavfli POSTlar `Idempotency-Key` talab qiladi. Scope: actor + route/resource + key; request hash saqlanadi. Bir xil key/payload qayta kelsa avvalgi natija qaytadi; boshqa payload — `409 idempotency_conflict`. Bir xil key uchun parallel so‘rov bitta amal yaratadi. Muvaffaqiyatli replay eski `expected_version` sabab rad etilmaydi. Saqlash muddati texnik kontraktda ko‘rsatiladi.
- `200` o‘qish/command natijasi, `201` yangi resource, `202` queued job, `400` validatsiya, `403` ruxsat/CSRF, `404` yo‘q yoki begona obyekt, `409` holat/versiya/idempotency konflikti, `429` limit. Session authda anonymous so‘rov ham DRF konfiguratsiyasiga ko‘ra `403` bo‘lishi mumkin; UI `code` orqali ajratadi.
- `401 authentication_required` ishlatilishi tanlangan auth sxemasida belgilansa, OpenAPIga kiritilsin. Biznes error kodlari tarjimadan mustaqil bo‘lsin; frontend xabarni va maydon xatolarini ko‘rsatadi.
- HTTPS; cookie auth bo‘lsa CSRF; cheklangan originlar. Maxfiy javoblar, PDF va eksport uchun public cache qo‘llanmaydi. Sirlar `VITE_*`ga joylanmaydi.

Xato namunasi:

```json
{
  "code": "validation_error",
  "message": "Ma’lumotlarni tekshiring.",
  "field_errors": { "amount": ["Summa ruxsat etilgan qoldiqdan oshdi."] },
  "request_id": "req-example-001"
}
```

Holat xatosida `code: "transition_not_allowed"`, `reason_code: "advance_required"` kabi mashina o‘qiydigan sabab; versiya xatosida `current_version` qaytarilsin. Stack trace yoki boshqa mijoz ma’lumoti yuborilmasin.

## 6. Staff API endpointlari — taklif

Quyidagi yo‘llar `/api/v1/admin/`ga nisbatan yozilgan. `{id}` server ID. `GET list/detail` ikkita endpointni anglatadi. Umumiy PATCH faqat oddiy profil/katalog maydonlari uchun; status/approval/payment yozish uchun emas.

### 6.1. Akkaunt, katalog va o‘qish endpointlari

| Method / yo‘l | Vazifa va asosiy parametrlar |
| --- | --- |
| `GET auth/csrf/` | Session auth tanlansa login oldidan CSRF bootstrap |
| `POST auth/login/`, `POST auth/logout/`, `GET auth/me/` | Login, chiqish va joriy individual staff; login ham CSRF bilan himoyalanadi |
| `GET/POST staff/`, `GET/PATCH staff/{id}/` | Staff akkauntlari; yaratish/faolsizlantirish auditlanadi. Hozir Reactda staff boshqaruv ekrani yo‘q |
| `GET/POST customers/`, `GET/PATCH customers/{id}/` | Profil/izoh; consent va Telegram identityni oddiy PATCH bilan o‘zgartirmang |
| `GET/POST plumbers/`, `GET/PATCH plumbers/{id}/` | Hudud/yo‘nalish/faollik/individual komissiya, profil |
| `GET/POST shops/`, `GET/PATCH shops/{id}/` | Profil, faollik, individual komissiya |
| `POST plumbers/{id}/telegram-link/`, `POST shops/{id}/telegram-link/` | Tekshiriladigan akkaunt bog‘lash/almashtirish; duplicate/conflict tekshiruvi va audit |
| `GET regions/`, `GET categories/`, `GET units/` | Barqaror kod va tilga mos nomlar |
| `GET/POST services/`, `GET/PATCH services/{id}/` | Xizmat tarjimalari, kategoriya/birlik/kafolat/ko‘rinish |
| `GET/POST service-rates/`, `GET/PATCH service-rates/{id}/` | Service + region + rate/emergency_fee, versiya; eski snapshotlar saqlanadi |
| `GET/POST materials/`, `GET/PATCH materials/{id}/` | Material katalogi, buyurtmaga xos narxsiz |
| `GET orders/`, `GET orders/{id}/` | Summary ro‘yxati va batafsil staff DTO |
| `GET orders/{id}/assignments/`, `GET orders/{id}/eligible-plumbers/` | Tarix va server hisoblagan hudud/xizmatga mos faol ustalar |
| `GET orders/{id}/estimates/`, `GET orders/{id}/contracts/` | Barcha versiyalar va tasdiq holatlari |
| `GET orders/{id}/timeline/`, `GET orders/{id}/notes/`, `GET orders/{id}/deliveries/` | Tablar uchun sahifalanadigan yozuvlar |
| `GET orders/{id}/finance/` | Server hisoblagan tushum/qoldiq/komissiya/hamkor qarzi/naqd majburiyat |
| `GET payments/`, `GET payments/{id}/`, `GET payments/{id}/receipt/` | Moliyaviy yozuvlar va ruxsatli ichki kvitansiya |
| `GET reviews/`, `GET audit-events/` | Moderatsiya va read-only audit; auditga public create/PATCH/DELETE yo‘q |
| `GET/PATCH settings/` | Versiyali markaz/defaultlar; tugallanmagan sozlama `null` |
| `GET search/` | Staff global qidiruv: `search`, resource turi, cheklangan natija |
| `GET notifications/`, `POST notifications/{id}/read/` | Saqlanadigan xabarnomalar va o‘qilganlik |

Ro‘yxat filtrlari:

- Orders: `search`, `status`, `category_id`, `customer_id`, `plumber_id`, `shop_id`, `urgent`, `payment_state`, `created_from`, `created_to`.
- Partners: `search`, `is_active`, `region_id`, `category_id` (usta). Do‘kon tanlashda region majburiy emas.
- Payments: `order_id`, `type`, `method`, `status`, `collector`, `occurred_from`, `occurred_to`.
- Reviews: `status`, `target_type`, `target_id`, `order_id`, `created_from`, `created_to`.
- Audit: `actor_id`, `action`, `object_type`, `object_id`, `from`, `to`, `search`.

Profil tablari tegishli endpointlardan ID filtri bilan olinadi; butun `Database`ni brauzerga bir martada yuklamang.

### 6.2. Staff buyurtma commandlari

Har bir command ruxsat/versiya/holat tekshiradi va auditga yoziladi. Oddiy staff admin huquqi biznes shartlarini chetlab o‘tmaydi.

| Method / yo‘l | Body / shart |
| --- | --- |
| `POST orders/` | `customer_id`, service/category/region, address/location, description, media IDs, urgent request, qayd etilgan rozilik manbasi. Staff yaratish UI’da bor; mijozning roziligi o‘rniga taxminiy `true` yozilmasin |
| `POST orders/{id}/assign-plumber/` | `plumber_id`, `reason`; mos faol usta, yangi assignment va deadline; hali mijozga qabul xabari ketmaydi |
| `POST orders/{id}/assign-shop/` | `shop_id`, `reason`; barcha hududdan faol do‘kon, bir vaqtda bitta joriy shop assignment |
| `POST orders/{id}/confirm-urgency/` | `approved`, `reason`; markaz ish vaqti va xizmat/hudud tarifi tekshiriladi |
| `POST orders/{id}/notes/` | `text`; actor/time serverda, staff ichki izohi mijoz DTOsiga chiqmaydi |
| `POST orders/{id}/financial-terms/` | `advance_mode`, `advance_value`, partner stavkalari, `reason`; manba/snapshot saqlanadi, tasdiqlangan shartlar jim almashtirilmaydi |
| `POST orders/{id}/estimates/` | Vakolat doirasida qoralama/new revision, qatorlar va sabab. Staff narx tuzatishi auditlanadi; TZdagi mijoz-rad/usta cheklovi chetlab o‘tilmaydi |
| `POST orders/{id}/estimates/{eid}/submit/` | Aynan versiya mijozga taklif qilinadi; narx/mavjudlik/tarif/avans tayyorligi tekshiriladi |
| `POST orders/{id}/contracts/` | `estimate_id`, `template_version_id`, `language`; faqat tasdiqlangan smetadan snapshot va PDF job |
| `POST contracts/{id}/record-signatures/` | To‘rt tomon kodi bo‘yicha qog‘oz imzo qaydi; staff identity, qayd vaqti, ixtiyoriy scan ID; signed nusxa o‘zgarmaydi |
| `POST orders/{id}/disputes/` | `reason`, media; staff murojaatni qayd etsa manba/kimning nomidanligi alohida yoziladi |
| `POST disputes/{id}/resolve/` | `resolution`, `outcome`; davom ettirish/yangi smeta/bekor qilish kabi aniq qaror. Avvalgi statusga ko‘r-ko‘rona qaytmang |
| `POST orders/{id}/cancel/` | `initiator`, `reason`; earliest prep/work start dalilidan refund qarori shakllanadi |
| `POST orders/{id}/refund-decision/` | `decision`, ruxsat etilgan summa, `reason`; kompaniya/hamkor sababli holatda admin qarori. Qisman refund siyosati §15da |
| `POST orders/{id}/close/` | Mijoz ishni qabul qilgan, majburiy qoldiq yopilgan, faol nizo yo‘q; alohida partner payout holati saqlanadi |

Hozir UI’da ko‘rik/statusni admin almashtirish mumkin. API rejimida usta/do‘kon/mijoz amallari §7dagi rol endpointlariga o‘tadi. Staff uchun zarur istisno vakolat bo‘lsa, sabab/dalil bilan alohida kelishilgan command qilinadi; yashirin impersonation yoki universal `PATCH status` berilmaydi.

### 6.3. Moliya, shartnoma, moderatsiya va hisobot

| Method / yo‘l | Vazifa |
| --- | --- |
| `POST payments/` | Staff tashqi naqd/terminal hodisasini qayd etadi: order, type, method, amount, occurred_at, haqiqiy oluvchi/topshiruvchi, note |
| `POST payments/{id}/confirm/` | Markaz xodimi haqiqiy qabul/berishni tasdiqlaydi; record holati va barcha limitlar lock ichida qayta tekshiriladi |
| `POST payments/{id}/void/` | Faqat tasdiqlanmagan noto‘g‘ri yozuvni sabab bilan bekor qilish |
| `POST payments/{id}/reverse/` | Tasdiqlangan noto‘g‘ri yozuvni o‘chirish o‘rniga bog‘langan tuzatish; vakolat, dalil va keyingi hisoblar tekshiriladi. Bu yangi bank to‘lovi emas |
| `GET/POST contract-templates/`, `GET contract-templates/{id}/` | Oilalar/versiyalar, yangi draft; mavjud signed nusxalarga ta’sirsiz |
| `POST contract-templates/{id}/versions/` | Yangi matn/til/izoh bilan yangi versiya |
| `POST contract-templates/{id}/activate/` | Shu family/til ichida bitta faol versiya; oldingi active arxivlanadi |
| `GET contracts/{id}/pdf/` | Saqlangan snapshotga tegishli haqiqiy PDF; joriy andozadan qayta yasab almashtirmang |
| `POST reviews/{id}/moderate/` | `status: published|hidden`, reason; actor/time serverda |
| `GET dashboard/` | Sana/hudud kesimida KPI, trend, statuslar, kechikkan javoblar, moliya xulosasi |
| `GET reports/{kind}/` | `kind`: orders, lines, payments, commissions, partners, ratings; server agregatlari va satrlar |
| `POST exports/`, `GET exports/{id}/`, `GET exports/{id}/download/` | Report kind + format `csv|xlsx` + bir xil filterlar; queued/ready/failed, ruxsatli fayl |
| `POST files/`, `GET files/{id}/download/` | Multipart upload va obyekt ruxsatiga bog‘langan private download |

## 7. Mini App API endpointlari — taklif

Bu endpointlar React admin sahifalari emas, TZdagi to‘liq oqimni bajarish uchun kerak. Base: `/api/v1/mini/`. Actor Telegram kirishidan serverda aniqlanadi; `customer_id`, `plumber_id`, `shop_id` yuborish orqali rol tanlab bo‘lmaydi.

| Rol | Method / yo‘l | Amal |
| --- | --- | --- |
| Umumiy | `POST auth/telegram/`, `GET me/`, `PATCH me/`, `POST auth/logout/` | Validated initData bilan kirish, rol/til, profilning ruxsatli maydonlari, chiqish |
| Umumiy | `GET catalog/services/`, `GET center/` | Hudud/tildagi ko‘rinadigan xizmat/tariflar va markaz yordam kontaktlari |
| Umumiy | `GET notifications/`, `POST notifications/{id}/read/` | O‘ziga tegishli xabarlar |
| Mijoz | `POST orders/`, `GET orders/`, `GET orders/{id}/` | Rozilik, ulashilgan telefon, address/location bilan so‘rov; faqat o‘z buyurtmalari |
| Mijoz | `POST orders/{id}/estimates/{eid}/approve/` yoki `reject/` | Ko‘rsatilgan aynan joriy versiyani tasdiqlash/rad; rad sababi ixtiyoriy |
| Mijoz | `POST orders/{id}/material-receipt/` | Qabul yoki muammo, qism IDs, foto/izoh; shopning delivered hodisasidan farq qiladi |
| Mijoz | `POST orders/{id}/work-acceptance/` | Qabul yoki e’tiroz; e’tiroz nizo ochadi, o‘zi qoldiqni yopmaydi |
| Mijoz | `POST orders/{id}/cancel/` | Server refund qoidasini hisoblaydi, mijoz refund summasini belgilamaydi |
| Mijoz | `POST orders/{id}/reviews/` | Yakunlangan buyurtmadagi usta/do‘kon, 1–5, optional comment; pending |
| Mijoz | `GET orders/{id}/payments/`, `GET contracts/{id}/pdf/`, `GET payments/{id}/receipt/` | Faqat o‘ziga tegishli kvitansiya/shartnoma |
| Usta | `GET assignments/`, `GET orders/{id}/` | Faqat amaldagi tayinlash va zarur tarix doirasi |
| Usta | `POST assignments/{id}/accept/` yoki `reject/` | Aynan joriy tayinlashga javob; eski assignment yangi holatni o‘zgartirmaydi |
| Usta | `POST orders/{id}/inspection/`, `POST orders/{id}/schedule/` | Ko‘rik va taxminiy ish vaqti; o‘zgarish sababi, mijozga xabar |
| Usta | `POST orders/{id}/estimates/`, `POST orders/{id}/estimates/{eid}/submit/` | Xizmat/miqdor, katalog/erkin material; narx server tarifidan; rad qilingan smetani o‘sha usta qayta yubormaydi |
| Usta | `POST orders/{id}/work-start/`, `POST orders/{id}/work-finish/` | Haqiqiy start/end hodisasi; ixtiyoriy yakun fotosi; mijoz tasdig‘idan ajratilgan |
| Usta | `POST orders/{id}/payments/`, `GET orders/{id}/payments/` | Faqat mijozdan o‘zi olgan advance/balance cash/terminalni qayd etish va ruxsatli tarix; settlement/refund/confirm huquqi yo‘q |
| Do‘kon | `GET assignments/`, `GET orders/{id}/`, `POST assignments/{id}/accept/` yoki `reject/` | Faqat o‘ziga tayinlanganlar; reject uchun sabab majburiy |
| Do‘kon | `POST orders/{id}/material-offer/` | Joriy revision material narxi/mavjudligi/muqobili, tayyorlash daqiqasi, bir martalik yetkazish haqi; narx o‘zgarishi mijozga qayta yuboriladi |
| Do‘kon | `POST orders/{id}/preparation-start/` | Smeta + to‘rt imzo + yetarli avans guardlari |
| Do‘kon | `POST orders/{id}/deliveries/`, `POST deliveries/{id}/update/` | Qism yaratish; faqat o‘z qismlarining ruxsatli status/ETA o‘zgarishi, sabab |
| Ruxsatli ishtirokchi | `POST files/`, `GET files/{id}/download/` | Buyurtma doirasida ruxsatli media; har bir download qayta tekshiriladi |

Usta/do‘konning read DTOsi faqat bajarish uchun zarur ma’lumot va ularga tegishli yakuniy to‘lov summasini beradi. Staff komissiya stavkalari, markaz daromadi, boshqa hamkor hisobi va ichki izohlar yuborilmaydi.

## 8. Holatlar, hodisalar va guardlar

Frontenddagi asosiy status enumlari adapter orqali saqlanishi mumkin:

```text
new → assigned → accepted → inspection → estimating → shop_pending
    → approval → contract → preparing → transit → delivered
    → working → completion → completed
Qo‘shimcha ko‘rinishlar: partial, dispute, cancelled, rejected
```

Bu chiziq ruxsat beruvchi universal status endpointi emas. Assignment, estimate, contract, delivery, payment va dispute o‘z holatiga ega bo‘lsin; `display_status` ulardan hisoblanadi. `rejected` har doim butun buyurtma yopildi degani emas. UI `isClosed` ham uni yopilgan deb hisoblamaydi.

| Hodisa | Kim | Server sharti / natija |
| --- | --- | --- |
| So‘rov yaratish | Mijoz yoki rozilikni qayd etuvchi staff | Pilot hudud, manzil/nuqta/telefon/rozilik; shoshilinch so‘rovda markaz ish vaqti |
| Usta tayinlash | Staff | Faol va hudud/xizmatga mos; oldingi urinish tarixi saqlanadi; deadline; avtomatik tanlash yo‘q |
| Usta qabul/rad | Tayinlangan usta | Faqat pending joriy urinish; acceptdan so‘ng mijozga xabar va telefon ochiladi; rejectdan so‘ng staff qayta tayinlaydi |
| Ko‘rik belgilash | Usta | Qabul qilingan assignment; bepul, mijozning alohida approve amali talab qilinmaydi |
| Xizmat/material kiritish | Usta | Musbat miqdor va birlik, tarif serverdan; free materialda nom/miqdor/birlik majburiy |
| Do‘kon tayinlash/javobi | Staff / shop | Bir joriy do‘kon; hudud bilan cheklanmaydi; reject sababli; do‘konga response timer yoki auto reassignment yo‘q |
| Yakuniy smeta yuborish | Vakolatli rol | Material taklifi, barcha zarur narxlar/ta’minot shartlari, yetkazish/urgent, avans sharti tayyor; muqobil yoki narx o‘zgarsa yangi versiya |
| Smeta qabul/rad | Mijoz | Aynan current submitted versiya; approve snapshot; rejectda o‘sha usta uchun qayta yuborish blok, staff yopadi/boshqa ustaga beradi |
| Shartnoma chiqarish/imzo qaydi | Server / staff | Tasdiqlangan smetadan PDF; to‘rt tomonning qog‘oz imzosi; staff qayd qiladi; scan majburiy emas |
| Tayyorlash boshlash | Shop | Aynan amaldagi approved estimate va unga mos signed contract, yetarli confirmed avans, nizo/blok yo‘q; haqiqiy boshlanish vaqti |
| Yetkazish holati | Shop | Faqat o‘z order/parti, ruxsatli oldinga o‘tishlar; qismlar alohida, yetkazish haqi bir marta |
| Material qabul / muammo | Mijoz | Shop delivered degani avtomatik mijoz qabul qildi emas; qism/qator bo‘yicha to‘liqlik va muammo saqlanadi |
| Ish boshlash/tugatish | Usta | Shartnoma/avans va materialga bog‘liq talablar bajarilgan; ish tugadi → completion, hali customer accepted emas |
| Ish qabul / e’tiroz | Mijoz | Finish hodisasi mavjud; e’tiroz nizo ochadi, qoldiq/yakuniy partner payout bloklanadi |
| Yopish | Server/staff command | Mijoz qabul qilgan + majburiy qoldiq to‘langan + nizo yo‘q; hamkor to‘lovi alohida kuzatiladi |
| Bekor qilish/refund | Mijoz/staff | Sabab va prep/workning eng birinchi haqiqiy start vaqti; qaror qaydi, real refund alohida moliyaviy amal |

Yangi smeta/hamkor almashishi eski tasdiqni yangi ma’lumotga ko‘chirmaydi. Oldingi signed nusxa saqlanib, yangi shartlar uchun yangi shartnoma va zarur avans farqi hosil qilinadi. Eski mijoz tasdig‘i yangi versiyani tasdiqlay olmaydi.

Materiallarsiz xizmatda shop/four-party signature/delivery bosqichlarini qanday o‘tkazish TZda aniq yozilmagan. Ishlab chiqarishdan oldin bu yo‘l kelishiladi; hamma orderni sun’iy do‘kon/yetkazishga majburlamang yoki imzo talabini yashirincha olib tashlamang. Qisman material bilan ish boshlash tartibi ham alohida aniqlanadi.

## 9. Pul, komissiya va hisob-kitob qoidalari

### 9.1. Smeta

```text
xizmatlar = Σ (miqdor × tasdiqlangan hududiy birlik stavkasi)
materiallar = Σ (miqdor × do‘kon taklifidagi birlik narxi)
jami = xizmatlar + materiallar + bir martalik yetkazish + shoshilinch haq
platforma haqi = 0; QQS narxlarga kiritilgan, yana qo‘shilmaydi
usta komissiyasi = xizmatlar × kelishilgan usta stavkasi / 100
do‘kon komissiyasi = materiallar × kelishilgan do‘kon stavkasi / 100
```

Hisobni backend qiladi. Client taklif qilgan jami yoki komissiya summasiga ishonilmaydi. Noma’lum majburiy narx `null` bo‘lsa jami ham `null`; 0ga aylantirilmaydi va moliyaviy tasdiq ochilmaydi. Shoshilinch bo‘lmagan orderda shu qo‘shimcha haq aniq 0 bo‘lishi mumkin.

Pul/miqdor Decimal; pul scale, miqdor scale, foiz aniqligi va qator/umumiy yaxlitlash tartibi implementatsiyadan oldin belgilanadi. Masalan JSONdagi `.00` — format namunasi, tasdiqlangan buxgalteriya scale talabi emas. Foiz 0–100, miqdor >0, narx ≥0; server upper limitlari OpenAPIga yoziladi.

Hamkor individual komissiyasi `null` bo‘lsa standart olinadi; ikkisi ham noma’lum bo‘lsa hisob `null`. 0% to‘g‘ri qiymat, fallback sabab emas. Tanlangan stavka/manba moliyaviy shartlarga snapshot qilinadi. Komissiya yangilanishining keyingi buyurtmalarga qo‘llanish vaqti aniq bo‘lsin; eski order jim qayta hisoblanmaydi.

Avans percent yoki fixed. Fixed qiymat jamidan katta bo‘lsa rad etish yoki jami bilan cheklash siyosati kelishiladi; UI hozir `min(total, fixed)` qiladi. Avans 0ga sozlanishi mumkinligi ham aniq qaror bo‘lsin, `null` bilan tenglashtirilmasin.

### 9.2. Moliyaviy yozuvlar va invariantlar

Turlar: `advance`, `balance`, `cash_handover`, `shop_settlement`, `plumber_settlement`, `refund`; usullar: `cash`, `terminal`. Settlement naqd, mijoz to‘lovi naqd/terminal. Ichki yozuv tashqi pul o‘tkazmasini amalga oshirmaydi.

- Har bir hodisada ijobiy summa, UZS, order va haqiqiy tomonlar; `occurred_at` va server `recorded_at` ajratiladi. Qayta sana berish vakolati va sababi boshqariladi.
- `recorded` — hali ledgerga posted emas. `confirmed` — hisobga o‘tgan. Naqd topshirish va partner payout markaz xodimi tasdig‘idan keyin posted; boshqa receipts uchun tasdiqlash siyosati §15da tanlanadi.
- Mijozning sof to‘lovi confirmed advance + balance − haqiqiy refund, zarur reversal tuzatishlari bilan. Cash handover yoki hamkor payout mijoz to‘lovi sifatida yana qo‘shilmaydi.
- Naqd custody: ustaning confirmed naqd tushumi − markazga confirmed topshirgani − kelishilgan boshqa dalilli custody tuzatishlari. Terminal to‘lovi naqd topshirish qarziga kirmaydi; terminal mablag‘i qaysi hisobga tushishini kelishish kerak.
- Qoldiq to‘lov mijoz ishni qabul qilgandan keyin; nizo bo‘lsa balance va yakuniy partner payout blok. Avans/ortiqcha oldindan to‘lov siyosati UI cheklovidan mustaqil kelishiladi.
- Qabul/tasdiqlash vaqtida summa qoldiqdan oshmasligi, refund olinmagan mablag‘dan oshmasligi, handover real custodydan oshmasligi, payout hamkorning tasdiqlangan qarzidan oshmasligi lock ichida qayta hisoblanadi.
- Bir vaqtning o‘zida kelgan ikki confirm/refund/payoutdan faqat ruxsatli jami o‘tadi. Faqat oldindan o‘qilgan balance yoki bir xil turdagi pending yozuvni tekshirish yetmaydi.
- Posted yozuv tahrirlanmaydi/o‘chirilmaydi. Noto‘g‘ri yozuvga bog‘langan reversal va zarur yangi to‘g‘ri yozuv yaratiladi; refund esa real pul qaytarilishi bo‘lib, reversal bilan aralashtirilmaydi.
- Orderning operatsion yopilishi partner pulini berildi degani emas. Har hamkor bo‘yicha entitled/paid/due, mijoz balance/refund due va naqd custody alohida ko‘rsatiladi.
- Moliyaviy davr tushumi, komissiya daromadi va hamkorlarga qarz bir xil KPI emas. Komissiyani tan olish sanasi/holati buxgalteriya siyosatida belgilanadi.

### 9.3. Bekor qilish

Mijoz `preparation_started_at` va `work_started_at`ning eng birinchisidan oldin bekor qilsa avans to‘liq qaytariladi; ulardan biri boshlanganidan keyin avans qaytarilmaydi (TZ §8.2). Boshlanish hodisasi va bekor qilish bir vaqtda kelsa, server tranzaksiyasi tartibi hal qiladi; browser booleaniga tayanilmaydi.

Kompaniya/do‘kon/usta sabab bajarilmasa alohida admin qarori va asos yoziladi. Jarayonni bekor qilish ledgerdagi oldingi pul/majburiyatni o‘chirmaydi. Real refund alohida qayd/tasdiq qilinadi. Ish boshlanganidan keyingi hamkor xarajati, qisman qaytarish va oldingi payoutga ta’siri ochiq masala; demo `balance=0` formula bilan yashirilmaydi.

## 10. Autentifikatsiya va ma’lumot ruxsatlari

Staff uchun Django session cookie + CSRF, frontend/API bir origin ostida reverse proxy orqali — texnik taklif. Cookie `HttpOnly`/`Secure`, mos `SameSite`; login va session muddati, logout/revocation ham amalga oshiriladi. Frontend/API turli origin bo‘lsa cookie/CORS/CSRF deployment kontrakti alohida belgilanadi. DRF session authdagi CSRF va login talablari: [rasmiy hujjat](https://www.django-rest-framework.org/api-guide/authentication/#sessionauthentication).

Mini App serverga raw `Telegram.WebApp.initData` yuboradi. Server Telegramning [rasmiy validatsiya tartibi](https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app) bo‘yicha haqiqiylik va `auth_date` yangiligini tekshirib, undan keyin lokal session/identity yaratadi. `initDataUnsafe`, client yuborgan Telegram ID yoki rolning o‘zi ishonchli emas. Qayta ishlatish xavfi, sessiya muddati va limitlar belgilanadi. Bot token faqat serverda.

Telefon rozilik bilan haqiqiy ulashish jarayonidan olinadi; Telegram IDdan telefonni taxmin qilmang. Ulashilgan kontakt va kirgan identity mosligi serverda tekshiriladigan oqim bo‘lsin. Bir nechta profil/rolga bog‘langan Telegram identity siyosati kelishilsin.

Har bir list/detail/create/command/download/exportda obyekt ruxsatlari tekshiriladi. DRF list/create amallariga detaildagi object permission o‘z-o‘zidan to‘liq tatbiq bo‘lmaydi; queryset va create validatsiyasi alohida cheklanadi: [DRF permissions](https://www.django-rest-framework.org/api-guide/permissions/#limitations-of-object-level-permissions).

- Staff — individual akkaunt, TZ bo‘yicha to‘liq admin; har birining amali o‘z IDsi bilan. Majburiy boshqa xodim tasdig‘i avtomatik taxmin qilinmaydi.
- Mijoz — faqat o‘z orderlari; ustaning telefoni joriy assignment qabul qilingandan keyin. Do‘kon telefoni hech qachon mijoz DTOsiga qo‘shilmaydi.
- Usta/shop — faqat o‘ziga tegishli order va bajarish uchun zarur mijoz ma’lumoti; ichki moliyaviy breakdown va staff izohlari yo‘q.
- Reassign qilinganda eski hamkorning operational kirishi bekor qilinadi; o‘z tarixiy moliyaviy hujjatlariga zarur kirish alohida chegaralanadi.
- Auditda do‘konning umumiy akkaunti ko‘rsatiladi; mavjud bo‘lmagan xodim ismini aniqlangandek yozmang.
- Rozilik matni va maqsadi versiyalanadi. Buyurtmaga aloqasiz shaxsiy ma’lumotlar tarqatilmaydi; retention/o‘chirish siyosati TZdagi ochiq masala.

## 11. PDF, media, Telegram, ETA va audit

**PDF:** approved smetadan, order/parties/financial terms/template versiyasining muzlatilgan nusxasidan yaratiladi. Job queued/ready/failed holatiga ega; imzolangan nusxa keyingi andoza o‘zgarsa ham o‘zgarmaydi. UZ huquqiy jihatdan ustuvor, RU/EN tarjima. To‘rt tomon imzosining qaydi elektron imzo integratsiyasi degani emas; yuklangan scan ixtiyoriy.

**Media:** uploadda MIME/haqiqiy format, hajm/son limitlari, fayl nomi va xavfli kontent tekshiruvi; private storage. File ID order va uploaderga bog‘lanadi; boshqa orderga begona file ulash taqiqlanadi. Ruxsatli download yoki qisqa muddatli signed URL; URL mavjudligi doimiy public kirish bermasin. Ruxsatlar, retention va backup/o‘chirish siyosati kelishiladi.

**Xabarnoma:** asosiy biznes o‘zgarishi bilan bir tranzaksiyada outbox eventi yaratiladi. Commitdan keyin worker mijoz tilida Telegram yuboradi va in-app xabarni saqlaydi. Retry/dedupe, muvaffaqiyatsizlik holati va kuzatuv bo‘lsin; bot xatosi muvaffaqiyatli to‘lov/order amalini qayta bajartirmasin. Telegramda aynan bir marta yetkazilish kafolati taxmin qilinmaydi; imkon qadar takrorlarni kamaytirish va jo‘natish holatini saqlash kerak.

Eventlar: usta qabul qildi, ko‘rik/jadval o‘zgardi, smeta taklifi/qayta tasdiq, shartnoma tayyor, to‘lov tasdiqlangan/kvitansiya, prep/delivery/ETA, material muammosi, ish tugadi, nizo/qaror, yopilish va reyting so‘rovi. Mijozga usta tayinlanganining qabul xabari acceptdan oldin yuborilmaydi.

**Usta deadline:** server job muddati o‘tgan pending assignmentni tekshiradi; staffga bir marta/dedupe bilan ogohlantiradi. Allaqachon accept/reject/superseded bo‘lsa eski job ta’sir qilmaydi. Avtomatik usta qayta tayinlanmaydi; do‘kon uchun alohida timer yo‘q.

**ETA:** prep vaqtini shop qo‘lda beradi, yo‘l vaqtini keyin tanlanadigan routing provayderi. `eta`, `eta_source`, `calculated_at`, kerak bo‘lsa unavailable sababi qaytariladi. Har qismning ETA/statusi alohida; mijozga o‘zgarish xabari bor. Jonli kuryer koordinatalari yig‘ilmaydi. Xato yoki noma’lum ETA namunaviy soat bilan almashtirilmaydi.

**Audit:** muhim biznes amali bilan atomik server yozuvi: actor ID/role, amal, obyekt, oldingi/keyingi zarur qiymatlar, server vaqti, request/event ID. Staff/partner nomi snapshot bo‘lishi mumkin, lekin yagona identity emas. UI audit create/edit/delete qila olmaydi; DB/application vakolatlari bilan append-only himoya va backup belgilanadi. Parol, bot token, raw initData yoki keraksiz media/PII audit/logga ko‘chirilmaydi. Bir commandning umumiy/detail auditlari o‘zaro bog‘liq bo‘lsin, takror moliyaviy hodisa hisoblanmasin.

## 12. DTO va command namunalari

Quyidagi JSONlar kontraktni tushuntiruvchi **fragmentlar**; to‘liq serializer/OpenAPI sxemasi emas. ID, summa va vaqtlar namuna.

Staff order detail fragmenti:

```json
{
  "id": "9d7b015e-3d8f-4a67-a6b3-39c3bc282501",
  "number": "S-2026-000001",
  "version": 8,
  "status": "contract",
  "customer_id": "ce0a11bf-c536-47a7-8d84-ccbf9209c2b1",
  "location": { "latitude": "40.500000", "longitude": "72.330000" },
  "current_estimate": {
    "id": "b5e213e1-15ac-4fe2-a640-f292941c0c81",
    "version": 2,
    "status": "approved",
    "currency": "UZS",
    "totals": {
      "services": "300000.00",
      "materials": "500000.00",
      "delivery": "20000.00",
      "emergency": "0.00",
      "platform_fee": "0.00",
      "total": "820000.00"
    }
  },
  "finance": {
    "paid": "0.00",
    "balance": "820000.00",
    "advance_required": "246000.00"
  },
  "available_actions": ["create_contract"],
  "blocked_actions": [
    { "action": "start_preparation", "reason_code": "signed_contract_required" }
  ]
}
```

`available_actions` UX uchun; server baribir har commandni tekshiradi. Block sabablarining to‘liq ro‘yxati yoki birinchi sababni qaytarish siyosati OpenAPIda belgilanadi. Mini App DTOsidan staff-only finance va ichki maydonlar chiqarib tashlanadi.

Staff usta tayinlashi:

```http
POST /api/v1/admin/orders/9d7b015e-3d8f-4a67-a6b3-39c3bc282501/assign-plumber/
Content-Type: application/json
Idempotency-Key: assign-example-001
X-CSRFToken: <session-auth-tanlansa-csrf-token>

{
  "expected_version": 1,
  "plumber_id": "352fe9da-4e7e-41c8-9168-d69e3e3dc8b4",
  "reason": "Hudud va xizmat yo‘nalishi mos."
}
```

Avans yozuvi (tashqi pul o‘tkazmasi emas):

```json
{
  "expected_version": 10,
  "order_id": "9d7b015e-3d8f-4a67-a6b3-39c3bc282501",
  "type": "advance",
  "method": "cash",
  "amount": "100000.00",
  "currency": "UZS",
  "collector": "center",
  "occurred_at": "2026-10-20T14:35:00+05:00",
  "note": "Markazda qabul qilindi."
}
```

Staff markazda qabul qilsa oluvchi serverdagi current staffdan olinadi; boshqa haqiqiy oluvchi uchun tekshiriladigan reference kerak. Usta Mini Appidan `collector=center` yuborib markaz pulini qayd qila olmaydi. `recorded_by`, `confirmed_by`, `status` va `timestamp`ni browser o‘zi tasdiqlamaydi.

## 13. Hisobot va eksport semantikasi

Hozir `Reports.tsx` sana filtrini buyurtma yaratilgan vaqtiga, payments/ratingsda ularning sanasiga ham qo‘llaydi. Backendda bu jim ikki marta toraytiradigan filtrga aylanmasin: `date_basis` (`order_created`, `payment_occurred`, `review_created`) va interval semantikasi hujjatlashtirilsin; UI tanlangan asosni ko‘rsatsin.

Calendar filter `Asia/Tashkent`dagi kun boshidan keyingi kun boshigacha yarim ochiq intervalga aylantiriladi. Dashboarddagi taqqoslash davri, status konversiyasi va komissiya daromadining davrga kirish vaqti aniq belgilanadi. Demo davri eng yangi seed sanasiga bog‘langan bo‘lishi mumkin; server haqiqiy so‘ralgan davrdan foydalanadi.

Har hisobot `applied_filters`, vaqt asosi, totals va noma’lum summalar sonini beradi. `null` qiymatlarni 0 deb yashirmang. Published reytinglargina ommaviy o‘rtachaga kiradi; admin moderatsiya statistikasi alohida.

CSV/XLSX bir xil server query/agregatidan olinadi va **filtrlangan barcha ruxsatli yozuvlarni** qamraydi, faqat joriy sahifani emas. Eksport bir izchil snapshot/as-of vaqtiga ega bo‘lsin; katta natija fon jobi. CSVda UTF-8, satr/quote escaping va spreadsheet formula injection himoyasi; XLSXda ishonchsiz matn formula sifatida yozilmaydi. Download paytida ham staff ruxsati qayta tekshiriladi; faylning amal muddati belgilanadi.

## 14. Reactni APIga ulash tartibi

1. `src/domain/types.ts` — hozirgi UI modeli; API DTO turlari alohida yoziladi. `snake_case → camelCase`, ID/label, enum, nullable pul va sanalar adapterda xaritalanadi. Schema validation yoki typed client OpenAPIga mos bo‘lsin.
2. Yangi `src/api/` qatlami: HTTP client, auth/CSRF, typed errors, DTOlar, adapterlar, resource/command funksiyalari. Kutubxona tanlovi texnik qaror; dependency avtomatik almashtirilmaydi.
3. `src/app/store.tsx`dagi butun `Database` clone/mutate API rejimida server o‘rnini bosmaydi. Hozir §17dagi connector JSON/API o‘qishni ajratadi; API yozish bloklangan. Keyingi bosqichda sahifa bo‘yicha query/cache va server commandlari qo‘shiladi. Eski `VITE_DATA_MODE` o‘rniga `PUBLIC_API_MOCK` ishlatiladi.
4. `src/features/orders/useOrderActions.tsx` umumiy lokal mutation o‘rniga aniq commandlarga ulanadi. Demo customer approval/material receipt/work acceptance va hamkor status simulyatsiyasi API rejimida olib tashlanadi yoki tegishli rol ekraniga o‘tadi.
5. `EstimatePanel.tsx`, `ContractPanel.tsx`, `ProcessPanel.tsx` server versiyalari, PDF job holati, ruxsatli command va block sabablarini ko‘rsatadi. `OrderFinancePanel.tsx` va `PaymentDialog.tsx` server finance summaryga tayanadi. `src/domain/rules.ts` faqat UX preview bo‘lib qolishi mumkin; haqiqiy moliya serverdan.
6. Pul satrini tekshirmasdan `Number()`ga aylantirmang. Hozirgi `MoneyValue = number | null` uchun aniqlik/range kontrakti kelishiladi yoki decimal-aware view model/formatterga o‘tiladi. Moliya server qaytargan summalardan qayta hisoblanmaydi.
7. API POSTda dialog submiti takror bosilishdan himoyalanadi. Network timeout natija bo‘lmadi degani emas: xuddi shu idempotency key bilan qayta so‘raladi yoki resource holati olinadi. Har yangi biznes amal yangi key oladi.
8. Money/approval/signed snapshotlar optimistik o‘zgartirilmaydi. Muvaffaqiyatdan keyin order, finance, payments, timeline, audit, dashboard va tegishli report cachelari yangilanadi. `409`da joriy ma’lumot olinib, foydalanuvchiga konflikt ko‘rsatiladi; majburan overwrite yo‘q.
9. `DataTable` server pagination/order/filter oladi; faqat yuklangan sahifani lokal filtrdan o‘tkazib to‘liq natija deb ko‘rsatmang. Qidiruv debounce/cancel, loading/empty/error/retry va field-error mapping qo‘shiladi.
10. Productionda haqiqiy auth/session expiry/logout, role-aware UI, private media va downloads ishlasin. API ishlamasa mock seedga yashirin fallback qilinmasin; xato ko‘rsatilsin. Demo reset haqiqiy bazaga ta’sir qilmasin.
11. Nginx SPA fallback `/api/` xatolarini `index.html`ga aylantirmasligi kerak; API faqat backendga proxy. Backend domen/origin va CSRF/CORS sozlamasi mavjud frontend hostingiga mos kelishiladi. Productionda yangi tizim uchun migration, backup/restore va deployment alohida tayyorlanadi.

## 15. Implementatsiyadan oldin aniq belgilanadigan masalalar

| Masala | Holat / kerakli qaror |
| --- | --- |
| Haqiqiy katalog, hududiy stavkalar, birlik/markalar | TZ §15da ochiq; demo seed production katalogi emas |
| Markaz kontaktlari, ish vaqti, javob muddati, real hamkorlar | TZ §15; urgent uchun qaysi vaqt hodisasi va jadval istisnolari ham belgilanadi |
| Avans/komissiya qiymatlari | TZ §15; 0ga ruxsat, fixed > total, ortiqcha oldindan to‘lov va shartlar qachon snapshot bo‘lishi |
| Yetkazish/urgent tushum oluvchisi | TZ komissiya bazasini belgilagan, daromad taqsimoti to‘liq emas; buxgalteriya qarori |
| Pul, miqdor va foiz aniqligi/yaxlitlash | Demo whole-UZS algoritmi tasdiqlangan talab emas |
| Mijoz to‘lovi tasdig‘i | Qaysi receipt darhol posted/qaysi staff tasdig‘ini kutadi; ikkinchi boshqa xodim majburiymi — hozir belgilanmagan |
| Terminal mablag‘i | Markaz yoki ustadagi terminal tushumi qaysi hisobga boradi, hujjati qanday tekshiriladi |
| Bekor qilish va qisman refund/hamkor xarajati | TZdagi umumiy qoida, kompaniya sababli istisnolar; yurist/buxgalter bilan qaror |
| Materiallarsiz xizmat va qisman yetkazishda ish boshlash | Shop/to‘rt imzo/material receipt guardlarining muqobil oqimi aniq emas |
| Tayyorgarlik/ish boshlanganidan keyingi narx o‘zgarishi | TZ tayyorlashdan oldingi reapprovalni belgilaydi; keyingi qo‘shimcha ish/change-order yo‘li belgilanmagan |
| Reyting tahriri/soni | Har order/customer/target uchun bitta aktiv baho taklifi; qayta tahrir/moderatsiya siyosati |
| ETA provayderi va unavailable ko‘rinishi | TZ §12,15; qo‘lda taxmin real routing integratsiyasini almashtirmaydi |
| Auth/session, API versiyalash, baza/hosting/worker/storage | Ushbu hujjatda taklif; versiyalar va servislar hali alohida texnik qaror |
| Shartnoma, QQS/fiskal, maxfiylik/retention | TZ §15: huquqiy va buxgalteriya tekshiruvi, tasdiqlangan matn/saqlash muddati |

Ochiq masalalar mustaqil modullar yozilishini to‘xtatmaydi. Ularga bog‘liq haqiqiy operatsiya esa kelishilmagan qiymatni taxmin qilib bajarilmaydi.

## 16. Amalga oshirish ketma-ketligi va qabul mezonlari

1. **Kontrakt va asos:** ochiq qarorlarni qayd etish, OpenAPI, model/migratsiyalar, auth/object permissions, audit, transaction/idempotency va muhitlar.
2. **Katalog va order:** profillar, tariflar, rozilik, qo‘lda assignment, javob/rad tarixi, deadline, Mini App rol amallari.
3. **Smeta va shartnoma:** versiyalar, server narxlari, approve/reject, qayta tasdiq, immutable snapshot/PDF/to‘rt imzo.
4. **Moliya va bajarish:** receipts/confirm/ledger, avans guardi, prep/delivery/material receipt, work acceptance, dispute/cancel/refund/settlement.
5. **Integratsiya:** React API rejimi, Telegram/outbox, private media, routing ETA, dashboard/hisobot/CSV/XLSX; keyin production readiness.

Boshqa kompyuterda avtomatik tekshiriladigan asosiy ssenariylar:

- Begona order/detail/list/create/command/file/export va boshqa rol actor IDsi bilan ruxsatni chetlab bo‘lmaydi. Mijozga shop telefoni va staff moliyaviy breakdown chiqmaydi; usta telefoni acceptdan oldin yashirin.
- Soxta/eskirgan Telegram initData qabul qilinmaydi; inactive identity/session ishlamaydi; cookie mutationlar CSRFsiz bajarilmaydi.
- Deadline qayta tayinlangan eski urinishni o‘zgartirmaydi; auto reassignment va shop timer yaratilmaydi.
- Rad qilingan smetani o‘sha usta qayta yubora olmaydi. Eski versiya approvali yangi smetaga o‘tmaydi; katalog/andoza tahriri approved/signed tarixini o‘zgartirmaydi.
- Tasdiqlangan smeta, mos to‘rt imzo va yetarli avanssiz prep boshlanmaydi. Parallel cancel/prep to‘g‘ri refund chegarasini saqlaydi.
- Qisman yetkazish bir martalik delivery haqini ko‘paytirmaydi; delivered va customer receipt farqlanadi. Mijoz ishni qabul qilmaguncha balance, nizoda yakuniy hisob-kitob bloklanadi.
- Bir xil idempotency key/retry bitta payment/approval/audit biznes hodisasi yaratadi; parallel ikki payout/refund/confirm limitdan oshmaydi. Handover/payout tushumni ikki marta ko‘paytirmaydi; posted yozuvni oddiy PATCH/DELETE qilib bo‘lmaydi.
- Komissiya bazalari, null/0, tanlangan yaxlitlash, avans va refund/invariantlar serverda hisoblanadi; frontend summani almashtirib o‘ta olmaydi.
- PDF snapshotga mos, private media begonalarga yopiq; job/Telegram xatosi order/paymentni qayta bajarmaydi. Mijoz xabarlari o‘z tilida.
- Report sanalari/aggregatlari va CSV/XLSX to‘liq filtrlangan dataset bilan mos; yashirin field/formula injection chiqmaydi. Pending/hidden reyting ommaviy o‘rtachaga qo‘shilmaydi.
- React refreshdan keyin real data saqlanadi; server xatosida mockga o‘tmaydi; loading/error/conflict/session expiry hamda desktop/mobil oqimlar tekshiriladi.

Yakuniy topshiriladiganlar: backend manba kodi va migratsiyalar, OpenAPI, tasdiqlangan qarorlar ro‘yxati, muhit konfiguratsiyasi namunasi (sirlarsiz), testlar/natijalar, React integratsiyasi, ishga tushirish/backup/restore ko‘rsatmasi. **Bu hujjatning o‘zi backend yoki API amalga oshirildi degani emas.**

## 17. PUBLIC_API_MOCK va PUBLIC_API_BASE_URL — joriy ulanish

Bu bo‘lim frontendda hozir yozilgan GET connector kontrakti. §5–16dagi to‘liq biznes API loyihasini almashtirmaydi.

```dotenv
# Statik demo:
PUBLIC_API_MOCK=True
PUBLIC_API_BASE_URL=/api/v1/admin/

# Real o‘qish rejimi uchun True o‘rniga False yozing.
# PUBLIC_API_BASE_URL=https://api.example.com/api/v1/admin/
```

Sozlamalar build vaqtida olinadi. `PUBLIC_API_MOCK` True/False satrlarini case-insensitive o‘qiydi; noto‘g‘ri/bo‘sh qiymat xato, umuman yo‘q bo‘lsa default True. False va bo‘sh base URL — xato. Env o‘zgarsa dev restart yoki production rebuild kerak. Vite uchun `PUBLIC_API_` prefiksi ochilgan; sirlarni bu o‘zgaruvchilarga qo‘ymang.

### 17.1. Mock JSON

`GET /mock/database.json` (`import.meta.env.BASE_URL` hisobga olinadi) `public/mock/database.json`ni yuklaydi. Faylda barcha fixture qiymatlari statik berilgan: profillar, kataloglar, 18 order, to‘lov, reyting, andozalar, audit va sozlamalar. `orderDefaults`, `estimateDefaults`, `contractDefaults` va `estimates`/`contracts` dictionarylari takror ma’lumotni qisqartiradi. Har order `estimateId`, nullable `confirmedEstimateId`, `contractId` orqali JSONdagi snapshotni tanlaydi; bu backend resource ID kontrakti emas, faqat fixture formati.

`src/data/mock.ts` shu reference/defaultlarni mustaqil nusxalarga ochadi. Narx/status/sana tasodifiy generatsiya qilinmaydi; confirmed estimate va current estimate bir objectga bog‘lanmaydi. `src/data/seed.ts` testlar uchun aynan shu JSON adapteridan foydalanadi; ilova seed generatorni ishlatmaydi. Lokal mutation diskdagi JSONni o‘zgartirmaydi; reset faylni qayta yuklaydi.

### 17.2. Real GET endpointlari

`PUBLIC_API_MOCK=False` bo‘lsa quyidagi yo‘llar base URLga qo‘shiladi. Base URL **staff API prefiksi** bo‘lishi kerak (masalan `/api/v1/admin/`), faqat host yoki `/api/v1/` emas. Oxirgi slash avtomatik qo‘shiladi.

| GET suffix | Context kolleksiyasi |
| --- | --- |
| `customers/` | customers |
| `plumbers/` | plumbers |
| `shops/` | shops |
| `services/` | services |
| `materials/` | materials |
| `orders/` | orders |
| `payments/` | payments |
| `reviews/` | reviews |
| `contract-templates/` | templates |
| `audit-events/` | audit |
| `settings/` | settings object |

Ro‘yxat javobi oddiy massiv yoki `{ "count": 18, "next": "?page=2", "previous": null, "results": [] }`. `next` null bo‘lguncha sahifalar olinadi. Settings to‘g‘ridan-to‘g‘ri object. `Content-Type: application/json` yoki `+json` kerak; SPA HTML fallback rad etiladi. Cookie uchun `credentials: include`; login/sessionni backend ta’minlaydi, connector login yoki maxfiy token yaratmaydi.

**Hozirgi UI compatibility DTO:** har record `src/domain/types.ts`dagi camelCase maydonlar va ichki object/arraylar bilan to‘liq bo‘lishi kerak. Pul/miqdorlar finite JSON number yoki ruxsat etilgan joyda null, sanalar parse qilinadigan ISO satr, unset jadval vaqti bo‘sh satr. `orders/` hozir detailga kerakli estimate, confirmedEstimate, contract, deliveries va timeline ma’lumotlarini ham beradi. Ularning shakli `src/data/schema.ts`da tekshiriladi; noma’lum enum/reyting, yetishmagan nested maydon, noto‘g‘ri sana va takror ID yuklash xatosiga olib keladi.

Bu talab §5dagi taklif etilgan snake_case/decimal-string biznes DTOdan **vaqtinchalik farq qiladi**. Backend compatibility serializer berishi yoki keyingi integratsiyada aniq DTO adapter yozilishi kerak. Decimal satrlarni jimgina floatga o‘giruvchi yoki snake_case maydonlarni taxmin qilib o‘zgartiruvchi adapter yo‘q. Server o‘z moliyaviy hisoblarida Decimal va snapshot qoidalarini saqlaydi. Hozirgi UI hisoblari ko‘rish uchun lokal preview, server moliyaviy ledgeri o‘rnini bosmaydi.

Joriy context barcha kolleksiyalarni ko‘rishni talab qilgani uchun connector API sahifalarini birlashtiradi; bu kichik pilot uchun oraliq o‘qish yechimi. Bitta kolleksiya 10 000 yozuv yoki 200 sahifadan oshsa xato beriladi, jim kesilmaydi. Keyingi ishlab chiqarish integratsiyasida §14dagi sahifaga xos querylar va server agregatlari kerak; katta bazani brauzerga to‘liq yuklash maqsad emas.

### 17.3. Rejim va xatolar

- Mockda JSONdan olingan lokal ma’lumot o‘zgaradi; backendga POST/PATCH yuborilmaydi.
- Real rejimda GET natijasi ko‘rsatiladi; eski demo mutation/reset bloklanadi. Yozish endpointlari hali ulanmagani UI banneri, forma va tasdiqlash dialogida ko‘rsatiladi.
- API tarmoq/HTTP/schema xatosida mockga fallback yo‘q. Loading, xato va qayta urinish bor; real profilda serverdan yangilash bor. Muvaffaqiyatsiz yuklashda qisman dataset ko‘rsatilmaydi.
- Har request uchun 20 soniyalik timeout, unmount/reload uchun abort bor. Pagination havolasi API origin/prefiksidan tashqariga chiqolmaydi, cycle/limit xato beradi; redirectlar kuzatilmaydi.
- Tashqi APIga backend credentialed CORS va frontend CSP `connect-src` ruxsati kerak. Same-origin `/api/` backendga proxy qilinadi; hozirgi statik Nginx config bu proxy yoki backend manzilini o‘zicha taxmin qilmaydi.

`src/data/config.test.ts`, `src/data/source.test.ts` va JSON yuklash/retry E2E ssenariysi yozilgan. Ular bu kompyuterda bajarilmadi.

## Boshqa kompyuterda

Backendni shu kontrakt bo‘yicha amalga oshiring; migratsiya, test, build va integratsiya tekshiruvlarini o‘sha kompyuterda bajaring. Backend papkasi va buyruqlari hali yaratilmagani sababli bu yerda taxminiy ishga tushirish buyrug‘i berilmadi.
