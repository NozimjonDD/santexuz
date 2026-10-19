# Admin CRM — ReactJS statik UI spetsifikatsiyasi

**Loyiha:** Santexnika xizmatlari Telegram Mini App  
**Hujjat maqsadi:** ReactJS admin CRM interfeysini backend ulanmasdan, mock ma’lumotlar bilan qurish uchun ekranlar va o‘zaro ta’sirlarni belgilash  
**Manba:** `TZ_docs.md`  
**Bosqich:** MVP — Andijon viloyati, Marhamat tumani  
**UI tili:** O‘zbekcha  
**Valyuta:** UZS

> Ushbu hujjat UI qurish spetsifikatsiyasi. API, ma’lumotlar bazasi, autentifikatsiya integratsiyasi va serverdagi biznes mantiqni amalga oshirish doirasiga kirmaydi. Hozircha ekranlar lokal mock ma’lumotlardan foydalanadi.

## 1. CRM maqsadi

Xizmat markazi xodimi bitta web CRM orqali:

- yangi mijoz so‘rovlarini ko‘radi va santexnikka tayinlaydi;
- ko‘rik, smeta, do‘kon, shartnoma va buyurtma jarayonini kuzatadi;
- mijozlar, santexniklar, do‘konlar va kataloglarni boshqaradi;
- avans, to‘lov, komissiya, hamkorlarga hisob-kitob va qarzdorlikni nazorat qiladi;
- nizolar va reytinglarni ko‘rib chiqadi;
- muhim amallar jurnalini ko‘radi.

## 2. UI doirasi va asosiy qoidalar

1. Bu responsive web CRM; mijoz/usta/do‘kon Mini App ekranlari ushbu CRM doirasiga kirmaydi.
2. UI ReactJS’da quriladi. CRM backend bilan keyinchalik Django REST Framework API orqali ulanadi; hozircha API so‘rovlari yozilmaydi.
3. Barcha ro‘yxatlar, kartalar va grafiklar mock ma’lumot bilan ishlaydi. Qidirish, filtr, sahifalash, modal va tablar frontend holatida ishlashi kerak.
4. Tugmalar ko‘rinish uchun emas: mock rejimida modal ochish, forma validatsiyasi, lokal holatni o‘zgartirish, toast xabari yoki tegishli sahifaga o‘tish kabi aniq javob qaytaradi.
5. Narxlar `1 250 000 so‘m` ko‘rinishida formatlanadi. Valyuta UZS; QQS narxlarga kiritilgan.
6. Tasdiqlangan smeta — buyurtmaga saqlangan alohida nusxa; keyinchalik katalogdagi narx o‘zgarishi buyurtma summasini o‘zgartirmaydi.
7. Xizmat markazi xodimlari alohida akkauntga ega bo‘lsa-da, bu statik UI’da login oqimi simulyatsiya qilinmaydi. CRM ochilganda boshqaruv paneli ko‘rsatiladi.
8. Do‘kon bitta umumiy akkaunt ishlatadi. Auditda do‘kon akkaunti nomidan qilingan amal ko‘rinadi, alohida do‘kon xodimi ko‘rsatilmaydi.
9. Admin ruxsatlari to‘liq; xavfli amallarda tasdiqlash modali ishlatiladi. Server darajasidagi ruxsat nazorati keyingi backend ishidir.
10. Noma’lum manzil, tarif, komissiya va boshqa qiymatlar haqiqiydek ko‘rsatilmasin; namuna ma’lumotlari demo deb aniq belgilansin.

## 3. Navigatsiya va sahifalar

Chap panel doimiy navigatsiya, yuqori panel esa joriy hudud, global qidiruv va foydalanuvchi menyusini ko‘rsatadi.

| Menyu | Yo‘l | Sahifa vazifasi |
|---|---|---|
| Bosh sahifa | `/dashboard` | Operatsion va moliyaviy qisqa ko‘rsatkichlar |
| Buyurtmalar | `/orders` | Barcha so‘rov/buyurtmalar, qidirish va filtrlar |
| Mijozlar | `/customers` | Mijozlar ro‘yxati va buyurtma tarixi |
| Santexniklar | `/plumbers` | Ustalar, hudud/xizmat mosligi, reyting va holat |
| Do‘konlar | `/shops` | Do‘konlar, umumiy Telegram akkaunt va buyurtmalar |
| Katalog | `/catalog/services` | Xizmatlar va tariflar |
| Materiallar | `/catalog/materials` | Mahsulot katalogi |
| Moliya | `/finance` | To‘lovlar, komissiyalar, qarzdorlik, hamkor hisob-kitobi |
| Shartnomalar | `/contracts` | Shartnoma andozalari va versiyalari |
| Reytinglar | `/reviews` | Moderatsiya navbatidagi va chop etilgan baholar |
| Hisobotlar | `/reports` | Filtrlanadigan va eksport qilinadigan hisobotlar |
| Audit jurnali | `/audit` | Muhim amallar tarixi |
| Sozlamalar | `/settings` | Hudud, xizmat markazi, ish vaqti, umumiy sozlamalar |

Menyu guruhlari:

- **Ish jarayoni:** Bosh sahifa, Buyurtmalar
- **Hamkorlar:** Mijozlar, Santexniklar, Do‘konlar
- **Katalog va moliya:** Katalog, Materiallar, Moliya, Hisobotlar
- **Boshqaruv:** Shartnomalar, Reytinglar, Audit jurnali, Sozlamalar

Mobil kenglikda yon menyu yig‘iladi va menyu tugmasi orqali ochiladi. Joriy hudud navigatsiyada `Andijon viloyati / Marhamat tumani — Pilot` deb ko‘rsatiladi.

## 4. Umumiy layout va dizayn

### 4.1. Asosiy layout

- Chap sidebar: taxminan 248 px kenglik, brend nomi/logo, menyu guruhlari, joriy hudud.
- Yuqori toolbar: sahifa sarlavhasi/breadcrumb, global qidiruv, xabarnoma belgisi, foydalanuvchi nomi va menyu.
- Asosiy kontent: oq/och fon, maksimal foydalanish kengligi; jadval sahifalarida gorizontal scroll faqat kichik ekranlarda.
- Har sahifa sarlavhasi: nom, qisqa izoh, asosiy amal tugmasi.
- UI Uzbek lotin yozuvida. Vaqt formati `18.10.2026, 14:35`; telefon formati `+998 XX XXX XX XX`.

### 4.2. Vizual uslub

- Ishonchli, sodda CRM: och kulrang fon, oq kartalar, to‘q matn, ko‘k asosiy amal rangi.
- Statuslar rang va matn bilan birga beriladi; faqat rang bilan farqlanmaydi.
- Xavfli amallar qizil rangda va tasdiqlash dialogi bilan.
- Jadval satrlari aniq hover/focus holatiga ega; muhim summalar va statuslar tez ko‘zga tashlanadi.
- Bir xil tugma, badge, forma maydoni, modal, tooltip va toast uslublari barcha sahifalarda qo‘llanadi.

### 4.3. Responsive xulq

- Katta ekran: sidebar va to‘liq ma’lumotli jadvallar.
- O‘rta ekran: sidebar yig‘iladi; filtrlar ochiladigan panelga joylanadi.
- Kichik ekran: sidebar drawer; keng jadvallar muhim maydonlar saqlangan holda gorizontal aylantiriladi; formalar bir ustun bo‘ladi.
- Jadvaldagi harakat tugmalari mobil ekranda “...” menyusiga yig‘iladi.

## 5. Umumiy UI komponentlari

- `AppShell`: sidebar, toolbar, content container.
- `PageHeader`: sarlavha, izoh, breadcrumb va sahifaga xos asosiy amal.
- `StatCard`: label, qiymat, yordamchi ko‘rsatkich va ixtiyoriy belgi.
- `DataTable`: ustun saralash, sahifa o‘lchami, sahifa almashish, qator amallari, empty/loading/error holatlari.
- `SearchInput`, `DateRangePicker`, `FilterBar`, `FilterDrawer`.
- `StatusBadge`: buyurtma, to‘lov, hamkor va moderatsiya statuslari uchun.
- `Money`: UZS formatidagi pul qiymati; jadval va smetada bir xil format.
- `ConfirmDialog`: bekor qilish, yopish, statusni yakunlash kabi xavfli amallar.
- `FormField`: label, majburiy belgi, yordam matni, xato matni.
- `Toast`: muvaffaqiyat, ogohlantirish va xato bildirishnomasi.
- `EmptyState`: tushunarli izoh va keyingi amal tugmasi.
- `DetailDrawer` yoki `DetailPage`: ro‘yxat elementini tez ko‘rish va tahrirlash.
- `AuditTimeline`: muhim hodisalarni vaqt bo‘yicha ko‘rsatish.
- `FilePreview`: yuklangan rasm/video/PDF uchun preview yoki statik placeholder.

## 6. Ekranlar spetsifikatsiyasi

### 6.1. Bosh sahifa — `/dashboard`

**Sarlavha:** Bosh sahifa  
**Yuqoridagi filtr:** vaqt oralig‘i; hudud ko‘rsatkichi hozircha Marhamat pilotiga mahkamlangan.

**Ko‘rsatkich kartalari:**

- Yangi so‘rovlar
- Santexnik tayinlanishini kutayotganlar
- Smeta/do‘kon javobini kutayotganlar
- Faol buyurtmalar
- Bugungi tushum
- Hamkorlarga to‘lanishi kutilayotgan summa

**Asosiy panellar:**

- “Diqqat talab qiladi”: santexnik javob muddati o‘tgan so‘rov, do‘kon rad etgan buyurtma, smeta mijoz tasdig‘ini kutayotgan buyurtma, kechikkan yetkazish, mijoz nizosi.
- “Buyurtmalar holati”: bosqich bo‘yicha sonlar.
- “Oxirgi buyurtmalar”: raqam, mijoz, santexnik, status, jami va vaqt.
- “Moliyaviy qisqacha”: mijozlardan tushgan summa, avans, qoldiq, komissiya, hamkorlarga to‘langan/to‘lanmagan summa.

Kartani bosganda mos ro‘yxat sahifasi filtr bilan ochiladi. Grafiklar mock ma’lumot bilan; natijalar yo‘qligida empty state ko‘rinadi.

### 6.2. Buyurtmalar ro‘yxati — `/orders`

**Yuqori qism:**

- Sarlavha `Buyurtmalar`; “Yangi so‘rov” tugmasi (faqat CRM orqali admin buyurtma kiritishi kerak bo‘lsa mock modal ochadi).
- Tezkor tablar: Barchasi, Yangi so‘rovlar, Tayinlash kerak, Faol, Nizo, Yakunlangan, Bekor qilingan.
- Qidiruv: buyurtma raqami, mijoz ismi/telefon, santexnik, do‘kon.
- Filtrlar: status, xizmat guruhi/turi, santexnik, do‘kon, shoshilinch, yaratilgan sana, to‘lov holati.

**Jadval ustunlari:**

`Buyurtma raqami` · `Mijoz` · `Xizmat` · `Santexnik` · `Do‘kon` · `Status` · `Jami` · `Yaratilgan vaqt` · `Amallar`

Qator bosilganda `/orders/:id` tafsilot sahifasi ochiladi. Buyurtma raqami va shoshilinch belgisi ko‘zga aniq tashlanadi.

**Qator amallari:**

- Ko‘rish
- Santexnik tayinlash/qayta tayinlash
- Do‘kon tayinlash/qayta tayinlash
- Mijoz bilan telefon orqali bog‘lanish uchun telefonni ko‘rish
- Bekor qilish/yopish (tasdiqlash modali bilan)

### 6.3. Buyurtma tafsiloti — `/orders/:id`

**Sahifa sarlavhasi:** buyurtma raqami, joriy status badge, yaratilgan sana, “Ro‘yxatga qaytish”.

**Yuqori amallar statusga qarab:**

- Santexnik biriktirish / boshqa santexnikka o‘tkazish
- Do‘kon biriktirish / boshqa do‘konga o‘tkazish
- Statusni tasdiqlash yoki bekor qilish
- Admin izohi qo‘shish
- PDF shartnomani ko‘rish (statik preview)

**Tablar:**

1. **Umumiy:** mijoz, manzil, xarita nuqtasi placeholder, aloqa, xizmat guruhi, shoshilinch holati, muammo izohi va ilovalar.
2. **Smeta va materiallar:** xizmat qatorlari (xizmat nomi, birlik, miqdor, birlik narxi, jami); material qatorlari (nom, marka/izoh, miqdor, birlik, do‘kon narxi, mavjudlik); yetkazish, shoshilinch haq, jami.
3. **Jarayon:** vaqt jadvali, santexnik tayinlash, qabul/rad, ko‘rik sanasi, do‘kon javobi, tayyorlash va ETA, qisman yetkazishlar.
4. **Shartnoma:** andoza versiyasi, tanlangan til, hujjat statusi, to‘rt tomon imzo holati, kim/qachon “imzolandi” deb belgilagan.
5. **To‘lov va hisob-kitob:** avans, qoldiq, usul, kvitansiya, naqd topshirish, do‘kon/santexnik komissiyasi va hisob-kitob. Komissiya ma’lumoti admin ko‘rinishida.
6. **Nizo va baho:** mijoz e’tirozi, media preview, admin izohlari, moderatsiya statusi va mijoz bahosi.
7. **Audit:** faqat shu buyurtmaga taalluqli amallar.

**Smeta tasdiqlash UI qoidalari:**

- Har qanday o‘zgarish order ichidagi smeta nusxasini yangi versiya qiladi.
- Tasdiqlangan summa, yangi taklif etilgan summa, farq va avansdagi o‘zgarish aniq ajratiladi.
- Mijoz qayta tasdiqlamaguncha “Tasdiqlandi” ko‘rsatilmaydi; material tayyorlash statusi boshlanmaydi.
- Mock rejimida “Mijozga qayta tasdiqlash so‘rovini yuborish” tugmasi statusni `Tasdiq kutilmoqda`ga o‘tkazadi.

### 6.4. Santexniklar — `/plumbers`

**Jadval ustunlari:** ism, telefon, Telegram akkaunt bog‘langan/bog‘lanmagan, xizmat yo‘nalishlari, hudud, reyting, faol buyurtmalar, hisob holati, faol/no-faol.

**Amallar:** yangi santexnik, profilni ko‘rish/tahrirlash, faol/no-faol qilish, xizmat va hududni belgilash, akkaunt bog‘lash.

**Yangi/tahrirlash formasi:**

- Ism-familiya (majburiy)
- Telefon (majburiy, `+998` format)
- Telegram user ID yoki bot orqali akkaunt bog‘lash uchun identifikator
- Profil rasmi
- Tajriba (yil)
- Xizmat yo‘nalishlari (multi-select)
- Xizmat ko‘rsatadigan hudud
- Admin yozuvi (mijozga ko‘rsatilmaydi)
- Faol holati

**Tafsilot sahifasi tablari:** Profil, Faol/yakunlangan buyurtmalar, Reytinglar, Hisob-kitob, Audit tarixi.

> Akkauntni ro‘yxatdan o‘tkazish yoki Telegram tasdiqlash statik UI’da backendga ulanmaydi; ko‘rinish mock holat bilan ko‘rsatiladi.

### 6.5. Do‘konlar — `/shops`

**Jadval ustunlari:** do‘kon nomi, manzil, hudud, umumiy Telegram akkaunt, qabul qilingan/rad etilgan buyurtmalar, reyting, faol holati.

**Forma maydonlari:** do‘kon nomi, yuridik/aloqa nomi (agar mavjud bo‘lsa), manzil, hudud, telefon (faqat admin ko‘radi), Telegram akkaunt identifikatori, tavsif, faol holati.

**Tafsilot tablari:** Profil, Buyurtmalar, Komissiya va hisob-kitob, Reytinglar, Audit.

Do‘kon xodimi kesimidagi foydalanuvchilar yoki loginlar UI’da yaratilmaydi; bitta umumiy do‘kon akkaunti ko‘rsatiladi.

### 6.6. Xizmatlar katalogi — `/catalog/services`

**Ro‘yxat ustunlari:** xizmat nomi, guruh, birlik, Marhamat tarif, shoshilinch qo‘shimcha tarif, kafolat muddati, mijozga ko‘rinadi/ko‘rinmaydi, faol.

**Filtrlar:** guruh, faol holati, tarif kiritilgan/kiritilmagan.

**Yangi/tahrirlash formasi:**

- Xizmat nomi (o‘zbekcha; ruscha va inglizcha nomlar ixtiyoriy tarjima maydonlari)
- Guruh: ta’mirlash, o‘rnatish/almashtirish, quvur/kanalizatsiya, isitish
- O‘lchov birligi (dona, nuqta, holat, metr, m² yoki admin kiritadigan birlik)
- Hudud va birlik tarifi (UZS)
- Shoshilinch chaqiruv qo‘shimcha haqi (UZS; hudud/xizmat bo‘yicha)
- Kafolat muddati (kun/oy; bo‘sh qiymat “kafolat belgilanmagan”)
- Tavsif
- Faol / mijoz katalogida ko‘rsatish

Narx tahririda tasdiqlash modali ko‘rsatiladi: “Yangi narx faqat yangi smetalarga qo‘llanadi. Eski va tasdiqlangan buyurtmalar o‘zgarmaydi.”

### 6.7. Materiallar katalogi — `/catalog/materials`

**Ro‘yxat ustunlari:** mahsulot nomi, guruh, marka/model, o‘lcham/diametr, birlik, faol.

**Yangi/tahrirlash formasi:** nom (majburiy), guruh, marka/model, diametr/o‘lcham, birlik (dona, metr, komplekt, qadoq va boshqalar), tavsif, faol holati.

Material katalogida umumiy narx majburiy emas; do‘kon buyurtma kelganda ayni mahsulotning narxi va mavjudligini tasdiqlaydi. Erkin material qatorini umumiy katalogga qo‘shish admin uchun ixtiyoriy amal bo‘lishi mumkin.

### 6.8. Mijozlar — `/customers`

**Jadval ustunlari:** mijoz, telefon, Telegram akkaunt, buyurtmalar soni, oxirgi buyurtma, umumiy sarf (admin ko‘rinishi), ro‘yxatdan o‘tgan sana.

**Qidiruv/filtr:** ism/telefon, sana, buyurtmasi bor/yo‘q.

**Tafsilot:** aloqa ma’lumoti, buyurtmalar, to‘lovlar, mijoz izohlari, roziliklar va muhim audit hodisalari. Telefon/manzil faqat ruxsatli CRM kontekstida ko‘rsatiladi.

### 6.9. Moliya — `/finance`

**Yuqori kartalar:** tanlangan davr tushumi, mijozlardan avans, mijoz qoldig‘i, hamkorlarga to‘lanadigan, hamkorlarga to‘langan, platforma komissiyasi, santexnikdan topshirilishi kutilayotgan naqd.

**Sub-navigation:**

- Buyurtmalar bo‘yicha
- Mijoz to‘lovlari
- Santexnik naqd topshirishlari
- Hamkor hisob-kitoblari
- Qarzdorlik

**Jadval ustunlari:** sana, buyurtma, tomon, to‘lov turi, summa, avans/qoldiq/komissiya, status, qayd etgan admin.

**Amallar:**

- “To‘lov qayd etish” modal: buyurtma, to‘lov turi, summa, usul, sana/vaqt, qabul qiluvchi, izoh.
- “Santexnik pulini qabul qilish” modal: santexnik, buyurtma yoki topshirish guruhi, summa, qabul qilgan xodim, izoh.
- “Hamkorga hisob-kitob qayd etish” modal: do‘kon/santexnik, orderlar, jami, komissiya, beriladigan sof summa, to‘lov usuli (naqd), sana, tasdiqlovchi xodim.
- Har bir moliyaviy yozuv uchun tasdiqlash oynasi; tuzatishlar alohida audit hodisasi sifatida ko‘rsatiladi.

### 6.10. Hisobotlar — `/reports`

Hisobot filtrlari: davr, buyurtma statusi, santexnik, do‘kon, xizmat turi.

Hisobot turlari:

- Buyurtmalar va konversiya holatlari
- Material/xizmat summalari
- To‘lovlar, avans va qoldiqlar
- Do‘kon va santexnik komissiyalari
- Hamkorlarga to‘langan/to‘lanmagan summalar
- Santexnik/do‘kon reytingi

“CSV eksport” va “Excel eksport” tugmalari mock rejimida formatlangan namunaviy faylni yuklash/yaratish o‘rniga demo xabari berishi mumkin; export endpoint backend keyin ulanadi. Agar frontendda haqiqiy statik CSV generatsiyasi qilinsa, ekrandagi filtrlangan mock datasetdan foydalanadi.

### 6.11. Shartnomalar — `/contracts`

**Ro‘yxat:** andoza nomi, til, versiya, holat (qoralama/faol/arxiv), yaratilgan vaqt, muallif.

**Yangi versiya yaratish:** andoza nomi, til (UZ/RU/EN), versiya izohi, matn muharriri maydoni, preview va “Qoralama saqlash” / “Faol versiya qilish”.

- Faol andoza tahrirlanganda avvalgi versiya saqlanadi; mavjud imzolangan buyurtma hujjati o‘zgarmaydi.
- O‘zbekcha matn huquqiy ustuvor; RU/EN nusxalari tarjimalar.
- Statik UI matn muharririni ko‘rsatadi; real PDF generatsiyasi/API keyinchalik ulanadi.

### 6.12. Reytinglar — `/reviews`

**Tablar:** Tekshirish kutilmoqda, Ko‘rsatilgan, Yashirilgan.

**Ustunlar:** sana, mijoz, buyurtma, baho (1–5), baholangan tomon (santexnik/do‘kon), izoh, moderatsiya holati.

**Amallar:** ommaga chiqarish, yashirish, izohni to‘liq ko‘rish, buyurtmani ochish. Moderatsiya amali tasdiqlanadi va auditga yoziladi.

### 6.13. Audit jurnali — `/audit`

**Ustunlar:** sana/vaqt, admin akkaunt, amal turi, obyekt (buyurtma/xodim/katalog/to‘lov), obyekt ID, qisqa tafsilot.

**Filtrlar:** davr, admin, amal turi, obyekt turi, qidiruv.

Audit yozuvlari UI’dan tahrirlanmaydi yoki o‘chirilmaydi. Tafsilot modalida oldingi/yangi qiymatlar mock data bo‘lsa ko‘rsatiladi.

### 6.14. Sozlamalar — `/settings`

Tablar:

- **Hudud:** hozirgi pilot Andijon viloyati / Marhamat tumani; keyingi hudud qo‘shish UI’si bo‘lishi mumkin, ammo pilot ma’lumotini almashtirmaydi.
- **Xizmat markazi:** nom, manzil, telefon, ish vaqti.
- **So‘rovlar:** santexnikning so‘rovga javob berish muddati.
- **To‘lov:** avansning default foizi yoki qat’iy summasi; UI’da qiymat belgilanmaguncha “sozlanmagan” holati.
- **Komissiyalar:** rol bo‘yicha standart hamda hamkor bo‘yicha individual foizlar.
- **Til va bildirishnoma:** CRM ichki afzalliklari; Mini App mijoz tili foydalanuvchi tanlovi bo‘lib qoladi.

Har bir sozlama “Saqlash”dan oldin eski/yangi qiymatni tekshiradi, muvaffaqiyat toast beradi. Haqiqiy saqlash backend ulanmaguncha mock-only.

## 7. Statuslar va badge ko‘rinishi

Buyurtmalar ro‘yxatida quyidagi statuslar ishlatiladi; ayni backend enum keyin kelishiladi:

| Status label | UI ma’nosi |
|---|---|
| Yangi so‘rov | Mijoz yuborgan; tayinlash kerak |
| Santexnik tayinlangan | Javob kutilmoqda |
| Santexnik qabul qildi | Ko‘rikni rejalash/kirish |
| Ko‘rik belgilandi | Kelishilgan tashrif vaqti bor |
| Smeta tayyorlanmoqda | Santexnik ma’lumot kiritmoqda |
| Do‘kon javobi kutilmoqda | Do‘kon narx/mavjudlikni kiritmoqda |
| Mijoz tasdig‘i kutilmoqda | Smeta yoki o‘zgarish tasdiqlanishi kerak |
| Shartnoma/avans kutilmoqda | Qog‘oz shartnoma va avans jarayoni |
| Do‘kon tayyorlayapti | Avans/shartnomadan so‘ng yig‘ish boshlangan |
| Qisman yetkazildi | Yetkazishlarning bir qismi tugagan |
| Kuryer yo‘lda | Do‘kon yo‘lga chiqqanini belgilagan |
| Material yetkazildi | Mijoz material qabulini tasdiqlashi mumkin |
| Ish jarayonida | Santexnik ish boshlagan |
| Mijoz tasdig‘i kutilmoqda | Ish yakuni mijoz tomonidan tasdiqlanishi kerak |
| Nizo | Admin ko‘rib chiqishi kerak; qoldiq hisob-kitob bloklangan |
| Yakunlangan | Ish tasdiqlangan, qoldiq to‘langan, buyurtma yopilgan |
| Bekor qilingan | Buyurtma to‘xtatilgan; sabab ko‘rsatiladi |
| Rad etilgan | Santexnik/do‘kon so‘rovni rad qilgan; admin keyingi qarorni qiladi |

Status badge ranglari status guruhlariga ajratiladi: yangi/kutilayotgan — ko‘k; ish jarayoni — sariq; muvaffaqiyat/yakunlangan — yashil; rad/bekor — kulrang; nizo/xato — qizil.

## 8. Formlar, validatsiya va dialoglar

- Majburiy maydonlar `*` belgisi bilan; xato matni maydon tagida o‘zbekcha ko‘rinadi.
- Telefon `+998` formatini tekshiradi; manfiy narx yoki miqdor qabul qilinmaydi.
- Miqdor birlikka mos raqam qabul qiladi; `metr`/`m²` uchun kasrga ruxsat berilishi mumkin.
- Xizmat tarifi 0 bo‘lishiga ruxsat kerak bo‘lsa, bu alohida tasdiqlanadi; noma’lum qiymat “0” emas, “Sozlanmagan” ko‘rsatiladi.
- O‘chirish, bekor qilish, komissiya o‘zgartirish, shartnoma versiyasini faollashtirish uchun tasdiqlash dialogi.
- Modalda nom, nima o‘zgarishi, qaytarib bo‘lmasligi mumkin bo‘lgan ta’sir va ikkita aniq amal tugmasi bo‘ladi.
- Muvaffaqiyat/xato holatida toast; server xatolari API ulangandan keyin forma yoki sahifada inline xato holati sifatida ko‘rsatiladi.

## 9. Mock data uchun tavsiya etilgan tuzilma

Statik UI’ni keyinchalik backendga ulashni yengillashtirish uchun demo ma’lumotlar quyidagi asosiy obyektlarga ajratiladi:

- `Order`: id, createdAt, status, urgency, customerId, plumberId, shopId, address, serviceLines, materialLines, delivery, estimate, paymentSummary, contractSummary, timeline.
- `Customer`: id, name, phone, telegramLinked, orderCount, createdAt.
- `Plumber`: id, name, phone, telegramLinked, serviceCategories, district, rating, activeOrderCount, isActive.
- `Shop`: id, name, address, district, telegramAccountLabel, rating, isActive.
- `Service`: id, name, category, unit, areaRate, emergencyFee, warranty, isActive.
- `Material`: id, name, category, brand, size, unit, isActive.
- `Payment`: id, orderId, payer/payee, type, method, amount, timestamp, recordedBy, status.
- `AuditEvent`: id, actor, action, objectType, objectId, timestamp, summary, before/after.
- `Review`: id, orderId, customerId, targetType, targetId, score, comment, moderationStatus.

Mock data Marhamat pilotining namunaviy to‘plami deb belgilanadi. Buyurtmadagi `estimate` va tarif snapshoti katalogning joriy tarifidan alohida saqlanadi.

## 10. Demo ko‘rinish uchun namuna

Dashboard va jadvallar bo‘sh ko‘rinmasligi uchun bir nechta aniq “DEMO” label bilan test buyurtmalar kiritiladi:

- `DEMO-1001` — yangi so‘rov, santexnik tayinlash kerak.
- `DEMO-1002` — santexnik qabul qilgan, ko‘rik vaqti belgilangan.
- `DEMO-1003` — do‘kon narxi tasdiqlangan, mijoz smeta tasdig‘ini kutmoqda.
- `DEMO-1004` — shartnoma/avans jarayonida.
- `DEMO-1005` — qisman material yetkazilgan.
- `DEMO-1006` — mijoz nizosi, qoldiq hisob-kitob bloklangan.
- `DEMO-1007` — yakunlangan, komissiya va hamkor to‘lovi qayd etilgan.

Bu ma’lumotlar haqiqiy buyurtma yoki mijoz ma’lumotidek ko‘rinmasligi kerak; demo ekanligi UI’da aniq belgilanadi.

## 11. Accessibility va UX talablari

- Asosiy amallar klaviatura orqali boshqariladi; modal fokusni ushlab, yopilganda fokusni boshlang‘ich elementga qaytaradi.
- Form elementlari ko‘rinadigan labelga ega; placeholder label o‘rnini bosmaydi.
- Tugmalarning matni amalni anglatadi: “Saqlash”, “Tayinlash”, “Rad etish”, “Tasdiqlash”.
- Statuslar matn bilan beriladi; rang yagona signal emas.
- Rasm/video preview uchun tavsif, jadvalda bo‘sh holat izohi, ikon tugmalarida tooltip/aria-label.
- Forma xatolari ekran o‘quvchi va ko‘rinadigan matn bilan tushunarli.

## 12. Statik UI uchun yakuniy tayyorlik mezonlari

1. Yuqoridagi barcha sahifalar va yo‘llar orasida navigatsiya ishlaydi.
2. Mock ro‘yxatlarda qidirish, filtr, sort, sahifalash va empty state ko‘rsatiladi.
3. Yangi/tahrirlash formalarida required validation va modal/toast holatlari mavjud.
4. Buyurtma tafsilotida smeta, status timeline, to‘lov, hujjat, nizo va audit alohida bo‘limlarda ko‘rsatiladi.
5. Smeta/komissiya/to‘lovlar UZS formatida; qiymatlar mock data ekanligi aniq.
6. Mobil/o‘rta/katta ekran layoutlari oqilona moslashadi.
7. Foydalanuvchi tasdiqlamagan qiymat 0 yoki “tasdiqlangan” holat sifatida ko‘rsatilmaydi; “Sozlanmagan”, “Kutilmoqda” kabi aniq holat ishlatiladi.
8. Hech bir UI amali backend yoki haqiqiy to‘lov bajarilgandek ko‘rsatmaydi.

## 13. Keyingi integratsiya chegarasi

Statik UI tugagach, DRF API’ni ulashdan avval backend jamoasi bilan autentifikatsiya va rollar, sahifalash/filtrlash formati, buyurtma statuslari, smeta versiyalash, moliyaviy yozuvlar modeli, fayl yuklash, xatolik javoblari va audit yozuvlari kelishiladi. API endpointlari ushbu hujjatda ataylab belgilanmagan.
